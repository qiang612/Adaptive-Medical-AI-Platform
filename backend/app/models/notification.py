from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from app.models.base import Base

class NotificationType(str, enum.Enum):
    TASK_COMPLETE = "task_complete"  # 任务完成通知
    SYSTEM = "system"                # 系统通知（如模型下线）

class NotificationStatus(str, enum.Enum):
    UNREAD = "unread"    # 未读
    READ = "read"        # 已读

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="接收医生ID")
    title = Column(String(100), nullable=False, comment="通知标题（如：任务完成通知）")
    content = Column(Text, nullable=False, comment="通知内容（如：您的宫颈癌检测任务已完成）")
    notification_type = Column(Enum(NotificationType), nullable=False, comment="通知类型")
    related_task_id = Column(Integer, nullable=True, comment="关联任务ID（点击跳转任务详情）")
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD, comment="状态")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")