# backend/app/api/v1/statistics.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.inference_task import InferenceTask, TaskStatus
from app.models.user import User
from app.models.model_registry import ModelRegistry
from datetime import datetime, timedelta
import json

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 建立一个映射字典，把 AI 返回的英文类型翻译成好看的图表标签
DISEASE_MAP = {
    "Multimodal_Fusion (CNN + MLP)": "冠心病",
    "YOLOv8_Detection": "肺结节",
    "YOLOv8_Cervical": "宫颈病变"
}

MODEL_NAME_MAP = {
    "Multimodal_Fusion (CNN + MLP)": "CHD多模态大模型",
    "YOLOv8_Detection": "肺结节检测模型",
    "YOLOv8_Cervical": "宫颈筛查模型"
}


@router.get("/platform")
def get_platform_stats(time_range: str = Query("today", description="today, week, month"),
                       db: Session = Depends(get_db)):
    """获取平台全维度统计数据"""
    now = datetime.now()
    if time_range == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == "week":
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:  # month
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 1. 基础指标统计
    total_tasks = db.query(InferenceTask).filter(InferenceTask.created_at >= start_date).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_models = db.query(ModelRegistry).count()
    active_models = db.query(ModelRegistry).filter(ModelRegistry.is_active == True).count()

    # 2. 平均响应时间计算
    tasks_with_time = db.query(InferenceTask).filter(
        InferenceTask.created_at >= start_date,
        InferenceTask.start_time != None,
        InferenceTask.end_time != None
    ).all()

    total_duration = sum((t.end_time - t.start_time).total_seconds() for t in tasks_with_time)
    avg_response_time = round((total_duration / len(tasks_with_time)) * 1000) if tasks_with_time else 0

    # 3. 病种分布 (饼图)
    disease_counts = {}
    for t in db.query(InferenceTask).all():
        if t.result:
            try:
                res = json.loads(t.result) if isinstance(t.result, str) else t.result
                m_type = res.get("model_type", "未知")
                disease_name = DISEASE_MAP.get(m_type, "其他")
                disease_counts[disease_name] = disease_counts.get(disease_name, 0) + 1
            except:
                pass
    disease_distribution = [{"name": k, "value": v} for k, v in disease_counts.items()]
    if not disease_distribution:
        disease_distribution = [{"name": "暂无数据", "value": 0}]

    # 4. 模型调用排行 (柱状图)
    model_calls = db.query(
        ModelRegistry.model_name,
        func.count(InferenceTask.id).label("call_count")
    ).outerjoin(
        InferenceTask, InferenceTask.model_id == ModelRegistry.id
    ).group_by(ModelRegistry.id).order_by(func.count(InferenceTask.id).desc()).limit(5).all()

    model_rank = [{"model_name": row[0], "call_count": row[1]} for row in model_calls]

    # 5. 用户活跃度TOP10
    user_calls = db.query(
        User.full_name,
        func.count(InferenceTask.id).label("diagnosis_count")
    ).join(
        InferenceTask, InferenceTask.user_id == User.id
    ).group_by(User.id).order_by(func.count(InferenceTask.id).desc()).limit(10).all()

    user_rank = [{"full_name": row[0] or "未知用户", "diagnosis_count": row[1]} for row in user_calls]

    # 6. 最新任务列表
    recent_tasks_query = db.query(InferenceTask, User.full_name.label("doctor_name"),
                                  ModelRegistry.model_name.label("model_name")) \
        .outerjoin(User, InferenceTask.user_id == User.id) \
        .outerjoin(ModelRegistry, InferenceTask.model_id == ModelRegistry.id) \
        .order_by(InferenceTask.created_at.desc()).limit(5).all()

    latest_tasks = [{
        "task_id": t[0].task_id,
        "model_name": t[2] or f"模型_{t[0].model_id}",
        "doctor_name": t[1] or "未知",
        "status": t[0].status.value if hasattr(t[0].status, 'value') else t[0].status,
        "created_at": t[0].created_at.strftime("%Y-%m-%d %H:%M") if t[0].created_at else ""
    } for t in recent_tasks_query]

    # 7. 最新注册用户
    recent_users = db.query(User).order_by(User.create_time.desc()).limit(5).all()
    latest_users = [{
        "username": u.username,
        "full_name": u.full_name,
        "department": u.department or "-",
        "role": u.role.value if hasattr(u.role, 'value') else u.role,
        "created_at": u.create_time.strftime("%Y-%m-%d %H:%M") if u.create_time else ""
    } for u in recent_users]

    return {
        "totalTasks": total_tasks,
        "taskGrowth": 12.5,  # 此处可扩展真实的环比计算
        "activeUsers": active_users,
        "userGrowth": 5.2,
        "activeModels": active_models,
        "totalModels": total_models,
        "avgResponseTime": f"{avg_response_time}ms",
        "timeTrend": -2.3,
        "disease_distribution": disease_distribution,
        "model_rank": model_rank,
        "user_rank": user_rank,
        "latest_tasks": latest_tasks,
        "latest_users": latest_users
    }


@router.get("/trend")
def get_trend_stats(time_range: str = Query("today", description="today, week, month"), db: Session = Depends(get_db)):
    """获取任务趋势统计数据（折线图）"""
    now = datetime.now()
    x_axis = []
    total = []
    completed = []
    failed = []

    if time_range == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        for i in range(now.hour + 1):
            h_start = start_date.replace(hour=i)
            h_end = h_start + timedelta(hours=1)
            x_axis.append(f"{i:02d}:00")

            tasks = db.query(InferenceTask).filter(
                InferenceTask.created_at >= h_start,
                InferenceTask.created_at < h_end
            ).all()
            total.append(len(tasks))
            completed.append(len([t for t in tasks if t.status == TaskStatus.COMPLETED]))
            failed.append(len([t for t in tasks if t.status == TaskStatus.FAILED]))

    elif time_range == "week":
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        for i in range(7):
            d_start = start_date + timedelta(days=i)
            if d_start > now:
                break
            d_end = d_start + timedelta(days=1)
            x_axis.append(d_start.strftime("%m-%d"))

            tasks = db.query(InferenceTask).filter(
                InferenceTask.created_at >= d_start,
                InferenceTask.created_at < d_end
            ).all()
            total.append(len(tasks))
            completed.append(len([t for t in tasks if t.status == TaskStatus.COMPLETED]))
            failed.append(len([t for t in tasks if t.status == TaskStatus.FAILED]))

    else:  # month
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        for i in range(now.day):
            d_start = start_date + timedelta(days=i)
            d_end = d_start + timedelta(days=1)
            x_axis.append(f"{i + 1}日")

            tasks = db.query(InferenceTask).filter(
                InferenceTask.created_at >= d_start,
                InferenceTask.created_at < d_end
            ).all()
            total.append(len(tasks))
            completed.append(len([t for t in tasks if t.status == TaskStatus.COMPLETED]))
            failed.append(len([t for t in tasks if t.status == TaskStatus.FAILED]))

    return {
        "xAxis": x_axis,
        "total": total,
        "completed": completed,
        "failed": failed
    }


# ----------------- 下方保留原有的旧接口 -----------------

@router.get("/personal")
def get_personal_stats(start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    """获取个人基础诊断统计数据"""
    tasks = db.query(InferenceTask).all()

    total = len(tasks)
    completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    patients = set([t.patient_id for t in tasks if t.patient_id])

    total_duration = 0
    duration_count = 0
    low_risk, medium_risk, high_risk = 0, 0, 0

    for t in tasks:
        if t.start_time and t.end_time:
            total_duration += (t.end_time - t.start_time).total_seconds()
            duration_count += 1

        if t.result:
            try:
                res_data = t.result if isinstance(t.result, dict) else json.loads(t.result)
                risk = res_data.get("risk_level", "")
                if "高" in risk:
                    high_risk += 1
                elif "中" in risk:
                    medium_risk += 1
                elif "低" in risk:
                    low_risk += 1
            except:
                pass

    avg_time = round(total_duration / duration_count, 1) if duration_count > 0 else 0

    return {
        "totalDiagnosis": total,
        "diagnosisTrend": 12.5,
        "completedRate": f"{int((completed / total) * 100)}%" if total > 0 else "0%",
        "totalPatients": len(patients),
        "patientsTrend": 8.2,
        "avgTime": f"{avg_time}s",
        "timeTrend": -5.4,
        "low_risk_count": low_risk,
        "medium_risk_count": medium_risk,
        "high_risk_count": high_risk
    }


@router.get("/disease")
def get_disease_stats(db: Session = Depends(get_db)):
    """获取病种分布统计"""
    tasks = db.query(InferenceTask).all()
    disease_counts = {}

    for t in tasks:
        if t.result:
            try:
                res_data = t.result if isinstance(t.result, dict) else json.loads(t.result)
                model_type = res_data.get("model_type", "")
                disease = DISEASE_MAP.get(model_type, "其他未知病种")
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
            except:
                pass

    result = [{"name": k, "count": v} for k, v in disease_counts.items()]
    return result if result else [{"name": "暂无数据", "count": 0}]


@router.get("/model-call")
def get_model_call_stats(db: Session = Depends(get_db)):
    """获取模型调用统计"""
    tasks = db.query(InferenceTask).all()
    model_counts = {}

    for t in tasks:
        if t.result:
            try:
                res_data = t.result if isinstance(t.result, dict) else json.loads(t.result)
                raw_model_type = res_data.get("model_type", "")
                model_name = MODEL_NAME_MAP.get(raw_model_type, f"模型_{t.model_id}")
                model_counts[model_name] = model_counts.get(model_name, 0) + 1
            except:
                pass

    result = [{"model_name": k, "call_count": v} for k, v in model_counts.items()]
    return sorted(result, key=lambda x: x["call_count"], reverse=True)