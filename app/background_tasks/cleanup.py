"""
Cleanup tasks to prevent database bloat.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings
from app.models.location import LocationHistory


async def cleanup_old_location_history(days_to_keep: int = 30):
    """
    Delete location history records older than specified days.
    
    Runs: Daily at 2:00 AM
    Purpose: Prevent location_history table from growing infinitely
    """
    print(f"\n🧹 Starting location history cleanup (keeping last {days_to_keep} days)...")
    
    try:
        engine = create_async_engine(settings.db_url, echo=False)
        AsyncSessionLocal = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            
            # Count records to be deleted
            count_query = select(func.count(LocationHistory.id)).where(
                LocationHistory.recorded_at < cutoff_date
            )
            count_result = await session.execute(count_query)
            total_to_delete = count_result.scalar()
            
            if total_to_delete == 0:
                print("✅ No old records to delete")
                return
            
            # Delete old records
            delete_stmt = delete(LocationHistory).where(
                LocationHistory.recorded_at < cutoff_date
            )
            
            result = await session.execute(delete_stmt)
            await session.commit()
            
            print(f"✅ Deleted {result.rowcount} old location records")
            
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")