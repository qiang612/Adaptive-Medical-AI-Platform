# backend/app/models/patient.py
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from app.models.base import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    gender = Column(String(10), nullable=False)
    birthday = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    id_card = Column(String(18), unique=True, index=True, nullable=True)
    phone = Column(String(20), index=True, nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    medical_history = Column(Text, nullable=True)
    remark = Column(Text, nullable=True)
    avatar = Column(String(255), nullable=True)
    diagnosis_count = Column(Integer, default=0)
    last_diagnosis_time = Column(DateTime, nullable=True)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())