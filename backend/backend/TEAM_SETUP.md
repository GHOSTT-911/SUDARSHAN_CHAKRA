# Sudarshan Chakra — team setup guide

This is the FastAPI/MySQL backend for the SIH prototype. It provides JWT login, role-based case access, encrypted document and evidence storage, SHA-256 integrity checks, version history, and a hash-linked audit trail.

## Before sharing

Share the project folder **without** `.env`, `.venv`, `venv`, `storage`, and `__pycache__` folders. Never send database passwords, JWT tokens, Fernet keys, or real investigation documents in chat or source control.

Keep `.env.example` in the shared folder; each teammate makes their own local `.env` from it.

## Prerequisites

- Python 3.11
- MySQL 8.4 (or a compatible MySQL server)
- A local database named `sudarshan_chakra`

## First-time setup

Open PowerShell in the backend folder.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-py311.txt
Copy-Item .env.example .env
```

Edit only the local `.env` file and set `DATABASE_URL` to that teammate's own MySQL credentials. Generate local secrets without displaying them publicly:

```powershell
$jwt = python -c "from secrets import token_urlsafe; print(token_urlsafe(48))"; $fernet = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"; Add-Content .env "`nJWT_SECRET_KEY=$jwt`nFERNET_KEY=$fernet"
```

Create the added secure-module tables. This does not modify or delete the original `Officers`, `Cases`, or `Evidence` data.

```powershell
python -m app.db.migrate
```

Start the application:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Verify it is working

- Health check: `http://127.0.0.1:8000/api/v1/health`
- Swagger interface: `http://127.0.0.1:8000/docs`

Use an existing MySQL officer account to log in through `/api/v1/auth/login`. Authorize the returned bearer token in Swagger. Do not put tokens in screenshots, commits, or team chats.

## Demo sequence

1. Admin logs in and creates or opens a case.
2. Admin adds an investigating officer under `POST /api/v1/cases/{case_id}/members`.
3. Officer logs in, sees only their assigned case, and uploads a harmless sample document.
4. Run the document integrity endpoint and show `integrity_verified: true`.
5. Upload a new document version and show the retained history.
6. Admin opens `/api/v1/audit/` to show the hash-linked audit events.

## Current prototype boundary

The current backend implements the secure core. MinIO/MongoDB, a blockchain network, Tesseract image OCR, AI assistance, and officer-specific PKI signatures are future enhancements, not current claims.
