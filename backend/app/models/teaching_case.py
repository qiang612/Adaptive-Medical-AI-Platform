# backend/app/models/teaching_case.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from app.models.base import Base

class TeachingCase(Base):
    __tablename__ = "teaching_cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    disease_type = Column(String(50), nullable=False)
    case_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    description = Column(Text)
    findings = Column(JSON)
    images = Column(JSON)
    diagnosis = Column(Text)
    treatment = Column(Text)
    tags = Column(JSON)
    view_count = Column(Integer, default=0)
    star_count = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)