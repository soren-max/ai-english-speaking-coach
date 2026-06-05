"""StarAgent — Analyzes project answers using the STAR method.

Extracts Situation, Task, Action, Result from the candidate's
project-related responses, scores each component 0-10,
identifies missing parts, and provides improvement suggestions.

Output (stored in state.star_analysis):
{
  "examples": [
    {
      "situation": { "content": "...", "score": 8, "present": true },
      "task":      { "content": "...", "score": 7, "present": true },
      "action":    { "content": "...", "score": 9, "present": true },
      "result":    { "content": "...", "score": 5, "present": true }
    }
  ],
  "missing_parts": ["result"],
  "suggestions": [
    "Quantify your result with specific metrics (e.g., 'reduced latency by 40%')."
  ],
  "overall_star_score": 7.25
}
"""

import json
from typing import Dict, Any

from services.deepseek_service import DeepSeekClient
from agents.state import InterviewState


SYSTEM_PROMPT = """You are an expert interview coach specializing in the STAR method (Situation, Task, Action, Result).

Analyze the candidate's project-related answers and extract STAR components.

Return ONLY valid JSON — no markdown, no code fences.

Schema:
{
  "examples": [
    {
      "situation": {
        "content": "<the specific situation described, verbatim or paraphrased>",
        "score": <int 0-10>,
        "present": <true|false>
      },
      "task": {
        "content": "<the task or responsibility>",
        "score": <int 0-10>,
        "present": <true|false>
      },
      "action": {
        "content": "<specific actions taken by the candidate>",
        "score": <int 0-10>,
        "present": <true|false>
      },
      "result": {
        "content": "<outcome, metrics, or impact>",
        "score": <int 0-10>,
        "present": <true|false>
      }
    }
  ],
  "missing_parts": ["<part that is missing or weak: situation|task|action|result>"],
  "suggestions": ["<specific, actionable advice to improve STAR usage>"],
  "overall_star_score": <float 0-10>
}

Scoring guidelines for each component:
- 9-10: Excellent — clear, specific, well-articulated
- 7-8:  Good — present but could be more specific
- 5-6:  Adequate — mentioned but lacks detail
- 3-4:  Weak — vague or incomplete
- 1-2:  Barely mentioned
- 0:    Missing entirely (set present=false)

Rules:
- Extract up to 3 STAR examples from the conversation.
- If a component is missing, set present=false, content="", score=0.
- missing_parts: list of components (situation/task/action/result) that are absent or weak (score<5).
- suggestions: 3-5 actionable tips specific to the candidate's answers.
- overall_star_score: average of all present component scores across all examples."""

_client = DeepSeekClient(system_prompt=SYSTEM_PROMPT)


def _extract_project_answers(history: list) -> str:
    """Extract project-related Q&A pairs from the conversation.

    Looks for exchanges related to projects, experience, or
    technical implementations (Stages 2-3 in the interview).
    """
    lines = []
    for i, msg in enumerate(history):
        if msg["role"] == "user":
            # Find preceding question
            prev_q = ""
            for j in range(i - 1, -1, -1):
                if history[j]["role"] == "assistant":
                    prev_q = history[j]["content"]
                    break
            lines.append(f"Q: {prev_q[:200]}")
            lines.append(f"A: {msg['content']}")
            lines.append("---")

    return "\n".join(lines) if lines else "No project answers found."


async def star_agent(state: InterviewState) -> Dict[str, Any]:
    """Analyze project answers for STAR method usage.

    Node: star_agent
    Reads: conversation_history
    Writes: star_analysis

    Behaviour:
    - Extracts all user answers from the conversation.
    - Sends them to DeepSeek for STAR analysis.
    - Returns structured JSON with scores, missing parts, suggestions.
    - If no project answers exist, returns an empty analysis.
    """
    history = state.get("conversation_history", [])

    user_answers = [m for m in history if m["role"] == "user"]
    if not user_answers:
        return {
            "star_analysis": {
                "examples": [],
                "missing_parts": ["situation", "task", "action", "result"],
                "suggestions": [
                    "Provide specific project examples using the STAR format.",
                    "Describe the situation and your specific task clearly.",
                    "Detail the actions you personally took.",
                    "Quantify the results with metrics where possible.",
                ],
                "overall_star_score": 0,
            }
        }

    transcript = _extract_project_answers(history)

    prompt = (
        "Analyze the following project-related Q&A from a technical interview. "
        "Extract STAR (Situation, Task, Action, Result) components from each answer.\n\n"
        f"{transcript}"
    )

    response = await _client.generate_response(
        [{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,
    )

    analysis = _parse_star_response(response)

    return {"star_analysis": analysis}


def _parse_star_response(response: str) -> Dict[str, Any]:
    """Parse the JSON STAR analysis response."""
    import re

    text = response.strip()

    # Strategy 1: Strip fences
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
        match = re.search(r'\{[\s\S]*"overall_star_score"[\s\S]*\}', text)
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

    # Fallback
    return {
        "examples": [],
        "missing_parts": ["situation", "task", "action", "result"],
        "suggestions": ["Unable to parse STAR analysis. Review your project answers for STAR completeness."],
        "overall_star_score": 0,
    }
