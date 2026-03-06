from pydantic import BaseModel
from typing import Optional, Dict, Any
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
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error_msg: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True