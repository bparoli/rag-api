from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are a precise and helpful assistant.
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say "I don't have enough information to answer that."
Be concise, accurate, and cite which part of the context supports your answer."""


def build_context(chunks: List[Dict[str, Any]]) -> str:
    return "\n\n---\n\n".join(
        f"[Source: {c['metadata']['doc_id']}, chunk {c['metadata']['chunk_index']}]\n{c['text']}"
        for c in chunks
    )


def generate_answer(question: str, chunks: List[Dict[str, Any]]) -> str:
    """Generate an answer grounded in the retrieved chunks."""
    context = build_context(chunks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        },
    ]
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content
