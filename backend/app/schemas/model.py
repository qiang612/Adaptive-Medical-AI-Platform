from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ModelBase(BaseModel):
    model_name: str
    model_code: str
    model_type: str
    adapter_class: str
    description: Optional[str] = None
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    model_version: str = "1.0.0"



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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

