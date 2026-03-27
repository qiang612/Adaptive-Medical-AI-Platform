from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.core.security import get_current_user, get_current_admin_user
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.login_log import LoginLog
from app.models.operation_log import OperationLog, OperationType, UserRole as OpUserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse, Token, UserListResponse
from app.services.user_service import user_service
from pydantic import BaseModel
from datetime import datetime, timedelta
import redis
import logging
import os
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["用户管理"])


MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 15 * 60


def get_redis_client():
    redis_url = settings.REDIS_URL
    if redis_url.startswith('redis://'):
        redis_url = redis_url.replace('redis://', '')
    parts = redis_url.split('/')
    db = int(parts[1]) if len(parts) > 1 else 0
    host_port = parts[0].split(':')
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 6379
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_login_attempts(redis_client, username: str) -> int:
    key = f"login_attempts:{username}"
    attempts = redis_client.get(key)
    return int(attempts) if attempts else 0


def increment_login_attempts(redis_client, username: str):
    key = f"login_attempts:{username}"
    redis_client.incr(key)
    redis_client.expire(key, LOCKOUT_DURATION)


def reset_login_attempts(redis_client, username: str):
    key = f"login_attempts:{username}"
    redis_client.delete(key)


def is_account_locked(redis_client, username: str) -> bool:
    attempts = get_login_attempts(redis_client, username)
    return attempts >= MAX_LOGIN_ATTEMPTS


def get_lockout_remaining(redis_client, username: str) -> int:
    key = f"login_attempts:{username}"
    ttl = redis_client.ttl(key)
    return max(0, ttl)


def create_login_log(db: Session, username: str, full_name: str, role: str, 
                     ip_address: str, user_agent: str, status: str, fail_reason: str = None):
    log = LoginLog(
        username=username,
        full_name=full_name,
        role=role,
        ip_address=ip_address,
        user_agent=user_agent,
        location="",
        status=status,
        fail_reason=fail_reason,
        login_time=datetime.now()
    )
    db.add(log)
    db.commit()


def create_operation_log(db: Session, operator_id: int, operator_role: str, 
                         operation_type: OperationType, operation_content: str,
                         ip_address: str, success: bool = True, error_msg: str = None):
    log = OperationLog(
        operator_id=operator_id,
        operator_role=OpUserRole.ADMIN if operator_role == "admin" else OpUserRole.DOCTOR,
        operation_type=operation_type,
        operation_content=operation_content,
        ip_address=ip_address,
        success=success,
        error_msg=error_msg,
        operation_time=datetime.now()
    )
    db.add(log)
    db.commit()


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db), request: Request = None,
             current_user: User = Depends(get_current_admin_user)):
    """用户注册（仅管理员可用）"""
    user = user_service.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    new_user = user_service.create_user(db, user_in=user_in)
    
    ip_address = get_client_ip(request) if request else "unknown"
    create_operation_log(
        db=db,
        operator_id=current_user.id,
        operator_role=current_user.role.value,
        operation_type=OperationType.USER_CREATE,
        operation_content=f"创建了新用户 [{user_in.username}] - {user_in.full_name}",
        ip_address=ip_address,
        success=True
    )
    
    return new_user


@router.post("/login", response_model=Token)
def login(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "unknown")
    
    try:
        redis_client = get_redis_client()
    except Exception as e:
        logger.warning(f"Redis连接失败，跳过登录限制检查: {e}")
        redis_client = None
    
    if redis_client and is_account_locked(redis_client, form_data.username):
        remaining = get_lockout_remaining(redis_client, form_data.username)
        minutes = remaining // 60
        seconds = remaining % 60
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"账号已被锁定，请 {minutes}分{seconds}秒 后重试"
        )
    
    user = user_service.get_user_by_username(db, username=form_data.username)

    if not user:
        if redis_client:
            increment_login_attempts(redis_client, form_data.username)
            attempts_left = MAX_LOGIN_ATTEMPTS - get_login_attempts(redis_client, form_data.username)
        create_login_log(db, form_data.username, "", "", ip_address, user_agent, 
                        "fail", "用户不存在")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"用户名或密码错误，剩余尝试次数: {max(0, attempts_left) if redis_client else '无限'}"
        )

    if not user.is_active:
        create_login_log(db, form_data.username, user.full_name, user.role.value, 
                        ip_address, user_agent, "fail", "账号已被禁用")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号已被禁用"
        )

    if not verify_password(form_data.password, user.password):
        if redis_client:
            increment_login_attempts(redis_client, form_data.username)
            attempts_left = MAX_LOGIN_ATTEMPTS - get_login_attempts(redis_client, form_data.username)
            if attempts_left <= 0:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="登录失败次数过多，账号已被锁定15分钟"
                )
        create_login_log(db, form_data.username, user.full_name, user.role.value, 
                        ip_address, user_agent, "fail", "密码错误")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"用户名或密码错误，剩余尝试次数: {max(0, attempts_left) if redis_client else '无限'}"
        )

    if redis_client:
        reset_login_attempts(redis_client, form_data.username)

    create_login_log(db, form_data.username, user.full_name, user.role.value, 
                    ip_address, user_agent, "success")

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "code": 200,
        "message": "登录成功"
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息（所有已登录用户可用）"""
    return current_user


@router.get("/", response_model=UserListResponse)
def get_users(
        page: int = 1,
        page_size: int = 10,
        keyword: str = "",
        role: str = "",
        is_active: str = "",
        department: str = "",
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):
    """获取用户列表（仅管理员可用），支持分页和搜索"""
    query = db.query(User)
    
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) |
            (User.full_name.contains(keyword)) |
            (User.phone.contains(keyword)) |
            (User.email.contains(keyword))
        )
    
    if role:
        query = query.filter(User.role == UserRole(role))
    
    if is_active:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter(User.is_active == is_active_bool)
    
    if department:
        query = query.filter(User.department == department)
    
    total = query.count()
    items = query.order_by(User.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {"total": total, "items": items}


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
        user_id: int,
        user_in: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)  # 仅管理员可修改用户
):
    """修改用户信息（仅管理员可用）"""
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user_service.update_user(db, db_user=user, user_in=user_in)

# --- 补充前端需要的请求 Schema ---
class UserStatusUpdate(BaseModel):
    is_active: bool

class PasswordReset(BaseModel):
    new_password: str

class UserRoleUpdate(BaseModel):
    role_id: str

# --- 补充缺失的接口 ---

@router.patch("/{user_id}/status")
def toggle_user_status(
    user_id: int,
    status_in: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """切换用户状态"""
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = status_in.is_active
    db.commit()
    return {"message": "状态更新成功"}

@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    pwd_in: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """重置用户密码"""
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    from app.core.hashing import get_password_hash
    user.password = get_password_hash(pwd_in.new_password)  # 注意你模型里可能是 hashed_password 或 password，请对齐
    db.commit()
    return {"message": "密码重置成功"}

@router.put("/{user_id}/role")
def update_user_role(
    user_id: int,
    role_in: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新用户角色"""
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.role = UserRole(role_in.role_id)
    db.commit()
    return {"message": "角色更新成功"}


@router.post("/me/avatar")
async def upload_avatar(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只能上传图片文件")
    
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持 JPG、PNG、GIF、WEBP 格式的图片")
    
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    import uuid
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    
    avatar_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)
    
    file_path = os.path.join(avatar_dir, filename)
    
    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过 2MB")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    avatar_url = f"/uploads/avatars/{filename}"
    
    current_user.avatar = avatar_url
    db.commit()
    
    return {
        "message": "头像上传成功",
        "avatar_url": avatar_url
    }


@router.post("/{user_id}/avatar")
async def upload_user_avatar(
        user_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只能上传图片文件")
    
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持 JPG、PNG、GIF、WEBP 格式的图片")
    
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    import uuid
    import os
    filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    
    avatar_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)
    
    file_path = os.path.join(avatar_dir, filename)
    
    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过 2MB")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    avatar_url = f"/uploads/avatars/{filename}"
    
    user.avatar = avatar_url
    db.commit()
    
    return {
        "message": "头像上传成功",
        "avatar_url": avatar_url
    }