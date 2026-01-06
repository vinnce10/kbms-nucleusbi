from typing import Optional
from uuid import UUID

from app.models.internal.conversation import ConversationListResponse, InternalConversation, ConversationListItem
import sqlite3


class ConversationRepository:
    def __init__(self, db_path: str = "kbms.sqlite3"):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self):
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

        with self._connect() as connection:
            row = connection.execute(
                "SELECT id FROM conversations WHERE provider=? AND external_id=?",
                (conversation.provider, conversation.external_id),
            ).fetchone()

            if row:
                return UUID(row["id"]), True

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
        items = []
        with self._connect() as connection:
            records = connection.execute("SELECT payload_json FROM conversations ORDER BY created_at DESC").fetchall()

        for record in records:
            conversation = InternalConversation.model_validate_json(record["payload_json"])
            items.append(
                ConversationListItem(
                    id=conversation.id,
                    provider=conversation.provider,
                    external_id=conversation.external_id,
                    created_at=conversation.created_at,
                    updated_at=conversation.updated_at,
                    participant_count=len(conversation.participants),
                    message_count=len(conversation.messages),
                )
            )
            pass
        return ConversationListResponse(items=items)

    def get_conversation(self, conversation_id: UUID) -> Optional[InternalConversation]:
        raise NotImplementedError
