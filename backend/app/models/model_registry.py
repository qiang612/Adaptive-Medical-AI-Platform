from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON

from app.models.base import Base

class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_code = Column(String(50), unique=True, index=True, nullable=False, comment="模型编码（唯一标识）")
    model_name = Column(String(100), nullable=False, comment="模型名称（如：宫颈癌检测-YOLOv8）")
    model_type = Column(String(50), nullable=False, comment="模型类型（单模态/多模态）")
    task_type = Column(String(50), nullable=False, comment="任务类型（分类/检测/预测）")
    model_version = Column(String(20), nullable=False, comment="模型版本（如v1.0）")
    model_path = Column(String(255), nullable=False, comment="模型权重文件路径")
    input_schema = Column(JSON, nullable=False, comment="输入协议（前端自适应渲染依据）")
    output_schema = Column(JSON, nullable=False, comment="输出协议（结果可视化依据）")
    accuracy = Column(Float, nullable=True, comment="模型精度（如准确率85%）")
    description = Column(Text, nullable=True, comment="模型描述（适用病种、数据要求）")
    is_active = Column(Boolean, default=True, comment="是否启用（管理员控制上线/下线）")
    create_time = Column(DateTime, default=datetime.now, comment="注册时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")