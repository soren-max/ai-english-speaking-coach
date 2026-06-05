"""FollowupAgent — Analyzes user answers and generates grounded follow-ups.

Two-phase process:
  1. Analysis:  Scan the user's answer for technical claims, design decisions,
                technologies mentioned, and vague statements.
  2. Generate:  Pick the most promising follow-up point and craft a specific,
                contextual question that probes deeper.

Key principle: every follow-up must be DIRECTLY grounded in what the
user actually said. No generic questions.
"""

import json
from typing import Dict, Any, Optional

from services.deepseek_service import DeepSeekClient
from agents.state import InterviewState


SYSTEM_PROMPT = """You are a senior technical interviewer conducting a live interview.
Your job is to analyze the candidate's answer and generate a single, precise follow-up question.

CRITICAL: You MUST return valid JSON. No markdown. No code fences. No explanation outside JSON.

Two steps:

STEP 1 — ANALYSIS
Scan the candidate's answer for these follow-up signals:
- Technical claims: "I built a system that handles 10K QPS"
- Design decisions: "We chose MongoDB over PostgreSQL"
- Technology mentions: "We used Redis for caching"
- Vague statements: "We used microservices"
- Trade-offs mentioned: "We prioritized availability over consistency"
- Metrics/numbers: "We achieved 99.9% uptime"
- Architecture choices: "Event-driven architecture"

STEP 2 — GENERATION
Select the SINGLE most important follow-up point. Generate exactly ONE question.

CONSTRAINTS for the question:
1. Exactly ONE sentence. One question mark only.
2. Must directly reference something the candidate said (quote exact phrase).
3. Must probe deeper — cannot be answered with yes/no.
4. Must reveal depth of understanding.
5. NEVER ask two things in one question. No "and", "or" that joins two questions.

Return ONLY this JSON — no other text:
{
  "analysis": {
    "key_claims": [],
    "technical_decisions": [],
    "technologies_mentioned": [],
    "vague_areas": [],
    "potential_followup_points": []
  },
  "selected_focus": "",
  "reasoning": "",
  "follow_up_question": ""
}"""

_client = DeepSeekClient(system_prompt=SYSTEM_PROMPT)


def _build_prompt(
    position: str,
    stage: int,
    current_question: str,
    user_answer: str,
    context: list,
    resume_data: Optional[Dict[str, Any]] = None,
) -> str:
    """Build a detailed analysis prompt grounded in the user's answer.

    Args:
        position: Job position being interviewed for.
        stage: Current interview stage (1-5).
        current_question: The question that prompted this answer.
        user_answer: The candidate's actual response.
        context: Recent conversation history (last 3-4 turns).
        resume_data: Structured resume data for additional context.

    Returns:
        Formatted prompt string.
    """
    lines = [
        f"Position: {position}",
        f"Stage: {stage}/5",
        "",
        "CONTEXT — Recent conversation:",
    ]

    for msg in context[-4:]:
        role = msg["role"].upper()
        content = msg["content"][:400]
        lines.append(f"  {role}: {content}")

    lines.extend([
        "",
        f"THE QUESTION ASKED:",
        f"  {current_question}",
        "",
        f"THE CANDIDATE'S ANSWER:",
        f"  {user_answer}",
        "",
        "INSTRUCTIONS:",
        "1. Analyze the answer thoroughly — identify every technical claim,",
        "   design decision, technology mention, and vague statement.",
        "2. Select the ONE most revealing follow-up point.",
        "3. Generate a concrete question that references their exact words.",
        "4. The question must be answerable ONLY by someone with real depth.",
    ])

    if resume_data and resume_data.get("skills"):
        lines.append(f"\nNote — candidate's known skills: {', '.join(resume_data['skills'][:8])}")

    return "\n".join(lines)


async def followup_agent(state: InterviewState) -> Dict[str, Any]:
    """Analyze the user's last answer and generate a grounded follow-up.

    Node: followup_agent
    Reads: conversation_history, current_question, position, stage, resume_data
    Writes: current_question, conversation_history, followup_reasoning

    Behaviour:
    - If last message is from 'user': analyze → select → generate.
    - Otherwise: pass through unchanged.
    - Saves the reasoning (why this follow-up was chosen) to state.
    """
    history = state.get("conversation_history", [])
    existing_question = state.get("current_question", "")
    position = state.get("position", "")
    stage = state.get("stage", 1)
    resume_data = state.get("resume_data")

    # Only act when user just answered
    if not history or history[-1].get("role") != "user":
        return {
            "conversation_history": history,
            "followup_reasoning": state.get("followup_reasoning"),
        }

    user_answer = history[-1]["content"]

    prompt = _build_prompt(
        position=position,
        stage=stage,
        current_question=existing_question,
        user_answer=user_answer,
        context=history,
        resume_data=resume_data,
    )

    response = await _client.generate_response(
        [{"role": "user", "content": prompt}],
        temperature=0.5,  # Lower temp for more precise analysis
        max_tokens=1024,
    )

    # Parse structured JSON response
    parsed = _parse_followup_response(response)

    follow_up = parsed.get("follow_up_question", "")
    reasoning = json.dumps({
        "selected_focus": parsed.get("selected_focus", ""),
        "reasoning": parsed.get("reasoning", ""),
        "analysis": parsed.get("analysis", {}),
    }, ensure_ascii=False)

    # If parsing failed, generate a fallback question
    if not follow_up:
        follow_up = await _fallback_question(existing_question, user_answer)
        reasoning = json.dumps({
            "selected_focus": "fallback — direct follow-up",
            "reasoning": "Structured parsing failed; generated direct follow-up.",
            "analysis": {},
        }, ensure_ascii=False)

    # ── Update adaptive parameters based on answer quality ──
    analysis = parsed.get("analysis", {})
    key_claims = analysis.get("key_claims", []) if isinstance(analysis, dict) else []
    techs = analysis.get("technologies_mentioned", []) if isinstance(analysis, dict) else []
    vague = analysis.get("vague_areas", []) if isinstance(analysis, dict) else []

    difficulty = state.get("difficulty_score", 0.5)
    skill_scores = dict(state.get("skill_scores", {}))
    focus_areas = list(state.get("focus_areas", []))

    # Adjust difficulty: good answers increase, struggling decreases
    if len(key_claims) >= 2:
        difficulty = min(difficulty + 0.08, 1.0)
    if len(vague) >= 2:
        difficulty = max(difficulty - 0.1, 0.1)
    # Bounded
    difficulty = round(max(min(difficulty, 1.0), 0.1), 2)

    # Update skill_scores for detected technologies
    for tech in techs:
        tech_lower = tech.lower()
        if tech_lower in skill_scores:
            # Good mention → boost
            skill_scores[tech_lower] = round(min(skill_scores[tech_lower] + 0.1, 1.0), 2)

    # Remove recently-confirmed skills from focus_areas
    confirmed = [t.lower() for t in techs if t.lower() in skill_scores and skill_scores[t.lower()] >= 0.6]
    if confirmed:
        focus_areas = [f for f in focus_areas if f not in confirmed]

    updated_history = [
        *history,
        {"role": "assistant", "content": follow_up},
    ]

    return {
        "current_question": follow_up,
        "conversation_history": updated_history,
        "followup_reasoning": reasoning,
        "difficulty_score": difficulty,
        "skill_scores": skill_scores,
        "focus_areas": focus_areas,
    }


def _parse_followup_response(response: str) -> dict:
    """Parse the JSON response from DeepSeek, with multiple fallback strategies."""
    import re

    text = response.strip()

    # Strategy 1: Strip markdown fences
    try:
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 2: Extract JSON object with regex (handles text before/after JSON)
    try:
        match = re.search(r'\{[\s\S]*"follow_up_question"[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 3: Extract just the follow_up_question value with regex
    try:
        match = re.search(r'"follow_up_question"\s*:\s*"([^"]+)"', text)
        if match:
            return {"follow_up_question": match.group(1)}
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 4: Try to find any JSON object at all
    try:
        brace_start = text.index("{")
        brace_end = text.rindex("}")
        obj_str = text[brace_start : brace_end + 1]
        return json.loads(obj_str)
    except (ValueError, json.JSONDecodeError, Exception):
        pass

    return {}


async def _fallback_question(question: str, answer: str) -> str:
    """Fallback: generate a direct follow-up when structured parsing fails."""
    client = DeepSeekClient(
        system_prompt="You are a technical interviewer. Generate ONE follow-up question."
    )
    return await client.generate_response(
        [
            {
                "role": "user",
                "content": (
                    f"Previous question: {question}\n\n"
                    f"Candidate's answer: {answer}\n\n"
                    f"Generate a single follow-up question that probes deeper "
                    f"into something specific the candidate mentioned."
                ),
            }
        ],
        temperature=0.6,
        max_tokens=256,
    )
