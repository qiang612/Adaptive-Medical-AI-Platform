from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.append(connection)
            for dead in dead_connections:
                self.disconnect(user_id, dead)

    async def broadcast(self, message: dict):
        for user_id in self.active_connections:
            await self.send_personal_message(user_id, message)

    async def send_task_update(self, user_id: int, task_id: str, status: str, result: dict = None):
        message = {
            "type": "task_update",
            "task_id": task_id,
            "status": status,
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_personal_message(user_id, message)

    async def send_notification(self, user_id: int, title: str, content: str):
        message = {
            "type": "notification",
            "title": title,
            "content": content,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_personal_message(user_id, message)


ws_manager = ConnectionManager()
