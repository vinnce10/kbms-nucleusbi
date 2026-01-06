from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class IntercomConversationRaw(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    type: Optional[str] = Field(default=None)
    id: str = Field(..., description="Intercom conversation id")
    created_at: Optional[int] = Field(default=None, description="Unix timestamp seconds")
    updated_at: Optional[int] = Field(default=None, description="Unix timestamp seconds")
    source: Optional[Dict[str, Any]] = None
    conversation_parts: Optional[Dict[str, Any]] = None
