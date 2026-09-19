# ============================================================
# FILE: ml/build_graph.py
# ============================================================
# Builds a Neo4j knowledge graph of Indian financial regulations
# and how they relate: which supersede/amend/reference each other.
#
# WHY THIS MATTERS:
# ChromaDB's semantic search might return an OLD version of a
# rule (e.g. RBI KYC 2016) instead of the current one (2023),
# because they use similar wording. The graph tracks which
# version is CURRENT, so the chatbot can be corrected/enhanced
# to always prefer current regulations.
#
# HOW TO RUN:
#   python ml/build_graph.py
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Regulation nodes: (id, name, year, status)
REGULATIONS = [
    ("rbi_kyc_2016", "RBI KYC Master Direction 2016", 2016, "superseded"),
    ("rbi_kyc_2023", "RBI KYC Master Direction 2023", 2023, "current"),
    ("pmla_2002", "Prevention of Money Laundering Act 2002", 2002, "current"),
    ("pmla_2013_amend", "PMLA Amendment 2013", 2013, "current"),
    ("pmla_2019_amend", "PMLA Amendment 2019", 2019, "current"),
    ("rbi_digital_lending_2022", "RBI Digital Lending Guidelines 2022", 2022, "superseded"),
    ("rbi_digital_lending_2025", "RBI Digital Lending Directions 2025", 2025, "current"),
    ("rbi_fraud_2016", "RBI Fraud Circular 2016", 2016, "current"),
    ("dpdp_2023", "Digital Personal Data Protection Act 2023", 2023, "current"),
    ("dpdp_rules_2025", "DPDP Rules 2025", 2025, "current"),
]

# Relationships: (from_id, relationship_type, to_id)
RELATIONSHIPS = [
    ("rbi_kyc_2023", "SUPERSEDES", "rbi_kyc_2016"),
    ("pmla_2013_amend", "AMENDS", "pmla_2002"),
    ("pmla_2019_amend", "AMENDS", "pmla_2002"),
    ("rbi_digital_lending_2025", "SUPERSEDES", "rbi_digital_lending_2022"),
    ("dpdp_rules_2025", "VERSION_OF", "dpdp_2023"),
    ("rbi_fraud_2016", "REFERENCES", "pmla_2002"),
    ("rbi_kyc_2023", "REFERENCES", "pmla_2002"),
    ("rbi_digital_lending_2025", "REFERENCES", "rbi_kyc_2023"),
]


def main():
    from neo4j import GraphDatabase

    if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
        print("ERROR: NEO4J_URI, NEO4J_USERNAME, or NEO4J_PASSWORD missing from .env")
        return

    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    driver.verify_connectivity()
    print("Connected successfully.")

    with driver.session() as session:
        print("Clearing existing graph...")
        session.run("MATCH (n) DETACH DELETE n")

        print("Creating regulation nodes...")
        for reg_id, name, year, status in REGULATIONS:
            session.run(
                """
                CREATE (r:Regulation {
                    id: $id, name: $name, year: $year, status: $status
                })
                """,
                id=reg_id, name=name, year=year, status=status,
            )
            marker = "(current)" if status == "current" else f"({status})"
            print(f"  + {name} {marker}")

        print("Creating relationships...")
        for from_id, rel_type, to_id in RELATIONSHIPS:
            session.run(
                f"""
                MATCH (a:Regulation {{id: $from_id}}), (b:Regulation {{id: $to_id}})
                CREATE (a)-[:{rel_type}]->(b)
                """,
                from_id=from_id, to_id=to_id,
            )
            print(f"  + {rel_type}: {from_id} -> {to_id}")

        print("\nTesting supersession lookup...")
        result = session.run(
            """
            MATCH (old:Regulation {id: 'rbi_kyc_2016'})<-[:SUPERSEDES]-(current:Regulation)
            RETURN current.id AS current_id
            """
        )
        record = result.single()
        if record:
            print(f"  rbi_kyc_2016 -> current version: {record['current_id']} ✓")
        else:
            print("  WARNING: supersession lookup returned nothing.")

    driver.close()
    print("\nKnowledge graph built successfully!")
    print(f"Nodes: {len(REGULATIONS)}")
    print(f"Relationships: {len(RELATIONSHIPS)}")


def get_current_version(regulation_id: str) -> str:
    """
    Given a regulation id (possibly superseded), return the id of
    the CURRENT version. Used to correct/enhance chatbot answers.
    Returns the same id if it's already current or has no successor.
    """
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        result = session.run(
            """
            MATCH (old:Regulation {id: $id})
            OPTIONAL MATCH (old)<-[:SUPERSEDES]-(current:Regulation)
            RETURN COALESCE(current.id, old.id) AS current_id
            """,
            id=regulation_id,
        )
        record = result.single()
    driver.close()
    return record["current_id"] if record else regulation_id


if __name__ == "__main__":
    main()
