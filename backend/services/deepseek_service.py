"""DeepSeek AI service for interview simulation.

Uses the OpenAI-compatible API client to communicate with DeepSeek models.
Now supports configurable system prompts per agent.
"""

from typing import Optional

from openai import AsyncOpenAI

from core.config import settings


# Default system prompt for the interview coach persona
DEFAULT_SYSTEM_PROMPT = """You are a senior software engineering interviewer with over 10 years of experience conducting technical interviews at top tech companies.

Rules:
1. Speak in English only — never switch to another language.
2. Ask exactly ONE question per turn — never ask multiple questions at once.
3. Listen carefully to the candidate's answer and follow up naturally based on what they said.
4. Never proactively end the interview — wait for the candidate to signal they are done.
5. Maintain a professional, encouraging, and constructive tone throughout.
6. Cover a mix of technical depth, system design, problem-solving, and behavioral topics appropriate for the role.
7. Provide brief, specific feedback after an answer when it adds value, then move to the next question."""

MAX_CONTEXT_MESSAGES = 40


class DeepSeekClient:
    """Client for interacting with DeepSeek's API (OpenAI-compatible).

    Usage:
        client = DeepSeekClient(system_prompt="...")
        reply = await client.generate_response(conversation_history)
    """

    def __init__(self, system_prompt: Optional[str] = None) -> None:
        self.api_key: str = settings.deepseek_api_key
        self.base_url: str = settings.deepseek_base_url
        self.model: str = settings.deepseek_model
        self.system_prompt: str = system_prompt or DEFAULT_SYSTEM_PROMPT

        if not self.api_key or self.api_key == "sk-your-deepseek-api-key":
            import warnings
            warnings.warn(
                "DEEPSEEK_API_KEY is not set. "
                "Set it in your .env file or environment variables.",
                RuntimeWarning,
            )

        self._client: Optional[AsyncOpenAI] = None

    @property
    def client(self) -> AsyncOpenAI:
        """Lazy-initialized async OpenAI client."""
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    def _build_messages(self, conversation_history: list[dict]) -> list[dict]:
        """Prepend the system prompt and trim context window."""
        trimmed = conversation_history[-MAX_CONTEXT_MESSAGES:]
        return [
            {"role": "system", "content": self.system_prompt},
            *trimmed,
        ]

    async def generate_response(
        self,
        conversation_history: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Send conversation history to DeepSeek and return the AI's reply."""
        messages = self._build_messages(conversation_history)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
