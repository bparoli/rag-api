from typing import List
from app.core.config import settings


def chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    chunks = []
    start = 0

    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap

    return [c for c in chunks if c.strip()]


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from uploaded file. Supports .txt and .pdf."""
    if filename.endswith(".pdf"):
        try:
            import pdfplumber
            import io
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                return "\n".join(
                    page.extract_text() or "" for page in pdf.pages
                )
        except ImportError:
            raise ValueError("pdfplumber not installed. Run: pip install pdfplumber")

    # Default: treat as plain text
    return file_bytes.decode("utf-8", errors="ignore")
