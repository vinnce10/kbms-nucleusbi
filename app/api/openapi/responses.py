from app.api.openapi.examples import (
    EXAMPLE_INGEST_CREATED,
    EXAMPLE_INGEST_DEDUP,
    EXAMPLE_ERROR_INVALID_JSON,
    EXAMPLE_ERROR_VALIDATION,
    EXAMPLE_NOT_FOUND,
    EXAMPLE_INVALID_UUID,
    EXAMPLE_INTERNAL_CONVERSATION,
)
from app.models.errors import ErrorResponse
from app.services.ingestion import IngestResponse
from app.models.internal.conversation import ConversationListResponse, InternalConversation


INGEST_INTERCOM_RESPONSES = {
    200: {
        "model": IngestResponse,
        "description": "Deduplicated replay (same provider + external_id already stored)",
        "content": {"application/json": {"examples": {"deduplicated": {"value": EXAMPLE_INGEST_DEDUP}}}},
    },
    201: {
        "model": IngestResponse,
        "description": "Created (new provider + external_id)",
        "content": {"application/json": {"examples": {"created": {"value": EXAMPLE_INGEST_CREATED}}}},
    },
    400: {
        "model": ErrorResponse,
        "description": "Malformed JSON",
        "content": {"application/json": {"examples": {"invalid_json": {"value": EXAMPLE_ERROR_INVALID_JSON}}}},
    },
    422: {
        "model": ErrorResponse,
        "description": "Validation error",
        "content": {"application/json": {"examples": {"validation_error": {"value": EXAMPLE_ERROR_VALIDATION}}}},
    },
}

GET_CONVERSATION_RESPONSES = {
    200: {
        "model": InternalConversation,
        "description": "OK",
        "content": {
            "application/json": {
                "examples": {
                    "conversation": {"value": EXAMPLE_INTERNAL_CONVERSATION}
                }
            }
        },
    },
    404: {
        "model": ErrorResponse,
        "description": "Not found",
        "content": {"application/json": {"examples": {"not_found": {"value": EXAMPLE_NOT_FOUND}}}},
    },
    422: {
        "model": ErrorResponse,
        "description": "Invalid UUID / validation error",
        "content": {"application/json": {"examples": {"invalid_uuid": {"value": EXAMPLE_INVALID_UUID}}}},
    },
}


LIST_CONVERSATIONS_RESPONSES = {
    200: {
        "model": ConversationListResponse,
        "description": "OK",
    }
}
