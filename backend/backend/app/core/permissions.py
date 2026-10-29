from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_officer
from app.db.models import Officer


def require_role(*allowed_roles: str):
    def role_checker(
        current_officer: Officer = Depends(get_current_officer)
    ):
        if current_officer.role_clearance not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return current_officer

    return role_checker