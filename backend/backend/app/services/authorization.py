from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Case, CaseMember, Officer


def can_access_case(db: Session, officer: Officer, case: Case) -> bool:
    if officer.role_clearance == "admin":
        return True
    if officer.role_clearance == "judge":
        return case.assigned_judge_id == officer.officer_id
    return db.query(CaseMember).filter(
        CaseMember.case_id == case.case_id,
        CaseMember.officer_id == officer.officer_id,
    ).first() is not None


def require_case_access(db: Session, officer: Officer, case: Case) -> None:
    if not can_access_case(db, officer, case):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this case")


def require_case_management(db: Session, officer: Officer, case: Case) -> None:
    if officer.role_clearance == "admin":
        return
    membership = db.query(CaseMember).filter(
        CaseMember.case_id == case.case_id,
        CaseMember.officer_id == officer.officer_id,
    ).first()
    if not membership or membership.access_level not in {"lead_investigator", "judge"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to manage this case")
