from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ---------- Auth ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "researcher"  # admin | researcher | field


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Manufacturer ----------
class ManufacturerCreate(BaseModel):
    name: str
    address: Optional[str] = None
    country: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class ManufacturerOut(BaseModel):
    id: str
    name: str
    country: Optional[str]
    verified: bool
    source: str

    class Config:
        from_attributes = True


# ---------- Medicine ----------
class MedicineCreate(BaseModel):
    name: str
    generic_name: Optional[str] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    manufacturer_id: Optional[str] = None


class MedicineOut(BaseModel):
    id: str
    name: str
    generic_name: Optional[str]
    strength: Optional[str]
    dosage_form: Optional[str]
    manufacturer_id: Optional[str]

    class Config:
        from_attributes = True
