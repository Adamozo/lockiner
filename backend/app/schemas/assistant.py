from pydantic import BaseModel
from typing import Optional


class AssistantMessage(BaseModel):
    role: str
    content: str


class AssistantChatRequest(BaseModel):
    messages: list[AssistantMessage]
    conversation_id: Optional[str] = None


class AssistantChatResponse(BaseModel):
    answer: str
    conversation_id: Optional[str] = None
