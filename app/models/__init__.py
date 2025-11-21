# app/models/__init__.py
from app.models.user import User
from app.models.driver import Driver
from app.models.terminal import Terminal
from app.models.bus import Bus
from app.models.assignment import DailyAssignment
from app.models.location import LocationHistory

__all__ = [
    "User",
    "Driver", 
    "Terminal",
    "Bus",
    "DailyAssignment",
    "LocationHistory"
]