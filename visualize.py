from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

from solver import Solution


class CaseVisualizer:
    def visualize(self, solution: Solution):
        plt.figure(figsize=(14, 10))

        # Harita ayarları
        plt.xlim(-5, 105)
        plt.ylim(-5, 105)
        plt.grid(True, alpha=0.3)

        # No-fly zone'ları çiz
        for zone in solution.Case.noflyzones:
            polygon = Polygon(zone.coordinates, alpha=0.3, color='red', edgecolor='darkred', linewidth=2)
            plt.gca().add_patch(polygon)
            center = np.mean(zone.coordinates, axis=0)
            plt.text(center[0], center[1], f'NFZ-{zone.id}\n{zone.active_time[0].strftime("%X")}-{zone.active_time[1].strftime("%X")}',
                    ha='center', va='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

        # Paketleri çiz
        for package in solution.Case.packages:
            plt.scatter(package.pos[0], package.pos[1], s=80, c='gray', marker='o', alpha=0.5)
            plt.text(package.pos[0], package.pos[1] + 1.5, f'P{package.id}', fontsize=7, ha='center', color='gray')

        # Drone başlangıç noktaları
        for drone in solution.Case.drones:
            plt.scatter(drone.start_pos[0], drone.start_pos[1], s=200, c='green', marker='s',
                        edgecolor='darkgreen', linewidth=2)
            plt.text(drone.start_pos[0], drone.start_pos[1], f'D{drone.id}',
                    ha='center', va='center', fontsize=10, color='white', fontweight='bold')

        # Drone rotaları
        colors = ['blue', 'orange', 'purple', 'brown', 'cyan', 'magenta', 'olive', 'black']  # Extend if more drones
        drone_paths = solution.dronePaths

        for drone_id, paths in drone_paths.items():
            color = colors[drone_id % len(colors)]
            for i, path in enumerate(paths):
                points = np.array(path.points)
                linestyle = '--' if path.isReturn else '-'
                label = f'D{drone_id + 1} {"Return" if path.isReturn else "Delivery"}' if i < 2 else ""
                plt.plot(points[:, 0], points[:, 1], linestyle=linestyle, color=color, linewidth=2, label=label)

                # Draw arrows for direction
                for j in range(len(points) - 1):
                    dx, dy = points[j+1][0] - points[j][0], points[j+1][1] - points[j][1]
                    plt.arrow(points[j][0], points[j][1], dx * 0.8, dy * 0.8, shape='full', lw=0,
                            length_includes_head=True, head_width=1.2, head_length=2, color=color, alpha=0.5)

                # Optional: mark delivery points with stars
                if not path.isReturn and len(points) > 1:
                    delivery_point = points[-1]
                    plt.scatter(delivery_point[0], delivery_point[1], marker='*', s=150, color=color, edgecolor='black', zorder=5)

        # Başlık ve eksen etiketleri
        plt.title(f'Drone Delivery Plan - {solution.solverName}', fontsize=14, fontweight='bold')
        plt.xlabel('X Koordinatı (metre)')
        plt.ylabel('Y Koordinatı (metre)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        # Add solver info box (top right corner inside plot)
        info_text = (f"Solver: {solution.solverName}\n"
                     f"Total Distance: {solution.totalDistance:.2f} m\n"
                     f"Total Consumption: {solution.totalConsumption:.2f} mah")

        plt.gca().text(1.02, 0.1, info_text, transform=plt.gca().transAxes, fontsize=10,
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.axis('equal')
        plt.tight_layout()
        print(solution.Case.get_successful_delivery_percent())
        plt.show()
