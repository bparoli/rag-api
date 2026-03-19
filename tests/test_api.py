import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# --- Health ---

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# --- Ingest ---

@patch("app.api.routes.vector_store")
@patch("app.api.routes.extract_text", return_value="Sample document text for testing purposes.")
@patch("app.api.routes.chunk_text", return_value=["chunk one", "chunk two"])
def test_ingest_success(mock_chunk, mock_extract, mock_vs):
    mock_vs.add_chunks.return_value = 2
    response = client.post(
        "/api/v1/ingest",
        files={"file": ("test.txt", b"Sample document text for testing purposes.", "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["chunks_stored"] == 2
    assert data["filename"] == "test.txt"
    assert "doc_id" in data


def test_ingest_empty_file():
    response = client.post(
        "/api/v1/ingest",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert response.status_code == 400


# --- Query ---

@patch("app.api.routes.generate_answer", return_value="This is the answer.")
@patch("app.api.routes.vector_store")
def test_query_success(mock_vs, mock_llm):
    mock_vs.query.return_value = [
        {"text": "relevant chunk", "metadata": {"doc_id": "abc", "chunk_index": 0}}
    ]
    response = client.post("/api/v1/query", json={"question": "What is this about?"})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is the answer."
    assert len(data["sources"]) == 1


def test_query_empty_question():
    response = client.post("/api/v1/query", json={"question": "   "})
    assert response.status_code == 400


@patch("app.api.routes.vector_store")
def test_query_no_results(mock_vs):
    mock_vs.query.return_value = []
    response = client.post("/api/v1/query", json={"question": "Something not in the docs"})
    assert response.status_code == 404
