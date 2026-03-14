# backend/app/models/login_log.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean
from datetime import datetime
import enum
from app.models.base import Base

class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=False, comment="登录账号")
    full_name = Column(String(100), nullable=True, comment="真实姓名")
    role = Column(String(20), nullable=True, comment="角色")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="设备信息")
    location = Column(String(100), nullable=True, comment="登录地点")
    status = Column(String(20), default="success", comment="状态(success/fail)")
    fail_reason = Column(String(255), nullable=True, comment="失败原因")
    login_time = Column(DateTime, default=datetime.now, comment="登录时间")