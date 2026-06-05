"""CommunityService — Business logic for peer review and AI evaluation.

Handles:
  - Sharing interview answers (with anonymization)
  - AI-powered evaluation of shared answers
  - Peer review aggregation
  - Community feed
"""

from typing import Dict, List, Optional, Any

from services.deepseek_service import DeepSeekClient
from services.community_store import CommunityStore


AI_REVIEW_PROMPT = """You are an expert interview coach. Evaluate the following interview answer.

Provide a constructive evaluation covering:
1. Strengths (what the candidate did well)
2. Improvement areas (what could be better)
3. STAR completeness (Situation, Task, Action, Result)
4. Score (1-10)

Return ONLY valid JSON — no markdown, no code fences.

Schema:
{
  "score": <int 1-10>,
  "strengths": ["<string>", ...],
  "improvements": ["<string>", ...],
  "star_completeness": {
    "situation": <bool>,
    "task": <bool>,
    "action": <bool>,
    "result": <bool>
  },
  "summary": "<string: 2-3 sentence evaluation>"
}"""

_client = DeepSeekClient(system_prompt=AI_REVIEW_PROMPT)

store = CommunityStore.get_instance()


async def create_share(
    session_id: str,
    question: str,
    answer: str,
    position: str,
    is_anonymous: bool = True,
) -> Dict[str, Any]:
    """Share an interview Q&A pair. AI generates an evaluation automatically."""
    # Generate AI evaluation
    prompt = (
        f"Position: {position}\n\n"
        f"Question: {question}\n\n"
        f"Answer: {answer}"
    )
    try:
        response = await _client.generate_response(
            [{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        ai_review = _parse_review(response)
    except Exception:
        ai_review = {
            "score": 0,
            "strengths": [],
            "improvements": [],
            "star_completeness": {"situation": False, "task": False, "action": False, "result": False},
            "summary": "AI evaluation temporarily unavailable.",
        }

    share = store.create_share({
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "position": position,
        "is_anonymous": is_anonymous,
        "ai_review": ai_review,
    })

    return share


def get_feed(
    position: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """Get the community feed of shared answers."""
    return store.list_shares(position=position, page=page, page_size=page_size)


def get_share_detail(share_id: str) -> Optional[Dict[str, Any]]:
    """Get a shared answer with its AI review and peer reviews."""
    share = store.get_share(share_id)
    if not share:
        return None
    reviews = store.get_reviews(share_id)
    avg_rating = store.get_avg_rating(share_id)
    return {
        **share,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "review_count": len(reviews),
    }


def add_peer_review(
    share_id: str,
    rating: int,
    comment: str,
    reviewer_name: str = "Anonymous Peer",
) -> Optional[Dict[str, Any]]:
    """Add a peer review to a shared answer."""
    return store.add_review(share_id, {
        "reviewer_name": reviewer_name,
        "rating": max(1, min(5, rating)),
        "comment": comment,
    })


def get_stats() -> Dict[str, Any]:
    """Get community statistics."""
    return store.get_stats()


def _parse_review(response: str) -> Dict[str, Any]:
    """Parse the AI review JSON response."""
    import re
    text = response.strip()
    for strategy in [
        lambda t: _try_clean_json(t),
        lambda t: _try_regex(t, r'\{[\s\S]*"score"[\s\S]*"summary"[\s\S]*\}'),
        lambda t: _try_braces(t),
    ]:
        result = strategy(text)
        if result is not None:
            return result
    return {
        "score": 0, "strengths": [], "improvements": [],
        "star_completeness": {"situation": False, "task": False, "action": False, "result": False},
        "summary": "Could not parse AI evaluation.",
    }


def _try_clean_json(text: str) -> Optional[Dict]:
    try:
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        import json
        return json.loads(text)
    except Exception:
        return None


def _try_regex(text: str, pattern: str) -> Optional[Dict]:
    import re, json
    try:
        match = re.search(pattern, text)
        if match:
            return json.loads(match.group())
    except Exception:
        return None
    return None


def _try_braces(text: str) -> Optional[Dict]:
    import json
    try:
        start = text.index("{")
        end = text.rindex("}")
        return json.loads(text[start:end + 1])
    except Exception:
        return None
