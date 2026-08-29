from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401 — ensures models are registered before create_all
from app.routers import auth, admin, search, ocr

app = FastAPI(title="PharmaDiscover API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(search.router)
app.include_router(ocr.router)


@app.on_event("startup")
def on_startup():
    # Dev convenience only — use Alembic migrations once the schema stabilizes.
    Base.metadata.create_all(bind=engine)


@app.get("/")
def health():
    return {"status": "ok", "service": "PharmaDiscover API"}
