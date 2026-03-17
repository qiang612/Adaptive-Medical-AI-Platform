# backend/app/schemas/model.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ModelBase(BaseModel):
    model_name: str
    model_code: str
    model_type: str
    task_type: Optional[str] = None
    model_path: str
    description: Optional[str] = None
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    model_version: str = "1.0.0"
    accuracy: Optional[float] = None
    auc: Optional[float] = None

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):

    model_name: Optional[str] = None
    model_code: Optional[str] = None
    model_type: Optional[str] = None
    task_type: Optional[str] = None
    model_path: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    accuracy: Optional[float] = None
    auc: Optional[float] = None
    is_active: Optional[bool] = None

class ModelResponse(ModelBase):
    id: int
    is_active: bool
    create_time: datetime
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True