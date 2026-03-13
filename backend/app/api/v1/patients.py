# backend/app/api/v1/patients.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import traceback
from fastapi.responses import JSONResponse
from app.models.inference_task import InferenceTask
from app.core.database import SessionLocal
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientList

router = APIRouter(prefix="/patients", tags=["Patients"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 💡 注意：这里去掉了 response_model=PatientList，为了拦截报错并展示在页面上
@router.get("/")
def get_patients(
        keyword: Optional[str] = None,
        gender: Optional[str] = None,
        age_range: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1),
        db: Session = Depends(get_db)
):
    try:
        query = db.query(Patient)

        if keyword:
            query = query.filter(
                or_(
                    Patient.name.contains(keyword),
                    Patient.id_card.contains(keyword),
                    Patient.phone.contains(keyword)
                )
            )
        if gender:
            query = query.filter(Patient.gender == gender)

        if age_range:
            if age_range == "0-18":
                query = query.filter(Patient.age <= 18)
            elif age_range == "19-40":
                query = query.filter(Patient.age >= 19, Patient.age <= 40)
            elif age_range == "41-60":
                query = query.filter(Patient.age >= 41, Patient.age <= 60)
            elif age_range == "60+":
                query = query.filter(Patient.age > 60)

        if start_time and end_time:
            query = query.filter(Patient.create_time >= start_time, Patient.create_time <= end_time)

        total = query.count()
        patients = query.order_by(Patient.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        # 尝试执行 Pydantic 校验（通常是这里崩溃了）
        result = PatientList.model_validate({
            "total": total,
            "items": patients,
            "page": page,
            "page_size": page_size
        })
        return result.model_dump()

    except Exception as e:
        # 💡 核心代码：如果报错，把详细的红字报错直接返回给浏览器！
        error_trace = traceback.format_exc()
        print(error_trace)  # 终端也打印一份
        return JSONResponse(
            status_code=500,
            content={
                "error": "后端数据校验失败，请把下面的报错发给 AI！",
                "detail": str(e),
                "trace": error_trace
            }
        )


@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient_update: PatientUpdate, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="未找到该患者")
    for key, value in patient_update.model_dump(exclude_unset=True).items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="未找到该患者")
    db.delete(db_patient)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="未找到该患者")
    return db_patient


@router.get("/{patient_id}/diagnosis")
def get_patient_diagnosis(
        patient_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1),
        db: Session = Depends(get_db)
):
    try:
        db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not db_patient:
            raise HTTPException(status_code=404, detail="未找到该患者")

        # 匹配对应患者门诊号或姓名的任务
        query = db.query(InferenceTask).filter(
            or_(
                InferenceTask.patient_id == db_patient.patient_id,
                InferenceTask.patient_name == db_patient.name
            )
        )
        total = query.count()
        items = query.order_by(InferenceTask.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        # 转换为字典返回
        result_items = []
        for item in items:
            item_dict = {
                "id": item.id,
                "task_id": item.task_id,
                "model_id": item.model_id,
                "patient_name": item.patient_name,
                "patient_id": item.patient_id,
                "status": item.status,
                "error_msg": item.error_msg,
                "result": item.result,
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else None,
            }
            result_items.append(item_dict)

        return {
            "total": total,
            "items": result_items,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        error_trace = traceback.format_exc()
        print(error_trace)
        return JSONResponse(status_code=500, content={"error": str(e)})