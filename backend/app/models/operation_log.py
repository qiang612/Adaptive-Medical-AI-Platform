# backend/app/models/operation_log.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from app.models.base import Base

# 先定义自己的枚举，避免循环导入 UserRole
class UserRole(str, enum.Enum):
    ADMIN = "admin"    # 管理员
    DOCTOR = "doctor"  # 医生

class OperationType(str, enum.Enum):
    MODEL_REGISTER = "model_register"  # 注册模型
    MODEL_UPDATE = "model_update"      # 更新模型
    MODEL_DISABLE = "model_disable"    # 禁用模型
    TASK_SUBMIT = "task_submit"        # 提交任务
    USER_CREATE = "user_create"        # 创建用户（管理员新增医生）

class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="操作人ID")
    operator_role = Column(Enum(UserRole), nullable=False, comment="操作人角色")
    operation_type = Column(Enum(OperationType), nullable=False, comment="操作类型")
    operation_content = Column(Text, nullable=False, comment="操作内容（如：注册模型宫颈癌检测-v1.0）")
    ip_address = Column(String(50), nullable=True, comment="操作IP")
    success = Column(Boolean, default=True, comment="操作是否成功")
    error_msg = Column(Text, nullable=True, comment="错误信息（失败时存储）")
    operation_time = Column(DateTime, default=datetime.now, comment="操作时间")