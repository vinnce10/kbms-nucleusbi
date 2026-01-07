from uuid import UUID


def intercom_payload(external_id: str = "1122334455") -> dict:
    return {
        "type": "conversation",
        "id": external_id,
        "created_at": 1567693209,
        "updated_at": 1568367881,
        "conversation_message": {
            "id": "409820079",
            "body": "Initial message",
            "author": {
                "type": "user",
                "id": "5310d8e7598c9a0b24000002",
                "name": "",
                "email": "",
            },
        },
        "conversation_parts": {
            "type": "conversation_part.list",
            "conversation_parts": [
                {
                    "id": "1223445555",
                    "body": "Follow-up message",
                    "created_at": 1567693273,
                    "author": {
                        "type": "user",
                        "id": "5310d8e7598c9a0b24000002",
                        "name": "",
                        "email": "",
                    },
                }
            ],
            "total_count": 1,
        },
        "some_future_field": {"new": "value"},
    }


def unwrap_detail_if_needed(body: dict) -> dict:
    return body.get("detail", body)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ingest_happy_path_returns_201_and_persists(client):
    payload = intercom_payload("1122334455")
    r = client.post("/integrations/intercom/conversations", json=payload)

    assert r.status_code == 201
    body = r.json()
    assert body["provider"] == "intercom"
    assert body["external_id"] == "1122334455"
    assert body["deduplicated"] is False
    UUID(body["id"])

    r2 = client.get("/internal/conversations")
    assert r2.status_code == 200
    items = r2.json()["items"]
    assert len(items) == 1
    assert items[0]["external_id"] == "1122334455"
    assert items[0]["participant_count"] >= 1
    assert items[0]["message_count"] >= 1
    assert items[0]["last_message_preview"] is not None


def test_ingest_dedup_returns_200_same_external_id(client):
    payload = intercom_payload("1122334455")

    r1 = client.post("/integrations/intercom/conversations", json=payload)
    assert r1.status_code == 201
    id1 = r1.json()["id"]

    r2 = client.post("/integrations/intercom/conversations", json=payload)
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["deduplicated"] is True
    assert body2["external_id"] == "1122334455"
    assert body2["id"] == id1


def test_ingest_unknown_fields_are_tolerated(client):
    payload = intercom_payload("999")
    payload["a_new_field"] = {"x": 1, "y": 2}

    r = client.post("/integrations/intercom/conversations", json=payload)
    assert r.status_code == 201


def test_ingest_malformed_json_returns_400(client):
    bad_json = '{"id": "112233", "created_at": 123'

    r = client.post(
        "/integrations/intercom/conversations",
        data=bad_json,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    body = r.json()
    assert body["error_code"] == "invalid_json"
    assert body["details"] is None


def test_ingest_missing_required_field_returns_422_with_field_errors(client):
    payload = intercom_payload("1122334455")
    payload.pop("created_at")

    r = client.post("/integrations/intercom/conversations", json=payload)
    assert r.status_code == 422
    body = r.json()
    assert body["error_code"] == "validation_error"
    assert isinstance(body.get("details"), list)
    assert any(d["field"].endswith("created_at") for d in body["details"])


def test_ingest_nested_missing_field_returns_422_with_nested_path(client):
    payload = intercom_payload("1122334455")
    del payload["conversation_message"]["author"]["id"]

    r = client.post("/integrations/intercom/conversations", json=payload)
    assert r.status_code == 422
    body = r.json()
    assert body["error_code"] == "validation_error"
    assert isinstance(body.get("details"), list)
    assert any("conversation_message.author.id" in d["field"] for d in body["details"])


def test_ingest_type_validation_returns_422(client):
    payload = intercom_payload("1122334455")
    payload["created_at"] = "not-an-int"

    r = client.post("/integrations/intercom/conversations", json=payload)
    assert r.status_code == 422
    body = r.json()
    assert body["error_code"] == "validation_error"
    assert isinstance(body.get("details"), list)
    assert any(d["field"].endswith("created_at") for d in body["details"])


def test_get_conversation_by_id_returns_200(client):
    payload = intercom_payload("1122334455")
    r = client.post("/integrations/intercom/conversations", json=payload)
    assert r.status_code == 201
    conv_id = r.json()["id"]

    r2 = client.get(f"/internal/conversations/{conv_id}")
    assert r2.status_code == 200
    body = r2.json()
    assert body["external_id"] == "1122334455"
    assert body["provider"] == "intercom"
    assert len(body["participants"]) >= 1
    assert len(body["messages"]) >= 1


def test_get_conversation_not_found_returns_404(client):
    missing_id = "00000000-0000-0000-0000-000000000000"
    r = client.get(f"/internal/conversations/{missing_id}")
    assert r.status_code == 404

    body = unwrap_detail_if_needed(r.json())
    assert body["error_code"] == "not_found"
    assert body["message"] == "Conversation not found"
