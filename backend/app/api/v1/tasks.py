# backend/app/api/v1/tasks.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
import uuid
import os
import json
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse
from app.services.task_service import task_service
from app.services.inference_service import run_inference_task

# 补充缺失的模型引入
from app.models.inference_task import InferenceTask
from app.models.model_registry import ModelRegistry
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["推理任务"])


# 供批量删除接收 JSON 请求体使用
class BatchDeleteRequest(BaseModel):
    ids: List[int]


@router.get("/", response_model=TaskListResponse)
def get_user_tasks(
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
        model_id: Optional[str] = None,  # 接收前端可能传来的空字符串 ""
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """获取当前用户的任务列表（全面支持分页、搜索、分类等）"""

    # 过滤空字符串 "" 并进行类型转换
    valid_model_id = int(model_id) if model_id and model_id.isdigit() else None
    valid_keyword = keyword if keyword and keyword.strip() else None
    valid_status = status if status and status.strip() else None
    valid_risk = risk_level if risk_level and risk_level.strip() else None

    return task_service.get_paginated_user_tasks(
        db, user_id=current_user.id, page=page, page_size=page_size,
        keyword=valid_keyword, model_id=valid_model_id, status=valid_status, risk_level=valid_risk
    )


# ======================================================================
# 注意：以下所有的静态路由（/queue-stats, /workers, /all），都必须放在 @router.get("/{task_id}") 前面
# ======================================================================

@router.get("/queue-stats")
def get_task_queue_stats(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """管理员：获取任务队列统计"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权访问")

    # 按状态分组统计任务数量
    stats = db.query(InferenceTask.status, func.count(InferenceTask.id)).group_by(InferenceTask.status).all()
    stat_dict = {status: count for status, count in stats}

    return {
        "pending": stat_dict.get("pending", 0),
        "processing": stat_dict.get("processing", 0),
        "completed": stat_dict.get("completed", 0),
        "failed": stat_dict.get("failed", 0)
    }


@router.get("/workers")
def get_worker_nodes(current_user=Depends(get_current_user)):
    """管理员：获取 Worker 计算节点集群状态"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权访问")

    # 如果平台暂未接入真实的 Celery 集群状态监控，先返回兜底的模拟监控数据以保证前端正常渲染
    return [
        {
            "id": "node-1",
            "worker_name": "GPU-Worker-01",
            "is_online": True,
            "hostname": "192.168.1.101",
            "model_names": ["LungNodule_YOLO", "Cervical_UNet"],
            "current_task_id": None,
            "cpu_usage": 45,
            "memory_usage": 68,
            "processed_count": 342,
            "last_heartbeat": "刚刚"
        },
        {
            "id": "node-2",
            "worker_name": "CPU-Worker-02",
            "is_online": True,
            "hostname": "192.168.1.102",
            "model_names": ["CHD_MLP"],
            "current_task_id": None,
            "cpu_usage": 20,
            "memory_usage": 40,
            "processed_count": 156,
            "last_heartbeat": "刚刚"
        }
    ]


@router.get("/all")
def get_all_tasks_for_admin(
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
        model_id: Optional[str] = None,  # 接收前端可能传来的空字符串 ""
        status: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """管理员：获取平台全局诊断任务队列"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权访问")

    # 联表查询，关联模型表获取 model_name，关联用户表获取医生真实姓名(doctor_name)
    query = db.query(InferenceTask, ModelRegistry.model_name, User.full_name.label("doctor_name")) \
        .outerjoin(ModelRegistry, InferenceTask.model_id == ModelRegistry.id) \
        .outerjoin(User, InferenceTask.user_id == User.id)

    # 过滤空字符串 "" 判断
    if status and status.strip():
        query = query.filter(InferenceTask.status == status)
    if model_id and model_id.isdigit():
        query = query.filter(InferenceTask.model_id == int(model_id))
    if keyword and keyword.strip():
        query = query.filter(or_(
            InferenceTask.patient_name.ilike(f"%{keyword}%"),
            InferenceTask.patient_id.ilike(f"%{keyword}%"),
            InferenceTask.task_id.ilike(f"%{keyword}%")
        ))

    all_results = query.order_by(InferenceTask.created_at.desc()).all()

    filtered_items = []
    for task, model_name, doctor_name in all_results:
        # 转换为字典
        task_dict = {c.name: getattr(task, c.name) for c in task.__table__.columns}
        task_dict["model_name"] = model_name or "未知模型"
        task_dict["doctor_name"] = doctor_name or "未知医生"

        # 👇 补充前端需要的 worker_name 给处理节点列显示 👇
        if hasattr(task, 'worker_name') and task.worker_name:
            task_dict["worker_name"] = task.worker_name
        else:
            if task.status in ["processing", "completed"]:
                task_dict["worker_name"] = "GPU-Worker-01"  # 模拟节点
            elif task.status == "failed":
                task_dict["worker_name"] = "CPU-Worker-02"  # 模拟节点
            else:
                task_dict["worker_name"] = None

        # 补充前端需要的耗时字段
        task_dict["duration"] = None
        if task.start_time and task.end_time:
            task_dict["duration"] = int((task.end_time - task.start_time).total_seconds())

        filtered_items.append(task_dict)

    # 内存分页
    total = len(filtered_items)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = filtered_items[start_idx:end_idx]

    return {
        "total": total,
        "items": paginated_items
    }


# ======================================================================
# 动态路由 ({task_id}) 放在最下方，防止拦截
# ======================================================================

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """获取单个任务详情"""
    task = task_service.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权访问该任务")
    return task


@router.post("/", response_model=TaskResponse)
async def create_task(
        model_id: int = Form(...),
        patient_name: Optional[str] = Form(None),
        patient_id: Optional[str] = Form(None),
        input_data: Optional[str] = Form(None),  # JSON字符串
        files: List[UploadFile] = File([]),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """创建推理任务（支持文件上传）"""
    # 处理文件上传
    file_paths = []
    file_infos = []  # 🔥 新增：收集原文件信息供数据库记录
    for file in files:
        if file.filename:
            # 生成唯一文件名
            file_ext = os.path.splitext(file.filename)[-1]
            filename = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join(settings.UPLOAD_DIR, "images", filename)

            # 保存文件
            with open(file_path, "wb") as f:
                f.write(await file.read())
            file_paths.append(file_path)

            # 🔥 新增：将原始文件名和路径存入 file_infos，传给 service 层
            file_infos.append({
                "file_name": file.filename,
                "file_path": file_path
            })

    # 解析输入数据（JSON字符串转字典）
    input_data_dict = {}
    if input_data:
        try:
            input_data_dict = json.loads(input_data)
        except:
            raise HTTPException(status_code=400, detail="input_data 格式错误，需为JSON字符串")

    # 创建任务
    task_in = TaskCreate(
        model_id=model_id,
        patient_name=patient_name,
        patient_id=patient_id,
        input_data=input_data_dict
    )
    task = task_service.create_task(
        db,
        task_in=task_in,
        user_id=current_user.id,
        file_paths=file_paths,
        file_infos=file_infos  # 🔥 新增：把收集好的文件详情传给下层
    )

    # 异步执行推理任务
    run_inference_task.delay(task.id)

    return task


@router.delete("/batch")
def batch_delete_tasks(
        req: BatchDeleteRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """批量删除任务（前端单删和批量删都调用此接口）"""
    deleted_count = task_service.batch_delete_tasks(
        db, task_ids=req.ids, user_id=current_user.id, role=current_user.role
    )
    return {"message": f"成功删除 {deleted_count} 个任务"}


@router.delete("/{task_id}")
def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """删除任务（仅自己或管理员）"""
    task = task_service.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除该任务")

    # 删除关联文件
    if task.file_paths:
        for file_path in task.file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

    task_service.delete_task(db, task_id=task_id)
    return {"message": "任务已删除"}


# 下载报告接口
@router.get("/{task_id}/download-report")
async def download_report(
        task_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    from fastapi.responses import FileResponse
    from app.utils.report_generator import MedicalReportGenerator

    task = task_service.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权访问")
    if not task.result:
        raise HTTPException(status_code=400, detail="任务未完成，无法生成报告")

    # 生成PDF
    report_filename = f"诊断报告_{task.patient_name or '未知'}_{uuid.uuid4().hex}.pdf"
    report_path = os.path.join(settings.UPLOAD_DIR, "reports", report_filename)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    generator = MedicalReportGenerator(task, task.result)
    generator.generate(report_path)

    return FileResponse(
        path=report_path,
        filename=report_filename,
        media_type='application/pdf'
    )


@router.post("/{task_id}/retry")
def retry_failed_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """管理员重试失败任务"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权操作")

    task = task_service.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task_service.update_task_status(db, task_id=task_id, status="pending", error_msg=None)
    run_inference_task.delay(task.id)  # 重新抛入 Celery
    return {"message": "任务已重新提交"}


@router.post("/{task_id}/terminate")
def terminate_running_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """管理员终止处理中的任务"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权操作")

    task = task_service.get_task_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task_service.update_task_status(db, task_id=task_id, status="failed", error_msg="已被管理员强制终止")
    return {"message": "任务已终止"}