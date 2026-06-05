"""AdaptiveAgent — Initializes personalized interview parameters from resume data.

Sets initial:
  - difficulty_score: based on years of experience, project complexity, role seniority
  - skill_scores: per-skill proficiency estimated from resume content
  - focus_areas: skills needing deeper validation (low confidence or unlisted)

This runs once at session start, after ResumeAgent has parsed the resume.
"""

import re
from typing import Dict, Any, List, Optional

from agents.state import InterviewState


# ── Default skill taxonomy by position ──

POSITION_SKILLS = {
    "Backend Engineer": [
        "python", "go", "java", "sql", "database", "redis", "kafka",
        "docker", "kubernetes", "aws", "api_design", "microservices",
        "caching", "message_queue", "system_design",
    ],
    "Software Engineer": [
        "python", "java", "javascript", "typescript", "react", "sql",
        "data_structures", "algorithms", "design_patterns", "testing",
        "git", "ci_cd", "agile", "system_design",
    ],
    "AI Engineer": [
        "python", "pytorch", "tensorflow", "nlp", "transformers", "llm",
        "rag", "mlops", "docker", "kubernetes", "data_pipeline",
        "model_deployment", "statistics", "deep_learning",
    ],
}

DEFAULT_SKILLS = [
    "python", "sql", "database", "system_design", "algorithms",
    "communication", "architecture",
]

# ── Keywords that indicate skill depth ──

SKILL_SIGNALS: Dict[str, List[str]] = {
    "python": ["python", "django", "flask", "fastapi", "pandas", "numpy"],
    "go": ["go", "golang", "goroutine"],
    "java": ["java", "spring", "jvm"],
    "sql": ["sql", "query", "index", "postgresql", "mysql"],
    "database": ["database", "sql", "nosql", "postgres", "mongodb", "cassandra"],
    "redis": ["redis", "cache", "caching"],
    "kafka": ["kafka", "message queue", "event-driven", "streaming"],
    "docker": ["docker", "container"],
    "kubernetes": ["kubernetes", "k8s", "orchestration"],
    "aws": ["aws", "ec2", "s3", "lambda", "cloud"],
    "api_design": ["api", "rest", "grpc", "endpoint"],
    "microservices": ["microservice", "service mesh", "service-oriented"],
    "system_design": ["system design", "architecture", "scalable", "distributed"],
    "algorithms": ["algorithm", "complexity", "big o", "data structure"],
    "testing": ["test", "unit test", "integration test", "tdd"],
    "nlp": ["nlp", "natural language", "tokenization", "embedding"],
    "llm": ["llm", "gpt", "transformer", "language model", "prompt"],
    "rag": ["rag", "retrieval", "vector database", "pinecone"],
    "mlops": ["mlops", "pipeline", "deployment", "monitoring", "drift"],
    "deep_learning": ["deep learning", "neural network", "cnn", "rnn", "transformer"],
}


def _estimate_experience_level(resume_data: Optional[Dict[str, Any]]) -> float:
    """Estimate experience level as difficulty_base (0.0 ~ 1.0)."""
    if not resume_data:
        return 0.4  # Default: mid-level

    years = 0
    exp_list = resume_data.get("experience", [])
    for exp in exp_list:
        y = exp.get("years", 0)
        if isinstance(y, (int, float)):
            years += y

    if years >= 8:
        return 0.85
    if years >= 5:
        return 0.7
    if years >= 3:
        return 0.55
    if years >= 1:
        return 0.4
    return 0.3


def _estimate_skill_scores(
    resume_data: Optional[Dict[str, Any]],
    position: str,
) -> Dict[str, float]:
    """Estimate per-skill proficiency from resume keywords.

    Scoring:
      0.0 = not mentioned
      0.3 = listed in skills
      0.6 = used in project
      0.9 = used in experience description with depth signals
    """
    scores: Dict[str, float] = {}
    position_skills = POSITION_SKILLS.get(position, DEFAULT_SKILLS)

    if not resume_data:
        return {s: 0.3 for s in position_skills}

    resume_text_parts: List[str] = []
    for exp in resume_data.get("experience", []):
        desc = exp.get("description", "")
        if desc:
            resume_text_parts.append(desc.lower())
    for proj in resume_data.get("projects", []):
        resume_text_parts.append(proj.get("name", "").lower())
        resume_text_parts.extend([t.lower() for t in proj.get("tech_stack", [])])
    resume_text_parts.extend([s.lower() for s in resume_data.get("skills", [])])

    all_text = " ".join(resume_text_parts)

    for skill in position_skills:
        score = 0.0
        signals = SKILL_SIGNALS.get(skill, [skill])

        # Check if skill or its signals appear in skills list
        skill_list = [s.lower() for s in resume_data.get("skills", [])]
        if any(sig in all_text for sig in signals):
            # Check depth signals in experience descriptions
            for exp in resume_data.get("experience", []):
                desc = exp.get("description", "").lower()
                match_count = sum(1 for sig in signals if sig in desc)
                if match_count >= 2:
                    score = max(score, 0.85)
                elif match_count >= 1:
                    score = max(score, 0.6)

            # Boost if in explicit skills list
            if any(sig in all_text for sig in signal_list(skill, skill_list)):
                score = max(score, 0.5)

            # Minimum mention score
            if score == 0.0:
                score = 0.35

        scores[skill] = round(min(max(score, 0.0), 1.0), 2)

    return scores


def signal_list(skill: str, skill_list: List[str]) -> List[str]:
    """Return the signal keywords that match the given skill list."""
    signals = SKILL_SIGNALS.get(skill, [skill])
    return [s for s in signals if any(s in sl for sl in skill_list)]


def _determine_focus_areas(
    skill_scores: Dict[str, float],
    position: str,
) -> List[str]:
    """Identify skills needing deeper validation.

    Focus on:
    - Skills with low scores (weak or unmentioned)
    - Skills with medium scores (listed but unverified)
    """
    weak = [s for s, v in skill_scores.items() if v < 0.3]
    unverified = [s for s, v in skill_scores.items() if 0.3 <= v < 0.6]

    # Prioritize: weakest first
    weak.sort(key=lambda s: skill_scores[s])
    unverified.sort(key=lambda s: skill_scores[s])

    return weak + unverified


async def adaptive_agent(state: InterviewState) -> Dict[str, Any]:
    """Initialize adaptive interview parameters from resume data.

    Node: adaptive_agent
    Reads: resume_data, position
    Writes: difficulty_score, skill_scores, focus_areas

    Runs once per session (after ResumeAgent, before PositionAgent).
    Subsequent invocations are pass-through (adaptive params already set).
    """
    position = state.get("position", "")
    resume_data = state.get("resume_data")

    # If already initialized, pass through
    existing_difficulty = state.get("difficulty_score", 0.0)
    if existing_difficulty > 0.0:
        return {
            "difficulty_score": state["difficulty_score"],
            "skill_scores": state.get("skill_scores", {}),
            "focus_areas": state.get("focus_areas", []),
        }

    # Calculate initial adaptive parameters
    difficulty = _estimate_experience_level(resume_data)
    skills = _estimate_skill_scores(resume_data, position)
    focus = _determine_focus_areas(skills, position)

    return {
        "difficulty_score": difficulty,
        "skill_scores": skills,
        "focus_areas": focus,
    }
