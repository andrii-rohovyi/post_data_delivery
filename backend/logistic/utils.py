from haversine import haversine
from typing import Tuple

from logistic.config import MODE_TO_SPEED


def duration_approximation(point_1: Tuple[float, float], point_2: Tuple[float, float], mode: str) -> float:
    """

    Parameters
    ----------
    point_1: Tuple[float, float]
        start point in (lat, lon) format
    point_2: Tuple[float, float]
        end point in (lat, lon) format
    mode: str
        Mode which we are trying to approximate
        There can be several modes that is supported: "driving", "walking", "bicycling", "transit"

    Returns
    -------
    float
        Duration of movement between points in seconds in choosing mode

    """
    distance = haversine(point_1, point_2)
    return distance / MODE_TO_SPEED[mode]

