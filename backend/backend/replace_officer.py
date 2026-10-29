from getpass import getpass

from sqlalchemy import delete, select

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.db.models import Case, CaseMember, Evidence, Officer


old_officer_id = input("Officer ID to delete: ").strip()
new_officer_id = input("New officer ID: ").strip()
full_name = input("New full name: ").strip()
email = input("New email: ").strip()
role = input("Role (police/judge/admin): ").strip().lower()
password = getpass("New login password: ")

if not all((old_officer_id, new_officer_id, full_name, email, password)):
    raise SystemExit("All fields are required.")
if role not in {"police", "judge", "admin"}:
    raise SystemExit("Role must be police, judge, or admin.")

with SessionLocal() as db:
    old_officer = db.scalar(select(Officer).where(Officer.officer_id == old_officer_id))
    if old_officer is None:
        raise SystemExit("The officer to delete was not found.")
    if db.scalar(select(CaseMember).where(CaseMember.officer_id == old_officer_id)):
        raise SystemExit("Cannot delete: officer has case memberships.")
    if db.scalar(select(Case).where(Case.assigned_judge_id == old_officer_id)):
        raise SystemExit("Cannot delete: officer is assigned as a judge.")
    if db.scalar(select(Evidence).where(Evidence.uploaded_by == old_officer_id)):
        raise SystemExit("Cannot delete: officer uploaded evidence.")
    if db.scalar(select(Officer).where((Officer.officer_id == new_officer_id) | (Officer.email == email))):
        raise SystemExit("The new officer ID or email already exists.")

    db.execute(delete(Officer).where(Officer.officer_id == old_officer_id))
    db.add(Officer(
        officer_id=new_officer_id,
        full_name=full_name,
        email=email,
        role_clearance=role,
        password_hash=hash_password(password),
        public_key="local-demo-key",
        is_active=True,
    ))
    db.commit()

print(f"Replaced {old_officer_id} with {new_officer_id} ({role}).")
