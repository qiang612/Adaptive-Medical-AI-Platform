# backend/app/models/teaching_case.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from app.models.base import Base

class TeachingCase(Base):
    __tablename__ = "teaching_cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    disease_type = Column(String(50), nullable=False) # 宫颈癌, 肺结节 等
    case_type = Column(String(50), nullable=False)    # 典型病例, 疑难病例 等
    difficulty = Column(String(50), nullable=False)   # 入门, 进阶, 高级
    description = Column(Text)
    findings = Column(JSON) # 存储阳性发现的数组
    view_count = Column(Integer, default=0)
    star_count = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.now)