import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Float, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class RoleEnum(str, enum.Enum):
    admin = "admin"
    researcher = "researcher"
    field = "field"


class SourceEnum(str, enum.Enum):
    internal = "internal"
    openfda = "openfda"
    dailymed = "dailymed"
    orange_book = "orange_book"
    ndc = "ndc"
    who = "who"
    manual = "manual"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.researcher)
    created_at = Column(DateTime, default=datetime.utcnow)


class Manufacturer(Base):
    __tablename__ = "manufacturers"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False, index=True)
    normalized_name = Column(String, index=True)  # lowercased/stripped, for fuzzy matching
    address = Column(String, nullable=True)
    country = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    source = Column(Enum(SourceEnum), default=SourceEnum.manual)
    verified = Column(Boolean, default=False)  # admin sign-off, per your role-flow diagram
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    certifications = relationship("Certification", back_populates="manufacturer")
    medicines = relationship("Medicine", back_populates="manufacturer")


class Certification(Base):
    __tablename__ = "certifications"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    manufacturer_id = Column(UUID(as_uuid=False), ForeignKey("manufacturers.id"), nullable=False)
    type = Column(String, nullable=False)  # GMP / ISO / USFDA / WHO-GMP / EU-GMP
    issued_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    verified = Column(Boolean, default=False)

    manufacturer = relationship("Manufacturer", back_populates="certifications")


class Medicine(Base):
    __tablename__ = "medicines"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False, index=True)          # Trade_Name
    generic_name = Column(String, nullable=True, index=True)    # Ingredient
    ndc_code = Column(String, nullable=True, index=True)
    strength = Column(String, nullable=True)
    dosage_form = Column(String, nullable=True)
    route = Column(String, nullable=True)
    manufacturer_id = Column(UUID(as_uuid=False), ForeignKey("manufacturers.id"), nullable=True)
    source = Column(Enum(SourceEnum), default=SourceEnum.manual)
    created_at = Column(DateTime, default=datetime.utcnow)

    manufacturer = relationship("Manufacturer", back_populates="medicines")


class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False, index=True)
    atc_code = Column(String, nullable=True)  # from WHO ATC/DDD, once confirmed


class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    related_type = Column(String, nullable=False)  # "manufacturer" | "medicine"
    related_id = Column(UUID(as_uuid=False), nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class Embedding(Base):
    __tablename__ = "embeddings"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    source_type = Column(String, nullable=False)  # "manufacturer" | "medicine" | "document"
    source_id = Column(UUID(as_uuid=False), nullable=False)
    chunk_text = Column(Text, nullable=False)
    vector_ref = Column(String, nullable=True)  # id/key in FAISS or ChromaDB — Member 2's territory
    created_at = Column(DateTime, default=datetime.utcnow)


class SearchLog(Base):
    __tablename__ = "search_logs"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    query_text = Column(Text, nullable=False)
    result_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class OcrScan(Base):
    __tablename__ = "ocr_scans"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    image_path = Column(String, nullable=False)
    extracted_product = Column(String, nullable=True)
    extracted_manufacturer = Column(String, nullable=True)
    extracted_batch = Column(String, nullable=True)
    extracted_expiry = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    matched_manufacturer_id = Column(UUID(as_uuid=False), ForeignKey("manufacturers.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Export(Base):
    __tablename__ = "exports"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    type = Column(String, nullable=False)  # "pdf" | "excel"
    content_ref = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
