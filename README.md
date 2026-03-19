# rag-api

A **production-ready Retrieval-Augmented Generation (RAG) API** built with FastAPI, ChromaDB, and OpenAI.

Upload documents, ask questions in natural language, get grounded answers — with sources.

---

## Architecture

```
┌──────────┐     POST /ingest      ┌─────────────┐     embed     ┌─────────────┐
│  Client  │ ───────────────────▶  │  FastAPI    │ ──────────▶   │  ChromaDB   │
│          │                       │  (rag-api)  │               │ (vector DB) │
│          │     POST /query       │             │    retrieve    │             │
│          │ ───────────────────▶  │             │ ◀──────────    │             │
│          │                       │             │                └─────────────┘
│          │                       │             │    generate
│          │ ◀───────────────────  │             │ ──────────▶   ┌─────────────┐
│          │      answer +         └─────────────┘               │  OpenAI LLM │
│          │      sources                                         └─────────────┘
└──────────┘
```

**RAG Flow:**
1. `POST /ingest` — document is chunked, embedded, and stored in ChromaDB
2. `POST /query` — question is embedded, top-k chunks retrieved, LLM generates grounded answer

---

## Getting Started

### Prerequisites

- Python 3.11+
- An OpenAI API key

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/rag-api.git
cd rag-api

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run locally

```bash
uvicorn app.main:app --reload
```

API docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Run with Docker

```bash
docker-compose up --build
```

---

## API Reference

### `POST /api/v1/ingest`

Upload a document (`.txt` or `.pdf`) to the knowledge base.

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@your_document.pdf"
```

**Response:**
```json
{
  "doc_id": "3f7a1c2e-...",
  "chunks_stored": 24,
  "filename": "your_document.pdf"
}
```

---

### `POST /api/v1/query`

Ask a question. The API retrieves relevant chunks and generates a grounded answer.

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the payment processing SLA requirements?"}'
```

**Response:**
```json
{
  "answer": "According to the documentation, the SLA requirement is 99.99% uptime...",
  "sources": [
    {
      "text": "The platform must sustain 99.99% SLA...",
      "metadata": { "doc_id": "3f7a1c2e-...", "chunk_index": 4 }
    }
  ]
}
```

---

### `DELETE /api/v1/documents/{doc_id}`

Remove a document and all its chunks from the knowledge base.

```bash
curl -X DELETE http://localhost:8000/api/v1/documents/3f7a1c2e-...
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
rag-api/
├── app/
│   ├── api/
│   │   └── routes.py        # API endpoints: /ingest, /query, /documents
│   ├── core/
│   │   ├── config.py        # Settings via pydantic-settings + .env
│   │   └── ingestion.py     # Text extraction and chunking logic
│   ├── services/
│   │   ├── vector_store.py  # ChromaDB wrapper
│   │   └── llm.py           # OpenAI completion with grounded prompting
│   └── main.py              # FastAPI app, middleware, router
├── tests/
│   └── test_api.py          # Endpoint tests with mocked dependencies
├── infra/
│   └── AWS_ARCHITECTURE.md  # Production AWS deployment reference
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Design Decisions

**Why ChromaDB?**
Simple to run locally with zero infrastructure. For production on AWS, this swaps cleanly to OpenSearch Serverless — same interface, managed scaling. See [`infra/AWS_ARCHITECTURE.md`](infra/AWS_ARCHITECTURE.md).

**Why chunking with overlap?**
Sliding window chunking (configurable size + overlap via `.env`) preserves context across chunk boundaries, reducing hallucinations in retrieved answers.

**Why temperature 0.2?**
RAG answers should be grounded and deterministic. Low temperature reduces creative deviation from the retrieved context.

---

## AWS Production Deployment

See [`infra/AWS_ARCHITECTURE.md`](infra/AWS_ARCHITECTURE.md) for the full reference architecture using ECS Fargate, API Gateway, OpenSearch, and Secrets Manager.

---

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) — API framework
- [ChromaDB](https://www.trychroma.com/) — Vector database
- [OpenAI](https://platform.openai.com/) — Embeddings + LLM
- [pdfplumber](https://github.com/jsvine/pdfplumber) — PDF text extraction
- [Docker](https://www.docker.com/) — Containerization

---

## License

MIT
