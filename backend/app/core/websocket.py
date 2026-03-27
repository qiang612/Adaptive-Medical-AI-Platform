from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self._heartbeat_interval = 30
    
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: user_id={user_id}, total_connections={len(self.active_connections[user_id])}")
    
    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    async def send_personal_message(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send message to user {user_id}: {e}")
                    dead_connections.append(connection)
            for dead in dead_connections:
                self.disconnect(user_id, dead)
    
    async def broadcast(self, message: dict):
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(user_id, message)
    
    async def send_task_update(self, user_id: int, task_id: str, status: str, result: dict = None):
        message = {
            "type": "task_update",
            "task_id": task_id,
            "status": status,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(user_id, message)
    
    async def send_notification(self, user_id: int, title: str, content: str, notification_type: str = "info"):
        message = {
            "type": "notification",
            "notification_type": notification_type,
            "title": title,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(user_id, message)
    
    async def send_system_alert(self, user_id: int, level: str, message: str):
        alert = {
            "type": "system_alert",
            "level": level,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(user_id, alert)
    
    async def broadcast_system_alert(self, level: str, message: str):
        alert = {
            "type": "system_alert",
            "level": level,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(alert)
    
    def get_online_users(self) -> List[int]:
        return list(self.active_connections.keys())
    
    def get_connection_count(self, user_id: int = None) -> int:
        if user_id:
            return len(self.active_connections.get(user_id, []))
        return sum(len(conns) for conns in self.active_connections.values())


ws_manager = ConnectionManager()
