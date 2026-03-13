# backend/app/api/v1/inference.py
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from fastapi.responses import Response
import random

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.inference_service import inference_service
from app.models.model_registry import ModelRegistry  # 引入模型表用于查询模型名称

router = APIRouter(prefix="/inference", tags=["推理核心"])


@router.get("/status/{task_id}")
def get_task_status(task_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return inference_service.get_task_status(db, task_id=task_id, user_id=current_user.id)


@router.post("/batch")
def batch_inference(req: dict = Body(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    批量多模型对比推理接口
    """
    model_ids = req.get("model_ids", [])
    patient_info = req.get("patient_info", {})

    results = []
    # 遍历前端传来的所有模型ID
    for m_id in model_ids:
        # 查询真实的模型名称
        model = db.query(ModelRegistry).filter(ModelRegistry.id == m_id).first()
        model_name = model.model_name if model else f"未知模型 {m_id}"

        # 为了让前端流程跑通，这里构造符合 Vue 渲染期望的返回结构
        # 实际开发中：此处应调用 inference_service 生成任务，或汇总 Celery 结果
        risk_level = random.choice(["高风险", "中风险", "低风险"])
        results.append({
            "model_id": m_id,
            "model_name": model_name,
            "status": "completed",
            "risk_level": risk_level,
            "risk_score": round(random.uniform(0.6, 0.95) if risk_level == "高风险" else random.uniform(0.1, 0.5), 2),
            "confidence": round(random.uniform(0.75, 0.99), 2),
            "duration": round(random.uniform(2.0, 15.0), 1),
            "diagnosis_summary": f"基于 {model_name} 的算法分析，结合患者特征得出的诊断结论。",
            "primary_diagnosis": "待临床确认",
            "recommendation": "建议结合医生经验进一步复查",
            "findings": ["发现异常形态特征", "病灶边界特征明显"]
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