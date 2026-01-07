from typing import Optional
from uuid import UUID

from app.models.internal.conversation import ConversationListResponse, InternalConversation, ConversationListItem
import sqlite3


class ConversationRepository:
    """Persistence layer for normalized conversations.

    For this take-home scope we store the *entire* normalized InternalConversation as JSON
    in a single SQLite table. Dedup/idempotency is enforced via UNIQUE(provider, external_id).
    """

    def __init__(self, db_path: str = "kbms.sqlite3"):
        # SQLite file path (can be overridden in tests with a temp file)
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        """Open a DB connection with Row access by column name."""
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self):
        """Create tables if they don't exist.

        Note: UNIQUE(provider, external_id) is the key constraint for basic idempotency.
        """
        with self._connect() as connection:
            connection.execute(
                """
                 CREATE TABLE IF NOT EXISTS conversations (
                  id TEXT PRIMARY KEY,
                  provider TEXT NOT NULL,
                  external_id TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  updated_at TEXT,
                  payload_json TEXT NOT NULL,
                  UNIQUE(provider, external_id)
                )
                """
            )
            connection.commit()

    def upsert(self, conversation: InternalConversation) -> tuple[UUID, bool]:
        """Insert conversation if not already present for (provider, external_id).

        Returns:
        - (existing_or_new_internal_id, deduplicated_flag)
        """
        with self._connect() as connection:
            # Check if we've already stored this provider conversation
            row = connection.execute(
                "SELECT id FROM conversations WHERE provider=? AND external_id=?",
                (conversation.provider, conversation.external_id),
            ).fetchone()

            if row:
                # Already exists => deduplicated ingestion
                return UUID(row["id"]), True

            # New record => store normalized internal JSON
            connection.execute(
                """
                INSERT INTO conversations (id, provider, external_id, created_at, updated_at, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(conversation.id),
                    conversation.provider,
                    conversation.external_id,
                    conversation.created_at.isoformat(),
                    conversation.updated_at.isoformat() if conversation.updated_at else None,
                    conversation.model_dump_json(),
                ),
            )
            connection.commit()
            return conversation.id, False

    def list_conversations(self) -> ConversationListResponse:
        """Return a stable list view for internal consumers.

        We compute list-only fields (counts + last_message preview) from the stored JSON.
        """
        items = []
        with self._connect() as connection:
            records = connection.execute(
                "SELECT payload_json FROM conversations ORDER BY created_at DESC"
            ).fetchall()

        for record in records:
            # Re-hydrate normalized conversation from JSON
            conversation = InternalConversation.model_validate_json(record["payload_json"])

            # Derive list preview from the last message (if any)
            last_msg = conversation.messages[-1] if conversation.messages else None
            last_message_at = last_msg.sent_at if last_msg else None

            last_message_preview = None
            if last_msg and last_msg.content is not None:
                text = last_msg.content.strip()
                last_message_preview = text[:120] if len(text) > 120 else text

            items.append(
                ConversationListItem(
                    id=conversation.id,
                    provider=conversation.provider,
                    external_id=conversation.external_id,
                    created_at=conversation.created_at,
                    updated_at=conversation.updated_at,
                    participant_count=len(conversation.participants),
                    message_count=len(conversation.messages),
                    last_message_at=last_message_at,
                    last_message_preview=last_message_preview,
                )
            )

        return ConversationListResponse(items=items)

    def get_conversation(self, conversation_id: UUID) -> Optional[InternalConversation]:
        """Fetch one conversation by internal UUID.

        Returns None if not found (router maps this to a 404 ErrorResponse).
        """
        with self._connect() as connection:
            record = connection.execute("SELECT payload_json FROM conversations WHERE id=?", (str(conversation_id),),).fetchone()

            if not record:
                return None

            return InternalConversation.model_validate_json(record["payload_json"])
