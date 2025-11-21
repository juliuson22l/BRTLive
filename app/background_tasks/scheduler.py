"""
APScheduler configuration and job scheduling.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .cleanup import cleanup_old_location_history
from .monitoring import check_inactive_buses, auto_end_expired_assignments


scheduler = AsyncIOScheduler()


def start_scheduler():
    """Start the background tasks scheduler."""
    
    # Cleanup old location history - Daily at 2 AM
    scheduler.add_job(
        cleanup_old_location_history,
        trigger=CronTrigger(hour=2, minute=0),
        id="cleanup_location_history",
        name="Cleanup old location history",
        replace_existing=True,
        kwargs={"days_to_keep": 30}
    )
    
    # Check inactive buses - Every 5 minutes
    scheduler.add_job(
        check_inactive_buses,
        trigger=IntervalTrigger(minutes=5),
        id="check_inactive_buses",
        name="Check for inactive buses",
        replace_existing=True,
        kwargs={"inactive_threshold_minutes": 15}
    )
    
    # Auto-end expired assignments - Every hour
    scheduler.add_job(
        auto_end_expired_assignments,
        trigger=IntervalTrigger(hours=1),
        id="auto_end_assignments",
        name="Auto-end expired assignments",
        replace_existing=True
    )
    
    scheduler.start()
    
    print("\n" + "="*60)
    print("📅 Background Tasks Scheduler Started")
    print("="*60)
    print("✅ Cleanup location history: Daily at 2:00 AM")
    print("✅ Check inactive buses: Every 5 minutes")
    print("✅ Auto-end expired assignments: Every hour")
    print("="*60 + "\n")


def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown()
        print("✅ Background tasks scheduler stopped")