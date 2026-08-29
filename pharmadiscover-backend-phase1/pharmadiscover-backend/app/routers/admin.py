from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(auth.require_role("admin"))])


# ---------- Manufacturers ----------
@router.get("/manufacturers", response_model=List[schemas.ManufacturerOut])
def list_manufacturers(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.Manufacturer).offset(skip).limit(limit).all()


@router.post("/manufacturers", response_model=schemas.ManufacturerOut)
def create_manufacturer(payload: schemas.ManufacturerCreate, db: Session = Depends(get_db)):
    m = models.Manufacturer(**payload.model_dump(), normalized_name=payload.name.strip().lower())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/manufacturers/{manufacturer_id}", response_model=schemas.ManufacturerOut)
def update_manufacturer(manufacturer_id: str, payload: schemas.ManufacturerCreate, db: Session = Depends(get_db)):
    m = db.query(models.Manufacturer).filter(models.Manufacturer.id == manufacturer_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    for field, value in payload.model_dump().items():
        setattr(m, field, value)
    m.normalized_name = payload.name.strip().lower()
    db.commit()
    db.refresh(m)
    return m


@router.delete("/manufacturers/{manufacturer_id}")
def delete_manufacturer(manufacturer_id: str, db: Session = Depends(get_db)):
    m = db.query(models.Manufacturer).filter(models.Manufacturer.id == manufacturer_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    db.delete(m)
    db.commit()
    return {"deleted": manufacturer_id}


@router.post("/manufacturers/{manufacturer_id}/verify", response_model=schemas.ManufacturerOut)
def verify_manufacturer(manufacturer_id: str, db: Session = Depends(get_db)):
    """Admin sign-off step from your role-flow diagram (Approve/Reject Data Updates)."""
    m = db.query(models.Manufacturer).filter(models.Manufacturer.id == manufacturer_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    m.verified = True
    db.commit()
    db.refresh(m)
    return m


# ---------- Medicines ----------
@router.get("/medicines", response_model=List[schemas.MedicineOut])
def list_medicines(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.Medicine).offset(skip).limit(limit).all()


@router.post("/medicines", response_model=schemas.MedicineOut)
def create_medicine(payload: schemas.MedicineCreate, db: Session = Depends(get_db)):
    med = models.Medicine(**payload.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


@router.delete("/medicines/{medicine_id}")
def delete_medicine(medicine_id: str, db: Session = Depends(get_db)):
    med = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(med)
    db.commit()
    return {"deleted": medicine_id}


# ---------- Users ----------
@router.get("/users", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()
