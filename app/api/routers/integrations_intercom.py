from fastapi import APIRouter, Request
from app.models.external.intercom import IntercomConversationRaw
from app.services.ingestion import IngestResponse, IngestionService


router = APIRouter(prefix="/integrations/intercom", tags=["integrations"])


@router.post("/conversations", response_model=IngestResponse)
def ingest_intercom_conversation(payload: IntercomConversationRaw, request: Request) -> IngestResponse:
    service = IngestionService(request.app.state.repo)
    return service.ingest_intercom(payload)
