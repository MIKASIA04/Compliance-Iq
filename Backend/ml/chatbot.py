# ============================================================
# FILE: ml/chatbot.py
# ============================================================
# ComplianceIQ — GraphRAG Compliance Chatbot
#
# Pipeline:
#   1. Retrieve relevant regulation chunks from ChromaDB
#   2. Read regulation_id from retrieved metadata
#   3. Resolve the regulation through Neo4j
#   4. Detect superseded -> current regulation relationships
#   5. Retrieve CURRENT regulation text from ChromaDB
#   6. Build grounded context using current regulation text
#   7. Generate answer using Groq
#   8. Return detailed citations and retrieval metadata
#
# Supports:
#   use_graph=True  -> GraphRAG
#   use_graph=False -> Flat RAG baseline
#
# Run from Backend:
#   python ml/chatbot.py
# ============================================================

import os

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "regulations"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

GROQ_MODEL = "openai/gpt-oss-120b"

TOP_K = 3

_collection = None
_neo4j_driver = None


# ============================================================
# CHROMADB
# ============================================================

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


# ============================================================
# NEO4J
# ============================================================

def _get_neo4j_driver():
    """Create and reuse the Neo4j driver."""

    global _neo4j_driver

    if _neo4j_driver is not None:
        return _neo4j_driver

    try:
        from neo4j import GraphDatabase

        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")

        if not uri or not username or not password:
            return None

        _neo4j_driver = GraphDatabase.driver(
            uri,
            auth=(username, password)
        )

        # Verify that the connection actually works.
        _neo4j_driver.verify_connectivity()

        return _neo4j_driver

    except Exception:
        _neo4j_driver = None
        return None


# ============================================================
# NEO4J — CURRENT VERSION RESOLUTION
# ============================================================

def _get_current_version(regulation_id):
    """
    Resolve a regulation to its latest current version.

    Example:

        rbi_kyc_2016
              |
          SUPERSEDES
              v
        rbi_kyc_2023

    Returns the current regulation ID.

    If no superseding regulation exists, the original regulation
    ID is returned.
    """

    driver = _get_neo4j_driver()

    if driver is None or not regulation_id:
        return regulation_id

    query = """
    MATCH (regulation:Regulation {id: $id})

    OPTIONAL MATCH
        (regulation)<-[:SUPERSEDES*1..]-(current:Regulation)

    WITH regulation, current

    ORDER BY
        CASE
            WHEN current IS NULL THEN regulation.year
            ELSE current.year
        END DESC

    RETURN COALESCE(current.id, regulation.id) AS current_id
    LIMIT 1
    """

    try:
        with driver.session() as session:
            result = session.run(
                query,
                id=regulation_id
            ).single()

            if result:
                return result["current_id"]

    except Exception:
        pass

    return regulation_id


# ============================================================
# NEO4J — REGULATION DETAILS
# ============================================================

def _get_regulation_details(regulation_id):
    """
    Get regulation metadata from Neo4j.
    """

    driver = _get_neo4j_driver()

    if driver is None or not regulation_id:
        return None

    query = """
    MATCH (r:Regulation {id: $id})
    RETURN
        r.id AS id,
        r.name AS name,
        r.year AS year,
        r.status AS status
    LIMIT 1
    """

    try:
        with driver.session() as session:
            result = session.run(
                query,
                id=regulation_id
            ).single()

            if result:
                return {
                    "id": result["id"],
                    "name": result["name"],
                    "year": result["year"],
                    "status": result["status"],
                }

    except Exception:
        pass

    return None


# ============================================================
# CHROMA — CURRENT REGULATION TEXT
# ============================================================

def _get_current_regulation_chunks(
    collection,
    regulation_id,
    question,
    n_results=TOP_K
):
    """
    Retrieve text specifically from the resolved CURRENT
    regulation.

    This is the important GraphRAG step.

    Neo4j tells us which regulation is current.
    ChromaDB then supplies the actual text belonging to
    that current regulation.
    """

    if not collection or not regulation_id:
        return [], []

    try:
        results = collection.query(
            query_texts=[question],
            n_results=n_results,
            where={
                "regulation_id": regulation_id
            }
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        return documents, metadatas

    except Exception:
        return [], []


# ============================================================
# GROQ
# ============================================================

def _call_groq(question, context_text):
    """
    Generate a grounded answer using only supplied regulation
    context.
    """

    import requests

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return (
            "GROQ_API_KEY is not set in .env — cannot generate "
            "an AI answer. Here is the relevant regulation text "
            "found instead:\n\n" + context_text
        )

    prompt = f"""
You are a compliance assistant for an Indian fintech company.

Answer the question using ONLY the regulation excerpts provided
below.

Important rules:
- Do not invent legal requirements.
- Do not use outside knowledge.
- If the excerpts do not contain the answer, say so honestly.
- Prefer the CURRENT regulation when current-version information
  is explicitly provided.
- Cite the regulation source when making a claim.
- Keep the answer concise and professional.

Regulation excerpts:

{context_text}

Question:
{question}

Answer in 2-4 sentences with inline source citations.
"""

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
            timeout=30,
        )

        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return (
            f"AI generation unavailable ({e}). "
            "Relevant regulation text:\n\n"
            + context_text
        )


# ============================================================
# MAIN QUESTION ANSWER FUNCTION
# ============================================================

def answer_question(question, use_graph=True):
    """
    Answer a compliance question.

    Parameters
    ----------
    question : str
        User's compliance question.

    use_graph : bool
        True  -> GraphRAG
        False -> Flat RAG baseline.

    Returns
    -------
    dict
        Contains answer, sources, citations and retrieval mode.
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
            "retrieval_mode": (
                "graph_rag" if use_graph else "flat_rag"
            ),
            "found_in_regulations": False,
        }

    # --------------------------------------------------------
    # STEP 1 — Initial Chroma retrieval
    # --------------------------------------------------------

    results = collection.query(
        query_texts=[question],
        n_results=TOP_K
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "question": question,
            "answer": (
                "No relevant regulation content was found "
                "for this question."
            ),
            "sources": [],
            "citations": [],
            "retrieval_mode": (
                "graph_rag" if use_graph else "flat_rag"
            ),
            "found_in_regulations": False,
        }

    # --------------------------------------------------------
    # FLAT RAG BASELINE
    # --------------------------------------------------------

    if not use_graph:

        context_parts = []
        sources = []
        citations = []

        for doc, meta in zip(documents, metadatas):

            source = meta.get(
                "source",
                "Unknown"
            )

            section = meta.get(
                "section",
                ""
            )

            regulation_id = meta.get(
                "regulation_id",
                ""
            )

            context_parts.append(
                f"[{source} — {section}]\n{doc}"
            )

            if source not in sources:
                sources.append(source)

            citations.append(
                {
                    "source": source,
                    "section": section,
                    "original_regulation_id": regulation_id,
                    "current_regulation_id": "",
                    "current_regulation_name": "",
                    "current_year": "",
                    "status": "",
                    "retrieval_mode": "flat_rag",
                }
            )

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
            "retrieval_mode": "flat_rag",
            "found_in_regulations": True,
        }

    # --------------------------------------------------------
    # GRAPHRAG
    # --------------------------------------------------------

    graph_context_parts = []
    sources = []
    citations = []

    processed_regulations = set()

    for original_doc, original_meta in zip(
        documents,
        metadatas
    ):

        source = original_meta.get(
            "source",
            "Unknown"
        )

        section = original_meta.get(
            "section",
            ""
        )

        original_regulation_id = original_meta.get(
            "regulation_id",
            ""
        )

        # ----------------------------------------------------
        # STEP 2 — Resolve regulation through Neo4j
        # ----------------------------------------------------

        current_regulation_id = _get_current_version(
            original_regulation_id
        )

        current_details = _get_regulation_details(
            current_regulation_id
        )

        # ----------------------------------------------------
        # STEP 3 — Retrieve CURRENT regulation text
        # ----------------------------------------------------

        current_documents, current_metadatas = (
            _get_current_regulation_chunks(
                collection,
                current_regulation_id,
                question,
                TOP_K
            )
        )

        # If current text is unavailable, fall back to the
        # originally retrieved text rather than inventing data.
        if current_documents:

            if current_regulation_id not in processed_regulations:

                for current_doc, current_meta in zip(
                    current_documents,
                    current_metadatas
                ):

                    current_source = current_meta.get(
                        "source",
                        "Unknown"
                    )

                    current_section = current_meta.get(
                        "section",
                        ""
                    )

                    graph_context_parts.append(
                        "[CURRENT REGULATION: "
                        f"{current_details['name'] if current_details else current_regulation_id}"
                        "]\n"
                        f"[{current_source} — {current_section}]\n"
                        f"{current_doc}"
                    )

                processed_regulations.add(
                    current_regulation_id
                )

        else:

            graph_context_parts.append(
                "[CURRENT REGULATION TEXT NOT FOUND IN "
                "VECTOR STORE]\n"
                f"[Original source: {source} — {section}]\n"
                f"{original_doc}"
            )

        # ----------------------------------------------------
        # Citation metadata
        # ----------------------------------------------------

        citation = {
            "source": source,
            "section": section,
            "original_regulation_id": original_regulation_id,
            "current_regulation_id": (
                current_details["id"]
                if current_details
                else current_regulation_id
            ),
            "current_regulation_name": (
                current_details["name"]
                if current_details
                else ""
            ),
            "current_year": (
                current_details["year"]
                if current_details
                else ""
            ),
            "status": (
                current_details["status"]
                if current_details
                else ""
            ),
            "retrieval_mode": "graph_rag",
        }

        citations.append(citation)

        if source not in sources:
            sources.append(source)

    # --------------------------------------------------------
    # STEP 4 — Generate answer from current regulation context
    # --------------------------------------------------------

    context_text = "\n\n".join(
        graph_context_parts
    )

    answer = _call_groq(
        question,
        context_text
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "citations": citations,
        "retrieval_mode": "graph_rag",
        "found_in_regulations": True,
    }


# ============================================================
# TEST
# ============================================================

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
        "NEO4J_URI       :",
        "SET ✓" if os.getenv("NEO4J_URI")
        else "NOT SET ✗"
    )

    test_question = (
        "What is the reporting threshold for large cash "
        "transactions under PMLA?"
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
        f"\nSources: {result['sources']}"
    )

    print(
        f"\nCitations:"
    )

    for citation in result["citations"]:
        print(citation)

    print(
        f"\nFound in regulations: "
        f"{result['found_in_regulations']}"
    )