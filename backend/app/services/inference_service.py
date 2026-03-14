# backend/app/services/inference_service.py

from celery import shared_task
from app.core.config import settings
import importlib
import traceback
import sys
import socket  # 🔥 新增导入：用于获取当前物理机/容器的主机名 🔥

# 🔥 移除顶部的从 task_service 和 database 导入，避免循环依赖 🔥

class InferenceService:
    def run_inference(self, task_id: int):
        """执行推理任务"""
        # 🔥 延迟导入：把导入移到函数内部，只有当真正执行任务时才加载 🔥
        from app.services.task_service import task_service
        from app.core.database import SessionLocal

        # 每次执行异步任务时，由于是在独立的 Worker 进程中，需要重新创建一个独立的数据库会话
        db = SessionLocal()
        try:
            # 获取任务信息
            task = task_service.get_task_by_id(db, task_id=task_id)
            if not task:
                return

            # 👇 获取当前处理任务的机器/容器名称，并更新到数据库的 worker_name 字段 👇
            try:
                current_worker = socket.gethostname()
                task.worker_name = current_worker
                db.commit()
            except Exception as e:
                print(f"获取或更新 worker_name 失败: {e}")

            # 更新任务状态为处理中 (processing)
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

            # 动态加载并实例化 AI 适配器 (如 YOLOCervicalAdapter)
            try:
                if not hasattr(sys.stdout, 'encoding'):
                    sys.stdout.encoding = 'utf-8'
                if not hasattr(sys.stderr, 'encoding'):
                    sys.stderr.encoding = 'utf-8'
                # 假设你的数据库中 adapter_class 存的是类似 "app.ai_adapters.yolo_cervical_adapter.YOLOCervicalAdapter"
                module_name, class_name = model.model_path.rsplit('.', 1)
                module = importlib.import_module(module_name)
                adapter_class = getattr(module, class_name)
                adapter = adapter_class()

                # 执行真正的推理过程
                result = adapter.process(
                    input_data=task.input_data or {},
                    file_paths=task.file_paths or []
                )

                # 推理成功，更新任务状态为已完成 (completed) 并存入结果
                task_service.update_task_result(
                    db, task_id=task_id,
                    status="completed",
                    result=result
                )

            except Exception as e:
                # 捕获推理过程中的算法异常或路径错误
                error_msg = f"推理失败: {str(e)}\n{traceback.format_exc()}"
                task_service.update_task_status(
                    db, task_id=task_id,
                    status="failed",
                    error_msg=error_msg
                )
        finally:
            # 无论成功还是失败，都必须关闭数据库会话，防止连接池耗尽
            db.close()

# 创建单例实例，供 FastAPI 路由或本地其他地方调用
inference_service = InferenceService()


# ==========================================
# Celery 异步任务定义区
# ==========================================
# 🚀 关键修复：使用 shared_task 替代 celery_app.task
@shared_task(bind=True, name="run_inference_task", max_retries=3)
def run_inference_task(self, task_id: int):
    """
    接收来自 FastAPI 的任务派发。
    因为是在独立进程运行，所以只传递 task_id，其余数据全部在 run_inference 中现查库获取。
    """
    inference_service.run_inference(task_id)