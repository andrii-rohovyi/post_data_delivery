from typing import Dict, List, Tuple


def extract_vector_from_pulp_variable(x: str) -> Dict[float, float]:
    """
    Function for formulating Dict of road vectors from PuLP variable

    Parameters
    ----------
    x: str
        String with pulp variable.
         Example: X_(0,_0)(_45,__45), what means road from (0, 0) -> (45, -45)

    Returns
    -------
    Dict[float, float]
        Dict with vector.Key - start position, Value - end position

    """
    x = x.replace(',__', ', -').replace('(_', '(-').replace('_', ' ')
    new_point_start_location = x.find(')(') + 1

    return {eval(x[2: new_point_start_location]): eval(x[new_point_start_location:])}


def extract_road_vector_from_mtsm_problem(x: str) -> str:
    """

    Parameters
    ----------
    x

    Returns
    -------

    """
    return x.split('&')[0]


def decode_list_from_vectors(points_graph: Dict[Tuple[float, float], Tuple[float, float]],
                             central_store: Tuple[float, float]
                             ) -> List[Tuple[float, float]]:
    """

    Parameters
    ----------
    points_graph
    central_store

    Returns
    -------

    """
    start_point = points_graph[central_store]
    points_sequence = [central_store, start_point]
    while start_point != central_store:
        start_point = points_graph[start_point]
        points_sequence += [start_point]

    return points_sequence[:-1]
