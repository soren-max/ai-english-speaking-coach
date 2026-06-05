"""StrategyAgent — Analyzes interview answer strategy.

Metrics:
  - STAR completeness: how fully the candidate covers Situation/Task/Action/Result
  - Technical depth: specificity of technical details, metrics, trade-offs
  - Project logic: narrative flow, cause-effect clarity, structured progression

Outputs per-answer analysis + overall scores + actionable recommendations.
Pedagogical value: teaches candidates HOW to structure answers, not just WHAT to say.
"""

import json
from typing import Dict, Any, List, Optional

from services.deepseek_service import DeepSeekClient
from agents.state import InterviewState
from agents.strategy_store import StrategyStore


SYSTEM_PROMPT = """You are an interview strategy coach. Analyze how the candidate structures their technical answers.

For each project/experience-related answer, evaluate three dimensions:

1. STAR COMPLETENESS (0-100)
   - Situation: Did they set the context? (team size, business problem, tech stack)
   - Task: Did they clarify their specific role? (what THEY did vs the team)
   - Action: Did they detail their technical approach? (architecture, code, decisions)
   - Result: Did they quantify the outcome? (metrics, impact, learnings)

2. TECHNICAL DEPTH (0-100)
   - Uses specific metrics (10K QPS, 99.9% uptime)
   - Mentions design decisions and trade-offs
   - Shows understanding of underlying technology
   - Discusses alternatives considered

3. PROJECT LOGIC (0-100)
   - Clear chronological or logical flow
   - Cause-effect relationships explained
   - Structured progression (problem → approach → implementation → result)
   - Easy for interviewer to follow

Return ONLY valid JSON — no markdown, no code fences.

Schema:
{
  "overall_strategy_score": <float 0-100>,
  "star_completeness": <float 0-100>,
  "technical_depth": <float 0-100>,
  "project_logic": <float 0-100>,
  "answer_analyses": [
    {
      "answer_index": <int>,
      "star": {
        "situation": {"present": <bool>, "score": <int 0-10>, "text": "<extracted text>"},
        "task": {"present": <bool>, "score": <int 0-10>, "text": "<extracted text>"},
        "action": {"present": <bool>, "score": <int 0-10>, "text": "<extracted text>"},
        "result": {"present": <bool>, "score": <int 0-10>, "text": "<extracted text>"}
      },
      "technical_depth_score": <float 0-100>,
      "logic_score": <float 0-100>,
      "missing_parts": ["<missing STAR component>"],
      "recommendation": "<specific advice for this answer>"
    }
  ],
  "recommendations": [
    "<overall strategy improvement tip>",
    "..."
  ]
}

Rules:
- Be specific — reference exact parts of the candidate's answers.
- Recommendations must be actionable (what to change, not just what's wrong).
- Prioritize the most impactful improvements."""

_client = DeepSeekClient(system_prompt=SYSTEM_PROMPT)


def _extract_project_answers(history: list) -> List[Dict]:
    """Extract question-answer pairs from conversation history."""
    pairs = []
    for i, msg in enumerate(history):
        if msg["role"] == "user":
            prev_q = ""
            for j in range(i - 1, -1, -1):
                if history[j]["role"] == "assistant":
                    prev_q = history[j]["content"]
                    break
            pairs.append({
                "index": len(pairs),
                "question": prev_q[:300],
                "answer": msg["content"],
            })
    return pairs


def _build_prompt(pairs: List[Dict], position: str) -> str:
    """Build the analysis prompt from all Q&A pairs."""
    lines = [
        f"Position: {position}",
        f"Total answers to analyze: {len(pairs)}",
        "",
        "INTERVIEW TRANSCRIPT (project-related answers):",
        "─" * 40,
    ]

    for pair in pairs:
        lines.append(f"\n--- Answer {pair['index'] + 1} ---")
        lines.append(f"Q: {pair['question']}")
        lines.append(f"A: {pair['answer']}")

    lines.extend([
        "",
        "─" * 40,
        "Analyze each answer's STAR completeness, technical depth, and project logic.",
        "Provide per-answer recommendations and overall strategy advice.",
    ])

    return "\n".join(lines)


async def strategy_agent(state: InterviewState) -> Dict[str, Any]:
    """Analyze interview answer strategy across all dimensions.

    Node: strategy_agent
    Reads: conversation_history, position
    Writes: (state not directly updated — stored in StrategyStore)
    Stores: StrategyStore (for API consumption)
    """
    history = state.get("conversation_history", [])
    position = state.get("position", "")
    session_id = state.get("session_id", "")

    # Need at least one user answer to analyze
    user_answers = [m for m in history if m["role"] == "user"]
    if not user_answers:
        empty = {
            "overall_strategy_score": 0,
            "star_completeness": 0,
            "technical_depth": 0,
            "project_logic": 0,
            "answer_analyses": [],
            "recommendations": [
                "Complete at least one project answer to receive strategy analysis."
            ],
        }
        if session_id:
            StrategyStore.get_instance().put(session_id, empty)
        return {"strategy_analysis": empty}

    pairs = _extract_project_answers(history)
    prompt = _build_prompt(pairs, position)

    response = await _client.generate_response(
        [{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
    )

    analysis = _parse_strategy(response)

    # Store for API
    if session_id:
        StrategyStore.get_instance().put(session_id, analysis)

    return {"strategy_analysis": analysis}


def _parse_strategy(response: str) -> Dict[str, Any]:
    """Parse the JSON strategy analysis response."""
    import re

    text = response.strip()

    for strategy in [
        lambda t: _try_parse(t),                              # direct json
        lambda t: _try_regex(t, r'\{[\s\S]*"overall_strategy_score"[\s\S]*"recommendations"[\s\S]*\}'),
        lambda t: _try_find_braces(t),                         # any json
    ]:
        result = strategy(text)
        if result is not None:
            return result

    return {
        "overall_strategy_score": 0,
        "star_completeness": 0,
        "technical_depth": 0,
        "project_logic": 0,
        "answer_analyses": [],
        "recommendations": ["Unable to parse strategy analysis."],
    }


def _try_parse(text: str) -> Optional[Dict]:
    try:
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)
    except Exception:
        return None


def _try_regex(text: str, pattern: str) -> Optional[Dict]:
    try:
        import re
        match = re.search(pattern, text)
        if match:
            return json.loads(match.group())
    except Exception:
        return None
    return None


def _try_find_braces(text: str) -> Optional[Dict]:
    try:
        start = text.index("{")
        end = text.rindex("}")
        return json.loads(text[start : end + 1])
    except Exception:
        return None
