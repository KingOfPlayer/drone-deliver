
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple
from shapely import LineString, Polygon

@dataclass
class NoFlyZone:
    id: int
    coordinates: List[Tuple[float, float]]
    active_time: Tuple[datetime, datetime]

    def is_active(self, current_time: datetime) -> bool:
        return self.active_time[0] <= current_time <= self.active_time[1]
    
    def is_path_conflict(self, start: Tuple[float, float], end: Tuple[float, float]) -> bool:
        polygon = Polygon(self.coordinates)
        line = LineString([start, end])

        intersection = line.intersection(polygon)

        return intersection.area > 0 or intersection.length > 0 and not line.boundary.contains(intersection)