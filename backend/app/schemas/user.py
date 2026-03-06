# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
from typing import Optional

# 补充 Token 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str
    code: Optional[int] = 200  # 兼容前端的状态码
    message: Optional[str] = "登录成功"  # 兼容前端的提示信息

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
    is_active: bool = True

class UserCreate(UserBase):
    password: str  # 注册时需要密码

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        orm_mode = True  # 关键：支持从 ORM 模型（User）转换为 Pydantic 模型
        protected_namespaces = ()  # 消除 model_ 前缀警告