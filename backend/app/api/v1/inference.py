# backend/app/api/v1/inference.py
from fastapi import APIRouter, Depends, Body, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import Response
from datetime import datetime
import uuid
import os

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.services.inference_service import inference_service, run_inference_task
from app.services.task_service import task_service
from app.models.model_registry import ModelRegistry
from app.models.inference_task import InferenceTask, TaskStatus
from app.models.operation_log import OperationLog, OperationType, UserRole as OpUserRole
from app.schemas.task import TaskCreate

router = APIRouter(prefix="/inference", tags=["推理核心"])


def get_client_ip(request: Request) -> str:
    """获取客户端真实IP"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def create_operation_log(db: Session, operator_id: int, operator_role: str, 
                         operation_type: OperationType, operation_content: str,
                         ip_address: str, success: bool = True, error_msg: str = None):
    """创建操作日志"""
    log = OperationLog(
        operator_id=operator_id,
        operator_role=OpUserRole.ADMIN if operator_role == "admin" else OpUserRole.DOCTOR,
        operation_type=operation_type,
        operation_content=operation_content,
        ip_address=ip_address,
        success=success,
        error_msg=error_msg,
        operation_time=datetime.now()
    )
    db.add(log)
    db.commit()


@router.get("/status/{task_id}")
def get_task_status(task_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return inference_service.get_task_status(db, task_id=task_id, user_id=current_user.id)


@router.post("/batch")
def batch_inference(req: dict = Body(...), db: Session = Depends(get_db), 
                    request: Request = None, current_user=Depends(get_current_user)):
    """
    批量多模型对比推理接口
    为每个选中的模型创建独立的Celery异步任务，支持前端轮询状态
    """
    model_ids = req.get("model_ids", [])
    patient_info = req.get("patient_info", {})
    clinical_data = req.get("clinical_data", {})
    file_ids = req.get("files", [])

    if not model_ids or len(model_ids) < 2:
        raise HTTPException(status_code=400, detail="请至少选择2个模型进行对比")

    batch_id = str(uuid.uuid4())[:8]
    created_tasks = []
    
    ip_address = get_client_ip(request) if request else "unknown"
    model_names = []

    for m_id in model_ids:
        model = db.query(ModelRegistry).filter(ModelRegistry.id == m_id).first()
        if not model:
            continue

        if not model.is_active:
            continue
        
        model_names.append(model.model_name)

        task_id_str = str(uuid.uuid4())
        
        file_paths = []
        if file_ids:
            from app.models.upload_file import UploadFile
            upload_files = db.query(UploadFile).filter(UploadFile.id.in_(file_ids)).all()
            file_paths = [f.file_path for f in upload_files if f.file_path]

        input_data = {
            "patient_name": patient_info.get("name", ""),
            "patient_id": patient_info.get("patient_id", ""),
            "gender": patient_info.get("gender", ""),
            "age": patient_info.get("age"),
            **clinical_data
        }

        db_task = InferenceTask(
            task_id=task_id_str,
            model_id=m_id,
            user_id=current_user.id,
            patient_name=patient_info.get("name", ""),
            patient_id=patient_info.get("patient_id", ""),
            input_data=input_data,
            file_paths=file_paths if file_paths else None,
            status=TaskStatus.PENDING,
            start_time=datetime.now()
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        run_inference_task.delay(db_task.id)

        created_tasks.append({
            "task_id": task_id_str,
            "db_task_id": db_task.id,
            "model_id": m_id,
            "model_name": model.model_name,
            "status": "pending"
        })

    if created_tasks:
        patient_name = patient_info.get("name", "未知患者")
        create_operation_log(
            db=db,
            operator_id=current_user.id,
            operator_role=current_user.role.value,
            operation_type=OperationType.TASK_SUBMIT,
            operation_content=f"提交了批量推理任务，患者: {patient_name}，模型: {', '.join(model_names)}",
            ip_address=ip_address,
            success=True
        )

    return {
        "code": 200,
        "message": "批量推理任务已提交",
        "batch_id": batch_id,
        "total_tasks": len(created_tasks),
        "tasks": created_tasks
    }


@router.get("/batch/{batch_id}/status")
def get_batch_status(
    batch_id: str,
    task_ids: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    查询批量推理任务状态
    通过task_ids参数传入任务ID列表（逗号分隔）
    """
    if not task_ids:
        return {"code": 200, "tasks": [], "all_completed": False}

    task_id_list = [t.strip() for t in task_ids.split(",") if t.strip()]
    
    tasks = db.query(InferenceTask).filter(
        InferenceTask.task_id.in_(task_id_list),
        InferenceTask.user_id == current_user.id
    ).all()

    results = []
    all_completed = True
    completed_count = 0

    for task in tasks:
        model = db.query(ModelRegistry).filter(ModelRegistry.id == task.model_id).first()
        model_name = model.model_name if model else "未知模型"

        task_result = {
            "task_id": task.task_id,
            "model_id": task.model_id,
            "model_name": model_name,
            "status": task.status.value if hasattr(task.status, 'value') else str(task.status)
        }

        if task.status == TaskStatus.COMPLETED and task.result:
            result_data = task.result
            task_result.update({
                "risk_level": result_data.get("risk_level", "未知"),
                "risk_score": result_data.get("risk_score", 0),
                "confidence": result_data.get("confidence", 0.85),
                "duration": int((task.end_time - task.start_time).total_seconds()) if task.end_time and task.start_time else 0,
                "diagnosis_summary": result_data.get("conclusion") or result_data.get("diagnosis_summary", ""),
                "primary_diagnosis": result_data.get("primary_diagnosis", "待临床确认"),
                "recommendation": result_data.get("recommendation", "建议结合医生经验进一步复查"),
                "findings": result_data.get("findings", []),
                "original_image": result_data.get("original_image"),
                "annotated_image": result_data.get("annotated_image"),
                "detections": result_data.get("detections", []),
                "image_analysis": result_data.get("image_analysis", "")
            })
            completed_count += 1
        elif task.status == TaskStatus.FAILED:
            task_result["error_msg"] = task.error_msg
            completed_count += 1
        else:
            all_completed = False

        results.append(task_result)

    return {
        "code": 200,
        "tasks": results,
        "completed_count": completed_count,
        "total_count": len(task_id_list),
        "all_completed": all_completed
    }


@router.get("/batch/{batch_id}/results")
def get_batch_results(
    batch_id: str,
    task_ids: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    获取批量推理的最终结果（用于前端展示对比结果）
    """
    if not task_ids:
        return {"code": 200, "results": []}

    task_id_list = [t.strip() for t in task_ids.split(",") if t.strip()]
    
    tasks = db.query(InferenceTask).filter(
        InferenceTask.task_id.in_(task_id_list),
        InferenceTask.user_id == current_user.id
    ).all()

    results = []
    for task in tasks:
        model = db.query(ModelRegistry).filter(ModelRegistry.id == task.model_id).first()
        model_name = model.model_name if model else "未知模型"

        if task.status == TaskStatus.COMPLETED and task.result:
            result_data = task.result
            results.append({
                "model_id": task.model_id,
                "model_name": model_name,
                "status": "completed",
                "risk_level": result_data.get("risk_level", "未知"),
                "risk_score": result_data.get("risk_score", 0),
                "confidence": result_data.get("confidence", 0.85),
                "duration": int((task.end_time - task.start_time).total_seconds()) if task.end_time and task.start_time else 0,
                "diagnosis_summary": result_data.get("conclusion") or result_data.get("diagnosis_summary", f"基于 {model_name} 的算法分析完成"),
                "primary_diagnosis": result_data.get("primary_diagnosis", "待临床确认"),
                "recommendation": result_data.get("recommendation", "建议结合医生经验进一步复查"),
                "findings": result_data.get("findings", ["AI分析完成"]),
                "original_image": result_data.get("original_image"),
                "annotated_image": result_data.get("annotated_image"),
                "detections": result_data.get("detections", []),
                "image_analysis": result_data.get("image_analysis", "")
            })

    return {"code": 200, "message": "success", "results": results}


@router.post("/export-compare")
def export_compare_report(req: dict = Body(...), current_user=Depends(get_current_user)):
    """
    导出多模型对比报告 PDF
    """
    # 模拟生成一个最小的有效 PDF 文件流返回给前端下载
    pdf_content = b"%PDF-1.4\n%Dummy PDF for Model Compare Report Export\n"
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=compare_report.pdf"}
    )