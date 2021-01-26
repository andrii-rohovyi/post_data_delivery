from typing import List, Tuple, Dict
from haversine import haversine
import pulp as pl
import logging
from sklearn.cluster import KMeans
import numpy as np

from logistic.utils import extract_vector_from_pulp_variable


class LogisticOptimizer(object):

    def __init__(self,
                 locations: List[Tuple[float, float]],
                 central_store: Tuple[float, float],
                 amount_of_delivery_man: int):
        """
        Class for scheduling delivery process

        Parameters
        ----------
        locations: List[Tuple[float, float]]
            List of all delivery points in format [(lat, lon).....]
        central_store: Tuple[float]
           Location of store from each delivery process starts in format (lat, lon)
        amount_of_delivery_man: int
            Amount of delivery man
        """
        self.locations = locations
        self.central_store = central_store
        self.total_locations = locations + [central_store]
        self.amount_of_delivery_man = amount_of_delivery_man
        self.road_to_weight = self.calculate_roads_weight()

    def calculate_roads_weight(self) -> Dict[str, float]:
        """
        Method for calculating weight in salesman problem between every points for optimization problem

        Returns
        -------
        Dict[str, float]
            Dict with weights for each locations pairs in (lat, lon) format. \
            Example: '((0, 0), (45, 45))' : 2

        """
        points_to_haversine = {}
        for i, point_1 in enumerate(self.total_locations):
            for j, point_2 in enumerate(self.total_locations[i + 1:]):
                points_to_haversine[f'{point_1}{point_2}'] = haversine(point_1, point_2)
                points_to_haversine[f'{point_2}{point_1}'] = points_to_haversine[f'{point_1}{point_2}']

        return points_to_haversine

    def salesman_problem(self, locations: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Method for solving Salesman Problem for individual person using PuLP package

        More detailed information you can find here: https://en.wikipedia.org/wiki/Travelling_salesman_problem

        Parameters
        ----------
        locations: List[Tuple[float, float]]
            List of delivery points for 1 delivery man in format [(lat, lon).....]

        Returns
        -------
        List[Tuple[float, float]]
            Sorted list of delivery points for 1 delivery man in format [(lat, lon).....]

        """
        X_var = pl.LpVariable.dicts("X",
                                    [f'{x}{y}' for x in locations for y in locations if x != y],
                                    cat=pl.LpBinary)
        n = len(locations)
        U_var = pl.LpVariable.dicts("U",
                                    [str(x) for x in locations[1:]])

        prob = pl.LpProblem("Schedule", pl.LpMinimize)

        prob += pl.lpSum([self.road_to_weight[i] * X_var[i] for i in X_var])
        for i in locations:
            prob += pl.lpSum([X_var[f'{i}{j}'] for j in locations if i != j]
                             ) == 1, f"From point {i} can be just one road to another point"
        for i in locations:
            prob += pl.lpSum([X_var[f'{j}{i}'] for j in locations if i != j]
                             ) == 1, f"In point {i} can be just one road from another point"
        for point_1 in locations[1:]:
            for point_2 in locations[1:]:
                if point_1 != point_2:
                    prob += pl.lpSum([U_var[f'{point_1}'] - U_var[f'{point_2}'] + n * X_var[f'{point_1}{point_2}']]
                                     ) <= n - 1, f"Limitations for connectness between point {point_1} and {point_2}"
        prob += 1 <= pl.lpSum([U_var[f'{point_1}'] for point_1 in locations[1:]]
                              ) <= n - 1, "Limitations for dummy variables"
        logging.info(f'Status of optimization problem {pl.LpStatus[prob.solve()]}')
        points_graph = {}
        for v in prob.variables():
            if (v.name[0] == 'X') and (v.varValue == 1):
                points_graph.update(extract_vector_from_pulp_variable(v.name))
        start_point = points_graph[self.central_store]
        points_sequence = [self.central_store, start_point]
        while start_point != self.central_store:
            start_point = points_graph[start_point]
            points_sequence += [start_point]

        return points_sequence[:-1]

    def solve_delivery_problem(self) -> List[List[Tuple[float, float]]]:
        """
        Method for solving global delivery problem.
        The idea is to cluster delivery points using kMeans algorithm. We use the standard euclidian distance,
        not a haversine, because for distance in one 1 city it is not such a big difference. After it for each points
        subset we add store points and run Salesman problem for each points subset.

        Returns
        -------
        List[List[Tuple[float, float]]]
            List of sorted sequence of delivery points for each delivery man.
            Every points subset starts with store location

        """
        X = np.array([x for x in self.locations])
        sorted_stores_locations = []
        clustering = KMeans(n_clusters=self.amount_of_delivery_man).fit(X)
        for i in range(self.amount_of_delivery_man):
            location_subset = [x for j, x in enumerate(self.locations) if clustering.labels_[j] == i
                               ] + [self.central_store]
            sorted_stores_locations.append(self.salesman_problem(location_subset))

        return sorted_stores_locations

