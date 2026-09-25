# ============================================================
# FILE: ml/build_vectorstore.py
# ============================================================
# Builds ChromaDB vector store with regulation metadata.
#
# The regulation_id connects ChromaDB retrieval results to the
# Neo4j knowledge graph used by GraphRAG.
# ============================================================

import os
import json

CHUNKS_FILE = "data/chunks.json"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "regulations"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def main():
    import chromadb
    from chromadb.utils import embedding_functions

    if not os.path.exists(CHUNKS_FILE):
        print(
            f"ERROR: {CHUNKS_FILE} not found. "
            "Run ml/extract_regulations.py first."
        )
        return

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print("Building ChromaDB vector store...")
    print(f"Found {len(chunks)} chunks to embed")
    print(f"Using local embedding model: {EMBEDDING_MODEL}")

    # Map Chroma source names to Neo4j regulation IDs
    source_to_regulation_id = {
        "Dpdp 2023": "dpdp_2023",
        "Pmla 2002": "pmla_2002",
        "Rbi Kyc Master Direction": "rbi_kyc_2023",
    }

    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Fresh start each time this script is run
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Existing ChromaDB collection deleted.")
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
            "regulation_id": source_to_regulation_id.get(
                c.get("source", ""),
                ""
            ),
        }
        for c in chunks
    ]

    # Check that every chunk received a regulation ID
    missing_ids = [
        c.get("source", "Unknown")
        for c in chunks
        if not source_to_regulation_id.get(c.get("source", ""), "")
    ]

    if missing_ids:
        print("\nWARNING: Some chunks have no regulation_id.")
        print("Sources without IDs:")
        for source in sorted(set(missing_ids)):
            print(f"  - {source}")

    else:
        print("All chunks mapped to Neo4j regulation IDs ✓")

    # Embed in batches
    batch_size = 50
    total_batches = (len(chunks) + batch_size - 1) // batch_size

    for batch_num, i in enumerate(
        range(0, len(chunks), batch_size),
        start=1
    ):
        collection.add(
            ids=ids[i:i + batch_size],
            documents=documents[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
        )

        print(
            f"Batch {batch_num}/{total_batches} embedded..."
        )

    print("\nAll chunks embedded successfully!")
    print(f"Vector store saved to: {CHROMA_DIR}/")

    # Quick sanity test
    test_query = "KYC requirement for large transfers"

    print(f'\nTest search: "{test_query}"')

    results = collection.query(
        query_texts=[test_query],
        n_results=1
    )

    if results["documents"] and results["documents"][0]:

        top_doc = results["documents"][0][0]
        top_meta = results["metadatas"][0][0]

        print(
            f"Top result: "
            f"{top_meta['source']} — "
            f"{top_doc[:150]}..."
        )

        print(
            f"Regulation ID: "
            f"{top_meta['regulation_id']}"
        )

        print("Search test passed ✓")

    else:
        print("WARNING: search returned no results.")


if __name__ == "__main__":
    main()