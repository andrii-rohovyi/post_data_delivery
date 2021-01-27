from typing import List, Tuple, Dict
from haversine import haversine
import pulp as pl
import logging
from collections import defaultdict
from sklearn.cluster import KMeans
import numpy as np
from itertools import product, combinations
from cached_property import cached_property

from logistic.utils import (extract_vector_from_pulp_variable,
                            decode_list_from_vectors)
from logistic.cofig import MIN_AMOUNT_OF_STORES_FOR_APPROXIMATION


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

    @cached_property
    def road_to_weight(self) -> Dict[str, float]:
        """
        Method for calculating weight in salesman problem between every points for optimization problem

        Returns
        -------
        Dict[str, float]
            Dict with weights for each locations pairs in (lat, lon) format. \
            Example: '((0, 0), (45, 45))' : 2

        """
        points_to_haversine = {}
        for point_1, point_2 in combinations(self.total_locations, 2):
            hv = haversine(point_1, point_2)
            points_to_haversine.update({
                f'{point_1}{point_2}': hv,
                f'{point_2}{point_1}': hv
            })

        return points_to_haversine

    def salesman_problem_mlp(self, locations: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
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

        # Define optimization variables
        X_var = pl.LpVariable.dicts("X",
                                    [f'{x}{y}' for x in locations for y in locations if x != y],
                                    cat=pl.LpBinary)
        n = len(locations)
        U_var = pl.LpVariable.dicts("U",
                                    [str(x) for x in locations[1:]])

        # Define the optimization problem
        prob = pl.LpProblem("Schedule", pl.LpMinimize)

        prob += pl.lpSum([self.road_to_weight[i] * X_var[i] for i in X_var])
        for i in locations:
            prob += pl.lpSum([X_var[f'{i}{j}'] for j in locations if i != j]
                             ) == 1, f"From point {i} can be just one road to another point"
        for i in locations:
            prob += pl.lpSum([X_var[f'{j}{i}'] for j in locations if i != j]
                             ) == 1, f"In point {i} can be just one road from another point"
        for point_1, point_2 in product(locations[1:], locations[1:]):
            if point_1 != point_2:
                prob += pl.lpSum([U_var[f'{point_1}'] - U_var[f'{point_2}'] + n * X_var[f'{point_1}{point_2}']]
                                 ) <= n - 1, f"Limitations for connectness between point {point_1} and {point_2}"
        prob += 1 <= pl.lpSum([U_var[f'{point_1}'] for point_1 in locations[1:]]
                              ) <= n - 1, "Limitations for dummy variables"
        logging.info(f'Status of 1-TSP optimization problem {pl.LpStatus[prob.solve()]}')
        points_graph = {}
        for v in prob.variables():
            if (v.name[0] == 'X') and (v.varValue == 1):
                points_graph.update(extract_vector_from_pulp_variable(v.name))

        return decode_list_from_vectors(points_graph=points_graph, central_store=self.central_store)

    def multiple_salesman_problem_mlp(self) -> List[List[Tuple[float, float]]]:
        """
        Here is the realization of MSTP using Linear Programming approach from https://arxiv.org/pdf/1803.09621.pdf
        from page 5. But with 1 difference 2a and 2b we use "<=" instead "=" in this case exist situations, when some
        deliverman (salesman) don't move to any stores.

        Returns
        -------
        List[List[Tuple[float, float]]]
            List of sorted sequence of delivery points for each delivery man.
            Every points subset starts with store location
        """

        # Define optimization variables
        X_var = pl.LpVariable.dicts("X",
                                    [f'{x}&{i}' for x in list(self.road_to_weight.keys())
                                     for i in range(self.amount_of_delivery_man)],
                                    cat=pl.LpBinary)
        U_var = pl.LpVariable.dicts("U",
                                    [f'{x}' for x in self.locations])
        n = len(self.total_locations)

        # Define the optimization problem

        prob = pl.LpProblem("Schedule", pl.LpMinimize)

        prob += pl.lpSum([self.road_to_weight[i.split('&')[0]] * X_var[i] for i in X_var])
        for i in self.locations:
            prob += pl.lpSum([X_var[f'{i}{j}&{k}']
                              for j in self.total_locations
                              for k in range(self.amount_of_delivery_man)
                              if i != j]
                             ) == 1, f"From point {i} can be just one road to another point"
        for i in self.locations:
            prob += pl.lpSum([X_var[f'{j}{i}&{k}']
                              for j in self.total_locations
                              for k in range(self.amount_of_delivery_man)
                              if i != j]
                             ) == 1, f"In point {i} can be just one road from another point"
        for k in range(self.amount_of_delivery_man):

            prob += pl.lpSum([X_var[f'{self.central_store}{i}&{k}'] for i in self.locations]) <= 1
            prob += pl.lpSum([X_var[f'{i}{self.central_store}&{k}'] for i in self.locations]) <= 1

            for i in self.locations:
                prob += pl.lpSum([X_var[f'{j}{i}&{k}'] for j in self.total_locations if j != i]
                                 ) == pl.lpSum([X_var[f'{i}{j}&{k}'] for j in self.total_locations if j != i]
                                               ), f'The number of times a delivery man {k} visits a non-depot location {i} equals the number of times it leaves the location'

        for point_1 in self.locations:
            for point_2 in self.locations:
                if point_1 != point_2:
                    prob += (U_var[f'{point_1}'] - U_var[f'{point_2}']
                             + (n - self.amount_of_delivery_man)
                             * pl.lpSum([X_var[f'{point_1}{point_2}&{k}'] for k in range(self.amount_of_delivery_man)]
                                        ) <= n - self.amount_of_delivery_man - 1)
        logging.info(f'Status of M-TSP optimization problem {pl.LpStatus[prob.solve()]}')

        # Decoding result
        points_graph = defaultdict(dict)
        for v in prob.variables():
            if (v.name[0] == 'X') and (v.varValue == 1):
                vector, deliver = v.name.split('&')
                deliver = int(deliver)
                points_graph[deliver].update(extract_vector_from_pulp_variable(vector))
        result = []
        for i in points_graph.keys():
            result.append(decode_list_from_vectors(points_graph=points_graph[i], central_store=self.central_store))

        return result

    def clustering_approximation(self) -> List[List[Tuple[float, float]]]:
        """
        Method for solving delivery problem.
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
            sorted_stores_locations.append(self.salesman_problem_mlp(location_subset))

        return sorted_stores_locations

    def solve_delivery_problem(self) -> List[List[Tuple[float, float]]]:
        """
        Method for solving delivery problem.
        Depending from hardness of request, we choose different solution to solve a problem.

        Returns
        -------
        List[List[Tuple[float, float]]]
            List of sorted sequence of delivery points for each delivery man.
            Every points subset starts with store location

        """
        if self.locations <= MIN_AMOUNT_OF_STORES_FOR_APPROXIMATION:
            return self.multiple_salesman_problem_mlp()
        else:
            return self.clustering_approximation()

