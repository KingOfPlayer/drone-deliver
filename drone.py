
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

@dataclass
class Drone:
    id: int
    max_weight: float
    battery: int
    speed: float
    start_pos: Tuple[float, float]
    atBusyDatetime: datetime = datetime.now()

    @staticmethod
    def calculate_distance(pos1:tuple,pos2:tuple):
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
    
    def can_carry(self, weight: float) -> bool:
        return weight <= self.max_weight
    
    def set_busy(self, datetime: datetime):
        print(f"Drone {self.id} is now busy until {datetime}")
        self.atBusyDatetime = datetime

    def is_available(self, datetime: datetime) -> bool:
        if self.atBusyDatetime is None:
            return True
        return datetime >= self.atBusyDatetime
    
    @staticmethod
    def calculate_energy_consumption(distance: float, weight: float) -> float:
        base_consumption = 35  # %/metre
        weight_factor = 1 + (weight / 10)
        return distance * base_consumption * weight_factor