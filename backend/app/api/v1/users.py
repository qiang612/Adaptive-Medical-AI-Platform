from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# 1. 补全缺失的导入（核心修复）
from app.core.database import get_db
from app.core.security import create_access_token, verify_password  # 补全 verify_password
from app.core.security import get_current_user, get_current_admin_user
from app.models.user import User, UserRole  # 补全 User 模型导入
from app.schemas.user import UserCreate, UserUpdate, UserResponse, Token
from app.services.user_service import user_service
from pydantic import BaseModel
router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """用户注册（仅管理员可用，实际可加权限校验）"""
    user = user_service.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    return user_service.create_user(db, user_in=user_in)


@router.post("/login", response_model=Token)  # 2. 补充响应模型，规范返回格式
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """登录接口（医生/管理员通用）"""
    # 3. 改用 user_service 统一查询，避免直接操作数据库（保持逻辑统一）
    user = user_service.get_user_by_username(db, username=form_data.username)

    # 3.1 检查用户是否存在
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 3.2 检查账号是否启用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号已被禁用"
        )

    # 3.3 验证密码
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 3.4 生成JWT Token（包含用户ID和角色，便于后续权限校验）
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    # 4. 按 Token 模型返回，同时兼容前端的 code/message
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


@router.get("/", response_model=list[UserResponse])
def get_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)  # 仅管理员可查看所有用户
):
    """获取用户列表（仅管理员可用）"""
    return user_service.get_users(db, skip=skip, limit=limit)


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
    # 转换为枚举类型
    user.role = UserRole(role_in.role_id)
    db.commit()
    return {"message": "角色更新成功"}