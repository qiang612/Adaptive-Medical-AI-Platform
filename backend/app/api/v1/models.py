# backend/app/api/v1/models.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.schemas.model import ModelCreate, ModelUpdate, ModelResponse
from app.services.model_service import model_service

router = APIRouter(prefix="/models", tags=["模型管理"])

@router.get("/", response_model=list[ModelResponse])
def get_active_models(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """获取所有激活的模型"""
    return model_service.get_active_models(db)

@router.get("/all", response_model=list[ModelResponse])
def get_all_models(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """管理员获取所有模型（包括未激活）"""
    return model_service.get_all_models(db)

@router.get("/{model_id}", response_model=ModelResponse)
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
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
    current_user = Depends(get_current_admin_user)
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
    current_user = Depends(get_current_admin_user)
):
    """更新模型（仅管理员）"""
    model = model_service.get_model_by_id(db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return model_service.update_model(db, model=model, model_in=model_in)

@router.delete("/{model_id}")
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """删除模型（仅管理员）"""
    model = model_service.get_model_by_id(db, model_id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    model_service.delete_model(db, model_id=model_id)
    return {"message": "模型已删除"}