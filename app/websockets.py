from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, customer_id: int):
        await websocket.accept()
        self.active_connections[customer_id] = websocket

    def disconnect(self, customer_id: int):
        if customer_id in self.active_connections:
            del self.active_connections[customer_id]

    async def send_personal_message(self, message: str, customer_id: int):
        if customer_id in self.active_connections:
            await self.active_connections[customer_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    async def send_notification(self, customer_id: int, notification_data: dict):
        message = json.dumps({
            "type": "notification",
            "data": notification_data
        })
        await self.send_personal_message(message, customer_id)

    async def send_transaction_update(self, customer_id: int, transaction_data: dict):
        message = json.dumps({
            "type": "transaction_update",
            "data": transaction_data
        })
        await self.send_personal_message(message, customer_id)

websocket_manager = ConnectionManager()