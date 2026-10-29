from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CaseCreate(BaseModel):
    case_id: str = Field(min_length=1, max_length=50)
    crime_domain: str = Field(min_length=1, max_length=100)
    filing_date: date
    status: str = "Pending Review"
    assigned_judge_id: str | None = None


class CaseUpdate(BaseModel):
    crime_domain: str | None = Field(None, min_length=1, max_length=100)
    filing_date: date | None = None
    status: str | None = None
    assigned_judge_id: str | None = None


class CaseMemberCreate(BaseModel):
    officer_id: str
    access_level: str = "viewer"


class CaseMemberResponse(BaseModel):
    member_id: str
    case_id: str
    officer_id: str
    access_level: str
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseResponse(BaseModel):
    case_id: str
    crime_domain: str
    filing_date: date
    status: str
    assigned_judge_id: str | None = None

    model_config = ConfigDict(from_attributes=True)
