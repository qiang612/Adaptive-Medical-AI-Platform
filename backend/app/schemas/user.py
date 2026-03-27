# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    code: Optional[int] = 200
    message: Optional[str] = "登录成功"

class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"

class UserBase(BaseModel):
    username: str
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: UserRole
    department: Optional[str] = None
    title: Optional[str] = None
    avatar: Optional[str] = None
    remark: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    avatar: Optional[str] = None
    remark: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        orm_mode = True
        protected_namespaces = ()


class UserListResponse(BaseModel):
    total: int
    items: list[UserResponse]

    class Config:
        protected_namespaces = ()