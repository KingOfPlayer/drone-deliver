import random

class RandomCaseGenerator:
    def __init__(self):
        pass

    def random_drone(self, drone_id):
        return {
            "id": drone_id,  
            "max_weight": round(random.uniform(2.0, 6.0), 1),
            "battery": random.randint(8000, 20000),
            "speed": round(random.uniform(5.0, 12.0), 1),
            "start_pos": (random.randint(0, 100), random.randint(0, 100))
        }

    def random_delivery(self, delivery_id):
        start_time = random.randint(0, 60)
        end_time = random.randint(start_time + 1, start_time + 60)  
        return {
            "id": delivery_id,  
            "pos": (random.randint(0, 100), random.randint(0, 100)),
            "weight": round(random.uniform(0.5, 4.5), 1),
            "priority": random.randint(1, 5),
            "time_window": (start_time, end_time)
        }

    def random_no_fly_zone(self, nfz_id):
        x1, y1 = random.randint(0, 80), random.randint(0, 80)
        x2, y2 = x1 + random.randint(10, 20), y1 + random.randint(10, 20)
        coords = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        start_time = random.randint(0, 60)
        end_time = random.randint(start_time + 1, start_time + 60)
        return {
            "id": nfz_id,  
            "coordinates": coords,
            "active_time": (start_time, end_time)
        }

    def get_random_data(self, num_drones, num_packages, num_nfz):
        drones = [self.random_drone(i + 1) for i in range(num_drones)]
        packages = [self.random_delivery(i + 1) for i in range(num_packages)]
        no_fly_zones = [self.random_no_fly_zone(i + 1) for i in range(num_nfz)]
        return drones, packages,no_fly_zones