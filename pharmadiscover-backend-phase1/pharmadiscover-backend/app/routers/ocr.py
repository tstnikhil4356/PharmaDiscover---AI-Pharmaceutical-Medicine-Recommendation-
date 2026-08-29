"""
STUB ROUTER — Member 3's territory (OCR extraction, auto-query, manufacturer matching).

Real image upload handling, EasyOCR/Tesseract calls, and fuzzy matching against
the manufacturers table go here in Phase 4. Keep response shapes stable.
"""
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional

from app.auth import get_current_user

router = APIRouter(prefix="/ocr", tags=["ocr"], dependencies=[Depends(get_current_user)])


class OcrConfirm(BaseModel):
    scan_id: str
    product_name: Optional[str] = None
    manufacturer: Optional[str] = None
    batch: Optional[str] = None
    expiry: Optional[str] = None


@router.post("/scan")
def scan(file: UploadFile = File(...)):
    # TODO(Member 3): save file, run OpenCV preprocessing + EasyOCR/Tesseract extraction
    return {
        "scan_id": "mock-scan-1",
        "extracted": {
            "product_name": "Paracetamol 500mg",
            "manufacturer": "Mock Pharma Ltd",
            "batch": "BP22345",
            "expiry": "03/2028",
        },
        "confidence": 0.0,
        "note": "stub — wire to real OCR pipeline in Phase 4",
    }


@router.post("/confirm")
def confirm(payload: OcrConfirm):
    # TODO(Member 3): persist user-edited fields, trigger auto-query against manufacturers/medicines
    return {"scan_id": payload.scan_id, "status": "confirmed", "note": "stub"}


@router.get("/{scan_id}/matches")
def matches(scan_id: str):
    # TODO(Member 3): fuzzy-match extracted manufacturer name against manufacturers.normalized_name
    return {"scan_id": scan_id, "matches": [], "note": "stub — implement fuzzy matching (e.g. rapidfuzz)"}
