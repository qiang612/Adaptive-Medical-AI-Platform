# backend/app/api/v1/system.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user  # 如果有 get_current_admin_user 可以用那个
from app.models.system import SystemConfig, NoticeTemplate
from app.schemas.system import NoticeTemplateCreate, NoticeTemplateUpdate, NoticeTemplateResponse, EmailTestRequest

router = APIRouter(prefix="/system", tags=["系统设置"])


def _get_config_value(db: Session, key: str) -> dict:
    cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    return cfg.value if cfg else {}


def _update_config_value(db: Session, key: str, value: dict):
    cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if cfg:
        cfg.value = value
    else:
        cfg = SystemConfig(key=key, value=value)
        db.add(cfg)
    db.commit()


# ==================== 1. 全局与邮件配置 ====================
@router.get("/config")
def get_system_config(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return {
        "global": _get_config_value(db, "global"),
        "email": _get_config_value(db, "email")
    }


@router.put("/config")
def update_system_config(data: Dict[str, Any], db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # 区分是保存邮件配置还是全局配置
    if "email" in data and isinstance(data["email"], dict):
        _update_config_value(db, "email", data["email"])
    else:
        _update_config_value(db, "global", data)
    return {"message": "配置保存成功"}


# ==================== 2. 存储引擎配置 ====================
@router.get("/storage-config")
def get_storage_config(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return _get_config_value(db, "storage")


@router.put("/storage-config")
def update_storage_config(data: Dict[str, Any], db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _update_config_value(db, "storage", data)
    return {"message": "存储配置保存成功"}


# ==================== 3. 通知模板管理 ====================
@router.get("/notice-templates", response_model=List[NoticeTemplateResponse])
def get_notice_templates(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(NoticeTemplate).order_by(NoticeTemplate.id.desc()).all()


@router.post("/notice-templates", response_model=NoticeTemplateResponse)
def create_notice_template(data: NoticeTemplateCreate, db: Session = Depends(get_db),
                           current_user=Depends(get_current_user)):
    # 检查编码是否冲突
    if db.query(NoticeTemplate).filter(NoticeTemplate.template_code == data.template_code).first():
        raise HTTPException(status_code=400, detail="模板编码已存在")

    tmpl = NoticeTemplate(**data.dict())
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return tmpl


@router.put("/notice-templates/{tmpl_id}", response_model=NoticeTemplateResponse)
def update_notice_template(tmpl_id: int, data: NoticeTemplateUpdate, db: Session = Depends(get_db),
                           current_user=Depends(get_current_user)):
    tmpl = db.query(NoticeTemplate).filter(NoticeTemplate.id == tmpl_id).first()
    if not tmpl:
        raise HTTPException(status_code=404, detail="模板未找到")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(tmpl, key, value)

    db.commit()
    db.refresh(tmpl)
    return tmpl


@router.delete("/notice-templates/{tmpl_id}")
def delete_notice_template(tmpl_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tmpl = db.query(NoticeTemplate).filter(NoticeTemplate.id == tmpl_id).first()
    if not tmpl:
        raise HTTPException(status_code=404, detail="模板未找到")

    db.delete(tmpl)
    db.commit()
    return {"message": "模板删除成功"}


# ==================== 4. 测试发送邮件 ====================
@router.post("/test-email")
def test_email_notice(data: EmailTestRequest, current_user=Depends(get_current_user)):
    # 这里仅做模拟占位，后续可接入真实的 SMTP 推送逻辑
    return {"message": f"测试邮件任务已生成，目标邮箱：{data.to_email}"}