# backend/app/services/inference_service.py

from celery import shared_task
from app.core.config import settings
import importlib
import traceback
import sys
import socket

from app.models.notification import Notification, NotificationType


class InferenceService:
    def run_inference(self, task_id: int):
        """执行推理任务"""
        from app.services.task_service import task_service
        from app.core.database import SessionLocal

        db = SessionLocal()
        try:
            task = task_service.get_task_by_id(db, task_id=task_id)
            if not task:
                return

            try:
                current_worker = socket.gethostname()
                task.worker_name = current_worker
                db.commit()
            except Exception as e:
                print(f"获取或更新 worker_name 失败: {e}")

            task_service.update_task_status(db, task_id=task_id, status="processing")

            model = task_service.get_model_by_id(db, model_id=task.model_id)
            if not model:
                task_service.update_task_status(
                    db, task_id=task_id,
                    status="failed",
                    error_msg="模型不存在"
                )
                return

            try:
                if not hasattr(sys.stdout, 'encoding'):
                    sys.stdout.encoding = 'utf-8'
                if not hasattr(sys.stderr, 'encoding'):
                    sys.stderr.encoding = 'utf-8'
                module_name, class_name = model.model_path.rsplit('.', 1)
                module = importlib.import_module(module_name)
                adapter_class = getattr(module, class_name)
                adapter = adapter_class()

                result = adapter.process(
                    input_data=task.input_data or {},
                    file_paths=task.file_paths or []
                )

                if 'detections' in result and 'image_analysis' not in result:
                    result['image_analysis'] = adapter.generate_clinical_advice(result)

                task_service.update_task_result(
                    db, task_id=task_id,
                    status="completed",
                    result=result
                )

                try:
                    patient_info = task.patient_name or "未知患者"
                    new_notice = Notification(
                        doctor_id=task.user_id,
                        title="任务完成通知",
                        content=f"您提交的【{patient_info}】病例检测任务已完成，请点击查看详细报告。",
                        notification_type=NotificationType.TASK_COMPLETE,
                        related_task_id=task.id
                    )
                    db.add(new_notice)
                    db.commit()
                except Exception as notice_err:
                    print(f"写入通知记录失败: {str(notice_err)}")

            except Exception as e:
                error_msg = f"推理失败: {str(e)}\n{traceback.format_exc()}"
                task_service.update_task_status(
                    db, task_id=task_id,
                    status="failed",
                    error_msg=error_msg
                )
        finally:
            db.close()


inference_service = InferenceService()


@shared_task(bind=True, name="run_inference_task", max_retries=3)
def run_inference_task(self, task_id: int):
    """
    接收来自 FastAPI 的任务派发。
    因为是在独立进程运行，所以只传递 task_id，其余数据全部在 run_inference 中现查库获取。
    """
    inference_service.run_inference(task_id)