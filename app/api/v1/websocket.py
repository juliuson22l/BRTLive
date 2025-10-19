from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.websocket import manager
from app.database import get_db

router = APIRouter()

@router.websocket("/live-tracking")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time bus tracking"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)