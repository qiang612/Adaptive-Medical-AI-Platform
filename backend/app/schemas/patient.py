# backend/app/schemas/patient.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime

class PatientBase(BaseModel):
    patient_id: Optional[str] = None
    name: str
    gender: str
    birthday: Optional[date] = None
    age: Optional[int] = None
    id_card: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None
    remark: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    avatar: Optional[str] = None
    diagnosis_count: int = 0
    last_diagnosis_time: Optional[datetime] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    # 这是 Pydantic V2 的规范写法，用来替代 orm_mode = True
    model_config = ConfigDict(from_attributes=True)

# 专门用于列表分页返回的 Schema
class PatientList(BaseModel):
    total: int
    items: List[PatientResponse]
    page: int
    page_size: int