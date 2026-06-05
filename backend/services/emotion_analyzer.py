"""EmotionAnalyzer — Text-based tension and confidence analysis.

Analyzes answer text for:
  - Filler word density (um, uh, like, you know)
  - Hesitation markers (I think, maybe, not sure)
  - Confidence markers (I designed, I built, I led)
  - Answer structure quality
  - Tension score (0-100)

No voice data needed — purely text-based analysis.
"""

import re
from typing import Dict, Any, List


# ── Lexicon ──

FILLER_WORDS = [
    "um", "uh", "er", "ah", "like", "you know", "kind of",
    "sort of", "actually", "basically", "literally", "honestly",
    "i mean", "right?", "you see",
]

HESITATION_MARKERS = [
    "i think", "i guess", "i'm not sure", "maybe", "perhaps",
    "probably", "possibly", "not really sure", "i don't know",
    "i'm not certain", "hard to say", "not entirely sure",
    "if that makes sense", "does that make sense",
]

CONFIDENCE_MARKERS = [
    "i designed", "i built", "i led", "i implemented", "i created",
    "i developed", "i architected", "i was responsible for",
    "i delivered", "i drove", "i owned", "i initiated",
    "i optimized", "i solved", "i introduced",
]

WEAK_CLAIM_MARKERS = [
    "we", "the team", "my team", "we all",
    "it was decided", "i was asked to", "they told me",
]


def analyze_tension(answer: str) -> Dict[str, Any]:
    """Analyze a text answer for emotional indicators.

    Returns:
        tension_score: 0 (calm) to 100 (very tense)
        confidence_level: "low" | "medium" | "high"
        fillers_found: list of detected filler words
        hesitation_found: list of hesitation markers
        confidence_signals: list of confidence markers
        suggestions: list of improvement tips
    """
    text = answer.lower()

    # Filler word density
    fillers_found = []
    for fw in FILLER_WORDS:
        count = len(re.findall(r'\b' + re.escape(fw) + r'\b', text))
        if count > 0:
            fillers_found.append({"word": fw, "count": count})

    total_fillers = sum(f["count"] for f in fillers_found)
    word_count = len(text.split())
    filler_density = (total_fillers / max(word_count, 1)) * 100

    # Hesitation markers
    hesitation_found = []
    for hm in HESITATION_MARKERS:
        if hm in text:
            hesitation_found.append(hm)

    # Confidence markers
    confidence_signals = []
    for cm in CONFIDENCE_MARKERS:
        if cm in text:
            confidence_signals.append(cm)

    # Weak claim markers
    weak_claims = []
    for wc in WEAK_CLAIM_MARKERS:
        if wc in text:
            weak_claims.append(wc)

    # Score calculation (0-100, higher = more tense)
    filler_score = min(filler_density * 4, 40)
    hesitation_score = min(len(hesitation_found) * 10, 30)
    confidence_boost = min(len(confidence_signals) * 5, 20)
    weak_claim_penalty = min(len(weak_claims) * 5, 15)
    short_answer_penalty = 15 if word_count < 15 else 0

    tension_score = max(0, min(100,
        filler_score + hesitation_score + weak_claim_penalty + short_answer_penalty - confidence_boost
    ))

    # Confidence level
    if confidence_signals and tension_score < 30:
        confidence_level = "high"
    elif tension_score < 50:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    # Suggestions
    suggestions = []
    if filler_density > 5:
        suggestions.append(f"Reduce filler words (detected {total_fillers} in {word_count} words)")
    if hesitation_found:
        suggestions.append("Replace hesitation phrases with direct statements")
    if not confidence_signals:
        suggestions.append("Use more 'I' statements (I designed, I built, I led)")
    if weak_claims:
        suggestions.append("Use active voice — take ownership of your contributions")
    if word_count < 20:
        suggestions.append("Provide more specific details and examples")
    if word_count > 150:
        suggestions.append("Keep answers concise — aim for 60-90 seconds")

    return {
        "tension_score": round(tension_score),
        "confidence_level": confidence_level,
        "filler_word_count": total_fillers,
        "filler_density": round(filler_density, 1),
        "fillers_found": fillers_found,
        "hesitation_found": hesitation_found,
        "confidence_signals": confidence_signals,
        "weak_claims": weak_claims,
        "word_count": word_count,
        "suggestions": suggestions,
        "adapted_difficulty": _adapt_difficulty(tension_score),
    }


def _adapt_difficulty(tension_score: float) -> str:
    """Suggest difficulty adjustment based on tension."""
    if tension_score >= 70:
        return "decrease — candidate showing high tension"
    if tension_score >= 45:
        return "maintain — moderate tension, keep current pace"
    return "can increase — candidate appears confident"


def batch_analyze(answers: List[str]) -> Dict[str, Any]:
    """Analyze multiple answers for overall tension trends."""
    results = [analyze_tension(a) for a in answers if a.strip()]
    if not results:
        return {"overall_tension": 0, "trend": "unknown", "analyses": []}

    avg_tension = sum(r["tension_score"] for r in results) / len(results)
    tensions = [r["tension_score"] for r in results]

    # Trend: is tension increasing or decreasing?
    if len(tensions) >= 3:
        first_half = sum(tensions[:len(tensions)//2]) / max(len(tensions)//2, 1)
        second_half = sum(tensions[len(tensions)//2:]) / max(len(tensions) - len(tensions)//2, 1)
        if second_half < first_half - 10:
            trend = "decreasing — candidate relaxed over time 📉"
        elif second_half > first_half + 10:
            trend = "increasing — candidate getting more tense 📈"
        else:
            trend = "stable"
    else:
        trend = "insufficient data for trend"

    return {
        "overall_tension": round(avg_tension),
        "trend": trend,
        "analyses": results,
    }
