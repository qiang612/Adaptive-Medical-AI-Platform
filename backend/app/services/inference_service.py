# backend/app/services/inference_service.py
from celery import shared_task
from app.core.celery_app import celery_app
from app.core.config import settings
import importlib
import traceback


# 🔥 移除顶部的 from app.services.task_service import task_service 🔥

class InferenceService:
    def run_inference(self, task_id: int):
        """执行推理任务"""
        # 🔥 延迟导入：把导入移到函数内部 🔥
        from app.services.task_service import task_service
        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            # 获取任务信息
            task = task_service.get_task_by_id(db, task_id=task_id)
            if not task:
                return

            # 更新任务状态为处理中
            task_service.update_task_status(db, task_id=task_id, status="processing")

            # 获取模型信息
            model = task_service.get_model_by_id(db, model_id=task.model_id)
            if not model:
                task_service.update_task_status(
                    db, task_id=task_id,
                    status="failed",
                    error_msg="模型不存在"
                )
                return

            # 动态加载适配器
            try:
                module_name, class_name = model.adapter_class.rsplit('.', 1)
                module = importlib.import_module(module_name)
                adapter_class = getattr(module, class_name)
                adapter = adapter_class()

                # 执行推理
                result = adapter.run(
                    input_data=task.input_data or {},
                    file_paths=task.file_paths or []
                )

                # 更新任务结果
                task_service.update_task_result(
                    db, task_id=task_id,
                    status="completed",
                    result=result
                )

            except Exception as e:
                # 捕获推理过程中的异常
                error_msg = f"推理失败: {str(e)}\n{traceback.format_exc()}"
                task_service.update_task_status(
                    db, task_id=task_id,
                    status="failed",
                    error_msg=error_msg
                )
        finally:
            db.close()


# 创建单例
inference_service = InferenceService()


# Celery 任务
@celery_app.task(bind=True, max_retries=3)
def run_inference_task(self, task_id: int):
    inference_service.run_inference(task_id)