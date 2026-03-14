from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi.responses import StreamingResponse
import io
import csv

from app.core.database import get_db
from app.models.operation_log import OperationLog, OperationType
from app.models.inference_task import InferenceTask, TaskStatus
from app.models.login_log import LoginLog
from app.models.user import User

router = APIRouter(tags=["Logs"])


# ================= 辅助函数：安全处理时间与截断 ISO 尾缀 =================
def apply_time_filter(query, model_column, start_time: str, end_time: str):
    if start_time and len(start_time) >= 10:
        # 只取前10位 YYYY-MM-DD，防丢弃前端传来的 T16:00:00.000Z 等时区后缀
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