from typing import Optional
from app.utils.helpers import calculate_distance

class ETAService:
    AVERAGE_SPEED_KMH = 30  # Average city speed
    TRAFFIC_FACTOR = 1.3  # Traffic multiplier
    STOP_TIME_PER_TERMINAL = 3  # Minutes per stop
    
    def calculate_eta(
        self,
        bus_lat: float,
        bus_lon: float,
        dest_lat: float,
        dest_lon: float,
        current_speed: Optional[float] = None,
        stops_remaining: int = 0
    ) -> dict:
        """Calculate ETA from bus location to destination"""
        
        # Calculate distance
        distance_km = calculate_distance(bus_lat, bus_lon, dest_lat, dest_lon)
        
        # Use current speed if available, otherwise use average
        speed = current_speed if current_speed and current_speed > 0 else self.AVERAGE_SPEED_KMH
        
        # Calculate base travel time
        travel_time_hours = distance_km / speed
        travel_time_minutes = travel_time_hours * 60
        
        # Apply traffic factor
        adjusted_time = travel_time_minutes * self.TRAFFIC_FACTOR
        
        # Add stop time
        total_time = adjusted_time + (stops_remaining * self.STOP_TIME_PER_TERMINAL)
        
        return {
            "eta_minutes": round(total_time),
            "distance_km": round(distance_km, 2),
            "estimated_speed_kmh": round(speed, 1)
        }
