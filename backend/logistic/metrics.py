from haversine import haversine
from typing import List, Tuple


def calculate_routes_distance(routes: List[List[Tuple[int, int]]]) -> List[float]:
    """
    Function for calculating vector of distances for routes to measure efficiency of solution

    Parameters
    ----------
    routes: List[List[Tuple[int, int]]]
        List of routes that build for deliverymen
        Example: [[(0, 0), (-84, -15), (-36, 107), (-71, -4), (23, 55)]]
    Returns
    -------
    List[float]
        List of distances
        Example: [34079.48355817763] (for the case up)

    """
    distances = []
    distance = 0
    for route in routes:
        for i, point in enumerate(route[:-1]):
            distance += haversine(point, route[i + 1])
        distances.append(distance)

    return distances
