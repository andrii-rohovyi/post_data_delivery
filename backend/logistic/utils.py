from typing import Dict


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
