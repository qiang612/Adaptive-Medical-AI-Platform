# backend/app/services/inference_service.py

from celery import shared_task
from app.core.config import settings
import importlib
import traceback
import sys
import socket  # 🔥 新增导入：用于获取当前物理机/容器的主机名 🔥

# 🔥 新增导入：引入通知模型和枚举类型 🔥
from app.models.notification import Notification, NotificationType


# 🔥 移除顶部的从 task_service 和 database 导入，避免循环依赖 🔥

def _generate_clinical_advice(detections):
    """根据检测出的病灶类型动态生成详细的医学辅助建议"""
    if not detections:
        return "本次影像 AI 分析未检测到明显的典型病灶特征。建议结合患者的临床症状、既往病史以及其他生化指标进行综合判断。"

    class_counts = {}
    highest_conf = 0.0
    for d in detections:
        cls_name = d.get('class', '未知病灶')
        conf = d.get('confidence', 0.0)
        class_counts[cls_name] = class_counts.get(cls_name, 0) + 1
        if conf > highest_conf:
            highest_conf = conf

    advice = [
        f"【AI 影像分析汇总】\n本次检测共发现 {len(detections)} 个疑似病灶区域，最高 AI 置信度达到 {highest_conf * 100:.1f}%。"]

    for cls_name, count in class_counts.items():
        advice.append(f"【{cls_name}】相关特征 (共 {count} 处)：")
        cls_lower = cls_name.lower()

        # 针对平台的常见病种提供精细化的医学建议
        if 'asc' in cls_lower or 'ascus' in cls_lower:
            advice.append(
                "  - 临床参考：意义不明的非典型鳞状细胞。建议结合 HPV 检测结果进行分流。若高危型 HPV 阳性，建议行阴道镜检查及宫颈活检；若阴性，建议 6-12 个月后定期随访复查。")
        elif 'lsil' in cls_lower:
            advice.append(
                "  - 临床参考：低级别鳞状上皮内病变。提示可能存在 HPV 感染，建议结合患者年龄及病史，必要时进行阴道镜检查以明确病变范围和程度。")
        elif 'hsil' in cls_lower:
            advice.append(
                "  - 临床参考：高级别鳞状上皮内病变。癌前病变风险较高，强烈建议进行阴道镜下活检，并根据组织病理学结果考虑进一步的临床干预（如 LEEP 刀或冷刀锥切）。")
        elif '结节' in cls_lower or 'nodule' in cls_lower:
            advice.append(
                "  - 临床参考：疑似肺部结节。建议结合患者吸烟史、肿瘤家族史等高危因素。若是实性结节且直径 >8mm，需结合增强 CT 或活检进一步评估；微小结节建议遵医嘱定期复查随访。")
        elif '斑块' in cls_lower or 'plaque' in cls_lower:
            advice.append(
                "  - 临床参考：疑似血管斑块。提示存在动脉粥样硬化风险，建议结合患者血脂（特别是 LDL-C）、血压水平综合评估，必要时进行生活方式干预或启动他汀类药物治疗。")
        else:
            advice.append(
                f"  - 临床参考：AI 提示该区域形态学存在异常。请主治医师结合患者实际临床症状及相关检验结果进行人工仔细阅片复核。")

    advice.append("【综合干预提示】")
    advice.append("1. 以上结果为 AI 基于影像形态学特征提取的辅助分析，仅供临床参考，并非最终诊断结论。")
    advice.append("2. 建议以患者为中心，开展多模态数据（影像+检验+病史）的综合评估，制定个性化诊疗方案。")

    return "\n".join(advice)


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

                # 🔥 新增逻辑：根据图像检测结果自动生成详细的辅助诊断建议 🔥
                if 'detections' in result:
                    result['image_analysis'] = _generate_clinical_advice(result['detections'])

                # 推理成功，更新任务状态为已完成 (completed) 并存入结果
                task_service.update_task_result(
                    db, task_id=task_id,
                    status="completed",
                    result=result
                )

                # ==========================================
                # 🔥 新增逻辑：在任务完成后，向数据库写入通知消息
                # ==========================================
                try:
                    patient_info = task.patient_name or "未知患者"
                    new_notice = Notification(
                        doctor_id=task.user_id,  # 注意：InferenceTask 表里存的是 user_id
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