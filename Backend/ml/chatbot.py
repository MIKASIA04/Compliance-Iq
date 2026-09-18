# ============================================================
# FILE: ml/chatbot.py
# ============================================================
# Answers compliance questions using RAG:
#   1. Embed the question (same local model as build_vectorstore.py)
#   2. Retrieve the most relevant regulation chunks from ChromaDB
#   3. Pass those chunks + the question to Groq's free Llama API
#   4. Return a cited, grounded answer
#
# HOW TO TEST:
#   python ml/chatbot.py
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "regulations"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GROQ_MODEL = "openai/gpt-oss-120b"
TOP_K = 3

_collection = None


def _get_collection():
    """Load the ChromaDB collection once and reuse it."""
    global _collection
    if _collection is not None:
        return _collection

    import chromadb
    from chromadb.utils import embedding_functions

    if not os.path.exists(CHROMA_DIR):
        return None

    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        _collection = client.get_collection(COLLECTION_NAME, embedding_function=embedder)
    except Exception:
        return None
    return _collection


def _call_groq(question: str, context_text: str) -> str:
    """Call Groq's free Llama API to write a grounded answer."""
    import requests

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return (
            "GROQ_API_KEY is not set in .env — cannot generate an AI answer. "
            "Here is the relevant regulation text found instead:\n\n" + context_text
        )

    prompt = f"""You are a compliance assistant for an Indian fintech company.
Answer the question using ONLY the regulation excerpts below. If the excerpts
don't contain the answer, say so honestly — do not make up information.
Cite the source name for any claim you make.

Regulation excerpts:
{context_text}

Question: {question}

Answer in 2-4 sentences, professional tone, with source citations inline."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.2,
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI generation unavailable ({e}). Relevant regulation text:\n\n{context_text}"


def answer_question(question: str) -> dict:
    """
    Main entry point. Returns:
    {
        "question": str,
        "answer": str,
        "sources": [str, ...],
        "found_in_regulations": bool,
    }
    """
    collection = _get_collection()

    if collection is None:
        return {
            "question": question,
            "answer": (
                "The regulation knowledge base isn't built yet. "
                "Run `python ml/extract_regulations.py` then "
                "`python ml/build_vectorstore.py` first."
            ),
            "sources": [],
            "found_in_regulations": False,
        }

    results = collection.query(query_texts=[question], n_results=TOP_K)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "question": question,
            "answer": "No relevant regulation content was found for this question.",
            "sources": [],
            "found_in_regulations": False,
        }

    context_parts = []
    sources = []
    for doc, meta in zip(documents, metadatas):
        source = meta.get("source", "Unknown")
        section = meta.get("section", "")
        context_parts.append(f"[{source} — {section}]\n{doc}")
        if source not in sources:
            sources.append(source)

    context_text = "\n\n".join(context_parts)
    answer = _call_groq(question, context_text)

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "found_in_regulations": True,
    }


if __name__ == "__main__":
    print("ChromaDB exists :", "YES ✓" if os.path.exists(CHROMA_DIR) else "NO ✗")
    print("GROQ_API_KEY    :", "SET ✓" if os.getenv("GROQ_API_KEY") else "NOT SET ✗")

    test_question = "What is the reporting threshold for large cash transactions under PMLA?"
    print(f'\nQ: "{test_question}"')
    result = answer_question(test_question)
    print(f"A: {result['answer']}")
    print(f"Sources: {result['sources']}")
    print(f"Found in regulations: {result['found_in_regulations']}")
