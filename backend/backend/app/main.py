from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import text

from app.db.database import engine
from app.routers.cases import router as cases_router
from app.routers.evidence import router as evidence_router
from app.routers.auth import router as auth_router
from app.routers.documents import router as documents_router
from app.routers.audit import router as audit_router
from app.routers.search import router as search_router


app = FastAPI(
    title="Sudarshan Chakra",
    version="1.0.0"
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Development origins for the static frontend. Restrict these further for deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000", "http://localhost:5000", "http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(cases_router)
app.include_router(evidence_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(audit_router)
app.include_router(search_router)


@app.get("/", include_in_schema=False)
def frontend_index():
    return FileResponse(PROJECT_ROOT / "index.html")


@app.get("/app.js", include_in_schema=False)
def frontend_script():
    return FileResponse(PROJECT_ROOT / "app.js", media_type="application/javascript")


@app.get("/style.css", include_in_schema=False)
def frontend_styles():
    return FileResponse(PROJECT_ROOT / "style.css", media_type="text/css")

@app.get("/api/v1/health")
def health_check():

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception as e:

        return JSONResponse(status_code=503, content={
            "status": "error",
            "database": "connection_failed",
            "detail": str(e)
        })

