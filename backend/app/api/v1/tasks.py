# backend/app/api/v1/tasks.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse
from app.services.task_service import task_service
from app.services.inference_service import run_inference_task

router = APIRouter(prefix="/tasks", tags=["推理任务"])

# 供批量删除接收 JSON 请求体使用
class BatchDeleteRequest(BaseModel):
    ids: List[int]


@router.get("/", response_model=TaskListResponse)
def get_user_tasks(
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
        model_id: Optional[int] = None,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """获取当前用户的任务列表（全面支持分页、搜索、分类等）"""
    return task_service.get_paginated_user_tasks(
        db, user_id=current_user.id, page=page, page_size=page_size,
        keyword=keyword, model_id=model_id, status=status, risk_level=risk_level
    )


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

    # 解析输入数据（JSON字符串转字典）
    import json
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
        file_paths=file_paths
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


# 下载报告接口（之前添加的）
@router.get("/{task_id}/download-report")
async def download_report(
        task_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    from fastapi.responses import FileResponse
    from app.utils.report_generator import MedicalReportGenerator
    import uuid

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