from fastapi import APIRouter, Request, Response, status
from app.models.external.intercom import IntercomConversationRaw
from app.services.ingestion import IngestResponse, IngestionService


router = APIRouter(prefix="/integrations/intercom", tags=["integrations"])


@router.post("/conversations", response_model=IngestResponse)
def ingest_intercom_conversation(payload: IntercomConversationRaw, 
                                 request: Request, 
                                 response: Response,) -> IngestResponse:
    service = IngestionService(request.app.state.repo)
    result = service.ingest_intercom(payload)
    response.status_code = (
        status.HTTP_200_OK if result.deduplicated else status.HTTP_201_CREATED
    )
    return result
