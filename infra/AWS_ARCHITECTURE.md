# RAG API — AWS Reference Architecture

## Production Deployment on AWS

```
┌─────────────────────────────────────────────────────────────────┐
│                          AWS Cloud                              │
│                                                                 │
│   ┌──────────┐     ┌──────────────┐     ┌──────────────────┐   │
│   │  Route53 │────▶│  API Gateway │────▶│   ECS Fargate    │   │
│   └──────────┘     └──────────────┘     │   (rag-api)      │   │
│                                         └────────┬─────────┘   │
│                                                  │             │
│                    ┌─────────────────────────────┼──────────┐  │
│                    │                             │          │  │
│             ┌──────▼──────┐             ┌────────▼───────┐  │  │
│             │  S3 Bucket  │             │  OpenSearch    │  │  │
│             │  (raw docs) │             │  (vector store)│  │  │
│             └─────────────┘             └────────────────┘  │  │
│                                                              │  │
│             ┌─────────────┐             ┌────────────────┐  │  │
│             │  Secrets    │             │   CloudWatch   │  │  │
│             │  Manager    │             │   (logs)       │  │  │
│             └─────────────┘             └────────────────┘  │  │
│                                                              │  │
└──────────────────────────────────────────────────────────────┘  
```

## Key AWS Services

| Service | Role |
|---|---|
| **ECS Fargate** | Serverless container hosting — no EC2 management |
| **API Gateway** | Rate limiting, auth, and routing |
| **S3** | Durable storage for original documents |
| **OpenSearch** | Managed vector search (alternative to local ChromaDB) |
| **Secrets Manager** | Secure storage for OpenAI API key |
| **CloudWatch** | Logs, metrics, and alerts |
| **Route 53** | DNS and health checks |

## Scalability Notes

- ECS auto-scales horizontally based on CPU/memory
- OpenSearch scales storage and compute independently
- API Gateway handles throttling and DDoS protection out of the box
- All secrets injected at runtime via Secrets Manager (zero secrets in code or env files)
