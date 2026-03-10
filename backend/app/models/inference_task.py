# backend/app/models/inference_task.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from app.models.base import Base

# 修改了 SUCCESS 为 COMPLETED，以匹配前端代码中 item.status === 'completed'
class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class InferenceTask(Base):
    __tablename__ = "inference_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String(50), unique=True, index=True, nullable=False, comment="任务编号") # 替换 task_no
    model_id = Column(Integer, nullable=False, comment="使用的模型ID") # 替换 model_code
    user_id = Column(Integer, nullable=False, comment="提交医生ID") # 替换 doctor_id
    patient_name = Column(String(50), nullable=True, comment="患者姓名") # 新增，供前端显示
    patient_id = Column(String(50), nullable=True, comment="患者门诊号") # 新增
    input_data = Column(JSON, nullable=True, comment="输入数据")
    file_paths = Column(JSON, nullable=True, comment="文件路径列表") # 新增，存放图片
    result = Column(JSON, nullable=True, comment="推理结果") # 替换 output_data
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, comment="任务状态")
    error_msg = Column(Text, nullable=True, comment="错误信息")
    start_time = Column(DateTime, default=datetime.now, comment="提交时间") # 替换 submit_time
    end_time = Column(DateTime, nullable=True, comment="完成时间") # 替换 complete_time
    created_at = Column(DateTime, default=datetime.now) # 新增，匹配 Schema
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)