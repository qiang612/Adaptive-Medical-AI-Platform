from fastapi import APIRouter
from app.api.v1 import users, models, tasks, inference
from app.api.v1 import roles
from app.api.v1 import users, models, tasks, inference, roles, patients, statistics, teaching
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(users.router)
api_router.include_router(models.router)
api_router.include_router(tasks.router)
api_router.include_router(inference.router)
api_router.include_router(roles.router)
api_router.include_router(patients.router) # 注册路由
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
api_router.include_router(teaching.router)