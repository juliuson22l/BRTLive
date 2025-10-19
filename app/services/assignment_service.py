from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, date
from typing import Optional, Sequence

from app.models.assignment import DailyAssignment
from app.models.driver import Driver
from app.models.bus import Bus
from app.schemas.assignment import AssignmentCreate, DailyAssignmentSummary

class AssignmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_assignment(self, assignment: AssignmentCreate) -> DailyAssignment:
        """Create a new driver-bus assignment"""
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
    
    async def get_assignments_by_date(self, assignment_date: date) -> Sequence[DailyAssignment]:
        """Get all assignments for a specific date"""
        query = select(DailyAssignment).where(
            DailyAssignment.assignment_date == assignment_date
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_driver_assignments(self, driver_id: str) -> Sequence[DailyAssignment]:
        """Get assignment history for a driver"""
        query = select(DailyAssignment).where(
            DailyAssignment.driver_id == driver_id
        ).order_by(DailyAssignment.assignment_date.desc())
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def end_assignment(
        self, assignment_id: str, end_time: datetime
    ) -> Optional[DailyAssignment]:
        """End a driver's shift"""
        query = select(DailyAssignment).where(DailyAssignment.id == assignment_id)
        result = await self.db.execute(query)
        assignment: DailyAssignment | None = result.scalar_one_or_none()
        
        if assignment:
            assignment.end_time = end_time
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