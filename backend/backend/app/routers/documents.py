from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import get_current_officer
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Document, DocumentVersion, Officer
from app.routers.cases import get_case_or_404
from app.schemas.document import DocumentResponse, DocumentVersionResponse
from app.services.audit import log_event
from app.services.authorization import require_case_access, require_case_management
from app.services.crypto import sha256
from app.services.storage import read_decrypted, store_encrypted
from app.services.ocr import extract_text

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt", ".doc", ".docx"}

async def validated_bytes(file: UploadFile) -> bytes:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS: raise HTTPException(status_code=422, detail="Unsupported file type")
    data = await file.read()
    if not data: raise HTTPException(status_code=422, detail="Uploaded file is empty")
    if len(data) > settings.MAX_UPLOAD_SIZE_BYTES: raise HTTPException(status_code=413, detail="File exceeds upload size limit")
    return data

@router.get("/", response_model=list[DocumentResponse])
def list_documents(case_id: str, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    case = get_case_or_404(db, case_id); require_case_access(db, current_officer, case)
    return db.query(Document).filter(Document.case_id == case_id).all()

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(request: Request, case_id: str = Form(...), title: str = Form(...), document_type: str = Form("Other"), file: UploadFile = File(...), db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    case = get_case_or_404(db, case_id); require_case_management(db, current_officer, case)
    data = await validated_bytes(file); document_id = f"DOC-{uuid4().hex[:20]}"; path = store_encrypted(data, "documents")
    document = Document(document_id=document_id, case_id=case_id, title=title, document_type=document_type, original_filename=Path(file.filename).name, storage_path=path, sha256_hash=sha256(data), encrypted=True, uploaded_by=current_officer.officer_id, current_version=1, extracted_text=extract_text(data, file.filename or ""))
    version = DocumentVersion(version_id=f"VER-{uuid4().hex[:20]}", document_id=document_id, version_number=1, storage_path=path, sha256_hash=document.sha256_hash, original_filename=document.original_filename, uploaded_by=current_officer.officer_id)
    db.add_all([document, version]); log_event(db, current_officer, "DOCUMENT_UPLOADED", "document", document_id, case_id, request.client.host if request.client else None, {"filename": document.original_filename})
    db.commit(); db.refresh(document)
    return document

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document: raise HTTPException(status_code=404, detail="Document not found")
    require_case_access(db, current_officer, document.case); log_event(db, current_officer, "DOCUMENT_VIEWED", "document", document_id, document.case_id, request.client.host if request.client else None); db.commit()
    return document

@router.post("/{document_id}/versions", response_model=DocumentVersionResponse, status_code=201)
async def add_version(document_id: str, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document: raise HTTPException(status_code=404, detail="Document not found")
    require_case_management(db, current_officer, document.case); data = await validated_bytes(file); next_version = document.current_version + 1; path = store_encrypted(data, "documents")
    version = DocumentVersion(version_id=f"VER-{uuid4().hex[:20]}", document_id=document_id, version_number=next_version, storage_path=path, sha256_hash=sha256(data), original_filename=Path(file.filename).name, uploaded_by=current_officer.officer_id)
    document.current_version = next_version; document.storage_path = path; document.sha256_hash = version.sha256_hash; document.original_filename = version.original_filename
    db.add(version); log_event(db, current_officer, "DOCUMENT_VERSION_CREATED", "document", document_id, document.case_id, request.client.host if request.client else None, {"version": next_version}); db.commit(); db.refresh(version)
    return version

@router.get("/{document_id}/versions", response_model=list[DocumentVersionResponse])
def versions(document_id: str, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document: raise HTTPException(status_code=404, detail="Document not found")
    require_case_access(db, current_officer, document.case)
    return db.query(DocumentVersion).filter(DocumentVersion.document_id == document_id).order_by(DocumentVersion.version_number).all()

@router.get("/{document_id}/verify")
def verify_document(document_id: str, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document: raise HTTPException(status_code=404, detail="Document not found")
    require_case_access(db, current_officer, document.case)
    try: actual = sha256(read_decrypted(document.storage_path)); verified = actual == document.sha256_hash
    except Exception: verified = False; actual = None
    log_event(db, current_officer, "INTEGRITY_VERIFIED" if verified else "INTEGRITY_FAILED", "document", document_id, document.case_id, request.client.host if request.client else None); db.commit()
    return {"document_id": document_id, "integrity_verified": verified, "expected_hash": document.sha256_hash, "actual_hash": actual}

@router.get("/{document_id}/download")
def download_document(document_id: str, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document: raise HTTPException(status_code=404, detail="Document not found")
    require_case_access(db, current_officer, document.case)
    try: data = read_decrypted(document.storage_path)
    except FileNotFoundError: raise HTTPException(status_code=404, detail="Stored document is unavailable")
    log_event(db, current_officer, "DOCUMENT_DOWNLOADED", "document", document_id, document.case_id, request.client.host if request.client else None); db.commit()
    return Response(data, media_type="application/octet-stream", headers={"Content-Disposition": f'attachment; filename="{document.original_filename}"'})
