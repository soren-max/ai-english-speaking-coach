"""CorrectionAgent — Real-time expression correction during interview.

Analyzes the user's last answer for grammar errors, awkward phrasing,
non-native expressions, and vocabulary improvements.

Generates structured corrections like:
  "I very like coding" → "I really enjoy coding"

Results are stored in:
  1. InterviewState.correction (for downstream consumers)
  2. CorrectionStore (for the REST API — no DB needed)
"""

import json
from typing import Dict, Any, Optional

from services.deepseek_service import DeepSeekClient
from agents.state import InterviewState
from agents.correction_store import CorrectionStore


SYSTEM_PROMPT = """You are a friendly English tutor embedded in a technical interview system.
After each candidate answer, check for natural improvement opportunities.

Focus on:
1. Grammar errors — tense, subject-verb agreement, articles, prepositions
2. Unnatural phrasing — "Chinglish" or direct translations from other languages
3. Vocabulary upgrades — simple words where more precise terms fit
4. Filler words — "um", "like", "you know", "actually" overuse

Return ONLY valid JSON — no markdown, no code fences. If the answer is already
natural and correct, return {"has_correction": false}.

Schema when correction IS needed:
{
  "has_correction": true,
  "original": "<the exact problematic phrase from the user>",
  "corrected": "<the natural English version>",
  "explanation": "<brief 1-sentence explanation in English>",
  "type": "grammar" | "vocabulary" | "style" | "fluency"
}

Schema when NO correction needed:
{
  "has_correction": false
}

Rules:
- Be encouraging, not critical.
- Only flag genuine issues — don't nitpick native-level speech.
- Prefer the most impactful single correction over many small ones.
- If the answer has multiple issues, pick the most important ONE."""

_client = DeepSeekClient(system_prompt=SYSTEM_PROMPT)

# TTS提示模板（用来生成语音纠正串）
TTS_PROMPT_TEMPLATE = (
    "Try saying it like this instead: \"{corrected}\". "
    "{explanation}"
)


async def correction_agent(state: InterviewState) -> Dict[str, Any]:
    """Analyze the user's last answer and generate a real-time correction.

    Node: correction_agent
    Reads: conversation_history (last user msg)
    Writes: correction (to state) + CorrectionStore (for API)

    Behaviour:
    - Only runs when the last message is from 'user'.
    - Sends the last answer to DeepSeek for grammar/style analysis.
    - Stores the structured correction in state + in-memory store.
    - Generates a TTS-ready voice hint string.
    """
    history = state.get("conversation_history", [])
    session_id = state.get("session_id", "")

    if not history or history[-1].get("role") != "user":
        return {
            "correction": state.get("correction"),
        }

    user_answer = history[-1]["content"]

    # Skip very short answers (just "yes", "no", "ok")
    if len(user_answer.strip().split()) < 3:
        return {
            "correction": {"has_correction": False},
        }

    # Also include the question context
    prev_question = ""
    for i in range(len(history) - 2, -1, -1):
        if history[i]["role"] == "assistant":
            prev_question = history[i]["content"]
            break

    prompt = (
        f"Question: {prev_question}\n\n"
        f"Candidate answer: {user_answer}\n\n"
        "Check for grammar or style improvements."
    )

    response = await _client.generate_response(
        [{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=512,
    )

    correction = _parse_correction(response)

    # Build TTS voice hint
    if correction.get("has_correction"):
        corrected = correction.get("corrected", "")
        explanation = correction.get("explanation", "")
        tts_text = TTS_PROMPT_TEMPLATE.format(
            corrected=corrected,
            explanation=explanation,
        )
        correction["tts_text"] = tts_text
    else:
        correction["tts_text"] = ""

    # Store for API access
    if session_id:
        CorrectionStore.get_instance().put(session_id, correction)

    return {"correction": correction}


def _parse_correction(response: str) -> Dict[str, Any]:
    """Parse the JSON correction response."""
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

    # Strategy 2: Regex
    try:
        match = re.search(r'\{[\s\S]*"has_correction"[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 3: Any JSON
    try:
        brace_start = text.index("{")
        brace_end = text.rindex("}")
        return json.loads(text[brace_start : brace_end + 1])
    except (ValueError, json.JSONDecodeError, Exception):
        pass

    return {"has_correction": False}
