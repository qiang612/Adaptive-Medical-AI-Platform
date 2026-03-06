# backend/app/core/hashing.py
from passlib.context import CryptContext

# 初始化密码上下文（必须用 pbkdf2_sha256 算法，和创建admin账号时一致）
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成加密密码"""
    return pwd_context.hash(password)