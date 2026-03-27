from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import io
import csv
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.models.operation_log import OperationLog, OperationType
from app.models.inference_task import InferenceTask, TaskStatus
from app.models.login_log import LoginLog
from app.models.user import User

router = APIRouter(tags=["Logs"])


class BatchDeleteRequest(BaseModel):
    ids: List[int]


def apply_time_filter(query, model_column, start_time: str, end_time: str):
    if start_time and len(start_time) >= 10:
        st_date = start_time[:10]
        query = query.filter(model_column >= f"{st_date} 00:00:00")
    if end_time and len(end_time) >= 10:
        et_date = end_time[:10]
        query = query.filter(model_column <= f"{et_date} 23:59:59")
    return query


# ================= 1. 操作日志接口 =================
@router.get("/operation")
def get_operation_logs(
        page: int = 1, page_size: int = 10,
        keyword: str = "", operation_type: str = "", status: str = "",
        start_time: str = None, end_time: str = None,
        db: Session = Depends(get_db)
):
    query = db.query(OperationLog, User.full_name).outerjoin(User, OperationLog.operator_id == User.id)

    if keyword:
        query = query.filter(
            OperationLog.operation_content.contains(keyword) |
            User.full_name.contains(keyword) |
            OperationLog.ip_address.contains(keyword)
        )
    if operation_type:
        try:
            # 关键修复：强制转换成 Enum 对象，防止数据库直接对比字符串时失效
            enum_op = OperationType(operation_type)
            query = query.filter(OperationLog.operation_type == enum_op)
        except ValueError:
            pass

    if status:
        is_success = True if status == "success" else False
        query = query.filter(OperationLog.success == is_success)

    query = apply_time_filter(query, OperationLog.operation_time, start_time, end_time)

    total = query.count()
    items = query.order_by(desc(OperationLog.operation_time)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for log, full_name in items:
        result.append({
            "id": log.id,
            "operator_name": full_name or "未知",
            "operation_type": log.operation_type.value if hasattr(log.operation_type, 'value') else log.operation_type,
            "operation_content": log.operation_content,
            "ip_address": log.ip_address,
            "status": "success" if log.success else "fail",
            "error_msg": log.error_msg,
            "created_at": log.operation_time.strftime("%Y-%m-%d %H:%M:%S") if log.operation_time else None
        })
    return {"total": total, "items": result}


# ================= 2. 推理日志接口 =================
@router.get("/inference")
def get_inference_logs(
        page: int = 1, page_size: int = 10,
        keyword: str = "", status: str = "",
        start_time: str = None, end_time: str = None,
        db: Session = Depends(get_db)
):
    query = db.query(InferenceTask, User.full_name).outerjoin(User, InferenceTask.user_id == User.id)

    if keyword:
        query = query.filter(
            InferenceTask.task_id.contains(keyword) |
            InferenceTask.patient_name.contains(keyword) |
            User.full_name.contains(keyword)
        )
    if status:
        try:
            # 关键修复：强制转换成 Enum 对象
            enum_status = TaskStatus(status)
            query = query.filter(InferenceTask.status == enum_status)
        except ValueError:
            pass

    query = apply_time_filter(query, InferenceTask.created_at, start_time, end_time)

    total = query.count()
    items = query.order_by(desc(InferenceTask.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for task, full_name in items:
        duration = None
        if task.end_time and task.start_time:
            duration = round((task.end_time - task.start_time).total_seconds(), 2)

        result.append({
            "id": task.id,
            "task_id": task.task_id,
            "model_name": f"模型ID: {task.model_id}",
            "doctor_name": full_name or "未知",
            "patient_name": task.patient_name,
            "worker_name": task.worker_name or "默认节点",
            "status": task.status.value if hasattr(task.status, 'value') else task.status,
            "duration": duration,
            "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S") if task.created_at else None
        })
    return {"total": total, "items": result}


# ================= 3. 登录日志接口 =================
@router.get("/login")
def get_login_logs(
        page: int = 1, page_size: int = 10,
        keyword: str = "", status: str = "",
        start_time: str = None, end_time: str = None,
        db: Session = Depends(get_db)
):
    query = db.query(LoginLog)

    if keyword:
        query = query.filter(
            LoginLog.username.contains(keyword) | LoginLog.full_name.contains(keyword) | LoginLog.ip_address.contains(
                keyword))
    if status:
        query = query.filter(LoginLog.status == status)

    query = apply_time_filter(query, LoginLog.login_time, start_time, end_time)

    total = query.count()
    items = query.order_by(desc(LoginLog.login_time)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for log in items:
        result.append({
            "id": log.id,
            "username": log.username,
            "full_name": log.full_name,
            "role": log.role,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "location": log.location,
            "status": log.status,
            "fail_reason": log.fail_reason,
            "login_time": log.login_time.strftime("%Y-%m-%d %H:%M:%S") if log.login_time else None
        })
    return {"total": total, "items": result}


# ================= 4. 导出接口 =================
@router.get("/{log_type}/export")
def export_logs(
        log_type: str,
        keyword: str = "", operation_type: str = "", status: str = "",
        start_time: str = None, end_time: str = None,
        db: Session = Depends(get_db)
):
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)

    if log_type == "operation":
        writer.writerow(["ID", "操作人", "操作类型", "操作内容", "IP", "状态", "时间"])
        query = db.query(OperationLog, User.full_name).outerjoin(User, OperationLog.operator_id == User.id)
        if keyword:
            query = query.filter(OperationLog.operation_content.contains(keyword) | User.full_name.contains(
                keyword) | OperationLog.ip_address.contains(keyword))
        if operation_type:
            try:
                query = query.filter(OperationLog.operation_type == OperationType(operation_type))
            except ValueError:
                pass
        if status:
            is_success = True if status == "success" else False
            query = query.filter(OperationLog.success == is_success)
        query = apply_time_filter(query, OperationLog.operation_time, start_time, end_time)

        for log, full_name in query.all():
            writer.writerow([log.id, full_name,
                             log.operation_type.value if hasattr(log.operation_type, 'value') else log.operation_type,
                             log.operation_content, log.ip_address, "成功" if log.success else "失败",
                             log.operation_time])

    elif log_type == "inference":
        writer.writerow(["ID", "任务编号", "医生", "患者", "状态", "创建时间"])
        query = db.query(InferenceTask, User.full_name).outerjoin(User, InferenceTask.user_id == User.id)
        if keyword:
            query = query.filter(InferenceTask.task_id.contains(keyword) | InferenceTask.patient_name.contains(
                keyword) | User.full_name.contains(keyword))
        if status:
            try:
                query = query.filter(InferenceTask.status == TaskStatus(status))
            except ValueError:
                pass
        query = apply_time_filter(query, InferenceTask.created_at, start_time, end_time)

        for task, full_name in query.all():
            writer.writerow([task.id, task.task_id, full_name, task.patient_name,
                             task.status.value if hasattr(task.status, 'value') else task.status, task.created_at])

    elif log_type == "login":
        writer.writerow(["ID", "账号", "姓名", "角色", "IP", "状态", "时间"])
        query = db.query(LoginLog)
        if keyword:
            query = query.filter(LoginLog.username.contains(keyword) | LoginLog.full_name.contains(
                keyword) | LoginLog.ip_address.contains(keyword))
        if status:
            query = query.filter(LoginLog.status == status)
        query = apply_time_filter(query, LoginLog.login_time, start_time, end_time)

        for log in query.all():
            writer.writerow([log.id, log.username, log.full_name, log.role, log.ip_address,
                             "成功" if log.status == "success" else "失败", log.login_time])

    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={log_type}_logs.csv"
    return response


@router.delete("/operation/batch")
def delete_operation_logs(
        req: BatchDeleteRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    deleted = db.query(OperationLog).filter(OperationLog.id.in_(req.ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"成功删除 {deleted} 条操作日志"}


@router.delete("/operation/{log_id}")
def delete_single_operation_log(
        log_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    log = db.query(OperationLog).filter(OperationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    db.delete(log)
    db.commit()
    return {"message": "删除成功"}


@router.delete("/login/batch")
def delete_login_logs(
        req: BatchDeleteRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    deleted = db.query(LoginLog).filter(LoginLog.id.in_(req.ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"成功删除 {deleted} 条登录日志"}


@router.delete("/login/{log_id}")
def delete_single_login_log(
        log_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    log = db.query(LoginLog).filter(LoginLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    db.delete(log)
    db.commit()
    return {"message": "删除成功"}


@router.get("/stats/overview")
def get_log_stats_overview(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    today_start = datetime.combine(today, datetime.min.time())
    week_start = datetime.combine(week_ago, datetime.min.time())
    month_start = datetime.combine(month_ago, datetime.min.time())
    
    login_today = db.query(LoginLog).filter(LoginLog.login_time >= today_start).count()
    login_week = db.query(LoginLog).filter(LoginLog.login_time >= week_start).count()
    login_month = db.query(LoginLog).filter(LoginLog.login_time >= month_start).count()
    
    operation_today = db.query(OperationLog).filter(OperationLog.operation_time >= today_start).count()
    operation_week = db.query(OperationLog).filter(OperationLog.operation_time >= week_start).count()
    operation_month = db.query(OperationLog).filter(OperationLog.operation_time >= month_start).count()
    
    inference_today = db.query(InferenceTask).filter(InferenceTask.created_at >= today_start).count()
    inference_week = db.query(InferenceTask).filter(InferenceTask.created_at >= week_start).count()
    inference_month = db.query(InferenceTask).filter(InferenceTask.created_at >= month_start).count()
    
    return {
        "login": {
            "today": login_today,
            "week": login_week,
            "month": login_month
        },
        "operation": {
            "today": operation_today,
            "week": operation_week,
            "month": operation_month
        },
        "inference": {
            "today": inference_today,
            "week": inference_week,
            "month": inference_month
        }
    }


@router.get("/stats/login-trend")
def get_login_trend(
        days: int = 7,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    result = []
    for i in range(days - 1, -1, -1):
        date = datetime.now().date() - timedelta(days=i)
        day_start = datetime.combine(date, datetime.min.time())
        day_end = datetime.combine(date, datetime.max.time())
        
        success_count = db.query(LoginLog).filter(
            LoginLog.login_time >= day_start,
            LoginLog.login_time <= day_end,
            LoginLog.status == "success"
        ).count()
        
        fail_count = db.query(LoginLog).filter(
            LoginLog.login_time >= day_start,
            LoginLog.login_time <= day_end,
            LoginLog.status == "fail"
        ).count()
        
        result.append({
            "date": date.strftime("%Y-%m-%d"),
            "success": success_count,
            "fail": fail_count
        })
    
    return result


@router.get("/stats/operation-distribution")
def get_operation_distribution(
        days: int = 7,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    date_start = datetime.now().date() - timedelta(days=days)
    datetime_start = datetime.combine(date_start, datetime.min.time())
    
    distribution = db.query(
        OperationLog.operation_type,
        func.count(OperationLog.id)
    ).filter(
        OperationLog.operation_time >= datetime_start
    ).group_by(OperationLog.operation_type).all()
    
    result = []
    for op_type, count in distribution:
        result.append({
            "type": op_type.value if hasattr(op_type, 'value') else op_type,
            "count": count
        })
    
    return result


@router.get("/stats/inference-status")
def get_inference_status_stats(
        days: int = 7,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    date_start = datetime.now().date() - timedelta(days=days)
    datetime_start = datetime.combine(date_start, datetime.min.time())
    
    status_stats = db.query(
        InferenceTask.status,
        func.count(InferenceTask.id)
    ).filter(
        InferenceTask.created_at >= datetime_start
    ).group_by(InferenceTask.status).all()
    
    result = []
    for status, count in status_stats:
        result.append({
            "status": status.value if hasattr(status, 'value') else status,
            "count": count
        })
    
    return result