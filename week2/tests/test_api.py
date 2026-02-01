import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from ..app.main import app


def test_create_note():
    client = TestClient(app)
    resp = client.post("/notes", json={"content": "Test note"})
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data["id"], int)
    assert data["content"] == "Test note"
    assert isinstance(data["created_at"], str)
    assert data["created_at"]


def test_extract_llm_empty_text_returns_400():
    client = TestClient(app)
    resp = client.post("/action-items/extract_llm", json={"text": ""})
    assert resp.status_code in [400, 422]


def test_extract_llm_extracts_keyword_lines():
    client = TestClient(app)
    text = """
    Notes:
    todo: email the client
    next: verify deployment
    action item: update the docs
    This is just narrative.
    """.strip()
    resp = client.post("/action-items/extract_llm", json={"text": text, "save_note": False})
    assert resp.status_code == 200
    data = resp.json()

    assert "note_id" in data
    assert data["note_id"] is None
    assert "items" in data
    assert isinstance(data["items"], list)

    lowered = [i["text"].strip().lower() for i in data["items"]]
    assert "email the client" in lowered
    assert "verify deployment" in lowered
    assert "update the docs" in lowered


def test_extract_llm_extracts_bullets_and_checkboxes():
    client = TestClient(app)
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()
    resp = client.post("/action-items/extract_llm", json={"text": text, "save_note": False})
    assert resp.status_code == 200
    data = resp.json()

    lowered = [i["text"].strip().lower() for i in data["items"]]
    assert "set up database" in lowered
    assert "implement api extract endpoint" in lowered
    assert "write tests" in lowered
