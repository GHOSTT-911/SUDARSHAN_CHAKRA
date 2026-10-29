# Sudarshan Chakra backend

Secure FastAPI backend for legal case and investigation-document management.

## Setup

Use Python 3.11 in a fresh virtual environment. Install the project dependencies, copy `.env.example` to `.env`, then add local MySQL credentials and secrets. Do not commit `.env`.

Run the additive migration before starting the app:

```powershell
python -m app.db.migrate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The migration creates only `CaseMembers`, `Documents`, `DocumentVersions`, and `AuditEvents`; it does not delete or change the established tables.

## Main API groups

- `/api/v1/auth/login`, `/api/v1/auth/me`
- `/api/v1/cases` including membership management
- `/api/v1/documents` encrypted upload, versions, download, integrity verification
- `/api/v1/evidence` encrypted upload, download, integrity verification
- `/api/v1/audit` (admin only)
- `/api/v1/search/documents`

File bytes are SHA-256 hashed before Fernet encryption. The audit stream stores a hash link to the preceding event, making alteration evident in a prototype demonstration.

Plain-text files and PDFs with embedded text are indexed automatically when PyMuPDF is installed. Image OCR can be added later with a locally configured Tesseract installation; it is deliberately not required for the secure core to start.
