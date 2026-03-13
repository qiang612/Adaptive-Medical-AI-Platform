# backend/app/services/task_service.py
from app.models.inference_task import InferenceTask, TaskStatus
from app.models.model_registry import ModelRegistry
from app.schemas.task import TaskCreate
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import uuid
import os

# 这个导入保留在顶部即可
from app.services.inference_service import inference_service


class TaskService:
    def get_task_by_id(self, db: Session, task_id: int):
        return db.query(InferenceTask).filter(InferenceTask.id == task_id).first()

    def get_user_tasks(self, db: Session, user_id: int, status: str = None):
        """原有的获取所有任务方法（保留以防其他内部逻辑调用）"""
        query = db.query(InferenceTask).filter(InferenceTask.user_id == user_id)
        if status:
            query = query.filter(InferenceTask.status == status)
        return query.order_by(InferenceTask.created_at.desc()).all()

    def get_paginated_user_tasks(
            self, db: Session, user_id: int, page: int = 1, page_size: int = 10,
            keyword: str = None, model_id: int = None, status: str = None, risk_level: str = None
    ):
        """新增：支持分页、搜索、多条件过滤和联表查询模型名称的方法"""
        # 联表查询获取关联的 model_name
        query = db.query(InferenceTask, ModelRegistry.model_name) \
            .outerjoin(ModelRegistry, InferenceTask.model_id == ModelRegistry.id) \
            .filter(InferenceTask.user_id == user_id)

        # 状态及模型 ID 过滤
        if status:
            query = query.filter(InferenceTask.status == status)
        if model_id:
            query = query.filter(InferenceTask.model_id == model_id)

        # 关键词搜索过滤 (匹配 姓名、患者ID、任务ID)
        if keyword:
            query = query.filter(or_(
                InferenceTask.patient_name.ilike(f"%{keyword}%"),
                InferenceTask.patient_id.ilike(f"%{keyword}%"),
                InferenceTask.task_id.ilike(f"%{keyword}%")
            ))

        # 提取全部符合条件的任务进行处理
        all_results = query.order_by(InferenceTask.created_at.desc()).all()

        filtered_items = []
        for task, model_name in all_results:
            # 转换成字典以注入额外字段，供 Schema 解析
            task_dict = {c.name: getattr(task, c.name) for c in task.__table__.columns}
            task_dict["model_name"] = model_name or "未知模型"

            # 从 result 中动态提取 risk_level (风险等级)
            current_risk = None
            if task.result and isinstance(task.result, dict):
                current_risk = task.result.get("risk_level") or task.result.get("riskLevel") or task.result.get(
                    "风险等级")
            task_dict["risk_level"] = current_risk

            # 风险等级分类过滤 (在 Python 端过滤 JSON 里的数据更加稳妥)
            if risk_level and current_risk != risk_level:
                continue

            # 计算耗时 (秒)
            task_dict["duration"] = None
            if task.start_time and task.end_time:
                task_dict["duration"] = int((task.end_time - task.start_time).total_seconds())

            filtered_items.append(task_dict)

        total = len(filtered_items)

        # 内存分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = filtered_items[start_idx:end_idx]

        return {
            "total": total,
            "items": paginated_items
        }

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

    def batch_delete_tasks(self, db: Session, task_ids: list, user_id: int, role: str):
        """新增：批量删除任务，并同时删除对应的物理图片文件"""
        tasks = db.query(InferenceTask).filter(InferenceTask.id.in_(task_ids)).all()
        deleted_count = 0
        for task in tasks:
            # 验证权限，只允许删除自己的或管理员删除
            if task.user_id == user_id or role == "admin":
                # 删除物理图片文件
                if task.file_paths:
                    for file_path in task.file_paths:
                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except Exception as e:
                                print(f"清理图片失败: {e}")
                db.delete(task)
                deleted_count += 1
        db.commit()
        return deleted_count

    def get_model_by_id(self, db: Session, model_id: int):
        return db.query(ModelRegistry).filter(ModelRegistry.id == model_id).first()


# 创建单例
task_service = TaskService()