from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional, List

from app.models.bus import Bus
from app.models.driver import Driver
from app.models.terminal import Terminal
from app.utils.distance import calculate_distance
from app.core.websocket_manager import manager
from app.services.eta_service import ETAService
from app.schemas.bus import BusWithETA

class TrackingService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def update_bus_location(
        self, phone_number: str, latitude: float, longitude: float, speed: float = 0.0
    ) -> bool:
        """Update bus location using driver's phone number"""
        query = select(Bus).join(Driver).where(Driver.phone_number == phone_number)
        result = await self.db.execute(query)
        bus = result.scalar_one_or_none()
        
        if not bus:
            return False
        
        bus.latitude = latitude
        bus.longitude = longitude
        bus.speed = speed
        bus.last_updated = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "location_update",
            "bus_id": bus.id,
            "plate_number": bus.plate_number,
            "latitude": latitude,
            "longitude": longitude,
            "speed": speed,
            "timestamp": bus.last_updated.isoformat()
        })
        
        return True
    
    async def get_bus_by_phone(self, phone_number: str) -> Optional[Bus]:
        """Get bus by driver's phone number"""
        query = select(Bus).join(Driver).where(Driver.phone_number == phone_number)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def calculate_eta_to_terminal(
        self, bus_phone: str, terminal_id: str, eta_service: ETAService
    ):
        """Calculate ETA for bus to reach terminal"""
        # Get bus
        bus = await self.get_bus_by_phone(bus_phone)
        if not bus or not bus.latitude or not bus.longitude:
            return None
        
        # Get terminal
        query = select(Terminal).where(Terminal.id == terminal_id)
        result = await self.db.execute(query)
        terminal = result.scalar_one_or_none()
        
        if not terminal:
            return None
        
        # Calculate ETA
        eta_data = eta_service.calculate_eta(
            bus.latitude, bus.longitude,
            terminal.latitude, terminal.longitude,
            bus.speed
        )
        
        return {
            "bus_id": bus.id,
            "plate_number": bus.plate_number,
            "terminal_id": terminal.id,
            "terminal_name": terminal.name,
            **eta_data
        }
    
    async def get_nearby_buses_with_eta(
        self, user_lat: float, user_lon: float, radius_km: float, eta_service: ETAService
    ) -> List[BusWithETA]:
        """Get all active buses within radius with ETA"""
        query = select(Bus).where(Bus.is_active == True)
        result = await self.db.execute(query)
        buses = result.scalars().all()
        
        nearby_buses = []
        for bus in buses:
            if not bus.latitude or not bus.longitude:
                continue
            
            distance = calculate_distance(
                user_lat, user_lon, bus.latitude, bus.longitude
            )
            
            if distance <= radius_km:
                eta_data = eta_service.calculate_eta(
                    bus.latitude, bus.longitude,
                    user_lat, user_lon,
                    bus.speed
                )
                
                bus_dict = {
                    "id": bus.id,
                    "plate_number": bus.plate_number,
                    "capacity": bus.capacity,
                    "current_terminal_id": bus.current_terminal_id,
                    "driver_id": bus.driver_id,
                    "is_active": bus.is_active,
                    "latitude": bus.latitude,
                    "longitude": bus.longitude,
                    "speed": bus.speed,
                    "last_updated": bus.last_updated,
                    "eta_minutes": eta_data["eta_minutes"],
                    "distance_km": eta_data["distance_km"]
                }
                nearby_buses.append(BusWithETA(**bus_dict))
        
        # Sort by ETA
        nearby_buses.sort(key=lambda x: x.eta_minutes if x.eta_minutes else float('inf'))
        return nearby_buses
    
    async def find_nearest_terminal(self, latitude: float, longitude: float):
        """Find nearest terminal to user's location"""
        query = select(Terminal)
        result = await self.db.execute(query)
        terminals = result.scalars().all()
        
        nearest = None
        min_distance = float('inf')
        
        for terminal in terminals:
            distance = calculate_distance(
                latitude, longitude,
                terminal.latitude, terminal.longitude
            )
            if distance < min_distance:
                min_distance = distance
                nearest = terminal
        
        if not nearest:
            return None
        
        return {
            "terminal_id": nearest.id,
            "terminal_name": nearest.name,
            "latitude": nearest.latitude,
            "longitude": nearest.longitude,
            "distance_km": round(min_distance, 2)
        }