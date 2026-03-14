# backend/app/schemas/system.py
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class NoticeTemplateBase(BaseModel):
    template_name: str
    template_code: str
    notice_type: str
    title: str
    content: str
    is_active: bool = True

class NoticeTemplateCreate(NoticeTemplateBase):
    pass

class NoticeTemplateUpdate(BaseModel):
    template_name: Optional[str] = None
    template_code: Optional[str] = None
    notice_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None

class NoticeTemplateResponse(NoticeTemplateBase):
    id: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # 兼容 Pydantic v2
        orm_mode = True        # 兼容 Pydantic v1

class EmailTestRequest(BaseModel):
    to_email: str