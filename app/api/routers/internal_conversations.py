from uuid import UUID

from fastapi import APIRouter

from app.models.internal.conversation import ConversationListResponse, InternalConversation

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/conversations", response_model=ConversationListResponse)
def list_conversations() -> ConversationListResponse:
    return ConversationListResponse(items=[])


@router.get("/conversations/{conversation_id}", response_model=InternalConversation)
def get_conversation(conversation_id: UUID) -> InternalConversation:
    return InternalConversation.placeholder(conversation_id)
