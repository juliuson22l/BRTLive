from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.driver import Driver
from app.models.bus import Bus
from app.schemas.driver import DriverCreate, DriverUpdate, DriverResponse, DriverWithBus
from app.dependencies import get_current_admin_user, get_current_active_user, get_pagination_params
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[DriverResponse])
async def get_all_drivers(
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all drivers with pagination"""
    query = select(Driver).offset(pagination["skip"]).limit(pagination["limit"])
    result = await db.execute(query)
    drivers = result.scalars().all()
    return drivers

@router.get("/{driver_id}", response_model=DriverWithBus)
async def get_driver_by_id(
    driver_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific driver by ID with bus info"""
    query = select(Driver).where(Driver.id == driver_id)
    result = await db.execute(query)
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Get assigned bus
    bus_query = select(Bus).where(Bus.driver_id == driver_id)
    bus_result = await db.execute(bus_query)
    bus = bus_result.scalar_one_or_none()
    
    driver_dict = {
        "id": driver.id,
        "name": driver.name,
        "phone_number": driver.phone_number,
        "is_active": driver.is_active,
        "created_at": driver.created_at,
        "bus_id": bus.id if bus else None,
        "bus_plate_number": bus.plate_number if bus else None
    }
    
    return DriverWithBus(**driver_dict)

@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(
    driver_data: DriverCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Create a new driver (Admin only)"""
    # Check if phone number already exists
    query = select(Driver).where(Driver.phone_number == driver_data.phone_number)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver with this phone number already exists"
        )
    
    # Check if license number already exists (if provided)
    if driver_data.license_number:
        license_query = select(Driver).where(Driver.license_number == driver_data.license_number)
        license_result = await db.execute(license_query)
        if license_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver with this license number already exists"
            )
    
    driver = Driver(
        user_id=driver_data.user_id,
        name=driver_data.name,
        phone_number=driver_data.phone_number,
        license_number=driver_data.license_number
    )
    
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    
    return driver

@router.put("/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: str,
    driver_data: DriverUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Update a driver (Admin only)"""
    query = select(Driver).where(Driver.id == driver_id)
    result = await db.execute(query)
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Update only provided fields
    if driver_data.name is not None:
        setattr(driver, "name", driver_data.name)
    if driver_data.phone_number is not None:
        # Check if new phone number is unique
        check_query = select(Driver).where(
            Driver.phone_number == driver_data.phone_number,
            Driver.id != driver_id
        )
        check_result = await db.execute(check_query)
        if check_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use"
            )
        setattr(driver, "phone_number", driver_data.phone_number)
    if driver_data.license_number is not None:
        # Check if new license number is unique
        check_query = select(Driver).where(
            Driver.license_number == driver_data.license_number,
            Driver.id != driver_id
        )
        check_result = await db.execute(check_query)
        if check_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License number already in use"
            )
        setattr(driver, "license_number", driver_data.license_number)
    if driver_data.is_active is not None:
        setattr(driver, "is_active", driver_data.is_active)
    
    await db.commit()
    await db.refresh(driver)
    
    return driver

@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(
    driver_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Delete a driver (Admin only)"""
    query = select(Driver).where(Driver.id == driver_id)
    result = await db.execute(query)
    driver = result.scalar_one_or_none()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Check if driver is assigned to a bus
    bus_query = select(Bus).where(Bus.driver_id == driver_id)
    bus_result = await db.execute(bus_query)
    if bus_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete driver assigned to a bus. Unassign first."
        )
    
    await db.delete(driver)
    await db.commit()
    
    return None
