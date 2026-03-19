from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="RAG API",
    description="A production-ready Retrieval-Augmented Generation API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
