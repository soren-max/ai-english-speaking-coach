"""CompanyProfiles — Simulated company culture interview styles.

Each company has:
  - Interview focus areas
  - Question style templates
  - Evaluation criteria
  - Cultural values
  - Difficulty baseline
"""

from typing import Dict, Any, List, Optional
import random

from services.question_bank import bank


# ── Company profiles ──

COMPANIES: Dict[str, Dict[str, Any]] = {
    "Google": {
        "full_name": "Google",
        "description": "Google interviews emphasize algorithmic thinking, system design, and Googleyness (cultural fit). Known for hard algorithm questions and multiple rounds.",
        "focus_areas": ["algorithms", "system_design", "data_structures", "googleyness"],
        "difficulty_baseline": 0.75,
        "question_style": "Problem-solving with clear communication. Interviewers want to see your thought process.",
        "values": ["Innovation", "Collaboration", "User focus", "Technical excellence"],
        "interview_flow": ["Phone Screen (algorithms)", "Technical Phone (algorithms + design)", "On-site (4-5 rounds: algorithms, design, behavioral, Googleyness)"],
    },
    "Amazon": {
        "full_name": "Amazon",
        "description": "Amazon interviews are built around 16 Leadership Principles. Every answer should demonstrate one or more principles. Bar Raiser ensures high hiring bar.",
        "focus_areas": ["leadership_principles", "system_design", "algorithms", "behavioral"],
        "difficulty_baseline": 0.7,
        "question_style": "STAR method is essential. Use specific metrics. Show ownership and customer obsession.",
        "values": ["Customer Obsession", "Ownership", "Invent and Simplify", "Hire and Develop the Best", "Insist on the Highest Standards"],
        "interview_flow": ["Phone Screen", "On-site (LP-based behavioral + system design + algorithms)", "Bar Raiser round"],
    },
    "Tencent": {
        "full_name": "Tencent (腾讯)",
        "description": "Tencent interviews focus on product sense, technical depth, and business acumen. Questions often tie to real products. Chinese and English mixed.",
        "focus_areas": ["product_sense", "system_design", "algorithms", "business_acumen"],
        "difficulty_baseline": 0.7,
        "question_style": "Product-oriented questions. 'How would you improve WeChat?' type questions. Deep technical dives.",
        "values": ["User value", "Innovation", "Collaboration", "Execution"],
        "interview_flow": ["Technical Phone (algorithms)", "Technical Deep-dive (system design)", "Cross-team (product sense)", "HR (cultural fit)"],
    },
    "Meta": {
        "full_name": "Meta (Facebook)",
        "description": "Meta interviews emphasize speed of execution, system design at scale, and cultural fit. Move fast and break things mindset.",
        "focus_areas": ["system_design", "algorithms", "product_sense", "behavioral"],
        "difficulty_baseline": 0.75,
        "question_style": "Fast-paced problem solving. Design questions at huge scale (billions of users). Behavioral focused on impact.",
        "values": ["Move fast", "Be bold", "Focus on impact", "Open culture"],
        "interview_flow": ["Phone Screen", "On-site (2 algorithms, 2 system design, 1 behavioral)"],
    },
    "Microsoft": {
        "full_name": "Microsoft",
        "description": "Microsoft interviews value structured thinking, problem-solving process, and growth mindset. Questions are methodical and thorough.",
        "focus_areas": ["algorithms", "system_design", "data_structures", "growth_mindset"],
        "difficulty_baseline": 0.65,
        "question_style": "Methodical problem-solving. Explain your approach before coding. Multiple follow-up questions.",
        "values": ["Growth mindset", "Customer focus", "Diversity & inclusion", "Be one company"],
        "interview_flow": ["Phone Screen", "Technical (algorithms + design)", "On-site (4 rounds: algorithms, design, behavioral, cross-group)"],
    },
}


def list_companies() -> List[Dict[str, Any]]:
    """Get list of all available company profiles."""
    return [
        {
            "id": cid,
            "name": profile["full_name"],
            "description": profile["description"],
            "focus_areas": profile["focus_areas"],
            "difficulty_baseline": profile["difficulty_baseline"],
        }
        for cid, profile in COMPANIES.items()
    ]


def get_company(company_id: str) -> Optional[Dict[str, Any]]:
    """Get full company profile."""
    return COMPANIES.get(company_id)


def get_company_questions(
    company_id: str,
    position: str,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Get interview questions tailored to a company's focus areas.

    Combines company-specific questions with position-relevant ones
    from the question bank, filtered by the company's focus areas.
    """
    company = COMPANIES.get(company_id)
    if not company:
        return []

    focus = company.get("focus_areas", [])

    # Get questions from bank, filtered by company focus topics
    questions = []
    for topic in focus:
        qs = bank.get_questions(position, topic=topic, limit=limit // len(focus) + 1)
        questions.extend(qs)

    # Add company-specific behavioral questions
    company_behaviors = _get_company_behavioral(company_id)
    questions.extend(company_behaviors)

    # Shuffle and limit
    random.shuffle(questions)
    return questions[:limit]


def _get_company_behavioral(company_id: str) -> List[Dict[str, Any]]:
    """Get company-specific behavioral questions."""
    behaviorals = {
        "Amazon": [
            {"question": "Tell me about a time you disagreed with your manager. How did you handle it?", "topic": "leadership_principles", "difficulty": 3, "source": "company"},
            {"question": "Describe a situation where you went above and beyond for a customer.", "topic": "leadership_principles", "difficulty": 3, "source": "company"},
            {"question": "Tell me about a time you innovated to solve a difficult problem.", "topic": "leadership_principles", "difficulty": 4, "source": "company"},
            {"question": "Give an example of a goal you didn't meet and how you handled it.", "topic": "leadership_principles", "difficulty": 3, "source": "company"},
        ],
        "Google": [
            {"question": "Tell me about a time you influenced a team to adopt your technical approach.", "topic": "googleyness", "difficulty": 3, "source": "company"},
            {"question": "Describe a project where you had to collaborate across multiple teams.", "topic": "googleyness", "difficulty": 3, "source": "company"},
            {"question": "How do you handle ambiguous requirements? Give a specific example.", "topic": "googleyness", "difficulty": 4, "source": "company"},
        ],
        "Tencent": [
            {"question": "如果一个功能只有10%的用户会用，但影响很大，你做不做？为什么？", "topic": "product_sense", "difficulty": 4, "source": "company"},
            {"question": "你觉得微信最大的优势是什么？如果你是产品经理会怎么改进？", "topic": "product_sense", "difficulty": 4, "source": "company"},
            {"question": "Describe a time you had to balance technical debt against shipping speed.", "topic": "business_acumen", "difficulty": 3, "source": "company"},
        ],
        "Meta": [
            {"question": "Tell me about a time you moved fast and broke something. How did you fix it?", "topic": "behavioral", "difficulty": 3, "source": "company"},
            {"question": "Describe your most impactful contribution. How did you measure success?", "topic": "behavioral", "difficulty": 3, "source": "company"},
        ],
        "Microsoft": [
            {"question": "Tell me about a time you had to learn a new technology quickly to deliver a project.", "topic": "growth_mindset", "difficulty": 3, "source": "company"},
            {"question": "Describe a situation where you had to convince others to adopt a different approach.", "topic": "behavioral", "difficulty": 3, "source": "company"},
        ],
    }
    return behaviorals.get(company_id, [])


def generate_interview_plan(
    company_id: str,
    position: str,
) -> Optional[Dict[str, Any]]:
    """Generate a complete interview plan for a company + position."""
    company = COMPANIES.get(company_id)
    if not company:
        return None

    questions = get_company_questions(company_id, position, limit=8)

    return {
        "company": company["full_name"],
        "position": position,
        "difficulty": company["difficulty_baseline"],
        "focus_areas": company["focus_areas"],
        "values": company["values"],
        "interview_flow": company["interview_flow"],
        "question_style": company["question_style"],
        "practice_questions": questions,
    }
