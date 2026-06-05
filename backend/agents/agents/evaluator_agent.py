"""EvaluatorAgent — Comprehensive interview evaluation.

Analyzes the FULL interview conversation history and produces
a structured assessment across four dimensions plus qualitative feedback.

Output (stored in state.evaluation):
{
  "overall_score":  <float 0-100>,
  "fluency":        <float 0-100>,
  "grammar":        <float 0-100>,
  "vocabulary":     <float 0-100>,
  "communication":  <float 0-100>,
  "summary":        "<string: 3-5 sentence overall assessment>",
  "strengths":      ["<string>", ...],
  "weaknesses":     ["<string>", ...],
  "suggestions":    ["<string>", ...]
}

The ReportAgent downstream uses this data to produce the final report.
The API service layer persists it to the reports table on session end.
"""

import json
from typing import Dict, Any

from services.deepseek_service import DeepSeekClient
from agents.state import InterviewState


SYSTEM_PROMPT = """You are an expert interview evaluator. Analyze the full interview conversation and produce a comprehensive evaluation.

Return ONLY valid JSON — no markdown, no code fences, no explanation.

Schema:
{
  "overall_score": <float 0-100>,
  "fluency": <float 0-100>,
  "grammar": <float 0-100>,
  "vocabulary": <float 0-100>,
  "communication": <float 0-100>,
  "summary": "<string: 3-5 sentence overall assessment>",
  "strengths": ["<string>", ...],
  "weaknesses": ["<string>", ...],
  "suggestions": ["<string>", ...]
}

Scoring guidelines:
- overall_score: weighted composite reflecting the candidate's overall interview performance
- fluency (25%): smoothness of expression, natural pacing, filler word usage, hesitation patterns
- grammar (25%): sentence structure, tense consistency, subject-verb agreement, article usage
- vocabulary (25%): word choice precision, range of expression, technical terminology accuracy
- communication (25%): clarity of ideas, logical structure, relevance to questions, persuasiveness

Rules:
- Score each dimension independently on a 0-100 scale
- 90-100 = Excellent (native-like, exceptional)
- 75-89  = Good (clear, minor issues)
- 60-74  = Adequate (understandable, noticeable gaps)
- Below 60 = Needs improvement
- strengths/weaknesses: 3-5 items each, specific to the candidate's actual responses
- suggestions: 3-5 actionable improvement tips
- summary: concise, balanced, encouraging tone"""

_client = DeepSeekClient(system_prompt=SYSTEM_PROMPT)


def _build_full_transcript(state: InterviewState) -> str:
    """Format the complete conversation for evaluation.

    Includes position, resume context, and all Q&A pairs
    organized by interview stage.
    """
    position = state.get("position", "Unknown")
    history = state.get("conversation_history", [])
    stage = state.get("stage", 1)

    lines = [
        f"Position: {position}",
        f"Stages completed: {max(stage - 1, 0)} of 5",
        f"Total exchanges: {len([m for m in history if m['role'] == 'user'])}",
        "",
        "FULL INTERVIEW TRANSCRIPT:",
        "─" * 40,
    ]

    for i, msg in enumerate(history):
        role_label = "INTERVIEWER" if msg["role"] == "assistant" else "CANDIDATE"
        content = msg["content"].strip()
        lines.append(f"\n[{role_label}]")
        lines.append(content)

    lines.extend([
        "",
        "─" * 40,
        "Evaluate the ENTIRE interview above.",
        "Score each dimension based on ALL the candidate's responses.",
        "Consider progression: did the candidate improve or struggle as difficulty increased?",
    ])

    return "\n".join(lines)


async def evaluator_agent(state: InterviewState) -> Dict[str, Any]:
    """Evaluate the full interview conversation.

    Node: evaluator_agent
    Reads: conversation_history, position, stage
    Writes: evaluation (comprehensive JSON with scores + qualitative feedback)

    Behaviour:
    - Runs on every graph invocation.
    - If there are fewer than 2 messages (no real conversation yet),
      returns a minimal evaluation.
    - Otherwise, analyzes ALL Q&A pairs across all completed stages.
    - Output schema maps directly to the Report DB model fields.
    """
    history = state.get("conversation_history", [])

    # Not enough data to evaluate
    user_messages = [m for m in history if m["role"] == "user"]
    if len(user_messages) < 1:
        return {
            "evaluation": {
                "overall_score": 0,
                "fluency": 0,
                "grammar": 0,
                "vocabulary": 0,
                "communication": 0,
                "summary": "Insufficient conversation data for evaluation.",
                "strengths": [],
                "weaknesses": [],
                "suggestions": ["Complete at least one Q&A round to receive evaluation."],
            }
        }

    transcript = _build_full_transcript(state)

    response = await _client.generate_response(
        [{"role": "user", "content": transcript}],
        temperature=0.3,
        max_tokens=2048,
    )

    evaluation = _parse_evaluation(response)

    return {"evaluation": evaluation}


def _parse_evaluation(response: str) -> Dict[str, Any]:
    """Parse the JSON evaluation response with fallback strategies."""
    import re

    text = response.strip()

    # Strategy 1: Strip fences and parse directly
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

    # Strategy 2: Regex-extract JSON object
    try:
        match = re.search(r'\{[\s\S]*"overall_score"[\s\S]*"suggestions"[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 3: Find any JSON object
    try:
        brace_start = text.index("{")
        brace_end = text.rindex("}")
        return json.loads(text[brace_start : brace_end + 1])
    except (ValueError, json.JSONDecodeError, Exception):
        pass

    # Fallback: return zeroed evaluation
    return {
        "overall_score": 0,
        "fluency": 0,
        "grammar": 0,
        "vocabulary": 0,
        "communication": 0,
        "summary": "Evaluation parsing encountered an error.",
        "strengths": [],
        "weaknesses": [],
        "suggestions": [],
    }
