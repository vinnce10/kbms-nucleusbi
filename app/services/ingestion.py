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
    """Orchestrates ingestion flow: validate -> normalize -> persist -> respond.

    Keeping this logic in a service layer keeps routers thin and makes it easier
    to add new providers (each with its own mapper) while reusing the same repo.
    """

    def __init__(self, repo: ConversationRepository):
        # Repository is injected so we can swap implementations (SQLite/in-memory/Postgres)
        # and easily test with a temporary database.
        self.repo = repo

    def ingest_intercom(self, payload: IntercomConversationRaw) -> IngestResponse:
        """Ingest one Intercom conversation payload.

        1) Map provider payload into stable internal contract
        2) Persist with deduplication via (provider, external_id)
        3) Return a small, stable response to the caller
        """
        internal_conversation = map_intercom_to_internal(payload)

        # upsert() returns (internal_id, deduplicated_flag)
        internal_id, deduplicated = self.repo.upsert(internal_conversation)

        return IngestResponse(
            id=internal_id,
            provider="intercom",
            external_id=internal_conversation.external_id,
            deduplicated=deduplicated,
        )
