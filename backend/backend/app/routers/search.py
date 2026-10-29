from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.auth import get_current_officer
from app.db.database import get_db
from app.db.models import Case, CaseMember, Document, Officer
from app.schemas.document import DocumentResponse
router = APIRouter(prefix="/api/v1/search", tags=["Search"])
@router.get("/documents", response_model=list[DocumentResponse])
def search_documents(q: str, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    term = f"%{q.strip()}%"; query = db.query(Document).filter(or_(Document.title.like(term), Document.document_type.like(term), Document.extracted_text.like(term)))
    if current_officer.role_clearance == "admin": return query.all()
    if current_officer.role_clearance == "judge": return query.join(Case).filter(Case.assigned_judge_id == current_officer.officer_id).all()
    return query.join(CaseMember, Document.case_id == CaseMember.case_id).filter(CaseMember.officer_id == current_officer.officer_id).all()
