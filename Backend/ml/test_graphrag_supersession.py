"""
test_graphrag_supersession.py

End-to-end verification of the ComplianceIQ GraphRAG supersession flow:

OLD regulation
    ↓
Neo4j supersession traversal
    ↓
CURRENT regulation
    ↓
ChromaDB current-regulation text retrieval
"""

from chatbot import (
    _get_collection,
    _get_current_version,
    _get_current_regulation_chunks,
)


OLD_REGULATION_ID = "rbi_kyc_2016"
EXPECTED_CURRENT_ID = "rbi_kyc_2023"


def test_supersession_resolution():
    print("=" * 70)
    print("GRAPHRAG SUPERSESSION TEST")
    print("=" * 70)

    print(f"\nOld regulation: {OLD_REGULATION_ID}")

    # Step 1: Resolve old regulation to current regulation through Neo4j
    current_id = _get_current_version(OLD_REGULATION_ID)

    print(f"Neo4j current regulation: {current_id}")

    assert current_id == EXPECTED_CURRENT_ID, (
        f"Expected {EXPECTED_CURRENT_ID}, but got {current_id}"
    )

    print("✓ Neo4j supersession resolution passed")

    # Step 2: Retrieve text specifically from the current regulation
    collection = _get_collection()

    texts, metadata = _get_current_regulation_chunks(
        collection,
        current_id,
        "What are the KYC requirements?",
        3,
    )

    print(f"Current regulation chunks retrieved: {len(texts)}")

    assert len(texts) > 0, (
        "No current-regulation text was retrieved from ChromaDB"
    )

    # Step 3: Verify every retrieved chunk belongs to the current regulation
    for item in metadata:
        regulation_id = item.get("regulation_id")
        status = item.get("status")

        print(
            f"Chunk: {item.get('section')} | "
            f"regulation_id={regulation_id} | "
            f"status={status}"
        )

        assert regulation_id == EXPECTED_CURRENT_ID, (
            f"Retrieved wrong regulation: {regulation_id}"
        )

        assert status == "current", (
            f"Retrieved regulation is not marked current: {status}"
        )

    print("✓ ChromaDB current-text retrieval passed")
    print("✓ All retrieved chunks belong to the current regulation")
    print("\n" + "=" * 70)
    print("GRAPHRAG SUPERSESSION TEST PASSED ✓")
    print("=" * 70)


if __name__ == "__main__":
    test_supersession_resolution()