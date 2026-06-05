"""ReportAgent — Generates a comprehensive interview report.

LangGraph node that aggregates the full conversation, evaluation,
and STAR analysis into a structured final report.
"""

import json
from typing import Dict, Any

from services.deepseek_service import DeepSeekClient
from agents.state import InterviewState


SYSTEM_PROMPT = """You are an expert interview evaluator. Generate a comprehensive final report.

Return ONLY valid JSON — no markdown, no code fences.

Schema:
{
  "overall_score": <float 0-100>,
  "fluency": <float 0-100>,
  "grammar": <float 0-100>,
  "vocabulary": <float 0-100>,
  "communication": <float 0-100>,
  "summary": "<string: 3-5 sentences>",
  "strengths": ["<string>", ...],
  "weaknesses": ["<string>", ...],
  "suggestions": ["<string>", ...]
}

Guidelines:
- overall_score: weighted composite of all dimensions
- strengths/weaknesses/suggestions: 3-5 items each
- summary: concise, actionable, encouraging
- Incorporate STAR analysis findings into strengths/weaknesses/suggestions"""

_client = DeepSeekClient(system_prompt=SYSTEM_PROMPT)


def _build_transcript(state: InterviewState) -> str:
    """Format the full conversation + evaluations + STAR for report generation."""
    history = state.get("conversation_history", [])
    position = state.get("position", "Unknown")
    evaluation = state.get("evaluation")
    star = state.get("star_analysis")

    lines = [
        f"Position: {position}",
        f"Total exchanges: {len(history) // 2}",
        "",
    ]

    # Evaluation data
    if evaluation:
        lines.append("EVALUATION SCORES:")
        for key in ("overall_score", "fluency", "grammar", "vocabulary", "communication"):
            val = evaluation.get(key)
            if val is not None:
                lines.append(f"  {key}: {val}/100")
        if evaluation.get("summary"):
            lines.append(f"  summary: {evaluation['summary']}")
        lines.append("")

    # STAR analysis
    if star and star.get("examples"):
        lines.append("STAR METHOD ANALYSIS:")
        lines.append(f"  Overall STAR score: {star.get('overall_star_score', 'N/A')}/10")
        if star.get("missing_parts"):
            lines.append(f"  Missing parts: {', '.join(star['missing_parts'])}")
        if star.get("suggestions"):
            lines.append("  STAR suggestions:")
            for s in star["suggestions"]:
                lines.append(f"    - {s}")
        lines.append("")

    # Full transcript
    if history:
        lines.append("FULL TRANSCRIPT:")
        for msg in history:
            lines.append(f"  {msg['role'].upper()}: {msg['content'][:400]}")

    return "\n".join(lines)


async def report_agent(state: InterviewState) -> Dict[str, Any]:
    """Generate the final interview report.

    Node: report_agent
    Reads: conversation_history, position, evaluation, star_analysis
    Writes: report
    """
    transcript = _build_transcript(state)

    response = await _client.generate_response(
        [{"role": "user", "content": transcript}],
        temperature=0.3,
        max_tokens=2048,
    )

    report = _parse_report(response)

    return {"report": report}


def _parse_report(response: str) -> Dict[str, Any]:
    """Parse the JSON report response."""
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

    # Strategy 2: Regex-extract JSON
    try:
        match = re.search(r'\{[\s\S]*"overall_score"[\s\S]*"suggestions"[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 3: Any JSON object
    try:
        brace_start = text.index("{")
        brace_end = text.rindex("}")
        return json.loads(text[brace_start : brace_end + 1])
    except (ValueError, json.JSONDecodeError, Exception):
        pass

    return {
        "overall_score": 0, "fluency": 0, "grammar": 0,
        "vocabulary": 0, "communication": 0,
        "summary": "Report generation encountered an error.",
        "strengths": [], "weaknesses": [], "suggestions": [],
    }
