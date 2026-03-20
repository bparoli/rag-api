import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.core.ingestion import extract_text, chunk_text
from app.services.vector_store import vector_store
from app.services.llm import generate_answer

router = APIRouter()


# --- Schemas ---

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

class IngestResponse(BaseModel):
    doc_id: str
    chunks_stored: int
    filename: str


# --- Endpoints ---

@router.post("/ingest", response_model=IngestResponse, summary="Ingest a document")
async def ingest_document(file: UploadFile = File(...)):
    """
    Upload a .txt or .pdf file. The document is chunked, embedded,
    and stored in the vector database for later retrieval.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")

    try:
        text = extract_text(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=422, detail="Could not extract text from document.")

    doc_id = str(uuid.uuid4())
    stored = vector_store.add_chunks(chunks, doc_id, filename=file.filename)

    return IngestResponse(doc_id=doc_id, chunks_stored=stored, filename=file.filename)


@router.post("/query", response_model=QueryResponse, summary="Query the knowledge base")
def query(request: QueryRequest):
    """
    Ask a question in natural language. The API retrieves the most relevant
    document chunks and generates a grounded answer using an LLM.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    chunks = vector_store.query(request.question)
    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant documents found.")

    answer = generate_answer(request.question, chunks)
    no_info = "i don't have enough information" in answer.lower()
    return QueryResponse(answer=answer, sources=[] if no_info else chunks)


@router.get("/documents", summary="List all documents")
def list_documents():
    """Return all documents stored in the vector database."""
    return vector_store.list_documents()


@router.delete("/documents/{doc_id}", summary="Delete a document")
def delete_document(doc_id: str):
    """Remove all chunks of a document from the vector store."""
    vector_store.delete_document(doc_id)
    return {"message": f"Document {doc_id} deleted successfully."}
