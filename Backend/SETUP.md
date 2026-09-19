# ComplianceIQ Backend — Setup Guide

Follow these steps in order on a fresh clone. Skipping steps will cause errors.

## 1. Prerequisites
- **Python 3.11** specifically (not 3.12+, not 3.13+, not 3.14). Check with `python --version`.
  If you have a different version installed, install 3.11 alongside it and use `py -3.11` (Windows) instead of `python`.
- Git

## 2. Clone and enter the Backend folder
```
git clone https://github.com/MIKASIA04/Compliance-Iq.git
cd Compliance-Iq/Backend
```

## 3. Create and activate a virtual environment
```
python -m venv .venv
```
Windows: `.venv\Scripts\activate`
Mac/Linux: `source .venv/bin/activate`

You must see `(.venv)` at the start of your terminal prompt for every step below.

## 4. Install dependencies
```
pip install -r requirements.txt
```

## 5. Create your own `.env` file
This is **not** in the repo (secrets aren't committed). Create `Backend/.env` with:
```
SECRET_KEY=any-random-string-here
GROQ_API_KEY=your-groq-key-here
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-neo4j-password
```
- `SECRET_KEY`: make up any random string, used to sign login tokens.
- `GROQ_API_KEY`: free, get one at https://console.groq.com/ → API Keys. Required for the chatbot to generate real answers (without it, the chatbot still works but returns raw regulation text instead of a written answer).
- `NEO4J_*`: only needed if you want to rebuild the knowledge graph (`ml/build_graph.py`). Get a free instance at https://neo4j.com/cloud/aura-free/. Not required for the core API, auth, transactions, or chatbot to work.

## 6. Create the database
```
python app/database.py
```
Creates `complianceiq.db` with default users:
| Email | Password | Role |
|---|---|---|
| admin@complianceiq.com | Admin@1234 | admin |
| officer@complianceiq.com | Officer@1234 | officer |
| analyst@complianceiq.com | Analyst@1234 | analyst |

## 7. Train the ML model
```
python ml/train_model.py
```
Takes 2-3 minutes. Creates `ml/model.pkl`, `ml/shap_explainer.pkl`, and `dataset/transactions.csv`.

## 8. Seed demo data (optional but recommended)
```
python seed_data.py
```

## 9. Build the RAG chatbot's knowledge base
```
python ml/extract_regulations.py
python ml/build_vectorstore.py
```
The first command works with zero setup (uses built-in demo regulation chunks if no PDFs are added to `data/regulations/`). The second downloads a small (~90MB) embedding model on first run — one-time, automatic, free.

## 10. (Optional) Build the knowledge graph
Requires Neo4j credentials in `.env` from step 5.
```
python ml/build_graph.py
```
**Note:** if this fails with an SSL certificate error, run `python -m pip install pip-system-certs` first, then retry. This is a known issue on networks/laptops that intercept HTTPS traffic (common on some college networks or laptops with certain security software).

## 11. Run the servers

**Main API (required):**
```
uvicorn app.main:app --reload
```
Runs on http://localhost:8000 — docs at http://localhost:8000/docs

**ML microservice (optional, only if you want the separate MLOps service):**
In a second terminal (repeat steps 3's activation first):
```
uvicorn ml_service.main:app --port 8001 --reload
```
Runs on http://localhost:8001 — docs at http://localhost:8001/docs

## 12. Verify everything works
With the main API running (step 11), in another terminal:
```
python test_everything.py
```
Should print `ALL 20 TESTS PASSED ✓`. If anything fails, check that steps 6-8 completed without errors first.

## Common errors and fixes

| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'X'` | `pip install X` (a few packages aren't pinned; install whatever's missing) |
| `No such file or directory: 'ml/model.pkl'` | Run step 7 |
| `No such file or directory: 'complianceiq.db'` | Run step 6 |
| Chatbot returns raw text instead of a written answer | `GROQ_API_KEY` missing/invalid in `.env` |
| SSL errors connecting to Neo4j | `pip install pip-system-certs`, then retry |
| `422 Unprocessable Entity` on `/auth/login` | Login needs form-encoded data (`username`/`password` fields), not JSON |

## For frontend integration
See `API_CONTRACT.md` in the repo root for exact request/response shapes of every endpoint.
