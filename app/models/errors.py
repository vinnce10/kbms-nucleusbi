from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class FieldError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field: str
    issue: str
    message: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    error_code: str
    message: str
    details: Optional[List[FieldError]] = None
