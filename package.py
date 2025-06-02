
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

@dataclass
class Package:
    id: int
    pos: Tuple[float, float]
    weight: float
    priority: int
    time_window: Tuple[datetime, datetime]
    delivered: bool = False
    can_deliver: bool = True

    def set_delivered(self):
        self.delivered = True

    def is_within_time_window(self, current_time: datetime) -> bool:
        return self.time_window[0] <= current_time <= self.time_window[1]
    
    def get_start_time(self) -> datetime:
        return self.time_window[0]
    
    def set_cannot_deliver(self):
        self.can_deliver = False
