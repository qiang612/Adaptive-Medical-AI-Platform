from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# ==== 纯 MySQL 兼容配置（移除 pymysql 不支持的参数）====
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,          # MySQL 连接池大小
    max_overflow=20,       # 最大溢出连接数
    pool_pre_ping=True,    # 检查 MySQL 连接有效性
    pool_recycle=3600,     # 1小时回收连接，避免 MySQL 超时
    connect_args={
        "charset": "utf8mb4",  # MySQL 中文编码（pymysql 支持）
        "autocommit": False    # pymysql 支持的参数
        # 移除 timeout：pymysql 不支持这个参数，是核心报错原因
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()