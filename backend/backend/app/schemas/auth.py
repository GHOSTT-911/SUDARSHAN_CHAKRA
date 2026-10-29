from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    officer_id: str
    full_name: str
    email: str
    password: str
    role: str = "police"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    officer_id: str
    full_name: str
    role: str