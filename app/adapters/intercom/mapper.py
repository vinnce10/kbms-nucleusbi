from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.models.external.intercom import IntercomConversationRaw
from app.models.internal.conversation import (
    InternalConversation,
    InternalMessage,
    InternalParticipant,
)


def _ts_to_dt(ts: Optional[int]) -> datetime:
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    return datetime.now(tz=timezone.utc)


def _normalize_empty_str(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s2 = s.strip()
    return s2 if s2 else None


def _map_role(intercom_type: Optional[str]) -> str:
    t = (intercom_type or "").lower()
    if t == "user":
        return "customer"
    if t == "admin":
        return "agent"
    if t == "bot":
        return "bot"
    return "unknown"


def _participant_from_author(author: Dict[str, Any]) -> InternalParticipant:
    return InternalParticipant(
        id=str(author.get("id", "unknown")),
        role=_map_role(author.get("type")),
        name=_normalize_empty_str(author.get("name")),
        email=_normalize_empty_str(author.get("email")),
    )


def map_intercom_to_internal(payload: IntercomConversationRaw) -> InternalConversation:
    d = payload.model_dump()  # includes extras because extra="allow"

    external_id = str(d.get("id"))
    created_at = _ts_to_dt(d.get("created_at"))
    updated_at = _ts_to_dt(d.get("updated_at")) if d.get("updated_at") is not None else None

    # --- collect messages ---
    messages: List[InternalMessage] = []

    conv_msg = d.get("conversation_message") or {}
    conv_msg_author = (conv_msg.get("author") or {})
    conv_msg_body = conv_msg.get("body")
    if conv_msg_body:
        messages.append(
            InternalMessage(
                id=str(conv_msg.get("id")) if conv_msg.get("id") is not None else None,
                author_participant_id=str(conv_msg_author.get("id", "unknown")),
                sent_at=created_at,  # fallback rule for missing timestamp
                content=str(conv_msg_body),
            )
        )

    parts = ((d.get("conversation_parts") or {}).get("conversation_parts") or [])
    for part in parts:
        author = part.get("author") or {}
        body = part.get("body")
        if not body:
            continue
        messages.append(
            InternalMessage(
                id=str(part.get("id")) if part.get("id") is not None else None,
                author_participant_id=str(author.get("id", "unknown")),
                sent_at=_ts_to_dt(part.get("created_at")),
                content=str(body),
            )
        )

    participants_by_id: Dict[str, InternalParticipant] = {}

    if conv_msg_author.get("id") is not None:
        p = _participant_from_author(conv_msg_author)
        participants_by_id[p.id] = p

    for part in parts:
        author = part.get("author") or {}
        if author.get("id") is None:
            continue
        p = _participant_from_author(author)
        participants_by_id[p.id] = p

    participants = list(participants_by_id.values())

    return InternalConversation(
        id=uuid4(),
        provider="intercom",
        external_id=external_id,
        created_at=created_at,
        updated_at=updated_at,
        participants=participants,
        messages=messages,
    )
