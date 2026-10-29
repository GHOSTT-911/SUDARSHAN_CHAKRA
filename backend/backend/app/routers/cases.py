from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.auth import get_current_officer
from app.db.database import get_db
from app.db.models import Case, CaseMember, Officer
from app.schemas.case import CaseCreate, CaseMemberCreate, CaseMemberResponse, CaseResponse, CaseUpdate
from app.services.audit import log_event
from app.services.authorization import require_case_access, require_case_management

router = APIRouter(prefix="/api/v1/cases", tags=["Cases"])
VALID_STATUSES = {"Pending Review", "Verified & Sealed", "Closed"}
VALID_ACCESS_LEVELS = {"lead_investigator", "investigator", "viewer", "judge"}

def get_case_or_404(db: Session, case_id: str) -> Case:
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.get("/", response_model=list[CaseResponse])
def get_cases(db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    query = db.query(Case)
    if current_officer.role_clearance == "admin":
        return query.all()
    if current_officer.role_clearance == "judge":
        return query.filter(Case.assigned_judge_id == current_officer.officer_id).all()
    return query.join(CaseMember).filter(CaseMember.officer_id == current_officer.officer_id).all()

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    if current_officer.role_clearance != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can create cases")
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid case status")
    if db.query(Case).filter(Case.case_id == payload.case_id).first():
        raise HTTPException(status_code=409, detail="Case ID already exists")
    if payload.assigned_judge_id and not db.query(Officer).filter(Officer.officer_id == payload.assigned_judge_id, Officer.role_clearance == "judge").first():
        raise HTTPException(status_code=422, detail="Assigned officer must be a judge")
    case = Case(**payload.model_dump())
    db.add(case)
    log_event(db, current_officer, "CASE_CREATED", "case", case.case_id, case.case_id, request.client.host if request.client else None)
    db.commit(); db.refresh(case)
    return case

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    case = get_case_or_404(db, case_id)
    require_case_access(db, current_officer, case)
    log_event(db, current_officer, "CASE_VIEWED", "case", case_id, case_id, request.client.host if request.client else None)
    db.commit()
    return case

@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(case_id: str, payload: CaseUpdate, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    case = get_case_or_404(db, case_id); require_case_management(db, current_officer, case)
    changes = payload.model_dump(exclude_unset=True)
    if "status" in changes and changes["status"] not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid case status")
    if "assigned_judge_id" in changes and changes["assigned_judge_id"] and not db.query(Officer).filter(Officer.officer_id == changes["assigned_judge_id"], Officer.role_clearance == "judge").first():
        raise HTTPException(status_code=422, detail="Assigned officer must be a judge")
    for field, value in changes.items(): setattr(case, field, value)
    log_event(db, current_officer, "CASE_UPDATED", "case", case_id, case_id, request.client.host if request.client else None, changes)
    db.commit(); db.refresh(case)
    return case

@router.get("/{case_id}/members", response_model=list[CaseMemberResponse])
def list_members(case_id: str, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    case = get_case_or_404(db, case_id); require_case_access(db, current_officer, case)
    return db.query(CaseMember).filter(CaseMember.case_id == case_id).all()

@router.post("/{case_id}/members", response_model=CaseMemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(case_id: str, payload: CaseMemberCreate, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    case = get_case_or_404(db, case_id); require_case_management(db, current_officer, case)
    if payload.access_level not in VALID_ACCESS_LEVELS: raise HTTPException(status_code=422, detail="Invalid access level")
    if not db.query(Officer).filter(Officer.officer_id == payload.officer_id, Officer.is_active.is_(True)).first(): raise HTTPException(status_code=404, detail="Active officer not found")
    if db.query(CaseMember).filter(CaseMember.case_id == case_id, CaseMember.officer_id == payload.officer_id).first(): raise HTTPException(status_code=409, detail="Officer is already a case member")
    member = CaseMember(member_id=f"MEM-{uuid4().hex[:20]}", case_id=case_id, **payload.model_dump())
    db.add(member); log_event(db, current_officer, "MEMBER_ADDED", "case_member", member.member_id, case_id, request.client.host if request.client else None, {"officer_id": payload.officer_id})
    db.commit(); db.refresh(member)
    return member

@router.delete("/{case_id}/members/{officer_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(case_id: str, officer_id: str, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    case = get_case_or_404(db, case_id); require_case_management(db, current_officer, case)
    member = db.query(CaseMember).filter(CaseMember.case_id == case_id, CaseMember.officer_id == officer_id).first()
    if not member: raise HTTPException(status_code=404, detail="Case member not found")
    log_event(db, current_officer, "MEMBER_REMOVED", "case_member", member.member_id, case_id, request.client.host if request.client else None, {"officer_id": officer_id})
    db.delete(member); db.commit()
