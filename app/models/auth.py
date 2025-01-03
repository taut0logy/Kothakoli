from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

class VerifyEmailRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: constr(min_length=6, max_length=6)
    password: constr(min_length=6)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
    name: str

class UpdateProfileRequest(BaseModel):
    name: str | None = None
    password: constr(min_length=6) | None = None
    apiKey: str | None = None
    modelName: str | None = None
    