from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.models.bus import Bus
from app.schemas.bus import BusCreate, BusUpdate
from app.core.exceptions import not_found, conflict

class BusService:
    """Business logic for bus operations"""
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Bus]:
        """Get all buses with filters"""
        query = select(Bus)
        
        if is_active is not None:
            query = query.filter(Bus.is_active == is_active)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_id(self, db: AsyncSession, bus_id: int) -> Bus:
        """Get bus by ID"""
        result = await db.execute(select(Bus).filter(Bus.id == bus_id))
        bus = result.scalar_one_or_none()
        
        if not bus:
            not_found(f"Bus {bus_id} not found")
        
        return bus
    
    async def create(self, db: AsyncSession, bus_data: BusCreate) -> Bus:
        """Create new bus"""
        # Check duplicate plate
        result = await db.execute(
            select(Bus).filter(Bus.plate_number == bus_data.plate_number)
        )
        
        if result.scalar_one_or_none():
            conflict(f"Plate number {bus_data.plate_number} already exists")
        
        new_bus = Bus(
            plate_number=bus_data.plate_number,
            capacity=bus_data.capacity,
            terminal_id=bus_data.current_terminal_id,
            driver_id=bus_data.driver_id,
            route_id=bus_data.current_route_id,
            status=bus_data.status if hasattr(bus_data, 'status') else None,
            is_active=bus_data.is_active,
            latitude=bus_data.latitude if hasattr(bus_data, 'latitude') else None,
            longitude=bus_data.longitude if hasattr(bus_data, 'longitude') else None,
            speed=bus_data.speed if hasattr(bus_data, 'speed') else 0.0,
            current_route_id=bus_data.current_route_id if hasattr(bus_data, 'current_route_id') else None
        )
        db.add(new_bus)
        await db.commit()
        await db.refresh(new_bus)
        
        return new_bus
    
    async def update(
        self,
        db: AsyncSession,
        bus_id: int,
        bus_data: BusUpdate
    ) -> Bus:
        """Update bus"""
        bus = await self.get_by_id(db, bus_id)
        
        # Update fields
        for field, value in bus_data.model_dump(exclude_unset=True).items():
            setattr(bus, field, value)
        
        await db.commit()
        await db.refresh(bus)
        
        return bus
    
    async def delete(self, db: AsyncSession, bus_id: int) -> None:
        """Delete bus"""
        bus = await self.get_by_id(db, bus_id)
        await db.delete(bus)
        await db.commit()
    
    async def activate(self, db: AsyncSession, bus_id: int) -> Bus:
        """Activate bus"""
        bus = await self.get_by_id(db, bus_id)
        bus.is_active
        await db.commit()
        await db.refresh(bus)
        return bus
    
    async def deactivate(self, db: AsyncSession, bus_id: int) -> Bus:
        """Deactivate bus"""
        bus = await self.get_by_id(db, bus_id)
        bus.is_active = False
        await db.commit()
        await db.refresh(bus)
        return bus

# Global instance
bus_service = BusService()