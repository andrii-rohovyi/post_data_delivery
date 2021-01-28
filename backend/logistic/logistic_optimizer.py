from typing import List, Tuple, Dict
from haversine import haversine
from itertools import combinations
from cached_property import cached_property
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


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
        self.total_locations = [central_store] + locations
        self.amount_of_delivery_man = amount_of_delivery_man

        # Create the routing index manager.
        self.manager = pywrapcp.RoutingIndexManager(len(self.total_locations), self.amount_of_delivery_man, 0)

    @cached_property
    def road_to_weight(self) -> Dict[Tuple[Tuple[float, float], Tuple[float, float]], float]:
        """
        Method for calculating weight in salesman problem between every points for optimization problem

        Returns
        -------
        ict[Tuple[Tuple[float, float], Tuple[float, float]], float]
            Dict with weights for each locations pairs in (lat, lon) format. \
            Example: ((0, 0), (45, 45)) : 2

        """
        points_to_haversine = {}
        for point_1, point_2 in combinations(self.total_locations, 2):
            hv = haversine(point_1, point_2)
            points_to_haversine.update({
                (point_1, point_2): hv,
                (point_2, point_1): hv
            })

        return points_to_haversine

    def weight_callback(self, from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = self.manager.IndexToNode(from_index)
        to_node = self.manager.IndexToNode(to_index)
        return self.road_to_weight[from_node, to_node]

    def decode_solution(self, solution, routing):
        routes = []
        for vehicle_id in range(self.amount_of_delivery_man):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                route.append(self.total_locations[self.manager.IndexToNode(index)])
                index = solution.Value(routing.NextVar(index))

            if len(route) > 1:
                routes.append(route)

        return routes

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

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(self.manager)

        transit_callback_index = routing.RegisterTransitCallback(self.weight_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Distance constraint.
        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            300000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name)
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        return self.decode_solution(solution, routing)

