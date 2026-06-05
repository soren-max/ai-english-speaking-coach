"""InterviewGPT — LangGraph StateGraph Workflow.

Multi-agent workflow:

    START
      ↓
    ResumeAgent
      ↓
    AdaptiveAgent
      ↓
    PositionAgent
      ↓
    InterviewerAgent
      ↓
    CorrectionAgent    ←  Real-time expression correction
      ↓
    FollowupAgent      ←  Context-aware follow-ups
      ↓
    EvaluatorAgent     ←  Fluency/grammar/vocabulary/communication
      ↓
    StarAgent          ←  STAR method analysis
      ↓
    StrategyAgent      ←  Answer strategy analysis (STAR completeness, technical depth, logic)
      ↓
    ReportAgent        ←  Aggregates final report
      ↓
    END

Usage:
    from agents.interview_graph import interview_graph

    graph = interview_graph()
    result = await graph.ainvoke({
        "position": "Software Engineer",
        "resume_content": "",
        "resume_data": None,
        "session_id": "",
        "conversation_history": [],
        "current_question": "",
        "stage": 1,
        "followup_reasoning": None,
        "difficulty_score": 0.0,
        "skill_scores": {},
        "focus_areas": [],
        "correction": None,
        "strategy_analysis": None,
        "evaluation": None,
        "star_analysis": None,
        "report": None,
    })
"""

from langgraph.graph import StateGraph, END

from agents.state import InterviewState
from agents.agents.resume_agent import resume_agent
from agents.agents.adaptive_agent import adaptive_agent
from agents.agents.position_agent import position_agent
from agents.agents.interviewer_agent import interviewer_agent
from agents.agents.correction_agent import correction_agent
from agents.agents.followup_agent import followup_agent
from agents.agents.evaluator_agent import evaluator_agent
from agents.agents.star_agent import star_agent
from agents.agents.strategy_agent import strategy_agent
from agents.agents.report_agent import report_agent


def interview_graph() -> StateGraph:
    """Build and compile the multi-agent interview StateGraph."""
    builder = StateGraph(InterviewState)

    builder.add_node("resume_agent", resume_agent)
    builder.add_node("adaptive_agent", adaptive_agent)
    builder.add_node("position_agent", position_agent)
    builder.add_node("interviewer_agent", interviewer_agent)
    builder.add_node("correction_agent", correction_agent)
    builder.add_node("followup_agent", followup_agent)
    builder.add_node("evaluator_agent", evaluator_agent)
    builder.add_node("star_agent", star_agent)
    builder.add_node("strategy_agent", strategy_agent)
    builder.add_node("report_agent", report_agent)

    builder.set_entry_point("resume_agent")
    builder.add_edge("resume_agent", "adaptive_agent")
    builder.add_edge("adaptive_agent", "position_agent")
    builder.add_edge("position_agent", "interviewer_agent")
    builder.add_edge("interviewer_agent", "correction_agent")
    builder.add_edge("correction_agent", "followup_agent")
    builder.add_edge("followup_agent", "evaluator_agent")
    builder.add_edge("evaluator_agent", "star_agent")
    builder.add_edge("star_agent", "strategy_agent")
    builder.add_edge("strategy_agent", "report_agent")
    builder.add_edge("report_agent", END)

    return builder.compile()
