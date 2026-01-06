from fastapi import APIRouter
from app.models.external.intercom import IntercomConversationRaw
from app.services.ingestion import IngestResponse
from app.adapters.intercom.mapper import map_intercom_to_internal

router = APIRouter(prefix="/integrations/intercom", tags=["integrations"])


@router.post("/conversations", response_model=IngestResponse)
def ingest_intercom_conversation(payload: IntercomConversationRaw) -> IngestResponse:
    internal_conversation = map_intercom_to_internal(payload)
    print(f"internal convo: {internal_conversation}")
    return IngestResponse(
        id="00000000-0000-0000-0000-000000000000",
        provider="intercom",
        external_id=payload.id,
        deduplicated=False,
    )
