"""ReportAgent — AI-powered interview report generation.

Generates structured evaluation reports from interview conversation history.
"""

import json
from typing import Any

from services.deepseek_service import DeepSeekClient


REPORT_SYSTEM_PROMPT = """You are an expert interview evaluator. Analyze the interview conversation and generate a structured report.

Return ONLY valid JSON — no markdown, no explanation, no code fences.

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
- overall_score: weighted average of all dimensions
- fluency: how smoothly and naturally the candidate expresses ideas
- grammar: grammatical accuracy and sentence structure
- vocabulary: range and precision of word choice
- communication: clarity, structure, and persuasiveness of responses

strengths/weaknesses/suggestions should each have 3-5 items minimum.
"""


STAR_SYSTEM_PROMPT = """You are an expert interview coach. Analyze the following interview conversation and extract STAR (Situation, Task, Action, Result) method examples.

Return ONLY valid JSON array — no markdown, no explanation.

Schema:
[
  {
    "situation": "<string>",
    "task": "<string>",
    "action": "<string>",
    "result": "<string>"
  }
]

Extract up to 3 STAR examples from the candidate's responses. If fewer are found, return what's available."""


ERROR_ANALYSIS_PROMPT = """You are an English interview coach. Analyze the following interview conversation for language errors and improvement opportunities.

Return ONLY valid JSON — no markdown, no explanation.

Schema:
{
  "error_count": <int>,
  "common_mistakes": ["<string>", ...],
  "improvement_tips": ["<string>", ...],
  "vocabulary_gaps": ["<string>", ...]
}
"""


class ReportAgent:
    """Generates structured interview reports using DeepSeek AI."""

    def __init__(self) -> None:
        self._client = DeepSeekClient()

    async def generate_report(self, conversation_history: list[dict]) -> dict[str, Any]:
        """Generate a complete interview report from conversation history.

        Args:
            conversation_history: Full list of message dicts with role + content.

        Returns:
            Dict with overall_score, fluency, grammar, vocabulary,
            communication, summary, strengths, weaknesses, suggestions.
        """
        messages = [
            {"role": "system", "content": REPORT_SYSTEM_PROMPT},
            *conversation_history,
        ]
        reply = await self._client.generate_response(
            messages, temperature=0.3, max_tokens=2048
        )
        return self._parse_json(reply, {
            "overall_score": 0, "fluency": 0, "grammar": 0,
            "vocabulary": 0, "communication": 0, "summary": "",
            "strengths": [], "weaknesses": [], "suggestions": [],
        })

    async def analyze_star(self, conversation_history: list[dict]) -> list[dict]:
        """Extract STAR method examples from the interview.

        Returns:
            List of dicts with situation/task/action/result keys.
        """
        messages = [
            {"role": "system", "content": STAR_SYSTEM_PROMPT},
            *conversation_history,
        ]
        reply = await self._client.generate_response(
            messages, temperature=0.3, max_tokens=1024
        )
        return self._parse_json(reply, [])

    async def analyze_errors(self, conversation_history: list[dict]) -> dict[str, Any]:
        """Analyze language errors and improvement opportunities.

        Returns:
            Dict with error_count, common_mistakes, improvement_tips, vocabulary_gaps.
        """
        messages = [
            {"role": "system", "content": ERROR_ANALYSIS_PROMPT},
            *conversation_history,
        ]
        reply = await self._client.generate_response(
            messages, temperature=0.3, max_tokens=1024
        )
        return self._parse_json(reply, {
            "error_count": 0, "common_mistakes": [],
            "improvement_tips": [], "vocabulary_gaps": [],
        })

    def _parse_json(self, text: str, default: Any) -> Any:
        """Safely parse JSON from AI response, stripping markdown fences."""
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                # Remove code fences
                lines = cleaned.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()
            return json.loads(cleaned)
        except (json.JSONDecodeError, AttributeError):
            return default
