from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.websocket import ws_manager
from app.core.middleware import RequestLoggingMiddleware, SlowRequestMiddleware
from app.core.exceptions import (
    AppException, app_exception_handler, validation_exception_handler,
    sqlalchemy_exception_handler, generic_exception_handler
)
from app.models import Base
from fastapi.staticfiles import StaticFiles
import os
import asyncio
import json
import threading
import redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

Base.metadata.create_all(bind=engine, checkfirst=True)

app = FastAPI(
    title="医疗AI模型接入平台",
    description="仅支持医生+管理员的多模型异步推理平台",
    version="1.0.0"
)

app.add_middleware(SlowRequestMiddleware, threshold=3.0)
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(api_router)


def get_redis_client():
    redis_url = settings.REDIS_URL
    if redis_url.startswith('redis://'):
        redis_url = redis_url.replace('redis://', '')
    parts = redis_url.split('/')
    db = int(parts[1]) if len(parts) > 1 else 0
    host_port = parts[0].split(':')
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 6379
    return redis.Redis(host=host, port=port, db=db)


def redis_subscriber():
    try:
        r = get_redis_client()
        pubsub = r.pubsub()
        pubsub.subscribe("task_updates:all")
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    user_id = data.get('user_id')
                    if user_id:
                        asyncio.run(ws_manager.send_task_update(
                            user_id,
                            data.get('task_id'),
                            data.get('status'),
                            data.get('result')
                        ))
                except Exception as e:
                    print(f"处理Redis消息失败: {e}")
    except Exception as e:
        print(f"Redis订阅线程启动失败: {e}")


@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=redis_subscriber, daemon=True)
    thread.start()


@app.get("/")
def root():
    return {"message": "医疗AI模型接入平台服务已启动（数据库：medical_ai_platform）"}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data) if isinstance(data, str) else data
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)


@app.post("/upload-test")
async def upload_test(files: list[UploadFile] = File(...)):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_files = []
    for file in files:
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        saved_files.append(file_path)
    return {"message": f"成功上传 {len(files)} 个文件", "files": saved_files}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
