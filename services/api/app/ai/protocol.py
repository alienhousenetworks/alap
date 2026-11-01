from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class GenerationResult:
    text: str
    input_tokens: int | None
    output_tokens: int | None
    provider: str
    model: str


class AIProvider(Protocol):
    async def generate(
        self, *, model: str, messages: list[ChatMessage], temperature: float = 0.8,
        max_tokens: int = 700,
    ) -> GenerationResult: ...
