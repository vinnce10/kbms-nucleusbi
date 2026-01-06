from pydantic import BaseModel, ConfigDict


class IngestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    provider: str
    external_id: str
    deduplicated: bool


class IngestionService:

    def __init__(self):
        pass

    def ingest_intercom(self, payload) -> IngestResponse:
        raise NotImplementedError
    