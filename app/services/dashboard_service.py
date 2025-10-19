from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.models.terminal import Terminal
from app.models.bus import Bus
from app.schemas.terminal import TerminalDashboard

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_terminal_dashboard(self) -> List[TerminalDashboard]:
        """Get bus count and wait times for all terminals"""
        query = select(
            Terminal,
            func.count(Bus.id).label("bus_count")
        ).outerjoin(Bus).group_by(Terminal.id)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        dashboard_data = []
        for terminal, bus_count in rows:
            wait_time = self._calculate_wait_time(bus_count)
            dashboard_data.append(
                TerminalDashboard(
                    id=terminal.id,
                    name=terminal.name,
                    latitude=terminal.latitude,
                    longitude=terminal.longitude,
                    address=terminal.address,
                    capacity=terminal.capacity,
                    bus_count=bus_count,
                    expected_wait_time=wait_time
                )
            )
        
        return dashboard_data
    
    def _calculate_wait_time(self, bus_count: int) -> int:
        """Calculate expected wait time based on bus count"""
        if bus_count == 0:
            return 30  # 30 minutes if no buses
        elif bus_count <= 2:
            return 15
        elif bus_count <= 5:
            return 10
        else:
            return 5