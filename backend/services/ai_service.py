"""High-level AI service that wraps DeepSeekClient for interview workflows."""

from services.deepseek_service import DeepSeekClient


class AIService:
    """Handles DeepSeek API interactions for interview simulation.

    This is a high-level facade over DeepSeekClient. For direct access
    to the underlying client, use DeepSeekClient directly.
    """

    def __init__(self) -> None:
        self._client = DeepSeekClient()

    async def generate_question(self, position: str, context: list[dict]) -> str:
        """Generate the first or next interview question based on context.

        Args:
            position: Target job position (e.g. "Software Engineer").
            context: Previous conversation turns.

        Returns:
            AI-generated question string.
        """
        opening_prompt = (
            f"You are interviewing a candidate for the position: {position}. "
            "Start the interview with an appropriate opening question."
        )
        if not context:
            messages = [{"role": "user", "content": opening_prompt}]
        else:
            messages = context

        return await self._client.generate_response(messages, temperature=0.8)

    async def evaluate_answer(
        self, question: str, answer: str, context: list[dict]
    ) -> dict:
        """Evaluate the user's answer and return feedback + next question.

        Args:
            question: The question that was asked.
            answer: The user's response.
            context: Full conversation history.

        Returns:
            Dict with keys: 'feedback' (str), 'next_question' (str).
        """
        messages = context + [
            {"role": "user", "content": answer},
            {
                "role": "system",
                "content": (
                    "First, provide brief constructive feedback on the candidate's last answer "
                    "(2-3 sentences). Then ask a single follow-up question. "
                    "Format your response as:\n\n"
                    "Feedback: <your feedback>\n\n"
                    "Question: <your next question>"
                ),
            },
        ]
        reply = await self._client.generate_response(messages, temperature=0.7)

        # Parse the structured response
        feedback = ""
        next_question = reply

        if "Feedback:" in reply and "Question:" in reply:
            parts = reply.split("Question:", 1)
            feedback = parts[0].replace("Feedback:", "").strip()
            next_question = parts[1].strip()

        return {"feedback": feedback, "next_question": next_question}

    async def generate_summary(self, messages: list[dict]) -> dict:
        """Generate an overall interview summary and score.

        Args:
            messages: Full interview conversation history.

        Returns:
            Dict with keys: 'summary', 'fluency', 'grammar',
            'vocabulary', 'communication'.
        """
        system_msg = {
            "role": "system",
            "content": (
                "You are an interview evaluator. Based on the entire interview conversation, "
                "provide a comprehensive evaluation. "
                "Format your response as JSON with these exact keys:\n"
                "- summary: overall assessment (3-5 sentences)\n"
                "- fluency: score 0-100\n"
                "- grammar: score 0-100\n"
                "- vocabulary: score 0-100\n"
                "- communication: score 0-100\n"
                "Respond with valid JSON only, no markdown."
            ),
        }
        reply = await self._client.generate_response(
            [system_msg] + messages,
            temperature=0.3,
            max_tokens=2048,
        )

        import json

        try:
            # Strip potential markdown fences
            cleaned = reply.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(cleaned)
        except (json.JSONDecodeError, AttributeError):
            return {
                "summary": reply,
                "fluency": 0,
                "grammar": 0,
                "vocabulary": 0,
                "communication": 0,
            }
