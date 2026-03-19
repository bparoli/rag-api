from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings


class VectorStoreService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        import os
        os.environ.setdefault("CHROMA_OPENAI_API_KEY", settings.openai_api_key)
        self.embed_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key_env_var="CHROMA_OPENAI_API_KEY",
            model_name=settings.embedding_model,
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            embedding_function=self.embed_fn,
        )

    def add_chunks(self, chunks: List[str], doc_id: str, filename: str = "") -> int:
        """Embed and store chunks. Returns number of chunks stored."""
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": doc_id, "chunk_index": i, "filename": filename} for i in range(len(chunks))]
        self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        return len(chunks)

    def query(self, question: str) -> List[Dict[str, Any]]:
        """Retrieve top-k most relevant chunks for a question."""
        results = self.collection.query(
            query_texts=[question],
            n_results=settings.top_k_results,
        )
        chunks = results["documents"][0]
        metadatas = results["metadatas"][0]
        seen = set()
        unique = []
        for c, m in zip(chunks, metadatas):
            if c not in seen:
                seen.add(c)
                unique.append({"text": c, "metadata": m})
        return unique

    def list_documents(self) -> List[Dict[str, Any]]:
        """Return one entry per unique doc_id with its metadata."""
        results = self.collection.get(include=["metadatas"])
        seen = {}
        for meta in results["metadatas"]:
            doc_id = meta.get("doc_id")
            if doc_id and doc_id not in seen:
                seen[doc_id] = meta
        return [{"doc_id": doc_id, "metadata": meta} for doc_id, meta in seen.items()]

    def delete_document(self, doc_id: str) -> None:
        """Remove all chunks belonging to a document."""
        results = self.collection.get(where={"doc_id": doc_id})
        if results["ids"]:
            self.collection.delete(ids=results["ids"])


vector_store = VectorStoreService()