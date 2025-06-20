
from collections import defaultdict
from datetime import datetime, timedelta
from deliverycase import DeliveryCase
from drone import Drone
from solver import DronePath, Solution, Solver


class AStarSolver(Solver):
    noflyzone_penalty:float  # No-fly zone cezası
    KNN = 4  # KNN için kullanılacak komşu sayısı
    deliverycase: DeliveryCase  # Teslimat vakası

    def __init__(self,noflyzone_penalty=100000000):
        self.noflyzone_penalty = noflyzone_penalty
        self.deliverycase = None

    def calculate_cost(self,distance:float,weight:float,priority:int):
        return (distance * weight) + (priority * 100)

    def calculate_hauristic(self,current_pos:tuple, target_pos:tuple) -> float:
        
        return Drone.calculate_distance(current_pos, target_pos)

    def build_graph(self, deliverycase):
        # Teslimat vakasından bir grafik oluşturma
        package_graph = {}

        for i, package1 in enumerate(deliverycase.packages):
            edges = {}
            for j, package2 in enumerate(deliverycase.packages):
                if i != j:
                    distance = Drone.calculate_distance(package1.pos, package2.pos)
                    edges[package2.id] = distance 
                    
            edges = dict(sorted(edges.items(), key=lambda item: item[1]))

            for i, (node_id,distance) in enumerate(edges.items()):
                if i < self.KNN:
                    package_graph[(package1.id, node_id)] = distance

        return package_graph
    
    def extract_packages_positions(self, deliverycase):
        # Teslimat vakasından paket ve drone konumlarını çıkarma
        positions = {}
        for package in deliverycase.packages:
            positions[package.id] = package.pos
        return positions
    
    def build_drone_graph(self, graph, packages, drone):
        # Drone düğümlerini grafiğe ekleme
        drone_graphs = graph.copy()

        edges = {}
        for package in packages:
            distance = Drone.calculate_distance(drone.start_pos, package.pos)
            edges[package.id] = distance
        edges = dict(sorted(edges.items(), key=lambda item: item[1]))

        for i, (node_id,distance) in enumerate(edges.items()):
            if i < self.KNN:
                drone_graphs[(-1, node_id)] = distance
        return drone_graphs
        
    def build_adjacency_list(self,graph):
        adj = defaultdict(dict)
        for (u, v), cost in graph.items():
            adj[u][v] = cost
            # Uncomment this line if the graph is undirected:
            adj[v][u] = cost
        return adj

    def find_path(self, start, end, graph, positions, speed, start_time):
        adj = self.build_adjacency_list(graph)

        open_set = {start}
        came_from = {}

        # g_score: node -> (distance_so_far, arrival_time)
        g_score = defaultdict(lambda: [float('inf'), start_time])
        g_score[start] = [0, start_time]

        # f_score: node -> (estimated_total_cost, estimated_arrival_time)
        f_score = defaultdict(lambda: [float('inf'), start_time])
        h = self.calculate_hauristic(positions[start], positions[end])
        f_score[start] = [h, start_time + timedelta(seconds=h / speed)]

        while open_set:
            # Select node with the lowest f_score (total estimated cost)
            current = min(open_set, key=lambda node: f_score[node][0])

            if current == end:
                path = []
                total_cost = g_score[end]
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1], total_cost

            open_set.remove(current)

            for neighbor, distance in adj[current].items():
                current_time = g_score[current][1]
                travel_time = timedelta(seconds=distance / speed)
                arrival_time = current_time + travel_time

                # Check for no-fly zone conflict at the moment of travel
                penalty = self.deliverycase.is_edge_conflict_noflyzone(
                    positions[current], positions[neighbor], current_time
                ) * self.noflyzone_penalty
                total_distance = g_score[current][0] + distance + penalty

                # Only update if this path is better
                if total_distance < g_score[neighbor][0]:
                    came_from[neighbor] = current
                    g_score[neighbor] = [total_distance, arrival_time]

                    h = self.calculate_hauristic(positions[neighbor], positions[end])
                    f_score[neighbor] = [total_distance + h, arrival_time + timedelta(seconds=h / speed)]

                    open_set.add(neighbor)

        return None, [float('inf'), start_time]
    
    def delivery_rotue(self, deliverycase:DeliveryCase,drone:Drone , package:DronePath, time:datetime):
        temp_time = time
        drone_graph = self.build_drone_graph(self.build_graph(deliverycase), deliverycase.packages, drone)
        drone_positions = self.extract_packages_positions(deliverycase)
        drone_positions[-1] = drone.start_pos  # Add drone's starting position
        deliver_path = self.find_path(
            start=-1,  # Assuming -1 is the drone's starting position
            end=package.id,
            graph=drone_graph,
            positions=drone_positions,
            speed=drone.speed,
            start_time=temp_time
        )
        if deliver_path[0] is None:
            return None, None, None
        temp_time = deliver_path[1][1]  # Update arrival time
        return_path = self.find_path(
            start=package.id,
            end=-1,  # Assuming -1 is the drone's starting position
            graph=drone_graph,
            positions=drone_positions,
            speed=drone.speed,
            start_time=temp_time  # Use arrival time from delivery path
        )
        temp_time = return_path[1][1]
        return deliver_path,return_path,temp_time

    def select_best_drone(self, deliverycase:DeliveryCase, package,time):
        # En iyi drone yolunu seçme
        best_drone_id = None
        best_cost = float('inf')

        for drone in deliverycase.drones:
            if not drone.is_available(time) or drone.can_carry(package.weight) is False:
                continue
            deliver_path, return_path, temp_time = self.delivery_rotue(deliverycase, drone, package, time)
            
            deliver_energy_consumption = Drone.calculate_energy_consumption(deliver_path[1][0], package.weight)
            return_energy_consumption = Drone.calculate_energy_consumption(return_path[1][0], 0)
            
            total_energy_consumption = deliver_energy_consumption + return_energy_consumption
            total_cost = deliver_path[1][0] + return_path[1][0]
            if total_cost < best_cost and package.is_within_time_window(temp_time) and total_energy_consumption < drone.battery:
                best_drone_id = drone.id
                best_cost = total_cost

        print(f"Best Drone ID: {best_drone_id}")
        return best_drone_id

    def solve(self, deliverycase:DeliveryCase, **kwargs) -> Solution:
        print("A* algorithm with multi-drone assignment and time windows starting...")
        
        self.deliverycase = deliverycase
        solution = Solution()
        solution.solverName = "A* Solver"
        solution.Case = deliverycase
        solution.dronePaths = defaultdict(list)

        print(f"Start time: {deliverycase.casetime}")
        
        while deliverycase.get_next_available_package(deliverycase.casetime) is not None:
            available_packages = deliverycase.get_avabile_packages(deliverycase.casetime)
            available_packages = deliverycase.sort_packages_by_priority(available_packages)
            if not available_packages:
                print("No available packages at the moment.")
                print(f"time {deliverycase.casetime}")
                deliverycase.casetime = deliverycase.get_next_available_package(deliverycase.casetime).get_start_time()
                print(f"to time {deliverycase.casetime}")
                continue
            for package in available_packages:
                drone_id = self.select_best_drone(deliverycase, package, deliverycase.casetime)
                if drone_id is None:
                    print(f"No available drone for Package ID: {package.id}")
                    print(f"time {deliverycase.casetime}")
                    next_drones = deliverycase.next_available_drones()
                    temp = deliverycase.casetime
                    for drone in next_drones:
                        if drone.atBusyDatetime > deliverycase.casetime:
                            deliverycase.casetime = drone.atBusyDatetime
                            break
                    if temp == deliverycase.casetime:
                        package.set_cannot_deliver()
                        print(f"Package ID: {package.id} cannot be delivered at this time.")
                    print(f"to time {deliverycase.casetime}")
                    break
                drone = deliverycase.get_drone_by_id(drone_id)
                print(f"Selected Drone ID: {drone_id} for Package ID: {package.id}")
                deliver_path, return_path, time = self.delivery_rotue(deliverycase, drone, package, deliverycase.casetime)
                if deliver_path  or return_path:
                    drone_positions = self.extract_packages_positions(deliverycase)
                    drone_positions[-1] = drone.start_pos  # Add drone's starting position
                    solution.dronePaths[drone_id].append(
                        DronePath(
                            node_path=deliver_path[0],
                            node_positions=drone_positions,
                            isReturn=False,
                            cost=deliver_path[1][0]
                        )
                    )
                    solution.dronePaths[drone_id].append(
                        DronePath(
                            node_path=return_path[0],
                            node_positions=drone_positions,
                            isReturn=True,
                            cost=return_path[1][0]
                        )
                    )
                    deliver_energy_consumption = Drone.calculate_energy_consumption(deliver_path[1][0], package.weight)
                    return_energy_consumption = Drone.calculate_energy_consumption(return_path[1][0], 0)

                    total_energy_consumption = deliver_energy_consumption + return_energy_consumption

                    total_cost = deliver_path[1][0] + return_path[1][0]
                    solution.totalDistance += total_cost
                    solution.totalConsumption += total_energy_consumption
                    package.set_delivered()
                    drone.set_busy(time)


        return solution
