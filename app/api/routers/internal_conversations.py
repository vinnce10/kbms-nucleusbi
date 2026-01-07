from uuid import UUID

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from app.models.errors import ErrorResponse

from app.models.internal.conversation import ConversationListResponse, InternalConversation
from app.api.openapi.responses import GET_CONVERSATION_RESPONSES, LIST_CONVERSATIONS_RESPONSES

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/conversations", 
            response_model=ConversationListResponse, 
            responses=LIST_CONVERSATIONS_RESPONSES)
def list_conversations(request: Request) -> ConversationListResponse:
    return request.app.state.repo.list_conversations()


@router.get(
    "/conversations/{conversation_id}",
    response_model=InternalConversation,
    responses=GET_CONVERSATION_RESPONSES,
)
def get_conversation(conversation_id: UUID, request: Request) -> InternalConversation:
    conversation = request.app.state.repo.get_conversation(conversation_id)
    if conversation is None:
        body = ErrorResponse(
            error_code="not_found",
            message="Conversation not found",
            details=None,
        )
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=body.model_dump())
    return conversation
