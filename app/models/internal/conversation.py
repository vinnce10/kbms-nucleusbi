from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InternalParticipant(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    role: str
    name: Optional[str] = None
    email: Optional[str] = None


class InternalMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: Optional[str] = None
    author_participant_id: str
    sent_at: datetime
    content: str


class InternalConversation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    provider: str = Field(default="intercom")
    external_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    participants: List[InternalParticipant] = Field(default_factory=list)
    messages: List[InternalMessage] = Field(default_factory=list)


class ConversationListItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    provider: str
    external_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    participant_count: int
    message_count: int

    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None


class ConversationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: List[ConversationListItem]
