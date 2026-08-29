"""
Ingests FDA Orange Book `products.txt` (from EOBZIP_2026_06) into the
manufacturers and medicines tables.

Usage:
    python scripts/ingest_orange_book.py /path/to/products.txt

Columns in products.txt (pipe/tilde `~` delimited):
Ingredient~DF;Route~Trade_Name~Applicant~Strength~Appl_Type~Appl_No~
Product_No~TE_Code~Approval_Date~RLD~RS~Type~Applicant_Full_Name

Deliberately skips patent.txt / exclusivity.txt — not used by any feature
in the current scope (see phase plan: Layer 3 is optional/future-scope).
"""
import sys
import pandas as pd
from sqlalchemy.orm import Session

sys.path.insert(0, ".")
from app.database import SessionLocal, engine, Base  # noqa: E402
from app import models  # noqa: E402


def normalize(name: str) -> str:
    return (name or "").strip().lower()


def ingest(products_path: str):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    df = pd.read_csv(products_path, sep="~", dtype=str, encoding="utf-8", on_bad_lines="skip")
    df = df.fillna("")

    manufacturer_cache = {}  # normalized_name -> Manufacturer.id, avoids duplicate rows/lookups
    created_manufacturers = 0
    created_medicines = 0

    for _, row in df.iterrows():
        applicant_full = row.get("Applicant_Full_Name", "").strip() or row.get("Applicant", "").strip()
        if not applicant_full:
            continue

        key = normalize(applicant_full)
        manufacturer_id = manufacturer_cache.get(key)

        if manufacturer_id is None:
            existing = db.query(models.Manufacturer).filter(
                models.Manufacturer.normalized_name == key
            ).first()
            if existing:
                manufacturer_id = existing.id
            else:
                m = models.Manufacturer(
                    name=applicant_full,
                    normalized_name=key,
                    source=models.SourceEnum.orange_book,
                    verified=False,  # goes through admin approval per your role-flow diagram
                )
                db.add(m)
                db.flush()  # get generated id without a full commit
                manufacturer_id = m.id
                created_manufacturers += 1
            manufacturer_cache[key] = manufacturer_id

        df_route = row.get("DF;Route", "")
        dosage_form, _, route = df_route.partition(";")

        medicine = models.Medicine(
            name=row.get("Trade_Name", "").strip(),
            generic_name=row.get("Ingredient", "").strip(),
            strength=row.get("Strength", "").strip(),
            dosage_form=dosage_form.strip(),
            route=route.strip(),
            manufacturer_id=manufacturer_id,
            source=models.SourceEnum.orange_book,
        )
        db.add(medicine)
        created_medicines += 1

        if created_medicines % 500 == 0:
            db.commit()  # periodic commit so a mid-run failure doesn't lose everything

    db.commit()
    db.close()
    print(f"Done. Manufacturers created: {created_manufacturers}. Medicines created: {created_medicines}.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/ingest_orange_book.py /path/to/products.txt")
        sys.exit(1)
    ingest(sys.argv[1])
