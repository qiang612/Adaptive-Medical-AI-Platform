from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

from app.models.base import Base

# 文件类型（贴合开题报告的多模态需求）
class FileType(str, enum.Enum):
    IMAGE = "image"    # 普通图片（JPG/PNG）
    DICOM = "dicom"    # 医学影像（DICOM）
    EXCEL = "excel"    # 批量数据（Excel）

class UploadFile(Base):
    __tablename__ = "upload_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_path = Column(String(255), nullable=False, comment="文件存储路径")
    file_type = Column(Enum(FileType), nullable=False, comment="文件类型")
    file_size = Column(Integer, nullable=True, comment="文件大小（字节）")
    task_id = Column(Integer, ForeignKey("inference_tasks.id"), nullable=False, comment="关联任务ID")
    upload_time = Column(DateTime, default=datetime.now, comment="上传时间")