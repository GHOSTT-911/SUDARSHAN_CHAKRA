from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Evidence, Officer, Case, CaseMember
from app.core.auth import get_current_officer
from app.schemas.evidence import EvidenceResponse
from app.routers.cases import get_case_or_404
from app.services.audit import log_event
from app.services.authorization import require_case_access, require_case_management
from app.services.crypto import sha256
from app.services.storage import read_decrypted, store_encrypted
from app.core.config import settings


router = APIRouter(
    prefix="/api/v1/evidence",
    tags=["Evidence"]
)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt", ".doc", ".docx"}


@router.get("/", response_model=list[EvidenceResponse])
def get_evidence(
    db: Session = Depends(get_db),
    current_officer: Officer = Depends(get_current_officer)
):
    """
    Get evidence according to officer's role.

    Admin:
        Can access all evidence.

    Judge:
        Can access evidence belonging to cases assigned to them.

    Police:
        Can access evidence they uploaded.
    """

    if current_officer.role_clearance == "admin":
        return db.query(Evidence).all()

    if current_officer.role_clearance == "judge":
        return (
            db.query(Evidence)
            .join(Case, Evidence.case_id == Case.case_id)
            .filter(
                Case.assigned_judge_id == current_officer.officer_id
            )
            .all()
        )

    if current_officer.role_clearance == "police":
        return (
            db.query(Evidence)
            .join(CaseMember, Evidence.case_id == CaseMember.case_id)
            .filter(CaseMember.officer_id == current_officer.officer_id)
            .all()
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access evidence"
    )


@router.post("/upload", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(request: Request, case_id: str = Form(...), evidence_id: str | None = Form(None), file: UploadFile = File(...), db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    case = get_case_or_404(db, case_id)
    require_case_management(db, current_officer, case)
    if Path(file.filename or "").suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail="Unsupported file type")
    data = await file.read()
    if not data: raise HTTPException(status_code=422, detail="Uploaded file is empty")
    if len(data) > settings.MAX_UPLOAD_SIZE_BYTES: raise HTTPException(status_code=413, detail="File exceeds upload size limit")
    if db.query(Evidence).filter(Evidence.evidence_id == (evidence_id or "")).first(): raise HTTPException(status_code=409, detail="Evidence ID already exists")
    evidence = Evidence(evidence_id=evidence_id or f"EVD-{uuid4().hex[:20]}", case_id=case_id, sha256_hash=sha256(data), encrypted_storage_path=store_encrypted(data, "evidence"), uploaded_by=current_officer.officer_id)
    db.add(evidence); log_event(db, current_officer, "EVIDENCE_UPLOADED", "evidence", evidence.evidence_id, case_id, request.client.host if request.client else None, {"filename": Path(file.filename or "upload").name})
    db.commit(); db.refresh(evidence)
    return evidence


@router.get("/{evidence_id}/verify")
def verify_evidence(evidence_id: str, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    evidence = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    if not evidence: raise HTTPException(status_code=404, detail="Evidence not found")
    require_case_access(db, current_officer, evidence.case)
    try: actual = sha256(read_decrypted(evidence.encrypted_storage_path)); verified = actual == evidence.sha256_hash
    except Exception: actual = None; verified = False
    log_event(db, current_officer, "INTEGRITY_VERIFIED" if verified else "INTEGRITY_FAILED", "evidence", evidence_id, evidence.case_id, request.client.host if request.client else None); db.commit()
    return {"evidence_id": evidence_id, "integrity_verified": verified, "expected_hash": evidence.sha256_hash, "actual_hash": actual}


@router.get("/{evidence_id}/download")
def download_evidence(evidence_id: str, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    evidence = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    if not evidence: raise HTTPException(status_code=404, detail="Evidence not found")
    require_case_access(db, current_officer, evidence.case)
    try: data = read_decrypted(evidence.encrypted_storage_path)
    except FileNotFoundError: raise HTTPException(status_code=404, detail="Stored evidence is unavailable")
    log_event(db, current_officer, "EVIDENCE_DOWNLOADED", "evidence", evidence_id, evidence.case_id, request.client.host if request.client else None); db.commit()
    return Response(data, media_type="application/octet-stream", headers={"Content-Disposition": f'attachment; filename="{evidence_id}"'})
