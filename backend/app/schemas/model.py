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
    # 👇 补充所有在前端编辑表单中可能被修改的字段
    model_name: Optional[str] = None
    model_code: Optional[str] = None
    model_type: Optional[str] = None
    task_type: Optional[str] = None
    model_path: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    accuracy: Optional[float] = None     # 🔥 修复：允许更新准确率
    auc: Optional[float] = None          # 🔥 修复：允许更新 AUC
    is_active: Optional[bool] = None

class ModelResponse(ModelBase):
    id: int
    is_active: bool
    create_time: datetime                # 替换 created_at，对齐数据库
    update_time: Optional[datetime] = None # 替换 updated_at，对齐数据库

    class Config:
        from_attributes = True