# ============================================================
# FILE: ml/build_vectorstore.py
# ============================================================
# Embeds all regulation chunks into ChromaDB using a FREE local
# embedding model (sentence-transformers) — no OpenAI API cost.
#
# Run ONCE. After this, semantic search is completely free and
# runs entirely on your machine.
#
# HOW TO RUN:
#   python ml/build_vectorstore.py
# ============================================================

import os
import json

CHUNKS_FILE = "data/chunks.json"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "regulations"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # small, fast, free, runs locally


def main():
    import chromadb
    from chromadb.utils import embedding_functions

    if not os.path.exists(CHUNKS_FILE):
        print(f"ERROR: {CHUNKS_FILE} not found. Run ml/extract_regulations.py first.")
        return

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Building ChromaDB vector store...")
    print(f"Found {len(chunks)} chunks to embed")
    print(f"Using local embedding model: {EMBEDDING_MODEL} (free, no API cost)")

    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Fresh start each time this is run
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedder,
    )

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "source": c.get("source", "Unknown"),
            "section": c.get("section", ""),
            "status": c.get("status", "current"),
        }
        for c in chunks
    ]

    # Embed in batches so progress is visible and memory stays low
    batch_size = 50
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    for batch_num, i in enumerate(range(0, len(chunks), batch_size), start=1):
        collection.add(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )
        print(f"Batch {batch_num}/{total_batches} embedded...")

    print("\nAll chunks embedded successfully!")
    print(f"Vector store saved to: {CHROMA_DIR}/")

    # Quick sanity test
    test_query = "KYC requirement for large transfers"
    print(f'\nTest search: "{test_query}"')
    results = collection.query(query_texts=[test_query], n_results=1)
    if results["documents"] and results["documents"][0]:
        top_doc = results["documents"][0][0]
        top_meta = results["metadatas"][0][0]
        print(f"Top result: {top_meta['source']} — {top_doc[:150]}...")
        print("Search test passed ✓")
    else:
        print("WARNING: search returned no results.")


if __name__ == "__main__":
    main()
