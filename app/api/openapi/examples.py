EXAMPLE_INGEST_CREATED = {
    "id": "e3eb0803-3260-4bd6-aa2c-f2c07f3a99af",
    "provider": "intercom",
    "external_id": "1122334455",
    "deduplicated": False,
}

EXAMPLE_INGEST_DEDUP = {
    "id": "e3eb0803-3260-4bd6-aa2c-f2c07f3a99af",
    "provider": "intercom",
    "external_id": "1122334455",
    "deduplicated": True,
}

EXAMPLE_ERROR_INVALID_JSON = {
    "error_code": "invalid_json",
    "message": "Malformed JSON body",
    "details": None,
}

EXAMPLE_ERROR_VALIDATION = {
    "error_code": "validation_error",
    "message": "Payload validation failed",
    "details": [
        {"field": "conversation_message.author.id", "issue": "missing", "message": "Field required"}
    ],
}

EXAMPLE_NOT_FOUND = {
    "error_code": "not_found",
    "message": "Conversation not found",
    "details": None,
}

EXAMPLE_INVALID_UUID = {
    "error_code": "validation_error",
    "message": "Payload validation failed",
    "details": [
        {"field": "path.conversation_id", "issue": "invalid", "message": "Input should be a valid UUID"}
    ],
}

EXAMPLE_INTERNAL_CONVERSATION = {
    "id": "e3eb0803-3260-4bd6-aa2c-f2c07f3a99af",
    "provider": "intercom",
    "external_id": "1122334455",
    "created_at": "2019-09-05T14:20:09Z",
    "updated_at": "2019-09-13T09:44:41Z",
    "participants": [
        {
            "id": "5310d8e7598c9a0b24000002",
            "role": "customer",
            "name": None,
            "email": None,
        }
    ],
    "messages": [
        {
            "id": "409820079",
            "author_participant_id": "5310d8e7598c9a0b24000002",
            "sent_at": "2019-09-05T14:20:09Z",
            "content": "Initial message",
        },
        {
            "id": "1223445555",
            "author_participant_id": "5310d8e7598c9a0b24000002",
            "sent_at": "2019-09-05T14:21:13Z",
            "content": "Follow-up message",
        },
    ],
}
