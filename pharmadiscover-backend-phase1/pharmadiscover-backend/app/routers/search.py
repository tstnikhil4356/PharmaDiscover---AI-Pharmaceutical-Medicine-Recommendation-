"""
STUB ROUTER — Member 2's territory (RAG search, chat, recommendations, compare, export).

These return mock data matching the agreed API contract shape so the frontend
and Member 1's work aren't blocked. Replace the bodies with real RAG/LLM calls
in Phase 4 — keep the request/response schemas stable so nothing downstream breaks.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

from app.auth import get_current_user
from app import models

router = APIRouter(tags=["search"], dependencies=[Depends(get_current_user)])


class SearchQuery(BaseModel):
    query: str


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


@router.post("/search/query")
def search_query(payload: SearchQuery):
    # TODO(Member 2): replace with RAG retrieval over the embeddings table
    return {
        "query": payload.query,
        "results": [
            {"manufacturer_id": "mock-1", "name": "Mock Pharma Ltd", "match_score": 0.91},
        ],
        "note": "stub response — wire to RAG in Phase 4",
    }


@router.post("/chat/message")
def chat_message(payload: ChatMessage):
    # TODO(Member 2): replace with LangChain/LLM orchestration
    return {
        "reply": f"(stub) You said: {payload.message}",
        "session_id": payload.session_id or "mock-session",
    }


@router.get("/manufacturers/{manufacturer_id}")
def manufacturer_detail(manufacturer_id: str):
    # TODO(Member 2 or 1): real DB lookup + enrichment
    return {"id": manufacturer_id, "name": "Mock Pharma Ltd", "certifications": ["GMP"], "note": "stub"}


@router.post("/compare")
def compare(manufacturer_ids: List[str]):
    return {"compared": manufacturer_ids, "note": "stub — implement side-by-side comparison logic"}


@router.get("/medicines/{medicine_id}/alternatives")
def alternatives(medicine_id: str):
    # TODO(Member 2): ingredient-similarity + WHO ATC-based ranking
    return {"medicine_id": medicine_id, "alternatives": [], "note": "stub"}


@router.post("/export")
def export(export_type: str = "pdf"):
    return {"export_type": export_type, "download_url": None, "note": "stub"}
