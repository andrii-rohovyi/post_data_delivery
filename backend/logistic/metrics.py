from haversine import haversine
from typing import List


def calculate_routes_distance(routes) -> List[float]:
    distances = []
    distance = 0
    for route in routes:
        for i, point in enumerate(route[:-1]):
            distance += haversine(point, route[i + 1])
        distances.append(distance)
    return distances
