# tests/conftest.py
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.repositories.conversations import ConversationRepository


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    app = create_app()

    # Use a temp sqlite DB for isolation per test run
    db_path = tmp_path / "test_kbms.sqlite3"
    repo = ConversationRepository(db_path=str(db_path))
    repo._init_db()
    app.state.repo = repo

    return TestClient(app)
