from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_officer
from app.db.database import get_db
from app.db.models import AuditEvent, Officer
from app.schemas.audit import AuditEventResponse
router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])
@router.get("/", response_model=list[AuditEventResponse])
def list_audit(case_id: str | None = None, limit: int = 100, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    if current_officer.role_clearance != "admin": raise HTTPException(status_code=403, detail="Only administrators can view audit logs")
    query = db.query(AuditEvent)
    if case_id: query = query.filter(AuditEvent.case_id == case_id)
    return query.order_by(AuditEvent.timestamp.desc()).limit(min(max(limit, 1), 500)).all()
