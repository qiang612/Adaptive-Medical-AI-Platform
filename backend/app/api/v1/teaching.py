# backend/app/api/v1/teaching.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import SessionLocal
from app.models.teaching_case import TeachingCase

router = APIRouter(prefix="/teaching", tags=["Teaching"])


# 获取数据库Session的依赖函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/cases")
def get_cases(
        page: int = 1,
        page_size: int = 9,
        keyword: Optional[str] = None,
        case_type: Optional[str] = None,
        disease_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        db: Session = Depends(get_db)
):
    query = db.query(TeachingCase)

    # 构建查询条件
    if keyword:
        query = query.filter(TeachingCase.title.contains(keyword) | TeachingCase.description.contains(keyword))
    if case_type:
        query = query.filter(TeachingCase.case_type == case_type)
    if disease_type:
        query = query.filter(TeachingCase.disease_type == disease_type)
    if difficulty:
        query = query.filter(TeachingCase.difficulty == difficulty)

    # 统计总数并分页
    total = query.count()
    cases = query.order_by(TeachingCase.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "items": cases,
        "page": page,
        "page_size": page_size
    }


# 👇 这是新增的获取单个详情的接口
@router.get("/cases/{case_id}")
def get_case_detail(case_id: int, db: Session = Depends(get_db)):
    case = db.query(TeachingCase).filter(TeachingCase.id == case_id).first()

    if not case:
        raise HTTPException(status_code=404, detail="教学案例不存在")

    # 每次查看详情，浏览量自增
    case.view_count += 1
    db.commit()
    db.refresh(case)

    return case