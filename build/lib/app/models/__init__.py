# app/models/__init__.py
from app.database import Base

# Import in this exact order:
from app.models.terminal import Terminal
from app.models.route import Route
from app.models.bus import Bus
from app.models.driver import Driver
from app.models.tracking import BusTracking
from app.models.eta import Eta          # Before User!
from app.models.user import User        # After Eta!

__all__ = [
    'Base',
    'Terminal', 
    'Route',
    'Bus',
    'Driver',
    'BusTracking',
    'Eta',
    'User'
]