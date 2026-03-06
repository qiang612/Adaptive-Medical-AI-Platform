from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.inference_service import inference_service

router = APIRouter(prefix="/inference", tags=["推理核心"])

@router.get("/status/{task_id}")
def get_task_status(task_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return inference_service.get_task_status(db, task_id=task_id, user_id=current_user.id)