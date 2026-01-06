from app.models.external.intercom import IntercomConversationRaw
from uuid import uuid4
from datetime import datetime
from app.models.internal.conversation import InternalParticipant, InternalMessage, InternalConversation


def map_intercom_to_internal(payload: IntercomConversationRaw) -> InternalConversation:
    payload_as_dict = payload.model_dump()
    id = uuid4()
    provider = "intercom" #TO DO: convert to Enums
    external_id = payload_as_dict["id"]
    created_at = datetime.fromtimestamp(payload_as_dict["created_at"])
    updated_at = datetime.fromtimestamp(payload_as_dict["updated_at"])
    participants = [InternalParticipant(
        id=payload_as_dict["conversation_message"]["author"]["id"],
        type=payload_as_dict["conversation_message"]["author"]["type"],
        name=payload_as_dict["conversation_message"]["author"]["name"],
        email=payload_as_dict["conversation_message"]["author"]["email"],
    )] + [InternalParticipant(
        id=cp["author"]["id"],
        type=cp["author"]["type"],
        name=cp["author"]["name"],
        email=cp["author"]["email"],
    ) for cp in payload_as_dict["conversation_parts"]["conversation_parts"]]
    messages = [InternalMessage(
            id=payload_as_dict["conversation_message"]["id"],
            author_participant_id=payload_as_dict["conversation_message"]["author"]["id"],
            sent_at=created_at,
            content=payload_as_dict["conversation_message"]["body"],
        )] + [ InternalMessage(
            id=cp["id"],
            author_participant_id=cp["author"]["id"],
            sent_at=datetime.fromtimestamp(cp["created_at"]),
            content=cp["body"],
        )
        for cp in payload_as_dict["conversation_parts"]["conversation_parts"]
        ]

    return InternalConversation(
        id=id,
        provider=provider,
        external_id=external_id,
        created_at=created_at,
        updated_at=updated_at,
        participants=participants,
        messages=messages,
    )
    raise NotImplementedError
