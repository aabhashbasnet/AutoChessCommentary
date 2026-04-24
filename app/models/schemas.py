# app/models/schemas.py
from pydantic import BaseModel, EmailStr


class PGNRequest(BaseModel):
    pgn: str
    depth: int = 15
    time_per_move: float = 1.0


# ── Auth ──
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True
