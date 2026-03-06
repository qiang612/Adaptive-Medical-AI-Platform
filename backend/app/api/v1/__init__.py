from fastapi import APIRouter
from app.api.v1 import users, models, tasks, inference

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(users.router)
api_router.include_router(models.router)
api_router.include_router(tasks.router)
api_router.include_router(inference.router)