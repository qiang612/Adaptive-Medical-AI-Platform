# D:\Adaptive-Medical-AI-Platform\backend\create_admin.py
import sys
import os
# 添加项目根目录到 Python 路径（解决导入错误）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 手动配置数据库连接（避免依赖其他文件）
# 如果你用 MySQL，替换为你的连接串：
# DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/medical_ai_platform?charset=utf8mb4"
# 如果你用 SQLite：
DATABASE_URL = "sqlite:///./medical_ai_platform.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 定义 User 模型（简化，避免导入错误）
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.DOCTOR)
    department = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 密码加密函数（内置，不依赖外部文件）
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], default="pbkdf2_sha256")

def get_password_hash(password):
    return pwd_context.hash(password[:100])

# 核心逻辑：创建管理员账号
db = SessionLocal()
try:
    # 检查 admin 用户是否存在
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("✅ 管理员账号已存在：")
        print(f"   用户名：admin")
        print(f"   密码：123456（默认）")
    else:
        # 创建新管理员
        new_admin = User(
            username="admin",
            password=get_password_hash("123456"),  # 密码：123456
            full_name="系统管理员",
            email="admin@example.com",
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_admin)
        db.commit()
        print("✅ 管理员账号创建成功！")
        print("   用户名：admin")
        print("   密码：123456")
except Exception as e:
    print(f"❌ 创建失败：{str(e)}")
    db.rollback()
finally:
    db.close()