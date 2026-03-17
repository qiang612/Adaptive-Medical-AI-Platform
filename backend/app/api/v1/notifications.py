from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.notification import Notification, NotificationStatus

router = APIRouter(prefix="/notifications", tags=["通知管理"])

@router.get("/unread-count")
def get_unread_count(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """获取当前用户的未读通知数量"""
    count = db.query(Notification).filter(
        Notification.doctor_id == current_user.id,
        Notification.status == NotificationStatus.UNREAD
    ).count()
    return {"count": count}

@router.post("/read-all")
def mark_all_as_read(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """将当前用户的所有通知标记为已读"""
    db.query(Notification).filter(
        Notification.doctor_id == current_user.id,
        Notification.status == NotificationStatus.UNREAD
    ).update({"status": NotificationStatus.READ})
    db.commit()
    return {"message": "全部标记为已读"}