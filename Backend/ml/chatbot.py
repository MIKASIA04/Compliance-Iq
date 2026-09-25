# ============================================================
# FILE: ml/chatbot.py
# ============================================================
# Compliance chatbot using Hybrid GraphRAG:
#
# 1. Retrieve relevant regulation chunks from ChromaDB.
# 2. Use Neo4j to resolve superseded regulations.
# 3. Prefer the CURRENT regulation version.
# 4. Send the final grounded context to Groq.
# 5. Return explicit citation metadata.
#
# HOW TO TEST:
#   python ml/chatbot.py
# ============================================================

import os
import json
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "regulations"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GROQ_MODEL = "openai/gpt-oss-120b"
TOP_K = 3

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

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
        _collection = client.get_collection(
            COLLECTION_NAME,
            embedding_function=embedder
        )
    except Exception:
        return None

    return _collection


def _get_neo4j_driver():
    """Create a Neo4j driver if credentials are available."""
    if not all([
        NEO4J_URI,
        NEO4J_USERNAME,
        NEO4J_PASSWORD
    ]):
        return None

    try:
        from neo4j import GraphDatabase

        return GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
    except Exception:
        return None


def _get_current_version(regulation_id: str) -> str:
    """
    Resolve a regulation ID to its current version using Neo4j.

    If the regulation is already current, its own ID is returned.
    If Neo4j is unavailable, the original ID is returned.
    """

    driver = _get_neo4j_driver()

    if driver is None:
        return regulation_id

    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (regulation:Regulation {id: $id})
                OPTIONAL MATCH
                    (regulation)<-[:SUPERSEDES*1..]-(current:Regulation)
                WITH regulation, current
                ORDER BY current.year DESC
                RETURN COALESCE(current.id, regulation.id) AS current_id
                LIMIT 1
                """,
                id=regulation_id
            )

            record = result.single()

            if record:
                return record["current_id"]

    except Exception as e:
        print(f"Neo4j lookup warning: {e}")

    finally:
        driver.close()

    return regulation_id


def _get_regulation_details(regulation_id: str) -> dict:
    """
    Retrieve regulation metadata from Neo4j.
    """

    driver = _get_neo4j_driver()

    if driver is None:
        return {}

    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (r:Regulation {id: $id})
                RETURN
                    r.id AS id,
                    r.name AS name,
                    r.year AS year,
                    r.status AS status
                """,
                id=regulation_id
            )

            record = result.single()

            if record:
                return {
                    "id": record["id"],
                    "name": record["name"],
                    "year": record["year"],
                    "status": record["status"],
                }

    except Exception as e:
        print(f"Neo4j metadata warning: {e}")

    finally:
        driver.close()

    return {}


def _call_groq(question: str, context_text: str) -> str:
    """Call Groq to write a grounded answer."""

    import requests

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return (
            "GROQ_API_KEY is not set in .env — cannot generate an AI answer. "
            "Here is the relevant regulation text found instead:\n\n"
            + context_text
        )

    prompt = f"""You are a compliance assistant for an Indian fintech company.

Answer the question using ONLY the regulation excerpts below.

Rules:
- Do not invent facts.
- If the excerpts do not contain the answer, say so honestly.
- Cite the regulation source used for each important claim.
- Prefer CURRENT regulation versions over superseded versions.
- Do not treat a superseded regulation as the current legal requirement.

Regulation excerpts:
{context_text}

Question:
{question}

Answer in 2-4 sentences, professional tone, with source citations inline."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 400,
                "temperature": 0.2,
            },
            timeout=15,
        )

        response.raise_for_status()

        data = json.loads(
            response.content.decode("utf-8")
        )

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return (
            f"AI generation unavailable ({e}). "
            f"Relevant regulation text:\n\n{context_text}"
        )


def answer_question(question: str, use_graph: bool = True) -> dict:
    """
    Main chatbot entry point.

    use_graph=True:
        Hybrid GraphRAG mode.

    use_graph=False:
        Original flat ChromaDB RAG mode.

    Returns:
    {
        "question": str,
        "answer": str,
        "sources": [...],
        "citations": [...],
        "retrieval_mode": str,
        "found_in_regulations": bool
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
            "citations": [],
            "retrieval_mode": "graph_rag" if use_graph else "flat_rag",
            "found_in_regulations": False,
        }

    results = collection.query(
        query_texts=[question],
        n_results=TOP_K
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "question": question,
            "answer": "No relevant regulation content was found for this question.",
            "sources": [],
            "citations": [],
            "retrieval_mode": "graph_rag" if use_graph else "flat_rag",
            "found_in_regulations": False,
        }

    context_parts = []
    sources = []
    citations = []

    for doc, meta in zip(documents, metadatas):

        original_source = meta.get("source", "Unknown")
        section = meta.get("section", "")

        citation = {
            "source": original_source,
            "section": section,
            "original_regulation_id": meta.get(
                "regulation_id",
                ""
            ),
            "current_regulation_id": "",
            "current_regulation_name": "",
            "current_year": "",
            "status": "",
            "retrieval_mode": "graph_rag" if use_graph else "flat_rag",
        }

        if use_graph:

            regulation_id = meta.get("regulation_id")

            if regulation_id:
                current_id = _get_current_version(
                    regulation_id
                )

                current_details = _get_regulation_details(
                    current_id
                )

                citation["current_regulation_id"] = current_id
                citation["current_regulation_name"] = (
                    current_details.get("name", "")
                )
                citation["current_year"] = (
                    current_details.get("year", "")
                )
                citation["status"] = (
                    current_details.get("status", "")
                )

                display_source = (
                    current_details.get("name")
                    or original_source
                )

                if current_id != regulation_id:
                    context_parts.append(
                        f"[CURRENT REGULATION: {display_source}]\n"
                        f"[Original retrieved source: {original_source}]\n"
                        f"[Section: {section}]\n"
                        f"{doc}"
                    )
                else:
                    context_parts.append(
                        f"[{display_source} — {section}]\n"
                        f"{doc}"
                    )

                if display_source not in sources:
                    sources.append(display_source)

            else:
                context_parts.append(
                    f"[{original_source} — {section}]\n"
                    f"{doc}"
                )

                if original_source not in sources:
                    sources.append(original_source)

        else:

            context_parts.append(
                f"[{original_source} — {section}]\n"
                f"{doc}"
            )

            if original_source not in sources:
                sources.append(original_source)

        citations.append(citation)

    context_text = "\n\n".join(context_parts)

    answer = _call_groq(
        question,
        context_text
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "citations": citations,
        "retrieval_mode": (
            "graph_rag"
            if use_graph
            else "flat_rag"
        ),
        "found_in_regulations": True,
    }


if __name__ == "__main__":

    print(
        "ChromaDB exists :",
        "YES ✓" if os.path.exists(CHROMA_DIR)
        else "NO ✗"
    )

    print(
        "GROQ_API_KEY    :",
        "SET ✓" if os.getenv("GROQ_API_KEY")
        else "NOT SET ✗"
    )

    print(
        "NEO4J configured:",
        "YES ✓"
        if all([
            NEO4J_URI,
            NEO4J_USERNAME,
            NEO4J_PASSWORD
        ])
        else "NO ✗"
    )

    test_question = (
        "What is the reporting threshold for "
        "large cash transactions under PMLA?"
    )

    print(
        f'\nQ: "{test_question}"'
    )

    result = answer_question(
        test_question,
        use_graph=True
    )

    print(
        f"\nRetrieval mode: "
        f"{result['retrieval_mode']}"
    )

    print(
        f"\nA: {result['answer']}"
    )

    print(
        f"\nSources: "
        f"{result['sources']}"
    )

    print(
        "\nCitations:"
    )

    for citation in result["citations"]:
        print(citation)

    print(
        f"\nFound in regulations: "
        f"{result['found_in_regulations']}"
    )