# backend/app/schemas/model.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ModelBase(BaseModel):
    model_name: str
    model_code: str
    model_type: str
    task_type: Optional[str] = None      # 加上数据库已有的 task_type
    model_path: str                      # 替换 adapter_class，对齐数据库
    description: Optional[str] = None
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    model_version: str = "1.0.0"
    accuracy: Optional[float] = None     # 加上数据库已有的 accuracy
    auc: Optional[float] = None

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    is_active: Optional[bool] = None

class ModelResponse(ModelBase):
    id: int
    is_active: bool
    create_time: datetime                # 替换 created_at，对齐数据库
    update_time: Optional[datetime] = None # 替换 updated_at，对齐数据库

    class Config:
        from_attributes = True