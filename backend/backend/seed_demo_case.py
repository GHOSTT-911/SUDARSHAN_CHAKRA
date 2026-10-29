from datetime import date, datetime, timezone
from hashlib import sha256

from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import Case, CaseMember, Evidence, Officer
from app.services.storage import store_encrypted


CASE_ID = "FIR-2026-SC-001"
OFFICER_ID = "POL-SC-002"
EVIDENCE_ID = "EVD-2026-SC-001"
PDF_BYTES = b"%PDF-1.4\nSudarshan Chakra demo evidence\n%%EOF\n"

with SessionLocal() as db:
    officer = db.scalar(select(Officer).where(Officer.officer_id == OFFICER_ID))
    if officer is None:
        raise SystemExit(f"Officer not found: {OFFICER_ID}")

    case = db.scalar(select(Case).where(Case.case_id == CASE_ID))
    if case is None:
        case = Case(
            case_id=CASE_ID,
            crime_domain="Cyber Financial Fraud",
            filing_date=date.today(),
            status="Pending Review",
        )
        db.add(case)

    membership = db.scalar(
        select(CaseMember).where(
            CaseMember.case_id == CASE_ID,
            CaseMember.officer_id == OFFICER_ID,
        )
    )
    if membership is None:
        db.add(CaseMember(
            member_id="MEM-2026-SC-001",
            case_id=CASE_ID,
            officer_id=OFFICER_ID,
            access_level="lead_investigator",
            assigned_at=datetime.now(timezone.utc),
        ))

    evidence = db.scalar(select(Evidence).where(Evidence.evidence_id == EVIDENCE_ID))
    if evidence is None:
        evidence = Evidence(
            evidence_id=EVIDENCE_ID,
            case_id=CASE_ID,
            sha256_hash=sha256(PDF_BYTES).hexdigest(),
            encrypted_storage_path=store_encrypted(PDF_BYTES, "evidence"),
            uploaded_by=OFFICER_ID,
            upload_timestamp=datetime.now(timezone.utc),
        )
        db.add(evidence)

    db.commit()

print(f"Case ready: {CASE_ID}")
print(f"Evidence ready: {EVIDENCE_ID}")
