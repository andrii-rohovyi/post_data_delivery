from typing import List, Tuple, Dict, Union
from haversine import haversine
from itertools import combinations
from cached_property import cached_property
import googlemaps
import os
import ortools
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from logistic.config import MAX_WEIGHT


class LogisticOptimizer(object):

    def __init__(self,
                 central_store: Dict,
                 stores: List[Dict],
                 couriers: List[Dict],
                 mode: str = 'driving'):
        """
        Class for scheduling delivery process

        Parameters
        ----------
        central_store: Dict
           Central store (HQ or a starting point) with all info
        stores: List[Dict]
            List of stores with all their info
        couriers: List[Dict]
            List of couriers with all their info
        mode: str
            Mode that is using for calculating graph weights.
            There can be several modes that is supported: "driving", "walking", "bicycling", "transit", "haversine"
        """
        self.central_store = central_store
        self.stores = stores
        self.couriers = couriers
        self.mode = mode

        self.total_locations = [central_store['location']] + [store['location'] for store in stores]
        self.stores_demands = [0] + [store['demand'] for store in stores]
        self.amount_of_couriers = len(couriers)
        self.couriers_capacities = [courier['capacity'] for courier in couriers]
        self.time_windows = [central_store['time_window']] + [store['time_window'] for store in stores]
        
        if mode != 'haversine':
            self.gmaps = googlemaps.Client(key=os.environ.get('API_KEY'))

        # Create the routing index manager.
        self.manager = pywrapcp.RoutingIndexManager(len(self.total_locations), self.amount_of_couriers, 0)

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
        points_to_weight = {(i, i): 0 for i in range(len(self.total_locations))}

        for point_1, point_2 in combinations(enumerate(self.total_locations), 2):
            if self.mode == 'haversine':
                hv = haversine(point_1[1], point_2[1])
                points_to_weight.update({
                    (point_1[0], point_2[0]): hv,
                    (point_2[0], point_1[0]): hv
                })

            else:
                info_1 = self.gmaps.directions(origin=point_1[1],
                                               destination=point_2[1],
                                               mode=self.mode,
                                               transit_mode=["bus", "subway", "train", "tram", "rail"]
                                               )
                weight_1 = info_1[0]['legs'][0]['duration']['value'] if info_1 != [] else MAX_WEIGHT

                info_2 = self.gmaps.directions(origin=point_2[1],
                                               destination=point_1[1],
                                               mode=self.mode,
                                               transit_mode=["bus", "subway", "train", "tram", "rail"]
                                               )
                weight_2 = info_2[0]['legs'][0]['duration']['value'] if info_2 != [] else MAX_WEIGHT

                points_to_weight.update({
                    (point_1[0], point_2[0]): weight_1,
                    (point_2[0], point_1[0]): weight_2
                })

        return points_to_weight

    def weight_callback(self, from_index, to_index) -> float:
        """
        Returns the weight between the two nodes.

        Parameters
        ----------
        from_index
        to_index

        Returns
        -------
        float
            Weight of node (route)

        """
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = self.manager.IndexToNode(from_index)
        to_node = self.manager.IndexToNode(to_index)
        return self.road_to_weight[(from_node, to_node)]

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
                        ) -> Dict[str, Union[List[Tuple[int, int]], List[List[Tuple[int, int]]]]]:
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
        Dict[str, Union[List[Tuple[int, int]], List[List[Tuple[int, int]]]]]
            List of routes that build for deliverymen amd list of nodes that can't be reached in this mode from
            central store
            Example: {'routes': [[(0, 0), (-84, -15), (-36, 107), (-71, -4), (23, 55)]], 'dropped_nodes': [] }

        """
        # calculate dropping nodes
        dropped_nodes = []

        for node in range(routing.Size()):
            if routing.IsStart(node) or routing.IsEnd(node):
                continue
            if solution.Value(routing.NextVar(node)) == node:
                dropped_nodes.append(self.total_locations[self.manager.IndexToNode(node)])

        # calculate route for deliveryman
        routes = []
        for vehicle_id in range(self.amount_of_couriers):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                route.append(self.total_locations[self.manager.IndexToNode(index)])
                index = solution.Value(routing.NextVar(index))

            if len(route) > 1:
                routes.append(route)

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

        routing = self._add_distance_dimention(routing)
        routing = self._add_time_window_dimention(routing)
        routing = self._add_capacity_dimention(routing)

       # Allow to drop nodes.
        for node in range(1, len(self.total_locations)):
            routing.AddDisjunction([self.manager.NodeToIndex(node)], MAX_WEIGHT)

        search_parameters = self._create_search_parameters()

        solution = routing.SolveWithParameters(search_parameters)

        return self.decode_solution(solution=solution, routing=routing)

    def _add_distance_dimention(self, routing):
        """
        Method for adding distance dimention to routing.
        Returns
        -------
        Rounting with added distance dimention.
        """

        transit_callback_index = routing.RegisterTransitCallback(self.weight_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Distance constraint.
        dimension_name = 'Distance'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            MAX_WEIGHT,  # vehicle maximum travel weight
            True,  # start cumul to zero
            dimension_name)

        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

        return routing

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

    def _add_time_window_dimention(self, routing):
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
            30,  # allow waiting time
            30,  # maximum time per vehicle
            False,  # Don't force start cumul to zero.
            dimension_name)

        time_dimension = routing.GetDimensionOrDie(dimension_name)
        # Add time window constraints for each location except depot.
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
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)

        search_parameters.time_limit.FromSeconds(1)

        return search_parameters

