from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone, date
from typing import Optional, List, cast, Any

from app.models.bus import Bus
from app.models.driver import Driver
from app.models.terminal import Terminal
from app.models.assignment import DailyAssignment
from app.models.location import LocationHistory
from app.utils.helpers import calculate_distance
from app.core.websocket import manager
from app.services.eta_service import ETAService
from app.schemas.bus import BusWithETA
from app.schemas.location import LocationUpdate

class TrackingService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def update_bus_location(
        self, phone_number: str, latitude: float, longitude: float, speed: float = 0.0,
        heading: Optional[float] = None, accuracy: Optional[float] = None
    ) -> bool:
        """Update bus location using driver's phone number and save to history"""
        # Get driver first
        driver_query = select(Driver).where(Driver.phone_number == phone_number)
        driver_result = await self.db.execute(driver_query)
        driver = driver_result.scalar_one_or_none()
        
        if not driver:
            return False
        
        # Get bus assigned to this driver
        bus_query = select(Bus).where(Bus.driver_id == driver.id)
        bus_result = await self.db.execute(bus_query)
        bus = bus_result.scalar_one_or_none()
        
        if not bus:
            return False
        
        # Update current bus location
        cast(Any, bus).latitude = latitude
        cast(Any, bus).longitude = longitude
        cast(Any, bus).speed_km = speed
        # cast to Any to satisfy the type-checker when assigning a datetime to a mapped Column attribute
        cast(Any, bus).last_updated = datetime.now(timezone.utc)
        
        
        # Save to location history
        location_record = LocationHistory(
            bus_id=bus.id,
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            heading=heading,
            accuracy=accuracy
        )
        self.db.add(location_record)
        
        await self.db.commit()
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "location_update",
            "bus_id": bus.id,
            "plate_number": bus.plate_number,
            "latitude": latitude,
            "longitude": longitude,
            "speed": speed,
            "heading": heading,
            "timestamp": bus.last_updated.isoformat()
        })
        
        return True
    
    async def get_bus_by_phone(self, phone_number: str) -> Optional[Bus]:
        # 1. Find driver by phone number
        driver_query = select(Driver).where(Driver.phone_number == phone_number)
        driver_result = await self.db.execute(driver_query)
        driver = driver_result.scalar_one_or_none()

        if not driver:
            raise ValueError(f"Driver with phone {phone_number} not found")

        # 2. Find today's active assignment for this driver

        assignment_query = select(DailyAssignment).where(
            DailyAssignment.driver_id == driver.id,
            DailyAssignment.assignment_date == datetime.now(timezone.utc).date()
        ).order_by(DailyAssignment.assignment_date.desc())

        assignment_result = await self.db.execute(assignment_query)
        assignment = assignment_result.scalar_one_or_none()

        if not assignment:
            raise ValueError(f"No active assignment found for driver {driver.name} today")

        # 3. Get the bus from the assignment
        bus_query = select(Bus).where(Bus.id == assignment.bus_id)
        bus_result = await self.db.execute(bus_query)
        bus = bus_result.scalar_one_or_none()

        if not bus:
            raise ValueError("Bus not found")

        # Now you have the bus for tracking
        return bus
    
    async def get_location_history(self, bus_id: int, limit: int = 100) -> List[LocationHistory]:
        """Get location history for a bus"""
        query = select(LocationHistory).where(
            LocationHistory.bus_id == bus_id
        ).order_by(LocationHistory.recorded_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def calculate_eta_to_terminal(
        self, bus_phone: str, terminal_id: str, eta_service: ETAService
    ):
        """Calculate ETA for bus to reach terminal"""
        # Get bus
        bus = await self.get_bus_by_phone(bus_phone)
        if not bus or bus.latitude is False or bus.longitude is False:
            raise ValueError("Bus location not available")
        
        # Get terminal
        query = select(Terminal).where(Terminal.id == terminal_id)
        result = await self.db.execute(query)
        terminal = result.scalar_one_or_none()
        
        if not terminal:
            raise ValueError("Terminal not found")
        
        # Calculate ETA
        eta_data = eta_service.calculate_eta(
            bus.latitude, 
            bus.longitude,
            terminal.latitude, 
            terminal.longitude,
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
            if bus.latitude is False or bus.longitude is False:
                continue
            
            distance = calculate_distance(
                user_lat, user_lon, bus.latitude, bus.longitude
            )
            
            if distance <= radius_km:
                eta_data = eta_service.calculate_eta(
                    bus.latitude, 
                    bus.longitude,
                    user_lat, 
                    user_lon,
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
                terminal.latitude, 
                terminal.longitude
            )
            if distance < min_distance:
                min_distance = distance
                nearest = terminal
        
        if not nearest:
            raise ValueError("No terminals found")
        
        return {
            "terminal_id": nearest.id,
            "terminal_name": nearest.name,
            "latitude": nearest.latitude,
            "longitude": nearest.longitude,
            "distance_km": round(min_distance, 2)
        }