"""
Monitoring tasks for system health and automation.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings
from app.models.bus import Bus
from app.models.assignment import DailyAssignment


async def check_inactive_buses(inactive_threshold_minutes: int = 15):
    """
    Check for buses that haven't updated location recently.
    
    Runs: Every 5 minutes
    """
    print(f"\n🚨 Checking for inactive buses (threshold: {inactive_threshold_minutes} mins)...")
    
    try:
        engine = create_async_engine(settings.db_url, echo=False)
        AsyncSessionLocal = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            threshold = datetime.now(timezone.utc) - timedelta(minutes=inactive_threshold_minutes)
            
            query = select(Bus).where(
                and_(
                    Bus.is_active == True,
                    Bus.last_updated < threshold,
                    Bus.last_updated.isnot(None)
                )
            )
            
            result = await session.execute(query)
            inactive_buses = result.scalars().all()
            
            if len(inactive_buses) == 0:
                print("✅ All active buses are reporting normally")
            else:
                print(f"⚠️  Found {len(inactive_buses)} inactive buses:")
                for bus in inactive_buses:
                    minutes_inactive = int((datetime.now(timezone.utc) - bus.last_updated).total_seconds() / 60)
                    print(f"   - Bus {bus.plate_number}: Last seen {minutes_inactive} mins ago")
            
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error checking inactive buses: {e}")


async def auto_end_expired_assignments():
    """
    Automatically end assignments that have passed their shift time.
    
    Runs: Every hour
    """
    print("\n⏰ Checking for expired assignments to auto-end...")
    
    try:
        engine = create_async_engine(settings.db_url, echo=False)
        AsyncSessionLocal = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            now = datetime.now(timezone.utc)
            
            query = select(DailyAssignment).where(
                and_(
                    DailyAssignment.end_time.is_(None),
                    DailyAssignment.start_time < (now - timedelta(hours=8))
                )
            )
            
            result = await session.execute(query)
            expired_assignments = result.scalars().all()
            
            if len(expired_assignments) == 0:
                print("✅ No expired assignments to end")
            else:
                print(f"📝 Auto-ending {len(expired_assignments)} expired assignments...")
                
                for assignment in expired_assignments:
                    assignment.end_time = assignment.start_time + timedelta(hours=8)
                
                await session.commit()
                print(f"✅ Successfully ended {len(expired_assignments)} assignments")
            
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error auto-ending expired assignments: {e}")