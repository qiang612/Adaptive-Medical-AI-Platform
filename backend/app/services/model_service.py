from sqlalchemy.orm import Session
from app.models.model_registry import ModelRegistry
from app.schemas.model import ModelCreate, ModelUpdate

class ModelService:
    def get_model_by_id(self, db: Session, model_id: int):
        return db.query(ModelRegistry).filter(ModelRegistry.id == model_id).first()

    def get_model_by_code(self, db: Session, model_code: str):
        return db.query(ModelRegistry).filter(ModelRegistry.model_code == model_code).first()

    def get_models(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(ModelRegistry).offset(skip).limit(limit).all()

    def get_active_models(self, db: Session):
        return db.query(ModelRegistry).filter(ModelRegistry.is_active == True).all()

    def create_model(self, db: Session, model_in: ModelCreate):
        db_model = ModelRegistry(**model_in.model_dump())
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model

    def update_model(self, db: Session, db_model: ModelRegistry, model_in: ModelUpdate):
        update_data = model_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_model, field, value)
        db.commit()
        db.refresh(db_model)
        return db_model

model_service = ModelService()