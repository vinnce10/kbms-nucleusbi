# KBMS Backend Integration Service (Take-home Assignment)

A small FastAPI service that ingests conversation payloads from an external provider (mocked Intercom), normalizes them into a stable internal contract, stores them (SQLite), and exposes internal APIs for downstream consumers (frontend/analytics/data science).

## Goals (per assignment)
- Provide a clear ingestion interface for a third-party provider (Intercom)
- Validate incoming payloads with explicit schemas
- Normalize provider payloads into a stable internal conversation model
- Provide internal-facing APIs with predictable contracts
- Keep provider logic isolated to make new integrations easy to add
- Document architecture, data flow, validation, and extensibility

---

## Architecture Overview

**Key components:**
- **API Routers** (`app/api/routers`)
  - `integrations_intercom.py`: external ingestion entry point
  - `internal_conversations.py`: internal consumer APIs
- **External Provider Models** (`app/models/external`)
  - `intercom.py`: minimal Intercom-shaped schema (subset required) with `extra="allow"`
- **Internal Contract Models** (`app/models/internal`)
  - `conversation.py`: stable internal schema used by internal teams
- **Adapter/Mapper** (`app/adapters/intercom/mapper.py`)
  - isolates provider payload from internal logic (provider → internal mapping)
- **Service Layer** (`app/services/ingestion.py`)
  - orchestrates mapping + persistence, returns ingestion response
- **Repository** (`app/repositories/conversations.py`)
  - SQLite persistence + dedup by `(provider, external_id)`
- **Error Handling** (`app/core/error_handlers.py`)
  - consistent error responses for validation failures (422) and malformed JSON (400)

---

## Data Flow

### Ingestion Flow (Intercom → Internal)
1. `POST /integrations/intercom/conversations`
2. FastAPI/Pydantic validates request body using `IntercomConversationRaw`
   - requires a small subset of fields
   - accepts extra fields via `extra="allow"`
3. `IngestionService.ingest_intercom()` maps payload → `InternalConversation` using `map_intercom_to_internal()`
4. `ConversationRepository.upsert()` stores conversation in SQLite
   - uses `UNIQUE(provider, external_id)` for deduplication
5. API returns an `IngestResponse` containing:
   - internal UUID
   - external_id
   - deduplicated flag

### Internal Consumption Flow
- `GET /internal/conversations` returns a summary list (stable schema + counts + preview)
- `GET /internal/conversations/{id}` returns full conversation details (participants + messages)

---

## Folder Structure

```
app/
  adapters/
    intercom/
      mapper.py
  api/
    routers/
      integrations_intercom.py
      internal_conversations.py
  core/
    error_handlers.py
  models/
    external/
      intercom.py
    internal/
      conversation.py
    errors.py
  repositories/
    conversations.py
  services/
    ingestion.py
  main.py

tests/
  conftest.py
  test_api.py
pytest.ini
```

---

## Running the Service

### With Docker Compose (recommended for demo)
```bash
docker compose up --build
```

Service runs at:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Health: `GET http://localhost:8000/health`

### Local (optional)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## Running Tests

### With Docker Compose
```bash
docker compose exec kbms sh -lc "cd /app && pytest -q"
```

### Local
```bash
pip install -r requirements.txt
pip install pytest
pytest -q
```

---

## API Contracts

### 1) Ingestion Endpoint (External)

#### `POST /integrations/intercom/conversations`
**Purpose:** Accept Intercom conversation payloads (mocked), validate, normalize, store.

**Status Codes**
- `201 Created` when a new `(provider, external_id)` is stored
- `200 OK` when the payload is a duplicate (deduplicated)
- `400 Bad Request` for malformed JSON (via validation handler)
- `422 Unprocessable Entity` for schema/type validation errors (via validation handler)

**Request Schema (subset required + extra allowed)**
Defined by `IntercomConversationRaw` in `app/models/external/intercom.py`.

Required:
- `id: str`
- `created_at: int`
- `conversation_message.body: str`
- `conversation_message.author.id: str`

Everything else is tolerated (Intercom is a large schema) via `extra="allow"`.

**Example Request**
```json
{
  "type": "conversation",
  "id": "1122334455",
  "created_at": 1567693209,
  "updated_at": 1568367881,
  "waiting_since": 1568367881,
  "snoozed_until": null,
  "assignee": {
    "type": "admin",
    "id": "1223334"
  },
  "open": true,
  "state": "open",
  "read": true,
  "tags": {
    "type": "tag.list",
    "tags": []
  },
  "conversation_rating": {
    "rating": null,
    "remark": null,
    "created_at": null,
    "customer": {
      "type": null,
      "id": null
    },
    "teammate": {
      "type": null,
      "id": null
    }
  },
  "conversation_parts": {
    "type": "conversation_part.list",
    "conversation_parts": [
      {
        "type": "conversation_part",
        "id": "1223445555",
        "part_type": "comment",
        "body": "We've removed this part of the conversation to comply with Twitter's terms and conditions. You can view the complete conversation in Intercom.",
        "created_at": 1567693273,
        "updated_at": 1567693273,
        "notified_at": 1567693273,
        "assigned_to": null,
        "author": {
          "type": "user",
          "id": "5310d8e7598c9a0b24000002",
          "name": "",
          "email": ""
        },
        "attachments": [],
        "external_id": null
      }
    ],
    "total_count": 1
  },
  "customer_first_reply": {
    "created_at": 1567693209,
    "type": "twitter",
    "url": ""
  },
  "conversation_message": {
    "type": "twitter",
    "id": "409820079",
    "delivered_as": "customer_initiated",
    "subject": "We've removed this part of the conversation to comply with Twitter's terms and conditions. You can view the complete conversation in Intercom.",
    "body": "We've removed this part of the conversation to comply with Twitter's terms and conditions. You can view the complete conversation in Intercom.",
    "author": {
      "type": "user",
      "id": "5310d8e7598c9a0b24000002",
      "name": "",
      "email": ""
    },
    "attachments": [],
    "url": ""
  },
  "customers": [
    {
      "type": "user",
      "id": "5310d8e7598c9a0b24000002"
    }
  ],
  "user": {
    "type": "user",
    "id": "5310d8e7598c9a0b24000002"
  }
}

```

**Example Success Response (201 created)**
```json
{
  "id": "e3eb0803-3260-4bd6-aa2c-f2c07f3a99af",
  "provider": "intercom",
  "external_id": "1122334455",
  "deduplicated": false
}
```

**Example Success Response (200 deduplicated)**
```json
{
  "id": "e3eb0803-3260-4bd6-aa2c-f2c07f3a99af",
  "provider": "intercom",
  "external_id": "1122334455",
  "deduplicated": true
}
```

---

### 2) Internal APIs (for internal consumers)

#### `GET /internal/conversations`
**Purpose:** Summary list view for internal consumers.

**Status Codes**
- `200 OK`

**Example Response**
```json
{
  "items": [
    {
      "id": "e3eb0803-3260-4bd6-aa2c-f2c07f3a99af",
      "provider": "intercom",
      "external_id": "1122334455",
      "created_at": "2019-09-05T14:20:09Z",
      "updated_at": "2019-09-13T09:44:41Z",
      "participant_count": 1,
      "message_count": 2,
      "last_message_at": "2019-09-05T14:21:13Z",
      "last_message_preview": "Follow-up message"
    }
  ]
}
```

#### `GET /internal/conversations/{conversation_id}`
**Purpose:** Retrieve full conversation details (stable internal contract).

**Status Codes**
- `200 OK`
- `404 Not Found` if the ID doesn’t exist

**Example Response (200)**
```json
{
  "id": "e3eb0803-3260-4bd6-aa2c-f2c07f3a99af",
  "provider": "intercom",
  "external_id": "1122334455",
  "created_at": "2019-09-05T14:20:09Z",
  "updated_at": "2019-09-13T09:44:41Z",
  "participants": [
    { "id": "5310d8e7598c9a0b24000002", "role": "customer", "name": null, "email": null }
  ],
  "messages": [
    {
      "id": "409820079",
      "author_participant_id": "5310d8e7598c9a0b24000002",
      "sent_at": "2019-09-05T14:20:09Z",
      "content": "Initial message"
    },
    {
      "id": "1223445555",
      "author_participant_id": "5310d8e7598c9a0b24000002",
      "sent_at": "2019-09-05T14:21:13Z",
      "content": "Follow-up message"
    }
  ]
}
```

**Example Response (404)**
```json
{
  "error_code": "not_found",
  "message": "Conversation not found",
  "details": null
}
```

---

## Validation Approach

### Strategy
- External provider payloads can be large and change over time.
- We validate a **required subset** needed for internal analysis:
  - `id`, `created_at`, `conversation_message.body`, `conversation_message.author.id`
- Everything else is accepted using:
  - `model_config = ConfigDict(extra="allow")`

### Error Schema (consistent)
Validation failures return a stable error body:

```json
{
  "error_code": "validation_error",
  "message": "Payload validation failed",
  "details": [
    { "field": "conversation_message.author.id", "issue": "missing", "message": "Field required" }
  ]
}
```

Malformed JSON returns:
```json
{
  "error_code": "invalid_json",
  "message": "Malformed JSON body",
  "details": null
}
```

---

## Deduplication / Idempotency

Deduplication is implemented using:
- SQLite constraint: `UNIQUE(provider, external_id)`
- Repository logic:
  - if a row exists for `(provider, external_id)`, return existing internal ID + `deduplicated=true`

This makes the ingestion endpoint safe to call multiple times for the same provider conversation.

---

## How to Add a New Provider Integration

To add a new provider (e.g., Zendesk, Zapier, etc.) without breaking internal consumers:

1. Create external model: `app/models/external/<provider>.py` (subset required + `extra="allow"`)
2. Create adapter/mapper: `app/adapters/<provider>/mapper.py` (map payload → `InternalConversation`)
3. Add ingestion router: `app/api/routers/integrations_<provider>.py`
4. Extend ingestion service: add `ingest_<provider>()` (or generalize via interface)
5. Mount router in `app/main.py`

Internal APIs (`/internal/*`) and internal models remain unchanged because all providers map into the same stable `InternalConversation` contract.

---

## Scalability Notes (within scope)

- **Async ingestion:** return `202 Accepted` and enqueue processing if mapping/enrichment becomes heavy.
- **Pagination:** add `limit/offset` or cursor pagination for `GET /internal/conversations`.
- **Indexes:** keep unique `(provider, external_id)`; add index on `created_at` for list sorting/filtering.
- **Storage evolution:** swap SQLite → Postgres; optionally separate raw payload storage from normalized entities.
- **Analytics modeling:** normalize messages/participants into separate tables if analytics queries grow.
- **Idempotency:** keep uniqueness constraints; optionally store provider event IDs / idempotency keys.

---

## Assumptions & Trade-offs

- Only one provider integration is implemented (Intercom), mocked payloads (no real Intercom API calls).
- No authentication (explicitly out of scope).
- SQLite chosen for simplicity and portability; repository layer allows switching to Postgres later.
- External schema validates a minimal subset (`extra="allow"`) to tolerate provider schema drift.
- Internal schema is strict (`extra="forbid"`) to protect internal consumers with a stable contract.
