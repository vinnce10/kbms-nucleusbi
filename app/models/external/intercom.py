from typing import Any, Dict, Optional, List
from pydantic import BaseModel, ConfigDict, Field


class IntercomAuthor(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: Optional[str] = None
    id: str = Field(..., description="Intercom author id")
    name: Optional[str] = None
    email: Optional[str] = None


class IntercomConversationMessage(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = None
    body: str = Field(..., description="Message body")
    author: IntercomAuthor                  


class IntercomConversationPart(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(...)
    body: str = Field(...)
    created_at: int = Field(...)
    author: IntercomAuthor


class IntercomConversationParts(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: Optional[str] = None
    conversation_parts: List[IntercomConversationPart] = Field(default_factory=list)
    total_count: Optional[int] = None


class IntercomConversationRaw(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: Optional[str] = Field(default=None)
    id: str = Field(..., description="Intercom conversation id")
    created_at: int = Field(..., description="Unix timestamp seconds") 
    updated_at: Optional[int] = Field(default=None, description="Unix timestamp seconds")
    source: Optional[Dict[str, Any]] = None
    conversation_parts: Optional[IntercomConversationParts] = None
    conversation_message: IntercomConversationMessage
