from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.model_registry import ModelRegistry
from app.schemas.model import ModelCreate, ModelUpdate


class ModelService:
    def get_model_by_id(self, db: Session, model_id: int):
        return db.query(ModelRegistry).filter(ModelRegistry.id == model_id).first()

    def get_model_by_code(self, db: Session, model_code: str):
        return db.query(ModelRegistry).filter(ModelRegistry.model_code == model_code).first()

    def get_models(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(ModelRegistry).offset(skip).limit(limit).all()

    def get_models_paginated(self, db: Session, page: int, page_size: int, keyword: str = None, model_type: str = None,
                             is_active: bool = None):
        """支持分页、关键词搜索、状态与类型过滤的模型查询"""
        query = db.query(ModelRegistry)

        if keyword:
            query = query.filter(or_(
                ModelRegistry.model_name.ilike(f"%{keyword}%"),
                ModelRegistry.model_code.ilike(f"%{keyword}%")
            ))
        if model_type:
            query = query.filter(ModelRegistry.model_type == model_type)

        if is_active is not None:
            # 兼容前端传参可能为字符串或布尔值
            if str(is_active).lower() == 'true' or is_active is True:
                query = query.filter(ModelRegistry.is_active == True)
            elif str(is_active).lower() == 'false' or is_active is False:
                query = query.filter(ModelRegistry.is_active == False)

        total = query.count()
        # 按照创建时间倒序排列，最新创建的在最前面
        items = query.order_by(ModelRegistry.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "total": total,
            "items": items
        }

    def get_active_models(self, db: Session):
        return db.query(ModelRegistry).filter(ModelRegistry.is_active == True).all()

    def create_model(self, db: Session, model_in: ModelCreate):
        # 排除 auc 字段，因为它是前端为了展示兼容加的，不一定在数据库模型中存在
        model_data = model_in.model_dump(exclude={"auc"})
        db_model = ModelRegistry(**model_data)
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model

    def update_model(self, db: Session, db_model: ModelRegistry, model_in: ModelUpdate):
        update_data = model_in.model_dump(exclude_unset=True)

        # 排除数据库中不存在的 auc 字段以防报错
        if "auc" in update_data and not hasattr(db_model, "auc"):
            update_data.pop("auc")

        for field, value in update_data.items():
            setattr(db_model, field, value)
        db.commit()
        db.refresh(db_model)
        return db_model

    def delete_model(self, db: Session, model_id: int):
        """删除指定模型"""
        model = self.get_model_by_id(db, model_id)
        if model:
            db.delete(model)
            db.commit()


model_service = ModelService()