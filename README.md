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

Web UI available at: [http://localhost:8000](http://localhost:8000)

### Run with Docker

```bash
docker-compose up --build
```

---

## Web UI

The application includes a built-in web interface accessible at `http://localhost:8000`.

### Features

**Document management (left panel)**
- Upload `.txt` or `.pdf` files via drag & drop or file picker
- View all documents currently stored in the knowledge base
- Delete individual documents from the vector store

**Q&A chat (right panel)**
- Ask questions in natural language
- Answers are grounded exclusively in the uploaded documents
- Each response includes the source fragments and the document they belong to, displayed separately from the answer

No additional setup is required — the UI is served directly by FastAPI from the `frontend/` directory.

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

### `GET /api/v1/documents`

List all documents stored in the knowledge base.

```bash
curl http://localhost:8000/api/v1/documents
```

**Response:**
```json
[
  {
    "doc_id": "3f7a1c2e-...",
    "metadata": { "filename": "your_document.pdf", "chunk_index": 0 }
  }
]
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
│   └── main.py              # FastAPI app, middleware, router, static files
├── frontend/
│   └── index.html           # Web UI (vanilla HTML/CSS/JS, served by FastAPI)
├── tests/
│   └── test_api.py          # Endpoint tests with mocked dependencies
├── infra/
│   ├── AWS_ARCHITECTURE.md  # Production AWS deployment reference
│   └── terraform/           # Infrastructure as code (VPC, ECS, ALB, EFS, ECR...)
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

The MVP infrastructure runs on **ECS Fargate + ALB + EFS**, provisioned with Terraform. ChromaDB data is persisted on EFS across container restarts.

### Infrastructure overview

| Service | Role |
|---|---|
| ECS Fargate | Serverless container hosting |
| Application Load Balancer | Public entry point (port 80) |
| ECR | Docker image registry |
| EFS | Persistent storage for ChromaDB |
| Secrets Manager | OpenAI API key |
| CloudWatch | Container logs |

### Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) configured (`aws configure`)
- [Docker](https://www.docker.com/) with BuildKit support

### 1. Provision the infrastructure

```bash
cd infra/terraform

cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — set your openai_api_key and aws_region

cp backend.hcl.example backend.hcl
# Edit backend.hcl — set your S3 bucket name for remote state

terraform init -backend-config=backend.hcl
terraform plan
terraform apply
```

After apply, note the outputs:

```bash
terraform output ecr_repository_url   # e.g. 123456789.dkr.ecr.us-east-1.amazonaws.com/rag-api
terraform output alb_dns_name         # e.g. rag-api-alb-xxxxx.us-east-1.elb.amazonaws.com
```

### 2. Build and push the Docker image

```bash
# Set your values
ECR_URL=$(terraform -chdir=infra/terraform output -raw ecr_repository_url)
AWS_REGION=us-east-1  # must match terraform.tfvars

# Authenticate Docker with ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_URL

# Build for linux/amd64 (required for Fargate)
docker build --platform linux/amd64 -t rag-api .

# Tag and push
docker tag rag-api:latest $ECR_URL:latest
docker push $ECR_URL:latest
```

### 3. Deploy

Force ECS to pull the new image:

```bash
aws ecs update-service \
  --cluster rag-api-cluster \
  --service rag-api-service \
  --force-new-deployment \
  --region $AWS_REGION
```

The service will be available at the ALB DNS name in ~1-2 minutes.

### Redeploying after code changes

Repeat steps 2 and 3 on every new release:

```bash
docker build --platform linux/amd64 -t rag-api .
docker tag rag-api:latest $ECR_URL:latest
docker push $ECR_URL:latest

aws ecs update-service \
  --cluster rag-api-cluster \
  --service rag-api-service \
  --force-new-deployment
```

### Monitoring logs

```bash
aws logs tail /ecs/rag-api --follow
```

### Teardown

```bash
cd infra/terraform
terraform destroy
```

> **Note:** `terraform destroy` does not delete the ECR images. Run `aws ecr batch-delete-image` first if you want a full cleanup.

See [`infra/AWS_ARCHITECTURE.md`](infra/AWS_ARCHITECTURE.md) for the full reference architecture including future additions (API Gateway, OpenSearch, Route 53).

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
