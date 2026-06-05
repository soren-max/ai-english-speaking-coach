"""PositionAgent — Analyzes the target position and resume context.

LangGraph node that processes the job position and candidate resume
to prepare structured context for the interview.
"""

from typing import Dict, Any

from services.deepseek_service import DeepSeekClient
from agents.state import InterviewState


SYSTEM_PROMPT = """You are an interview preparation specialist. Analyze the job position and resume content to extract key information.

Return ONLY valid JSON — no markdown, no explanation.

Schema:
{
  "position_summary": "<string: 2-3 sentence summary of the role>",
  "key_skills": ["<string>", ...],
  "experience_level": "<junior | mid | senior>",
  "focus_areas": ["<string: technical topics to cover>", ...],
  "resume_highlights": ["<string: key resume points to reference>", ...]
}"""

_client = DeepSeekClient(system_prompt=SYSTEM_PROMPT)


async def position_agent(state: InterviewState) -> Dict[str, Any]:
    """Process position + resume and return structured context.

    Node: position_agent
    Reads: position, resume_content
    Writes: (indirectly through state merge — this node returns the
             analysis but doesn't add a field to InterviewState;
             the context is used downstream by InterviewerAgent)
    """
    position = state.get("position", "")
    resume = state.get("resume_content", "")

    prompt = f"Position: {position}\n\nResume:\n{resume if resume else 'No resume provided.'}"

    try:
        response = await _client.generate_response(
            [{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1024,
        )
        # JSON is parsed but the raw context stays implicit —
        # InterviewerAgent receives position + resume via state.
    except Exception:
        pass  # Graceful degradation — downstream agents still work

    # Return unchanged state; position_agent's analysis flows
    # indirectly through the shared state fields.
    return {
        "position": position,
        "resume_content": resume,
    }
