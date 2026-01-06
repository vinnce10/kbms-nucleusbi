from typing import Optional
from uuid import UUID

from app.models.internal.conversation import ConversationListResponse, InternalConversation


class ConversationRepository:
    def __init__(self):
        pass

    def upsert(self, conversation: InternalConversation) -> tuple[UUID, bool]:
        raise NotImplementedError

    def list_conversations(self) -> ConversationListResponse:
        raise NotImplementedError

    def get_conversation(self, conversation_id: UUID) -> Optional[InternalConversation]:
        raise NotImplementedError
