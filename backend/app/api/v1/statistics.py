# backend/app/api/v1/statistics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.inference_task import InferenceTask, TaskStatus
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
        # 计算耗时
        if t.start_time and t.end_time:
            total_duration += (t.end_time - t.start_time).total_seconds()
            duration_count += 1

        # 计算风险分布 (键名确认是 risk_level)
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
                # 提取 model_type 并映射为病种
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
                # 提取 model_type 并映射为前端好看的模型名字
                raw_model_type = res_data.get("model_type", "")
                model_name = MODEL_NAME_MAP.get(raw_model_type, f"模型_{t.model_id}")
                model_counts[model_name] = model_counts.get(model_name, 0) + 1
            except:
                pass

    result = [{"model_name": k, "call_count": v} for k, v in model_counts.items()]
    return sorted(result, key=lambda x: x["call_count"], reverse=True)