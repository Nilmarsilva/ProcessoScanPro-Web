"""
Schemas Pydantic para usuário
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Schema base de usuário"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserInDB(UserBase):
    """Schema de usuário no banco de dados"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema público de usuário"""
    pass


class UserLogin(BaseModel):
    """Schema para login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema de token JWT"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Payload do token"""
    sub: Optional[int] = None
    exp: Optional[int] = None
