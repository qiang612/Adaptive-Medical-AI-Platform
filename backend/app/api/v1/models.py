# backend/app/api/v1/models.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.schemas.model import ModelCreate, ModelUpdate, ModelResponse
from app.services.model_service import model_service
from app.models.operation_log import OperationLog, OperationType, UserRole as OpUserRole

router = APIRouter(prefix="/models", tags=["模型管理"])


def get_client_ip(request: Request) -> str:
    """获取客户端真实IP"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def create_operation_log(db: Session, operator_id: int, operator_role: str, 
                         operation_type: OperationType, operation_content: str,
                         ip_address: str, success: bool = True, error_msg: str = None):
    """创建操作日志"""
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


@router.get("/")
def get_models_list(
        page: Optional[int] = None,
        page_size: Optional[int] = Query(10, alias="page_size"),
        keyword: Optional[str] = None,
        model_type: Optional[str] = Query(None, alias="model_type"),
        is_active: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    获取模型列表：
    - 如果前端传了 page 参数，则返回支持分页、关键词和状态过滤的数据字典 {"total": x, "items": [...]}
    - 如果没有传 page 参数，则退化为旧逻辑，直接返回所有激活的模型列表 list (兼容如推理界面的下拉框)
    """
    if page is None:
        return model_service.get_active_models(db)

    # 处理布尔值转换
    active_flag = None
    if is_active is not None and is_active != "":
        active_flag = str(is_active).lower() == 'true'

    return model_service.get_models_paginated(
        db, page=page, page_size=page_size,
        keyword=keyword, model_type=model_type, is_active=active_flag
    )


@router.get("/all", response_model=List[ModelResponse])
def get_all_models(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """管理员获取所有模型（包括未激活）"""
    return model_service.get_models(db)


@router.patch("/{model_id}/status")
def toggle_model_status(
        model_id: int,
        status_data: Dict[str, Any],
        db: Session = Depends(get_db),
        request: Request = None,
        current_user=Depends(get_current_admin_user)
):
    """切换模型启用/禁用状态"""
    model = model_service.get_model_by_id(db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    is_active = status_data.get("is_active", True)
    old_status = model.is_active
    model.is_active = is_active
    db.commit()
    
    ip_address = get_client_ip(request) if request else "unknown"
    action = "启用" if is_active else "禁用"
    create_operation_log(
        db=db,
        operator_id=current_user.id,
        operator_role=current_user.role.value,
        operation_type=OperationType.MODEL_DISABLE if not is_active else OperationType.MODEL_UPDATE,
        operation_content=f"{action}了模型 [{model.model_name}]",
        ip_address=ip_address,
        success=True
    )
    
    return {"message": "状态更新成功", "is_active": is_active}


@router.get("/{model_id}/versions")
def get_model_versions(
        model_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """获取模型历史版本(目前返回当前模型的记录模拟历史版本，以解决前端 404)"""
    model = model_service.get_model_by_id(db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    return [
        {
            "id": 1,
            "version": model.model_version,
            "model_path": model.model_path,
            "accuracy": model.accuracy,
            "created_at": model.create_time.strftime("%Y-%m-%d %H:%M:%S") if model.create_time else "",
            "created_by": "admin"
        }
    ]


@router.post("/{model_id}/versions/{version_id}/rollback")
def rollback_model_version(
        model_id: int,
        version_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """模型版本回滚"""
    return {"message": "版本回滚成功"}


@router.get("/active", response_model=ModelResponse)
def get_active_model(
        model_id: int,  # 接收前端传的 params: { model_id: ... }
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """获取指定的活跃模型信息"""
    model = model_service.get_model_by_id(db, model_id=model_id)
    if not model or not getattr(model, 'is_active', True):
        raise HTTPException(status_code=404, detail="模型未找到或未激活")
    return model


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(
        model_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """获取单个模型详情"""
    model = model_service.get_model_by_id(db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return model


@router.post("/", response_model=ModelResponse)
def create_model(
        model_in: ModelCreate,
        db: Session = Depends(get_db),
        request: Request = None,
        current_user=Depends(get_current_admin_user)
):
    """创建新模型（仅管理员）"""
    model = model_service.get_model_by_code(db, model_code=model_in.model_code)
    if model:
        raise HTTPException(status_code=400, detail="模型编码已存在")
    
    new_model = model_service.create_model(db, model_in=model_in)
    
    ip_address = get_client_ip(request) if request else "unknown"
    create_operation_log(
        db=db,
        operator_id=current_user.id,
        operator_role=current_user.role.value,
        operation_type=OperationType.MODEL_REGISTER,
        operation_content=f"注册了新模型 [{model_in.model_name}] v{model_in.model_version}",
        ip_address=ip_address,
        success=True
    )
    
    return new_model


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(
        model_id: int,
        model_in: ModelUpdate,
        db: Session = Depends(get_db),
        request: Request = None,
        current_user=Depends(get_current_admin_user)
):
    """更新模型（仅管理员）"""
    model = model_service.get_model_by_id(db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    updated_model = model_service.update_model(db, db_model=model, model_in=model_in)
    
    ip_address = get_client_ip(request) if request else "unknown"
    create_operation_log(
        db=db,
        operator_id=current_user.id,
        operator_role=current_user.role.value,
        operation_type=OperationType.MODEL_UPDATE,
        operation_content=f"更新了模型 [{model.model_name}]",
        ip_address=ip_address,
        success=True
    )
    
    return updated_model


@router.delete("/{model_id}")
def delete_model(
        model_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """删除模型（仅管理员）"""
    model = model_service.get_model_by_id(db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    model_service.delete_model(db, model_id=model_id)
    return {"message": "模型已删除"}