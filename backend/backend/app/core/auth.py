from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.db.models import Officer


bearer_scheme = HTTPBearer()


def get_current_officer(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials

        payload = decode_access_token(token)

        officer_id = payload.get("sub")

        if officer_id is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    officer = (
        db.query(Officer)
        .filter(Officer.officer_id == officer_id)
        .first()
    )

    if officer is None:
        raise credentials_exception

    if not officer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Officer account is inactive"
        )

    return officer