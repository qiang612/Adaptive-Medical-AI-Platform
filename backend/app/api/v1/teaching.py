# backend/app/api/v1/teaching.py
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.core.database import SessionLocal
from app.models.teaching_case import TeachingCase

router = APIRouter(prefix="/teaching", tags=["Teaching"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TeachingCaseCreate(BaseModel):
    title: str
    disease_type: str
    case_type: str
    difficulty: str
    description: Optional[str] = None
    findings: Optional[List[dict]] = None
    images: Optional[List[str]] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    tags: Optional[List[str]] = None


class TeachingCaseUpdate(BaseModel):
    title: Optional[str] = None
    disease_type: Optional[str] = None
    case_type: Optional[str] = None
    difficulty: Optional[str] = None
    description: Optional[str] = None
    findings: Optional[List[dict]] = None
    images: Optional[List[str]] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    tags: Optional[List[str]] = None


@router.get("/cases")
def get_cases(
        page: int = 1,
        page_size: int = 9,
        keyword: Optional[str] = None,
        case_type: Optional[str] = None,
        disease_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        tags: Optional[str] = None,
        sort_by: Optional[str] = "create_time",
        db: Session = Depends(get_db)
):
    query = db.query(TeachingCase)

    if keyword:
        query = query.filter(
            or_(
                TeachingCase.title.contains(keyword),
                TeachingCase.description.contains(keyword),
                TeachingCase.diagnosis.contains(keyword) if hasattr(TeachingCase, 'diagnosis') else False
            )
        )
    if case_type:
        query = query.filter(TeachingCase.case_type == case_type)
    if disease_type:
        query = query.filter(TeachingCase.disease_type == disease_type)
    if difficulty:
        query = query.filter(TeachingCase.difficulty == difficulty)
    if tags:
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        for tag in tag_list:
            query = query.filter(TeachingCase.tags.contains(tag))

    if sort_by == "view_count":
        query = query.order_by(TeachingCase.view_count.desc())
    elif sort_by == "star_count":
        query = query.order_by(TeachingCase.star_count.desc())
    else:
        query = query.order_by(TeachingCase.create_time.desc())

    total = query.count()
    cases = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "items": cases,
        "page": page,
        "page_size": page_size
    }


@router.get("/cases/{case_id}")
def get_case_detail(case_id: int, db: Session = Depends(get_db)):
    case = db.query(TeachingCase).filter(TeachingCase.id == case_id).first()

    if not case:
        raise HTTPException(status_code=404, detail="教学案例不存在")

    case.view_count += 1
    db.commit()
    db.refresh(case)

    return case


@router.post("/cases")
def create_case(
        case_data: TeachingCaseCreate,
        db: Session = Depends(get_db)
):
    new_case = TeachingCase(
        title=case_data.title,
        disease_type=case_data.disease_type,
        case_type=case_data.case_type,
        difficulty=case_data.difficulty,
        description=case_data.description,
        findings=case_data.findings,
        images=case_data.images,
        diagnosis=case_data.diagnosis,
        treatment=case_data.treatment,
        tags=case_data.tags,
        create_time=datetime.now()
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return {"message": "案例创建成功", "id": new_case.id}


@router.put("/cases/{case_id}")
def update_case(
        case_id: int,
        case_data: TeachingCaseUpdate,
        db: Session = Depends(get_db)
):
    case = db.query(TeachingCase).filter(TeachingCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="教学案例不存在")

    update_data = case_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(case, key, value)

    db.commit()
    db.refresh(case)
    return {"message": "案例更新成功", "case": case}


@router.delete("/cases/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(TeachingCase).filter(TeachingCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="教学案例不存在")

    db.delete(case)
    db.commit()
    return {"message": "案例删除成功"}


@router.post("/cases/{case_id}/star")
def toggle_star(case_id: int, db: Session = Depends(get_db)):
    case = db.query(TeachingCase).filter(TeachingCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="教学案例不存在")

    case.star_count = (case.star_count or 0) + 1
    db.commit()
    return {"message": "收藏成功", "star_count": case.star_count}


@router.get("/stats")
def get_teaching_stats(db: Session = Depends(get_db)):
    total = db.query(TeachingCase).count()
    
    disease_stats = db.query(
        TeachingCase.disease_type,
        db.func.count(TeachingCase.id)
    ).group_by(TeachingCase.disease_type).all()
    
    difficulty_stats = db.query(
        TeachingCase.difficulty,
        db.func.count(TeachingCase.id)
    ).group_by(TeachingCase.difficulty).all()
    
    return {
        "total": total,
        "by_disease": dict(disease_stats),
        "by_difficulty": dict(difficulty_stats)
    }