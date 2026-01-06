from app.models.external.intercom import IntercomConversationRaw
from app.models.internal.conversation import InternalConversation


def map_intercom_to_internal(payload: IntercomConversationRaw) -> InternalConversation:
    raise NotImplementedError
