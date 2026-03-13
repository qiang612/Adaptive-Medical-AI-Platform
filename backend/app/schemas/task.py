# backend/app/schemas/task.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.inference_task import TaskStatus

class TaskBase(BaseModel):
    model_id: int
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    task_id: str
    user_id: int
    model_name: Optional[str] = None  # 取消默认值兜底，由Service关联查询真实名称
    risk_level: Optional[str] = None  # 新增：风险等级
    duration: Optional[int] = None    # 新增：任务耗时(秒)
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error_msg: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 新增分页列表的 Schema 响应格式
class TaskListResponse(BaseModel):
    total: int
    items: List[TaskResponse]