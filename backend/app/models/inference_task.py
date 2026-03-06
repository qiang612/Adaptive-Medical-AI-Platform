from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON
import enum

from app.models.base import Base
# 任务状态（贴合开题报告的异步流程）
class TaskStatus(str, enum.Enum):
    PENDING = "pending"    # 排队中
    PROCESSING = "processing"  # 处理中
    SUCCESS = "success"    # 成功
    FAILED = "failed"      # 失败

class InferenceTask(Base):
    __tablename__ = "inference_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_no = Column(String(50), unique=True, index=True, nullable=False, comment="任务编号")
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="提交医生ID")
    model_code = Column(String(50), ForeignKey("model_registry.model_code"), nullable=False, comment="使用模型编码")
    input_data = Column(JSON, nullable=False, comment="输入数据（图片路径+表单数据）")
    output_data = Column(JSON, nullable=True, comment="推理结果（按output_schema格式存储）")
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, comment="任务状态")
    error_msg = Column(Text, nullable=True, comment="错误信息（失败时存储）")
    submit_time = Column(DateTime, default=datetime.now, comment="提交时间")
    complete_time = Column(DateTime, nullable=True, comment="完成时间")