from pydantic import BaseModel

class RouteStopBase(BaseModel):
    id:int
    route_id:int
    terminal_id:int
    stop_order:int
    estimated_travel_time_minutes:int=5

    class Config:
        orm_mode=True
