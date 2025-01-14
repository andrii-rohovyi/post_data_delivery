from typing import List, Tuple, Dict, Union
from itertools import combinations, chain
from cached_property import cached_property
import time
import ortools
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from logistic.config import MAX_WEIGHT, SOLUTION_CALCULATION_MAX_TIME, MODE_CONVERTER
from logistic.utils import duration_approximation


class LogisticOptimizer(object):

    def __init__(self,
                 central_store: Dict[str, Union[Tuple[float, float], Tuple[int, int]]],
                 stores: List[Dict[str, Union[Tuple[float, float], int, Tuple[int, int]]]],
                 couriers: List[Dict[str, Union[str, int]]],
                 routing_manager: object,
                 approximation: bool = True):
        """
        Class for scheduling delivery process

        Parameters
        ----------
        central_store: Dict[str, Union[Tuple[float, float], Tuple[int, int]]]
           Central store (HQ or a starting point) with all info
           Examples: {"location": [50.486228, 30.472595], "time_window": [0, 1]} or {"location": [50.486228, 30.472595]}
        stores: List[Dict[str, Union[Tuple[float, float], int, Tuple[int, int]]]]
            List of stores with all their info
                Examples:  [ {"location": [50.489023, 30.467676], "demand": 1, "time_window": [0, 1] }]
                        OR [ {"location": [50.489023, 30.467676], "time_window": [0, 1] }]
                        OR [ {"location": [50.489023, 30.467676], "demand": 1 }]
        couriers: List[Dict[str, Union[str, int]]]
            List of couriers with all their info
            Examples: [{"capacity": 2, "transport": "walking"}] OR [{"transport": "walking"}]
        approximation: bool
            False if we don't use Google API, True otherwise
        """
        self.time_constraint = any([bool(point.get('time_window')) for point in chain([central_store], stores)])
        self.capacities_constraint = True if any(['demand' in x.keys() for x in stores]) else False
        self.central_store = central_store
        self.stores = stores
        self.couriers = couriers

        # There can be several modes that is supported: "driving", "walking", "bicycling"
        self.mode = MODE_CONVERTER[couriers[0]['transport']]  # TODO Add processing for different transport types for different couriers

        self.total_locations = [central_store['location']] + [store['location'] for store in stores]
        self.amount_of_couriers = len(couriers)

        if self.capacities_constraint:
            self.stores_demands = [0] + [store.get('demand', 0) for store in stores]
            self.couriers_capacities = [courier.get('capacity', 0) for courier in couriers]

        if self.time_constraint:
            self.time_windows = ([central_store.get('time_window', [int(time.time()), MAX_WEIGHT])]
                                 + [store.get('time_window', [int(time.time()), MAX_WEIGHT]) for store in stores])

        if not approximation:
            self.routing_manager = routing_manager
        self.approximation = approximation

        # Create the routing index manager.
        self.manager = pywrapcp.RoutingIndexManager(len(self.total_locations), self.amount_of_couriers, 0)

    @cached_property
    def road_to_weight(self) -> Dict[Tuple[Tuple[float, float], Tuple[float, float]], float]:
        """
        Method for calculating weight in salesman problem between every points for optimization problem

        Returns
        -------
        Dict[Tuple[Tuple[float, float], Tuple[float, float]], float]
            Dict with weights for each locations pairs in (lat, lon) format. \
            Example: ((0, 0), (45, 45)) : 2

        """
        points_to_weight = {(i, i): 0 for i in range(len(self.total_locations))}

        if self.approximation:
            for point_1, point_2 in combinations(enumerate(self.total_locations), 2):
                duration = duration_approximation(point_1=point_1[1], point_2=point_2[1], mode=self.mode)
                points_to_weight.update({
                    (point_1[0], point_2[0]): duration,
                    (point_2[0], point_1[0]): duration
                })
        else:
            points2indexes = {tuple(point): i for i, point in enumerate(self.total_locations)}
            new_points_weights = self.routing_manager.duration_calculation(self.total_locations, self.mode)
            points_to_weight.update({(points2indexes[key[0]], points2indexes[key[1]]): value for key, value in new_points_weights.items()})
        return points_to_weight

    def demand_callback(self, from_index) -> int:
        """
        Returns the demand of the node.

        Parameters
        ----------
        from_index

        Returns
        -------
        int
            Number of products demanded by a node (route)

        """
        # Convert from routing variable Index to demands NodeIndex.
        from_node = self.manager.IndexToNode(from_index)
        return self.stores_demands[from_node]

    def time_callback(self, from_index, to_index) -> float:
        """
        Returns the travel time between the two nodes.

        Parameters
        ----------
        from_index
        to_index
        Returns
        -------
        float
            Time to get from one node to another (route time)

        """
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = self.manager.IndexToNode(from_index)
        to_node = self.manager.IndexToNode(to_index)
        return self.road_to_weight[(from_node, to_node)]

    def decode_solution(self,
                        routing: ortools.constraint_solver.pywrapcp.RoutingModel,
                        solution: ortools.constraint_solver.pywrapcp.Assignment
                        ) -> Dict[str, Union[List[Dict], List[Dict]]]:
        """
        Decode ortools solution to REST format

        Parameters
        ----------
        routing: ortools.constraint_solver.pywrapcp.RoutingModel
            Routing that was using for solving Vehicle Routing Problem
        solution: ortools.constraint_solver.pywrapcp.Assignment
            Solution of problem

        Returns
        -------
        Dict[str, Union[List[Dict], List[Dict]]]
        Example: 
        {
            'routes': [
                {
                    'courier_id': 'aaa111', 
                    'route': [{'lat': 0, 'lng': 0}, {'lat': 1, 'lng': 1}], 
                    'detailed_route': [{'lat': 0, 'lng': 0}, {'lat': 0.5, 'lng': 0.5}, {'lat': 1, 'lng': 1}]
                },
                {
                    'courier_id': 'bbb111', 
                    'route': [{'lat': 0, 'lng': 0}, {'lat': 2, 'lng': 2}], 
                    'detailed_route': [{'lat': 0, 'lng': 0}, {'lat': 1, 'lng': 1}, {'lat': 1, 'lng': 1}]
                },               
            ], 
            'dropped_nodes': [{'lat': 6, 'lng': 6}] 
        }

        """
        # calculate dropping nodes
        dropped_nodes = []

        for node in range(routing.Size()):
            if routing.IsStart(node) or routing.IsEnd(node):
                continue
            if solution.Value(routing.NextVar(node)) == node:
                lat, lng = self.total_locations[self.manager.IndexToNode(node)]
                dropped_nodes.append({'lat': lat, 'lng': lng})

        # calculate route for deliveryman
        routes = []
        for courier_number in range(self.amount_of_couriers):
            index = routing.Start(courier_number)
            route = []
            while not routing.IsEnd(index):
                lat, lng = self.total_locations[self.manager.IndexToNode(index)]
                route.append({'lat': lat, 'lng': lng})
                index = solution.Value(routing.NextVar(index))

            courier_id = self.couriers[courier_number]['pid']
            routes.append({'courier_id': courier_id, 'route': route})

        points = [[[coords['lng'], coords['lat']] for coords in obj['route']] for obj in routes]

        detailed_routes, new_drop = self.routing_manager.directions_calculation(points, self.mode)
        dropped_nodes.extend([{'lat': node[1], 'lng': node[0]} for node in new_drop])

        for i, route in enumerate(routes):
            route['detailed_route'] = [{'lat': p[0], 'lng': p[1]} for p in detailed_routes[i]]

            route['route'] = [coords for coords in route['route'] if coords not in dropped_nodes]

        return {'routes': routes, 'dropped_nodes': dropped_nodes}

    def solve(self) -> Dict[str, Union[List[Tuple[int, int]], List[List[Tuple[int, int]]]]]:
        """
        The main method of the class. Method for solving delivery problem.
        Depending from hardness of request, we add different dimentions to solve a problem.
        Returns
        -------
        Dict[str, Union[List[Tuple[int, int]], List[List[Tuple[int, int]]]]]
            routes:
                List of sorted sequence of delivery points for each delivery man.
                Every points subset starts with store location
            dropped_modes:
                Nodes that can't be reached from central store
        """
        routing = pywrapcp.RoutingModel(self.manager)

        routing = self._add_time_dimention(routing)

        if self.capacities_constraint:
            routing = self._add_capacity_dimention(routing)

        # Allow to drop nodes.
        for node in range(1, len(self.total_locations)):
            routing.AddDisjunction([self.manager.NodeToIndex(node)], MAX_WEIGHT)

        search_parameters = self._create_search_parameters()

        solution = routing.SolveWithParameters(search_parameters)

        return self.decode_solution(solution=solution, routing=routing)

    def _add_capacity_dimention(self, routing):
        """
        Method for adding capacity dimention to routing.
        Returns
        -------
        Rounting with added capacity dimention.
        """

        demand_callback_index = routing.RegisterUnaryTransitCallback(self.demand_callback)

        dimension_name = 'Capacity'
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            self.couriers_capacities,  # vehicle maximum capacities
            True,  # start cumul to zero
            dimension_name)

        return routing

    def _add_time_dimention(self, routing):
        """
        Method for adding time window dimention to routing.
        Returns
        -------
        Rounting with added time window dimention.
        """

        transit_callback_index = routing.RegisterTransitCallback(self.time_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Time Windows constraint.
        dimension_name = 'Time'
        routing.AddDimension(
            transit_callback_index,
            MAX_WEIGHT if self.time_constraint else 0,  # allow waiting time
            MAX_WEIGHT,  # maximum time per vehicle
            False if self.time_constraint else True,  # Don't force start cumul to zero.
            dimension_name)

        time_dimension = routing.GetDimensionOrDie(dimension_name)

        # Add time window constraints for each location except depot.
        if self.time_constraint:
            for location_idx, time_window in enumerate(self.time_windows):
                if location_idx == 0:
                    continue
                index = self.manager.NodeToIndex(location_idx)
                time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
            # Add time window constraints for each vehicle start node.
            for vehicle_id in range(self.amount_of_couriers):
                index = routing.Start(vehicle_id)
                time_dimension.CumulVar(index).SetRange(self.time_windows[0][0],
                                                        self.time_windows[0][1])

            # Instantiate route start and end times to produce feasible times.
            for i in range(self.amount_of_couriers):
                routing.AddVariableMinimizedByFinalizer(
                    time_dimension.CumulVar(routing.Start(i)))
                routing.AddVariableMinimizedByFinalizer(
                    time_dimension.CumulVar(routing.End(i)))

        return routing

    def _create_search_parameters(self):
        """
        Method for creating search parameters for our tasks.
        Returns
        -------
        Search parameters for all of our problems.
        """

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()

        # distance search parameter
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # capacity search parameter
        if self.capacities_constraint:
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
            search_parameters.time_limit.FromSeconds(SOLUTION_CALCULATION_MAX_TIME)

        return search_parameters

