import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（如果有的话）
load_dotenv()


class Settings(BaseSettings):
    # ================= 数据库配置 =================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@127.0.0.1:3306/medical_ai_platform")

    # ================= 安全与认证配置 =================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    # ================= 异步任务调度配置 (Celery + Redis) =================
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # ================= 业务文件与AI模型路径配置 =================
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", 100 * 1024 * 1024))  # 默认限制 100MB
    WEIGHTS_DIR: str = os.getenv("WEIGHTS_DIR", "./weights")  # AI模型权重文件(.pt, .pkl)存放目录

    # Pydantic v2 推荐的配置方式，用于忽略多余的环境变量
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# 实例化配置对象，供全局使用
settings = Settings()

# ================= 系统初始化：自动创建必要目录 =================
# 确保存放AI模型权重的目录存在
os.makedirs(settings.WEIGHTS_DIR, exist_ok=True)

# 确保上传根目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# 为多模态医疗数据分类创建专用子目录
# 用于存放宫颈癌涂片、肺结节CT等单模态图像数据
os.makedirs(os.path.join(settings.UPLOAD_DIR, "images"), exist_ok=True)
# 用于存放冠心病患者的生化指标、电子病历等表格/文本数据
os.makedirs(os.path.join(settings.UPLOAD_DIR, "tables"), exist_ok=True)
# 用于存放AI推理后生成的检测结果图或可视化报告
os.makedirs(os.path.join(settings.UPLOAD_DIR, "reports"), exist_ok=True)