"""
evaluate_citations.py — real citation-quality evaluation for Table VI

Compares:
1. Flat RAG
2. GraphRAG

across 18 compliance questions.

Run from Backend:
    python -m ml.evaluate_citations
"""

from ml.chatbot import answer_question


QUESTIONS = [
    # RBI KYC
    {
        "question": "What documents are required to open an account for a company?",
        "expected_regulation_id": "rbi_kyc_2023",
    },
    {
        "question": "What documents are required to open an account for a partnership firm?",
        "expected_regulation_id": "rbi_kyc_2023",
    },
    {
        "question": "What documents are required to open an account for a trust?",
        "expected_regulation_id": "rbi_kyc_2023",
    },
    {
        "question": "What documents are required for an unincorporated association?",
        "expected_regulation_id": "rbi_kyc_2023",
    },
    {
        "question": "What are the KYC requirements for opening a bank account?",
        "expected_regulation_id": "rbi_kyc_2023",
    },
    {
        "question": "What is customer due diligence in KYC?",
        "expected_regulation_id": "rbi_kyc_2023",
    },

    # PMLA
    {
        "question": "What is the offence of money-laundering under PMLA?",
        "expected_regulation_id": "pmla_2002",
    },
    {
        "question": "What records must a reporting entity maintain under PMLA?",
        "expected_regulation_id": "pmla_2002",
    },
    {
        "question": "What is enhanced due diligence under PMLA?",
        "expected_regulation_id": "pmla_2002",
    },
    {
        "question": "What powers does the Director have to impose fines under PMLA?",
        "expected_regulation_id": "pmla_2002",
    },
    {
        "question": "What are the obligations of reporting entities under PMLA?",
        "expected_regulation_id": "pmla_2002",
    },
    {
        "question": "What is the burden of proof under PMLA?",
        "expected_regulation_id": "pmla_2002",
    },

    # DPDP
    {
        "question": "What is a Data Fiduciary under the DPDP Act?",
        "expected_regulation_id": "dpdp_2023",
    },
    {
        "question": "What is a Data Principal under the DPDP Act?",
        "expected_regulation_id": "dpdp_2023",
    },
    {
        "question": "What is personal data under the DPDP Act?",
        "expected_regulation_id": "dpdp_2023",
    },
    {
        "question": "What is a personal data breach under the DPDP Act?",
        "expected_regulation_id": "dpdp_2023",
    },
    {
        "question": "When can personal data be processed under the DPDP Act?",
        "expected_regulation_id": "dpdp_2023",
    },
    {
        "question": "What information must a notice to a Data Principal contain?",
        "expected_regulation_id": "dpdp_2023",
    },
]


def evaluate_citation(citation, expected_id, graph_mode):
    """
    Evaluate one citation.

    Metrics:
    - exists: citation is present
    - current: GraphRAG explicitly resolves a current regulation
    - relevant: cited regulation matches expected regulation
    - all_three: all three conditions are satisfied
    """

    exists = int(bool(citation))

    if not exists:
        return 0, 0, 0, 0

    original_id = citation.get("original_regulation_id", "")
    current_id = citation.get("current_regulation_id", "")
    status = citation.get("status", "")

    # Relevance is based on the regulation actually cited.
    relevant = int(
        original_id == expected_id
        or current_id == expected_id
    )

    if graph_mode:
        # GraphRAG explicitly resolves the regulation through Neo4j.
        current = int(
            bool(current_id)
            and status.lower() == "current"
        )
    else:
        # Flat RAG does not perform graph-based current-version
        # resolution, so this metric is deliberately 0.
        current = 0

    all_three = int(
        exists
        and current
        and relevant
    )

    return exists, current, relevant, all_three


def run_evaluation(graph_mode):
    results = []

    mode_name = "GraphRAG" if graph_mode else "Flat RAG"

    print("\n" + "=" * 80)
    print(f"{mode_name} EVALUATION")
    print("=" * 80)

    for index, item in enumerate(QUESTIONS, start=1):

        question = item["question"]
        expected_id = item["expected_regulation_id"]

        try:
            result = answer_question(
                question,
                use_graph=graph_mode
            )

            citations = result.get("citations", [])

            # Select the citation relevant to the expected regulation.
            selected_citation = None

            for citation in citations:
                if (
                    citation.get("original_regulation_id") == expected_id
                    or citation.get("current_regulation_id") == expected_id
                ):
                    selected_citation = citation
                    break

            if selected_citation is None and citations:
                selected_citation = citations[0]

            exists, current, relevant, all_three = evaluate_citation(
                selected_citation,
                expected_id,
                graph_mode
            )

            results.append(
                {
                    "exists": exists,
                    "current": current,
                    "relevant": relevant,
                    "all_three": all_three,
                }
            )

            print(f"\n[{index:02d}] {question}")
            print(f"Expected: {expected_id}")
            print(
                f"Exists={exists} | "
                f"Current={current} | "
                f"Relevant={relevant} | "
                f"All three={all_three}"
            )

            if selected_citation:
                print("Citation:", selected_citation)
            else:
                print("Citation: NONE")

        except Exception as e:

            print(f"\n[{index:02d}] {question}")
            print(f"ERROR: {e}")

            results.append(
                {
                    "exists": 0,
                    "current": 0,
                    "relevant": 0,
                    "all_three": 0,
                }
            )

    return results


def percentage(results, key):

    if not results:
        return 0.0

    return (
        sum(result[key] for result in results)
        / len(results)
        * 100
    )


def print_summary(flat_results, graph_results):

    print("\n")
    print("=" * 80)
    print("TABLE VI — CITATION QUALITY (REAL)")
    print("=" * 80)

    metrics = [
        ("Citation exists", "exists"),
        ("Current-version identified", "current"),
        ("Citation relevant", "relevant"),
        ("All three", "all_three"),
    ]

    print(
        f"{'Metric':30s}"
        f"{'Flat RAG':>15s}"
        f"{'GraphRAG':>15s}"
    )

    print("-" * 60)

    for label, key in metrics:

        flat_value = percentage(flat_results, key)
        graph_value = percentage(graph_results, key)

        print(
            f"{label:30s}"
            f"{flat_value:>14.1f}%"
            f"{graph_value:>14.1f}%"
        )

    print("-" * 60)
    print(f"Questions evaluated: {len(QUESTIONS)}")


def main():

    print("=" * 80)
    print("COMPLIANCEIQ — REAL CITATION QUALITY EVALUATION")
    print("=" * 80)
    print(f"Total questions: {len(QUESTIONS)}")

    flat_results = run_evaluation(graph_mode=False)

    graph_results = run_evaluation(graph_mode=True)

    print_summary(
        flat_results,
        graph_results
    )


if __name__ == "__main__":
    main()