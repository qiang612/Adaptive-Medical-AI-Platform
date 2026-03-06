from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from app.models.base import Base

# 仅两类角色（贴合你的需求）
class UserRole(str, enum.Enum):
    ADMIN = "admin"    # 管理员（模型注册、系统配置）
    DOCTOR = "doctor"  # 医生（使用模型诊断）

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="登录用户名")
    password = Column(String(255), nullable=False, comment="加密密码")
    full_name = Column(String(100), nullable=False, comment="真实姓名（医生/管理员姓名）")
    email = Column(String(100), nullable=True, comment="邮箱（接收诊断结果通知）")
    phone = Column(String(20), nullable=True, comment="手机号")
    role = Column(Enum(UserRole), nullable=False, comment="角色（admin/doctor）")
    department = Column(String(100), nullable=True, comment="所属科室（仅医生）")
    is_active = Column(Boolean, default=True, comment="是否启用")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")