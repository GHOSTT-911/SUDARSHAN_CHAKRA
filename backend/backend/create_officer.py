from getpass import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.db.models import Officer


officer_id = input("Officer ID: ").strip()
full_name = input("Full name: ").strip()
email = input("Email: ").strip()
role = input("Role (police/judge/admin): ").strip().lower()
password = getpass("Login password: ")

if not officer_id or not full_name or not email or not password:
    raise SystemExit("Officer ID, name, email, and password are required.")
if role not in {"police", "judge", "admin"}:
    raise SystemExit("Role must be police, judge, or admin.")

with SessionLocal() as db:
    existing = db.scalar(
        select(Officer).where(
            (Officer.officer_id == officer_id) | (Officer.email == email)
        )
    )
    if existing:
        raise SystemExit("An officer with that ID or email already exists.")

    officer = Officer(
        officer_id=officer_id,
        full_name=full_name,
        email=email,
        role_clearance=role,
        password_hash=hash_password(password),
        public_key="local-demo-key",
        is_active=True,
    )
    db.add(officer)
    db.commit()

print(f"Officer created: {officer_id} ({role})")
