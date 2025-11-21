from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date

from app.database import get_db
from app.schemas.assignment import (
    AssignmentCreateWithPhone, AssignmentResponseWithDetails, AssignmentEnd, DailyAssignmentSummary,
    AssignmentResponse
)
from app.services.assignment_service import AssignmentService

router = APIRouter()

@router.post("/", response_model=AssignmentResponseWithDetails)
async def create_assignment(
    assignment: AssignmentCreateWithPhone,
    db: AsyncSession = Depends(get_db)
):
    """Assign a driver to a bus for a specific shift"""
    service = AssignmentService(db)
    return await service.create_assignment_with_phone(assignment)

@router.get("/daily/{assignment_date}", response_model=List[AssignmentResponse])
async def get_daily_assignments(
    assignment_date: date,
    db: AsyncSession = Depends(get_db)
):
    """Get all assignments for a specific date"""
    service = AssignmentService(db)
    return await service.get_assignments_by_date(assignment_date)

@router.get("/driver/{phone_number}", response_model=List[AssignmentResponse])
async def driver_assignments(
    phone_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get assignment history for a specific driver"""
    service = AssignmentService(db)
    return await service.get_driver_assignments_by_phone(phone_number)

@router.get("/summary/{assignment_date}", response_model=DailyAssignmentSummary)
async def get_daily_summary(
    assignment_date: date,
    db: AsyncSession = Depends(get_db)
):
    """Get summary of assignments for a specific date"""
    service = AssignmentService(db)
    return await service.get_daily_summary(assignment_date)

@router.patch("/{assignment_id}/end", response_model=AssignmentResponseWithDetails)
async def end_assignment(
    assignment_id: str,
    data: AssignmentEnd,
    db: AsyncSession = Depends(get_db)
):
    """End a driver's shift"""
    service = AssignmentService(db)
    result = await service.end_assignment(assignment_id, data.end_time)
    if not result:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return result