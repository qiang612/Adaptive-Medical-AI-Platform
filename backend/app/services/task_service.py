# backend/app/services/task_service.py
from app.models.inference_task import InferenceTask, TaskStatus
from app.models.model_registry import ModelRegistry
from app.schemas.task import TaskCreate
from app.core.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

# 这个导入保留在顶部即可
from app.services.inference_service import inference_service


class TaskService:
    def get_task_by_id(self, db: Session, task_id: int):
        return db.query(InferenceTask).filter(InferenceTask.id == task_id).first()

    def get_user_tasks(self, db: Session, user_id: int, status: str = None):
        query = db.query(InferenceTask).filter(InferenceTask.user_id == user_id)
        if status:
            query = query.filter(InferenceTask.status == status)
        return query.order_by(InferenceTask.created_at.desc()).all()

    def create_task(self, db: Session, task_in: TaskCreate, user_id: int, file_paths: list = []):
        task_id_str = str(uuid.uuid4())
        db_task = InferenceTask(
            task_id=task_id_str,
            model_id=task_in.model_id,
            user_id=user_id,
            patient_name=task_in.patient_name,
            patient_id=task_in.patient_id,
            input_data=task_in.input_data,
            file_paths=file_paths,
            status=TaskStatus.PENDING,
            start_time=datetime.now()
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    def update_task_status(self, db: Session, task_id: int, status: str, error_msg: str = None):
        task = self.get_task_by_id(db, task_id=task_id)
        if task:
            task.status = TaskStatus(status)
            if error_msg:
                task.error_msg = error_msg
            if status in ["completed", "failed"]:
                task.end_time = datetime.now()
            db.commit()
            db.refresh(task)
        return task

    def update_task_result(self, db: Session, task_id: int, status: str, result: dict):
        task = self.get_task_by_id(db, task_id=task_id)
        if task:
            task.status = TaskStatus(status)
            task.result = result
            task.end_time = datetime.now()
            db.commit()
            db.refresh(task)
        return task

    def delete_task(self, db: Session, task_id: int):
        task = self.get_task_by_id(db, task_id=task_id)
        if task:
            db.delete(task)
            db.commit()
        return True

    def get_model_by_id(self, db: Session, model_id: int):
        return db.query(ModelRegistry).filter(ModelRegistry.id == model_id).first()


# 创建单例
task_service = TaskService()