# backend/app/models/base.py
from sqlalchemy.ext.declarative import declarative_base

# 所有模型共享同一个 Base
Base = declarative_base()