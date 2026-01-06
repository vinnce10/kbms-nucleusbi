from pydantic import BaseModel, ConfigDict
from app.adapters.intercom.mapper import map_intercom_to_internal
from app.repositories.conversations import ConversationRepository
from app.models.external.intercom import IntercomConversationRaw
from uuid import UUID


class IngestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    provider: str
    external_id: str
    deduplicated: bool


class IngestionService:

    def __init__(self, repo: ConversationRepository):
        self.repo = repo

    def ingest_intercom(self, payload: IntercomConversationRaw) -> IngestResponse:
        internal_conversation = map_intercom_to_internal(payload)
        internal_id, deduplicated = self.repo.upsert(internal_conversation)
        return IngestResponse(
            id=internal_id,
            provider="intercom",
            external_id=internal_conversation.external_id,
            deduplicated=deduplicated,
        )
