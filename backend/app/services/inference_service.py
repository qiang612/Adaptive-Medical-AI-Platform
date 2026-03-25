# backend/app/services/inference_service.py

from celery import shared_task
from app.core.config import settings
import importlib
import traceback
import sys
import socket
import json
import redis

from app.models.notification import Notification, NotificationType


def get_redis_client():
    redis_url = settings.REDIS_URL
    if redis_url.startswith('redis://'):
        redis_url = redis_url.replace('redis://', '')
    parts = redis_url.split('/')
    db = int(parts[1]) if len(parts) > 1 else 0
    host_port = parts[0].split(':')
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 6379
    return redis.Redis(host=host, port=port, db=db)


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

            user_id = task.user_id

            try:
                current_worker = socket.gethostname()
                task.worker_name = current_worker
                db.commit()
            except Exception as e:
                print(f"获取或更新 worker_name 失败: {e}")

            task_service.update_task_status(db, task_id=task_id, status="processing")
            self._send_ws_notification(user_id, task.task_id, "processing")

            model = task_service.get_model_by_id(db, model_id=task.model_id)
            if not model:
                task_service.update_task_status(
                    db, task_id=task_id,
                    status="failed",
                    error_msg="模型不存在"
                )
                self._send_ws_notification(user_id, task.task_id, "failed", {"error": "模型不存在"})
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

                self._send_ws_notification(user_id, task.task_id, "completed", result)

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
                self._send_ws_notification(user_id, task.task_id, "failed", {"error": str(e)})
        finally:
            db.close()

    def _send_ws_notification(self, user_id: int, task_id: str, status: str, result: dict = None):
        try:
            r = get_redis_client()
            message = json.dumps({
                "type": "task_update",
                "user_id": user_id,
                "task_id": task_id,
                "status": status,
                "result": result
            })
            r.publish(f"task_updates:{user_id}", message)
            r.publish("task_updates:all", message)
        except Exception as e:
            print(f"发送WebSocket通知失败: {e}")


inference_service = InferenceService()


@shared_task(bind=True, name="run_inference_task", max_retries=3)
def run_inference_task(self, task_id: int):
    inference_service.run_inference(task_id)