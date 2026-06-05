"""InterviewerAgent — Stage-based interview question generator.

Generates exactly ONE question per invocation, progressing through
5 stages with position-specific content and increasing difficulty.

Stages:
    1. Self-introduction  —  Welcome + background
    2. Project experience  —  Resume projects deep-dive
    3. Technical deep-dive —  Position-specific technical grilling
    4. System design       —  Architecture & scale problems
    5. Behavioral          —  Soft skills, conflict, leadership

Supports positions: Backend Engineer, Software Engineer, AI Engineer.
"""

from typing import Dict, Any, Optional

from services.deepseek_service import DeepSeekClient
from agents.state import InterviewState


# ── Stage 1: Self-Introduction ──

STAGE1_PROMPTS = {
    "Backend Engineer": (
        "Welcome the candidate and ask them to introduce themselves, "
        "focusing on their backend engineering experience. Ask about "
        "the most complex backend system they've worked on."
    ),
    "Software Engineer": (
        "Welcome the candidate and ask them to introduce themselves, "
        "covering their overall software engineering background and "
        "what drew them to engineering."
    ),
    "AI Engineer": (
        "Welcome the candidate and ask them to introduce themselves, "
        "focusing on their AI/ML journey. Ask about the most interesting "
        "AI problem they've solved."
    ),
}

STAGE1_DEFAULT = (
    "Welcome the candidate and ask them to introduce themselves, "
    "covering their background and experience."
)


# ── Stage 2: Project Experience ──

STAGE2_PROMPTS = {
    "Backend Engineer": (
        "Ask the candidate to pick one of their past projects and "
        "describe the backend architecture in detail. Probe on: "
        "API design decisions, database schema choices, how they "
        "handled concurrency, and what they'd do differently."
    ),
    "Software Engineer": (
        "Ask the candidate to describe a significant project they "
        "built from scratch. Probe on: architecture decisions, "
        "technical challenges faced, trade-offs made, and lessons learned."
    ),
    "AI Engineer": (
        "Ask the candidate to walk through an ML/AI project they "
        "delivered. Probe on: data pipeline, model selection, "
        "evaluation metrics, deployment challenges, and monitoring."
    ),
}

STAGE2_DEFAULT = (
    "Ask the candidate to describe a past project in detail, "
    "focusing on their technical contributions and challenges."
)


# ── Stage 3: Technical Deep-Dive ──

STAGE3_PROMPTS = {
    "Backend Engineer": (
        "Ask a deep technical question about backend engineering. "
        "Topics: database indexing and query optimization, caching "
        "strategies (Redis, CDN), async processing with message queues, "
        "REST vs gRPC API design, authentication/authorization patterns. "
        "Make the question challenging but appropriate for a senior role."
    ),
    "Software Engineer": (
        "Ask a deep technical question covering core software engineering. "
        "Topics: design patterns and when to apply them, testing strategies "
        "(unit, integration, E2E), memory management, concurrency models, "
        "or algorithmic optimization. Challenge the candidate's depth."
    ),
    "AI Engineer": (
        "Ask a deep technical question about AI/ML engineering. "
        "Topics: transformer architecture details, training large models, "
        "RAG pipeline design, prompt engineering strategies, model "
        "evaluation and A/B testing, MLOps best practices."
    ),
}

STAGE3_DEFAULT = (
    "Ask a challenging technical question relevant to the position's "
    "core technologies. Probe the candidate's depth of understanding."
)


# ── Stage 4: System Design ──

STAGE4_PROMPTS = {
    "Backend Engineer": (
        "Ask a system design question appropriate for backend engineers. "
        "Options: Design a URL shortener (TinyURL), Design a ride-sharing "
        "platform (Uber), Design a real-time chat system, Design a "
        "distributed rate limiter, Design a payment system. "
        "Ask for one design. Require: traffic estimates, data model, "
        "API design, key components, and scaling strategy."
    ),
    "Software Engineer": (
        "Ask a system design question appropriate for senior software engineers. "
        "Options: Design a web crawler, Design a social media feed, "
        "Design a collaborative document editor (Google Docs), "
        "Design a video streaming platform. "
        "Require: requirements clarification, high-level design, "
        "data model, and trade-off analysis."
    ),
    "AI Engineer": (
        "Ask an ML system design question. "
        "Options: Design a recommendation system, Design a search engine, "
        "Design a real-time fraud detection pipeline, Design an LLM "
        "serving platform with low latency, Design a model training "
        "infrastructure. "
        "Require: data pipeline, model architecture, serving strategy, "
        "monitoring, and scaling approach."
    ),
}

STAGE4_DEFAULT = (
    "Ask a system design question. The candidate should walk through "
    "requirements, high-level design, data model, and scaling."
)


# ── Stage 5: Behavioral ──

STAGE5_PROMPTS = {
    "Backend Engineer": (
        "Ask a behavioral question relevant to backend engineering roles. "
        "Topics: Handling a production outage, dealing with technical debt, "
        "mentoring junior engineers, disagreeing with a technical decision, "
        "cross-team collaboration for a large migration."
    ),
    "Software Engineer": (
        "Ask a behavioral question. "
        "Topics: A time you failed and what you learned, leading a "
        "technical initiative, handling conflicting priorities, "
        "code review conflicts, adapting to new technologies quickly."
    ),
    "AI Engineer": (
        "Ask a behavioral question relevant to AI engineering. "
        "Topics: Ethical concerns with an AI project you worked on, "
        "handling model failures in production, communicating complex "
        "AI concepts to non-technical stakeholders, staying current "
        "with the rapidly evolving AI field."
    ),
}

STAGE5_DEFAULT = (
    "Ask a behavioral question about teamwork, leadership, or "
    "professional growth."
)


# ── Position-agnostic fallback chain ──

STAGE_PROMPTS = {
    1: (STAGE1_PROMPTS, STAGE1_DEFAULT, "Self-Introduction"),
    2: (STAGE2_PROMPTS, STAGE2_DEFAULT, "Project Experience"),
    3: (STAGE3_PROMPTS, STAGE3_DEFAULT, "Technical Deep-Dive"),
    4: (STAGE4_PROMPTS, STAGE4_DEFAULT, "System Design"),
    5: (STAGE5_PROMPTS, STAGE5_DEFAULT, "Behavioral"),
}

# ── Stage detection ──

STAGE_THRESHOLDS = [
    (1, 0),    # Stage 1: 0 QA pairs completed
    (2, 1),    # Stage 2: after 1 QA pair
    (3, 3),    # Stage 3: after 3 QA pairs
    (4, 5),    # Stage 4: after 5 QA pairs
    (5, 7),    # Stage 5: after 7 QA pairs
]


def _count_qa_pairs(history: list) -> int:
    """Count completed question-answer pairs.

    Each assistant message that has a following user message = 1 QA pair.
    """
    pairs = 0
    for i in range(len(history) - 1):
        if history[i]["role"] == "assistant" and history[i + 1]["role"] == "user":
            pairs += 1
    return pairs


def _get_target_stage(history: list) -> int:
    """Determine which stage the interview should be in based on QA count."""
    qa_count = _count_qa_pairs(history)
    for stage, threshold in reversed(STAGE_THRESHOLDS):
        if qa_count >= threshold:
            return stage
    return 1


# ── System prompt for the agent ──

SYSTEM_PROMPT = """You are a senior technical interviewer with 10+ years of experience.

Rules:
1. Speak in English only.
2. Ask exactly ONE question — never multiple questions.
3. Follow the stage instructions precisely.
4. Keep questions concise but meaty.
5. Be professional, encouraging, and natural.
6. NEVER answer the question yourself. Only ask."""

_client = DeepSeekClient(system_prompt=SYSTEM_PROMPT)


def _build_prompt(
    position: str,
    stage: int,
    resume_data: Optional[Dict[str, Any]],
    history: list,
    difficulty_score: float = 0.5,
    skill_scores: Optional[Dict[str, float]] = None,
    focus_areas: Optional[list] = None,
) -> str:
    """Build the prompt for the current stage and position."""
    prompts_map, fallback, stage_name = STAGE_PROMPTS[stage]
    instruction = prompts_map.get(position, fallback)

    sections = [
        f"Position: {position}",
        f"Stage: {stage_name} (Stage {stage} of 5)",
        f"Instruction: {instruction}",
    ]

    # ── Adaptive difficulty ──
    difficulty = difficulty_score or 0.5
    if difficulty >= 0.8:
        sections.append("DIFFICULTY LEVEL: EXPERT — Ask a very challenging question. Expect deep technical mastery.")
    elif difficulty >= 0.6:
        sections.append("DIFFICULTY LEVEL: INTERMEDIATE — Ask a solid technical question. Expect good depth.")
    elif difficulty >= 0.4:
        sections.append("DIFFICULTY LEVEL: MID — Ask a moderate question. Cover fundamentals clearly.")
    else:
        sections.append("DIFFICULTY LEVEL: JUNIOR — Ask a foundational question. Be encouraging.")

    # ── Skill-based focus ──
    if skill_scores:
        strong_skills = [s for s, v in skill_scores.items() if v >= 0.7][:3]
        weak_skills = [s for s, v in skill_scores.items() if v < 0.5][:3]
        if strong_skills:
            sections.append(f"Candidate's STRONG areas: {', '.join(strong_skills)}. (Avoid re-testing these.)")
        if weak_skills:
            sections.append(f"Prioritize probing WEAK areas: {', '.join(weak_skills)}.")

    if focus_areas:
        sections.append(f"FOCUS AREAS to validate: {', '.join(focus_areas[:4])}.")

    # Resume context
    if resume_data:
        rd = resume_data
        if rd.get("skills"):
            sections.append(f"Candidate skills: {', '.join(rd['skills'][:8])}")
        if rd.get("projects"):
            top = rd["projects"][0]
            sections.append(f"Key project: {top.get('name', 'N/A')} — {', '.join(top.get('tech_stack', []))}")
        if rd.get("experience"):
            recent = rd["experience"][0]
            sections.append(f"Recent role: {recent.get('title', 'N/A')} at {recent.get('company', 'N/A')}")

    # Recent conversation
    if history:
        recent = history[-4:]
        sections.append("\nRecent conversation:")
        for msg in recent:
            role = msg["role"].upper()
            content = msg["content"][:300]
            sections.append(f"  {role}: {content}")

    sections.append("\nGenerate exactly ONE question for this stage.")

    return "\n".join(sections)


async def interviewer_agent(state: InterviewState) -> Dict[str, Any]:
    """Generate one question for the current interview stage.

    Node: interviewer_agent
    Reads: position, resume_data, conversation_history, stage
    Writes: current_question, conversation_history, stage

    Behaviour:
    - Derives target stage from number of completed QA pairs.
    - If target stage > current stage: generates a question for
      the new stage, advances stage, appends to history.
    - Otherwise: passes through unchanged (let FollowupAgent
      handle in-stage follow-ups).
    - Exactly ONE question per invocation.
    """
    position = state.get("position", "")
    resume_data = state.get("resume_data")
    history = state.get("conversation_history", [])
    current_stage = state.get("stage", 1)

    # Determine what stage we should be at
    target_stage = _get_target_stage(history)
    existing_question = state.get("current_question", "")

    # Adaptive params
    difficulty_score = state.get("difficulty_score", 0.5)
    skill_scores = state.get("skill_scores", {})
    focus_areas = state.get("focus_areas", [])

    # Generate on two conditions:
    #   (a) first call — no question has been asked yet
    #   (b) stage has advanced since last generation
    should_generate = (not existing_question) or (target_stage > current_stage)

    if not should_generate:
        return {
            "stage": current_stage,
            "current_question": existing_question,
            "conversation_history": history,
            "difficulty_score": difficulty_score,
            "skill_scores": skill_scores,
            "focus_areas": focus_areas,
        }

    # Generate question for the new stage with adaptive parameters
    prompt = _build_prompt(
        position, target_stage, resume_data, history,
        difficulty_score=difficulty_score,
        skill_scores=skill_scores,
        focus_areas=focus_areas,
    )

    question = await _client.generate_response(
        [{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512,
    )

    updated_history = [
        *history,
        {"role": "assistant", "content": question},
    ]

    return {
        "stage": target_stage,
        "current_question": question,
        "conversation_history": updated_history,
        "difficulty_score": difficulty_score,
        "skill_scores": skill_scores,
        "focus_areas": focus_areas,
    }
