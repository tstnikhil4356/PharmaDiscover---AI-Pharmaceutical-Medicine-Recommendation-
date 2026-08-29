# PharmaDiscover Backend — Phase 1 Scaffold

## What's here
- `app/models.py` — the locked Phase 1 DB schema (SQLAlchemy)
- `app/routers/auth.py`, `app/routers/admin.py` — **real**, working (register, login, JWT, role-based admin CRUD)
- `app/routers/search.py`, `app/routers/ocr.py` — **stubs** for Member 2 and Member 3. Response shapes match
  the API contract from the phase plan — replace the mock bodies with real logic in Phase 4, keep the shapes stable.
- `scripts/ingest_orange_book.py` — tested against the real `products.txt` (48,502 rows, parses cleanly).
  Ingests into `manufacturers` + `medicines`, deduping manufacturers by normalized `Applicant_Full_Name`.

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env .env            # fill in your local Postgres URL + a real JWT secret

# create the database (adjust to your local Postgres setup)
createdb pharmadiscover

# run the API — tables auto-create on startup for now (swap to Alembic once schema is stable)
uvicorn app.main:app --reload
```
API docs at `http://localhost:8000/docs` once running.

## First run checklist
1. `uvicorn app.main:app --reload` → confirm `GET /` returns `{"status": "ok"}`
2. `POST /auth/register` an admin user, then `POST /auth/login` to get a token
3. Use the token to hit `POST /admin/manufacturers` and confirm it persists
4. Run `python scripts/ingest_orange_book.py /path/to/products.txt` and confirm manufacturers/medicines populate
5. `GET /admin/manufacturers` as the admin token and confirm the Orange Book data is there

## Handoff to Members 2 & 3
Both `search.py` and `ocr.py` are already wired into `main.py` and protected by
`get_current_user`, so the frontend/prototype can call them today and get valid
(mock) JSON. Replace the `# TODO` bodies — don't change the route paths or
response field names without updating the phase plan doc, since the frontend
and each other's code depend on that contract staying stable.

## Not yet done (intentionally, per phase plan)
- Alembic migrations (using `create_all` for dev speed — fine for now, not for production)
- `dm_spl_monthly_update`, `ndctext`, `OpenFDA`, `WHO` ingestion — waiting on confirmed column samples
- Embedding generation endpoint (`POST /admin/embeddings/generate`) — depends on Member 2's vector store choice (FAISS vs ChromaDB)
- Patent/exclusivity data from Orange Book — deliberately skipped, not used by any current feature
