# PharmaDiscover — Phased Development Plan

Team 2: Parishi Bhutwala (B041) · Nikhil Singh (B042) · Rishika Joshi (B054)
Guide: Dr. Yogesh Naik

Your submitted PPT already commits to 6 phases (Requirement Analysis → UI/UX & DB Design → Backend API Dev → AI & OCR Integration → Testing & QA → Deployment). Keeping those 6 so your submission stays consistent, but splitting Phase 3 and Phase 4 into per-member tracks so it's actually buildable by 3 people instead of "shared vaguely."

**Critical dependency to internalize:** Member 2 (RAG/chatbot) and Member 3 (OCR/matching) both sit on top of the DB schema and, for Member 2, the embeddings pipeline. If Member 1 doesn't lock the schema + seed data in Phase 1, Members 2 and 3 are blocked or building against a moving target. So Phase 1 is the actual critical path — do it first and don't let it slide.

---

## Phase 1 — Requirement Analysis & Technical Foundation
**Owner: Member 1, reviewed by all. Target: done before anyone else writes a line of AI/OCR code.**

Business need, roles, and literature review are already done (your Deliverable 1 doc). What's actually still open for dev to start:

### 1. Finalize DB schema (PostgreSQL)
```
users            id, name, email, password_hash, role[admin|researcher|field], created_at
manufacturers    id, name, normalized_name, address, country, contact_email, contact_phone,
                 source[internal|openfda|dailymed|who|manual], verified, created_at, updated_at
certifications   id, manufacturer_id FK, type[GMP|ISO|USFDA], issued_date, expiry_date, verified
medicines        id, name, generic_name, ndc_code, strength, form, manufacturer_id FK, source
ingredients      id, name (generic/INN name)
medicine_ingredients   medicine_id FK, ingredient_id FK, quantity
documents        id, related_type[manufacturer|medicine], related_id, file_path, uploaded_by, uploaded_at
embeddings       id, source_type[manufacturer|medicine|document], source_id, chunk_text, vector_ref
search_logs      id, user_id, query_text, result_count, created_at
ocr_scans        id, user_id, image_path, extracted_product, extracted_manufacturer, extracted_batch,
                 extracted_expiry, confidence, matched_manufacturer_id, created_at
exports          id, user_id, type[pdf|excel], content_ref, created_at
```
This maps directly to what's in your PPT's role-flow diagram (Manage Manufacturers, Manage Medicines, Data Sources, Certifications, OCR fields, Matched Manufacturers, Save/Export). Adjust field names once Member 1 sits with the actual dataset columns.

### 2. Lock the API contract (so Members 2 & 3 can build against stubs immediately)
```
POST /auth/login              POST /auth/register (admin-created)     GET /auth/me
GET/POST/PUT/DELETE /admin/manufacturers
GET/POST/PUT/DELETE /admin/medicines
GET/POST/PUT/DELETE /admin/users
POST /admin/documents/upload
POST /admin/embeddings/generate

POST /search/query             -> Member 2 (RAG)
POST /chat/message              -> Member 2
GET  /manufacturers/{id}
POST /compare
GET  /medicines/{id}/alternatives
POST /export

POST /ocr/scan                 -> Member 3 (image in, extracted fields out)
POST /ocr/confirm               -> Member 3 (user-edited fields, triggers auto-query)
GET  /ocr/{scan_id}/matches     -> Member 3 (fuzzy-matched manufacturers)
```
Member 1 stubs these (return mock JSON) by end of Phase 1 so Members 2 & 3 aren't blocked in Phase 3/4.

### 3. Map your Drive datasets to the schema
From the folder names you shared — confirm these before ingestion, my read on them:
- `OpenFDA` → NDC directory data (product + manufacturer records) → feeds `manufacturers` + `medicines`
- `dm_spl_monthly_update` → DailyMed Structured Product Labels → feeds `medicines` (composition, active ingredients, packaging text) — this is also your best source of realistic OCR ground-truth text for testing Member 3's pipeline
- `ndctext` → NDC text files (product/package listing) → feeds `medicines` + `manufacturers`, likely overlaps with OpenFDA — dedupe against it, don't double-ingest
- `WHO` → likely INN/essential medicines list → feeds `ingredients` (generic names) for the alternative-medicine matching logic
- `EOBZIP_2026_06` → unclear from the name alone — **check what's actually inside this one before Phase 2**, don't guess and build ingestion logic on a wrong assumption

### 4. Repo structure
```
/backend
  /app
    /models
    /routers      (auth, admin, search, chat, ocr)
    /services      (rag_service, ocr_service, matching_service, embedding_service)
    /db
  /scripts
    /data_ingestion   (one script per dataset source)
/frontend            (your existing HTML prototype — evolve in place, don't rewrite framework mid-project)
/data                (gitignored — synced from Drive locally, never committed raw)
docker-compose.yml
```

### Phase 1 checklist
- [ ] Member 1: schema above reviewed against actual dataset column names, finalized
- [ ] Member 1: API contract stubs live (FastAPI skeleton returning mock data)
- [ ] All: confirm what's in `EOBZIP_2026_06`
- [ ] All: repo created, each member has local Postgres + can hit the stub endpoints
- [ ] Member 1: auth (JWT) + role detection working end-to-end (matches your HTML prototype's login screen — 3 demo accounts)

Once this is done, Phase 3 (Member 1: real CRUD + ingestion + embeddings) and Phase 4 (Member 2: RAG/chat, Member 3: OCR) can start in parallel — that's your actual timeline compression, since 2 and 3 don't depend on each other, only on 1.

---

## Phase 2 — UI/UX & DB Design
Your HTML prototype already covers this (3 role-based screens, login, search/chat, OCR scan, results). Phase 2 here is just: reconcile the wireframe screens against the finalized schema/API contract from Phase 1, and mark which HTML elements are static mockup vs. need real API wiring in Phase 6. No new design work needed unless a field in the schema has no corresponding UI element yet (e.g., certifications expiry, source attribution).

## Phase 3 — Backend API Development
**Owner: Member 1.** Real CRUD replacing the Phase 1 stubs, admin panel, data ingestion scripts pulling from the 5 Drive datasets into Postgres, and the embedding generation pipeline (chunk manufacturer/medicine records + documents → embed → push to FAISS/ChromaDB). This is the gate for Phase 4 Track A.

## Phase 4 — AI & OCR Integration (parallel tracks)
- **Track A — Member 2:** RAG retrieval over the embeddings from Phase 3, chatbot orchestration (LangChain), semantic search endpoint, alternative-medicine recommendation (ingredient similarity), comparison, export.
- **Track B — Member 3:** OCR pipeline (EasyOCR/Tesseract + OpenCV preprocessing), text extraction from packaging images, auto-query against the manufacturers table, fuzzy-matching/entity resolution for name variants. Only depends on Phase 1's schema, not on Phase 3's embeddings — can start as soon as `manufacturers`/`medicines` tables have real data.

## Phase 5 — Testing & QA
Unit test each module solo (matches your PPT's stated approach), then integration test the 3 end-to-end flows from your role diagram: Admin manage → Researcher search/chat/compare/export → Field OCR scan/confirm/match.

## Phase 6 — Deployment & Documentation
Dockerize, deploy (Render/AWS as stated), write docs, prep final presentation.

---

## Next step
Confirm the schema field names against your actual dataset columns and tell me what's in `EOBZIP_2026_06` — then I can help Member 1 scaffold the actual FastAPI backend + ingestion scripts for Phase 1, or start on the HTML prototype changes if you want the UI adjusted first.
