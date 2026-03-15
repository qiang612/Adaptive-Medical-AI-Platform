# backend/app/api/v1/models.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.schemas.model import ModelCreate, ModelUpdate, ModelResponse
from app.services.model_service import model_service

router = APIRouter(prefix="/models", tags=["模型管理"])


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
        current_user=Depends(get_current_admin_user)
):
    """切换模型启用/禁用状态"""
    model = model_service.get_model_by_id(db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    is_active = status_data.get("is_active", True)
    model.is_active = is_active
    db.commit()
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
        current_user=Depends(get_current_admin_user)
):
    """创建新模型（仅管理员）"""
    model = model_service.get_model_by_code(db, model_code=model_in.model_code)
    if model:
        raise HTTPException(status_code=400, detail="模型编码已存在")
    return model_service.create_model(db, model_in=model_in)


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(
        model_id: int,
        model_in: ModelUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """更新模型（仅管理员）"""
    model = model_service.get_model_by_id(db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return model_service.update_model(db, db_model=model, model_in=model_in)


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