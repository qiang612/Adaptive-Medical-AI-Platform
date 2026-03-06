# backend/app/api/v1/roles.py
from fastapi import APIRouter

router = APIRouter(prefix="/roles", tags=["角色管理"])

@router.get("/")
def get_roles():
    """提供给前端的角色字典"""
    return [
        {"id": "admin", "name": "系统管理员"},
        {"id": "doctor", "name": "医生"}
    ]