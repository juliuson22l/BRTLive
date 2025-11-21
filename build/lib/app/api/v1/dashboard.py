from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.terminal import TerminalDashboard
from app.services.dashboard_service import DashboardService

router = APIRouter()

@router.get("/terminals", response_model=List[TerminalDashboard])
async def get_terminal_dashboard(db: AsyncSession = Depends(get_db)):
    """Get dashboard with bus count and wait times for all terminals"""
    service = DashboardService(db)
    return await service.get_terminal_dashboard()
