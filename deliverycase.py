
from datetime import datetime, timedelta
from typing import Any, List
from drone import Drone
from noflyzone import NoFlyZone
from package import Package

class DeliveryCase:
    casetime: datetime = datetime.now()
    drones:List[Drone] = []
    packages:List[Package] = []
    noflyzones:List[NoFlyZone] = []

    def __init__(self,casetime:datetime, drones: list[dict[str, Any]], packages: list[dict[str, Any]], noflyzones: list[dict[str, Any]]):
        self.casetime = casetime

        # Drone'ları yükle
        for d in drones:
            drone = Drone(
                id=d["id"],
                max_weight=d["max_weight"],
                battery=d["battery"],
                speed=d["speed"],
                start_pos=d["start_pos"],
                atBusyDatetime=self.casetime
            )
            self.drones.append(drone)

        # Paketleri yükle
        for d in packages:
            start_minutes = d["time_window"][0]
            end_minutes = d["time_window"][1]

            start_time = self.casetime + timedelta(minutes=start_minutes)
            end_time = self.casetime + timedelta(minutes=end_minutes)

            package = Package(
                id=d["id"],
                pos=d["pos"],
                weight=d["weight"],
                priority=d["priority"],
                time_window=(start_time, end_time)
            )
            # package.delivered = False
            self.packages.append(package)

        # No-fly zone'ları yükle
        for nfz in noflyzones:
            start_minutes = nfz["active_time"][0]
            end_minutes = nfz["active_time"][1]

            start_time = self.casetime + timedelta(minutes=start_minutes)
            end_time = self.casetime + timedelta(minutes=end_minutes)

            zone = NoFlyZone(
                id=nfz["id"],
                coordinates=nfz["coordinates"],
                active_time=(start_time, end_time)
            )
            self.noflyzones.append(zone)

    def get_avabile_packages(self,datetime: datetime) -> List[Package]:
        ## Verilen tarihe göre teslim edilebilecek paketleri döndür
        available_packages = []
        for package in self.packages:
            if not package.delivered and package.is_within_time_window(datetime) and package.can_deliver:
                available_packages.append(package)
        return available_packages
    
    def sort_packages_by_priority(self, packages: List[Package]) -> List[Package]:
        ## Paketleri önceliğe göre sırala
        return sorted(packages, key=lambda p: p.priority, reverse=True)

    def get_next_available_package(self, datetime: datetime) -> Package:
        ## Verilen tarihe göre en yakın teslim edilebilecek paketi döndür
        future_package = [package for package in self.packages if package.time_window[0] > datetime and not package.delivered and package.can_deliver]
        if future_package == []:
            return None
        return min(future_package, key=lambda p: p.time_window[0])

    def find_nearest_drone(self, package: Package, time:datetime) -> Drone:
        ## Verilen pakete en yakın dronu bul
        nearest_drone = None
        min_distance = float('inf')
        for drone in self.drones:
            if drone.battery > 0:
                distance = drone.calculate_distance(drone.start_pos, package.pos)
                if distance < min_distance and drone.can_carry(package.weight) and drone.is_available(time):
                    min_distance = distance
                    nearest_drone = drone
                    
        return nearest_drone
    
    def next_available_drones(self) -> Drone:
        ## En yakın işi bitecek dronu bul
        next_drone = None
        sorted_drones = sorted(self.drones, key=lambda d: d.atBusyDatetime if d.atBusyDatetime else datetime.max)
        
        return sorted_drones

    def is_case_completed(self) -> bool:
        ## Tüm paketler teslim edildiyse True döndür
        return all(package.delivered for package in self.packages)
    
    def is_edge_conflict_noflyzone(self, start_pos: tuple[float, float], end_pos: tuple[float, float], time: datetime) -> bool:
        ## Verilen başlangıç ve bitiş konumları için no-fly zone ile çakışma var mı kontrol et
        for zone in self.noflyzones:
            if zone.is_active(time):
                if zone.is_path_conflict(start_pos, end_pos):
                    return True
        return False

    def get_drone_by_id(self, drone_id: int) -> Drone:
        ## Drone ID'sine göre dronu döndür
        for drone in self.drones:
            if drone.id == drone_id:
                return drone
        return None
    
    def get_successful_delivery_percent(self) -> float:
        ## Başarılı teslimat yüzdesini döndür
        if not self.packages:
            return 0.0
        successful_deliveries = sum(1 for package in self.packages if package.delivered)
        print(f"Successful Deliveries: {successful_deliveries} out of {len(self.packages)}")
        return (successful_deliveries / len(self.packages)) * 100.0

    def case_summary(self):
        ## Özet bilgileri döndür
        print("Drone Sayısı:", len(self.drones))
        for drone in self.drones:
            print(f"Drone ID: {drone.id}, Max Weight: {drone.max_weight}, Battery: {drone.battery}, Speed: {drone.speed}, Start Position: {drone.start_pos}")
        print("Paket Sayısı:", len(self.packages))
        for package in self.packages:
            print(f"Package ID: {package.id}, Position: {package.pos}, Weight: {package.weight}, Priority: {package.priority}, Time Window: {package.time_window[0].strftime('%X')} to {package.time_window[1].strftime('%X')}, Delivered: {package.delivered}")
        print("No-Fly Zone Sayısı:", len(self.noflyzones))
        for zone in self.noflyzones:
            print(f"No-Fly Zone ID: {zone.id}, Coordinates: {zone.coordinates}, Active Time: {zone.active_time[0].strftime('%X')} to {zone.active_time[1].strftime('%X')}")