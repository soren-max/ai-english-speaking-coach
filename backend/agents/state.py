"""InterviewGPT — LangGraph Agent State.

Shared TypedDict for the multi-agent interview workflow.
"""

from typing import TypedDict, Optional, List, Dict, Any


class InterviewState(TypedDict):
    """State flowing through all LangGraph agent nodes.

    Fields:
        position: Target job position.
        resume_content: Raw resume text (or file path to a .pdf).
        resume_data: Structured resume extracted by ResumeAgent.
        conversation_history: Chronological list of {role, content} dicts.
        current_question: The latest question asked by the AI.
        stage: Current interview stage (1-5).
        followup_reasoning: Why the last follow-up question was chosen.
        difficulty_score: Adaptive difficulty 0.0~1.0.
        skill_scores: Per-skill proficiency.
        focus_areas: Skills to probe deeper.
        correction: Real-time expression correction (set by CorrectionAgent).
        evaluation: Per-turn or aggregated evaluation scores.
        star_analysis: STAR method analysis of project answers.
        report: Final interview report.
    """

    position: str
    resume_content: str
    resume_data: Optional[Dict[str, Any]]
    session_id: str
    conversation_history: List[Dict[str, str]]
    current_question: str
    stage: int
    followup_reasoning: Optional[str]
    difficulty_score: float
    skill_scores: Dict[str, float]
    focus_areas: List[str]
    correction: Optional[Dict[str, Any]]
    strategy_analysis: Optional[Dict[str, Any]]
    evaluation: Optional[Dict[str, Any]]
    star_analysis: Optional[Dict[str, Any]]
    report: Optional[Dict[str, Any]]
