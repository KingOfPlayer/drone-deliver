from abc import abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import List

from deliverycase import DeliveryCase
from drone import Drone

@dataclass
class DronePath:
    points: list[tuple[float, float]]  # List of (x, y) tuples representing the path
    isReturn: bool  # True if the path is a return path, False otherwise
    cost: float
    distence: float# Total distance of the path

    def __init__(self,node_path:List[float],node_positions:List[tuple[float, float]], isReturn:bool, cost:float=0.0):
        self.points = [node_positions[node] for node in node_path]
        self.distence = sum(Drone.calculate_distance(self.points[i], self.points[i + 1]) for i in range(len(self.points) - 1))
        self.isReturn = isReturn
        self.cost = cost

    def callculate_estimated_time(self, drone: Drone) -> timedelta:
        if drone.speed <= 0:
            return None
        total_time = self.distence / drone.speed
        return timedelta(seconds=total_time)


class Solution:
    solverName: str
    Case: DeliveryCase
    dronePaths: dict[list[DronePath]] = {}
    totalDistance: float = 0.0
    totalConsumption: float = 0.0

class Solver:
    @abstractmethod
    def solve(self,deliverycase:DeliveryCase,**kwargs) -> Solution:
        pass