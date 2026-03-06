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