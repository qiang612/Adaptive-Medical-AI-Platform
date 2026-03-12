from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import engine, SessionLocal
from app.core.celery_app import celery
# 🔥 关键：导入模型的 Base（已包含所有6张表的定义）
from app.models import Base
import os

# ===================== 核心建表逻辑（修正后） =====================
# 强制创建所有表（检测到模型并在 medical_ai_db 中生成）
# checkfirst=True：避免重复创建，已存在则跳过
Base.metadata.create_all(bind=engine, checkfirst=True)
print("✅ 数据库表检查完成：已自动创建缺失的表")

# ===================== 自动创建默认账号 =====================
from app.models import User, UserRole
from app.core.hashing import get_password_hash
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

db = SessionLocal()
try:
    # 1. 检查并创建管理员
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        new_admin = User(
            username="admin",
            password=get_password_hash("admin123"),  # 修改为前端提示的密码
            full_name="系统管理员",
            role=UserRole.ADMIN,
            is_active=True,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        db.add(new_admin)
        print("✅ 管理员账号创建成功：admin/admin123")

    # 2. 检查并创建测试医生
    doctor = db.query(User).filter(User.username == "doctor").first()
    if not doctor:
        new_doctor = User(
            username="doctor",
            password=get_password_hash("doctor123"),  # 修改为前端提示的密码
            full_name="李医生",
            department="放射科",
            role=UserRole.DOCTOR,
            is_active=True,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        db.add(new_doctor)
        print("✅ 医生账号创建成功：doctor/doctor123")

    db.commit()
except SQLAlchemyError as e:
    print(f"❌ 账号创建失败：{str(e)}")
    db.rollback()
finally:
    db.close()

# ===================== 其余 FastAPI 配置（保留） =====================
app = FastAPI(
    title="医疗AI模型接入平台",
    description="仅支持医生+管理员的多模型异步推理平台",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": f"医疗AI模型接入平台服务已启动（数据库：medical_ai_platform）"}

# 上传测试接口（保留）
@app.post("/upload-test")
async def upload_test(files: list[UploadFile] = File(...)):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_files = []
    for file in files:
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        saved_files.append(file_path)
    return {"message": f"成功上传 {len(files)} 个文件", "files": saved_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )