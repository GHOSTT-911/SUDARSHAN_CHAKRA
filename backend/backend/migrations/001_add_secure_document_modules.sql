-- Run once against the existing sudarshan_chakra database after backing it up.
-- This migration only adds tables; it does not alter Officers, Cases, or Evidence.
-- Prefer `python -m app.db.migrate` for the SQLAlchemy-managed version.

-- The application creates CaseMembers, Documents, DocumentVersions, and AuditEvents
-- with SQLAlchemy's metadata. Keeping this file records the deliberate additive strategy.
