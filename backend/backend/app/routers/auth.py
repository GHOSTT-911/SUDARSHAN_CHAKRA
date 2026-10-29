from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.core.auth import get_current_officer
from app.db.database import get_db
from app.db.models import Officer
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.services.audit import log_event


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


def require_admin(current_officer: Officer) -> None:
    if current_officer.role_clearance != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can manage officers")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(credentials: RegisterRequest, db: Session = Depends(get_db)):
    if credentials.role not in {"police", "judge", "admin"}:
        raise HTTPException(status_code=422, detail="Invalid role")
    if db.query(Officer).filter(
        (Officer.officer_id == credentials.officer_id) | (Officer.email == credentials.email)
    ).first():
        raise HTTPException(status_code=409, detail="Officer ID or email already exists")
    officer = Officer(
        officer_id=credentials.officer_id,
        full_name=credentials.full_name,
        email=credentials.email,
        role_clearance=credentials.role,
        password_hash=hash_password(credentials.password),
        public_key="local-demo-key",
        is_active=True,
    )
    db.add(officer)
    db.commit()
    return {"officer_id": officer.officer_id, "full_name": officer.full_name, "email": officer.email, "role": officer.role_clearance}


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    officer = (
        db.query(Officer)
        .filter(Officer.email == credentials.email)
        .first()
    )

    if officer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not officer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Officer account is inactive"
        )

    if not verify_password(
        credentials.password,
        officer.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": officer.officer_id,
            "role": officer.role_clearance
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "officer_id": officer.officer_id,
        "full_name": officer.full_name,
        "role": officer.role_clearance
    }


@router.get("/me")
def get_me(current_officer: Officer = Depends(get_current_officer)):
    return {"officer_id": current_officer.officer_id, "full_name": current_officer.full_name, "email": current_officer.email, "role": current_officer.role_clearance, "is_active": current_officer.is_active}


@router.get("/officers")
def list_officers(current_officer: Officer = Depends(get_current_officer), db: Session = Depends(get_db)):
    require_admin(current_officer)
    return [
        {
            "officer_id": officer.officer_id,
            "full_name": officer.full_name,
            "email": officer.email,
            "role": officer.role_clearance,
            "is_active": officer.is_active,
        }
        for officer in db.query(Officer).order_by(Officer.full_name).all()
    ]


@router.patch("/officers/{officer_id}/status")
def update_officer_status(officer_id: str, request: Request, db: Session = Depends(get_db), current_officer: Officer = Depends(get_current_officer)):
    require_admin(current_officer)
    officer = db.query(Officer).filter(Officer.officer_id == officer_id).first()
    if officer is None:
        raise HTTPException(status_code=404, detail="Officer not found")
    if officer.officer_id == current_officer.officer_id:
        raise HTTPException(status_code=400, detail="Administrators cannot disable their own account")
    officer.is_active = not officer.is_active
    log_event(db, current_officer, "OFFICER_STATUS_CHANGED", "officer", officer.officer_id, ip_address=request.client.host if request.client else None, details={"is_active": officer.is_active})
    db.commit()
    return {"officer_id": officer.officer_id, "is_active": officer.is_active}
