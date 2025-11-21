from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, date
from typing import List, Optional

from app.models.assignment import DailyAssignment
from app.models.driver import Driver
from app.models.bus import Bus
from app.schemas.assignment import AssignmentCreate, DailyAssignmentSummary, AssignmentCreateWithPhone

class AssignmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_assignment(self, assignment: AssignmentCreate) -> DailyAssignment:
        """Create a new driver-bus assignment (Traditional method using IDs)"""
        # Check if driver already has assignment for this date/shift
        existing = await self._check_existing_assignment(
            assignment.driver_id, assignment.assignment_date, assignment.shift
        )
        if existing:
            raise ValueError("Driver already has an assignment for this shift")
        
        # Create assignment
        db_assignment = DailyAssignment(
            driver_id=assignment.driver_id,
            bus_id=assignment.bus_id,
            assignment_date=assignment.assignment_date,
            shift=assignment.shift,
            start_time=assignment.start_time
        )
        
        self.db.add(db_assignment)
        await self.db.commit()
        await self.db.refresh(db_assignment)
        
        return db_assignment
    
    async def create_assignment_with_phone(
        self, assignment: AssignmentCreateWithPhone
    ) -> dict:
        """
        Create assignment using driver's phone number (Recommended method)
        
        This method:
        1. Finds driver by phone number
        2. Assigns bus to driver (sets bus.driver_id)
        3. Creates daily assignment
        4. Returns complete details
        """
        
        # 1. Find driver by phone number
        driver_query = select(Driver).where(
            Driver.phone_number == assignment.driver_phone_number
        )
        driver_result = await self.db.execute(driver_query)
        driver = driver_result.scalar_one_or_none()
        
        if not driver:
            raise ValueError(f"Driver with phone number {assignment.driver_phone_number} not found")
        
        # 2. Check if driver already has assignment for this date/shift
        existing = await self._check_existing_assignment(
            driver.id, assignment.assignment_date, assignment.shift
        )
        if existing:
            raise ValueError(f"Driver {driver.name} already has an assignment for {assignment.shift.value} shift on {assignment.assignment_date}")
        
        # 3. Get bus
        bus_query = select(Bus).where(Bus.id == assignment.bus_id)
        bus_result = await self.db.execute(bus_query)
        bus = bus_result.scalar_one_or_none()
        
        if not bus:
            raise ValueError(f"Bus with ID {assignment.bus_id} not found")
        
        # 4. Check if bus is already assigned to another driver
        if bus.driver_id and bus.driver_id != driver.id:
            # Get current driver name
            current_driver_query = select(Driver).where(Driver.id == bus.driver_id)
            current_driver_result = await self.db.execute(current_driver_query)
            current_driver = current_driver_result.scalar_one_or_none()
            current_driver_name = current_driver.name if current_driver else "another driver"
            
            raise ValueError(f"Bus {bus.plate_number} is already assigned to {current_driver_name}")
        
        # 5. Create daily assignment (shift scheduling)
        db_assignment = DailyAssignment(
            driver_id=driver.id,
            bus_id=assignment.bus_id,
            assignment_date=assignment.assignment_date,
            shift=assignment.shift,
            start_time=assignment.start_time
        )
        # 6. Assign bus to driver (operational link)
        bus.driver_id = driver.id

        self.db.add(bus)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(db_assignment)
        await self.db.refresh(bus)
        
        # 7. Return complete details
        return {
            "assignment_id": db_assignment.id,
            "driver": {
                "id": driver.id,
                "name": driver.name,
                "phone_number": driver.phone_number,
                "license_number": driver.license_number
            },
            "bus": {
                "id": bus.id,
                "plate_number": bus.plate_number,
                "capacity": bus.capacity
            },
            "shift": assignment.shift.value,
            "assignment_date": assignment.assignment_date,
            "start_time": assignment.start_time,
            "end_time": None,
            "tracking_url": f"/api/v1/tracking/bus/{driver.phone_number}",
            "message": f"✅ Successfully assigned {driver.name} to Bus {bus.plate_number} for {assignment.shift.value} shift"
        }
    
    async def get_assignments_by_date(self, assignment_date: date) -> List[DailyAssignment]:
        """Get all assignments for a specific date"""
        query = select(DailyAssignment).where(
            DailyAssignment.assignment_date == assignment_date
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_driver_assignments(self, driver_id: str) -> List[DailyAssignment]:
        """Get assignment history for a driver"""
        query = select(DailyAssignment).where(
            DailyAssignment.driver_id == driver_id
        ).order_by(DailyAssignment.assignment_date.desc())
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_driver_assignments_by_phone(self, phone_number: str) -> List[DailyAssignment]:
        """Get assignment history for a driver using phone number"""
        # Find driver by phone
        driver_query = select(Driver).where(Driver.phone_number == phone_number)
        driver_result = await self.db.execute(driver_query)
        driver = driver_result.scalar_one_or_none()
        
        if not driver:
            raise ValueError(f"Driver with phone number {phone_number} not found")
        
        # Get assignments
        return await self.get_driver_assignments(driver.id)
    
    async def end_assignment(
        self, assignment_id: str, end_time: datetime
    ) -> Optional[DailyAssignment]:
        """
        End a driver's shift and clear operational bus assignment
        """
        query = select(DailyAssignment).where(DailyAssignment.id == assignment_id)
        result = await self.db.execute(query)
        assignment = result.scalar_one_or_none()
        
        if assignment:
            assignment.end_time = end_time
            
            # Clear bus operational assignment when shift ends
            bus_query = select(Bus).where(Bus.id == assignment.bus_id)
            bus_result = await self.db.execute(bus_query)
            bus = bus_result.scalar_one_or_none()
            
            if bus and bus.driver_id == assignment.driver_id:
                bus.driver_id = None  # Clear operational link
                print(f"✅ Cleared operational assignment for bus {bus.plate_number}")
            
            await self.db.commit()
            await self.db.refresh(assignment)
        
        return assignment
    
    async def get_daily_summary(self, assignment_date: date) -> DailyAssignmentSummary:
        """Get summary statistics for a specific date"""
        # Count total assignments
        total_query = select(func.count(DailyAssignment.id)).where(
            DailyAssignment.assignment_date == assignment_date
        )
        total_result = await self.db.execute(total_query)
        total_assignments = total_result.scalar()
        
        # Count unique buses
        buses_query = select(func.count(func.distinct(DailyAssignment.bus_id))).where(
            DailyAssignment.assignment_date == assignment_date
        )
        buses_result = await self.db.execute(buses_query)
        active_buses = buses_result.scalar()
        
        # Count available drivers (active but not assigned today)
        drivers_query = select(func.count(Driver.id)).where(
            and_(
                Driver.is_active == True,
                ~Driver.id.in_(
                    select(DailyAssignment.driver_id).where(
                        DailyAssignment.assignment_date == assignment_date
                    )
                )
            )
        )
        drivers_result = await self.db.execute(drivers_query)
        available_drivers = drivers_result.scalar()
        
        return DailyAssignmentSummary(
            assignment_date=assignment_date,
            total_assignments=total_assignments,
            active_buses=active_buses,
            available_drivers=available_drivers
        )
    
    async def _check_existing_assignment(
        self, driver_id: str, assignment_date: date, shift
    ) -> Optional[DailyAssignment]:
        """Check if driver already has assignment for date/shift"""
        query = select(DailyAssignment).where(
            and_(
                DailyAssignment.driver_id == driver_id,
                DailyAssignment.assignment_date == assignment_date,
                DailyAssignment.shift == shift
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()