# backend/app/models/system.py
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from app.models.base import Base


class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, index=True, nullable=False)  # 'global', 'storage', 'email' 等
    value = Column(JSON, nullable=False)  # 存储配置的JSON对象
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class NoticeTemplate(Base):
    __tablename__ = "notice_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(100), nullable=False)
    template_code = Column(String(50), unique=True, index=True, nullable=False)
    notice_type = Column(String(20), nullable=False)  # 'email' 或 'message'
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())