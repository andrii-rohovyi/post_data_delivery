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
                 central_store: Tuple[float, float],
                 locations: List[Tuple[float, float]],
                 stores_demands: List[int],
                 amount_of_couriers: int,
                 couriers_capacities: List[int],
                 mode: str = 'driving'):
        """
        Class for scheduling delivery process

        Parameters
        ----------
        central_store: Tuple[float]
           Location of store from each delivery process starts in format (lat, lon)
        locations: List[Tuple[float, float]]
            List of all delivery points in format [(lat, lon).....]
        stores_demands: List[int]
            List of demands of each store
        amount_of_couriers: int
            Amount of couriers
        couriers_capacities: List[int]
            List of capacities of each courier
       mode: str
            Mode that is using for calculating graph weights.
            There can be several modes that is supported: "driving", "walking", "bicycling", "transit", "haversine"
        """
        self.total_locations = [central_store] + locations
        self.stores_demands = [0] + stores_demands
        self.amount_of_couriers = amount_of_couriers
        self.couriers_capacities = couriers_capacities
        self.mode = mode

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

    def solve(self):
        routing = pywrapcp.RoutingModel(self.manager)

        routing = self._add_distance_dimention(routing)
        routing = self._add_capacity_dimention(routing)

       # Allow to drop nodes.
        for node in range(1, len(self.total_locations)):
            routing.AddDisjunction([self.manager.NodeToIndex(node)], MAX_WEIGHT)

        search_parameters = self._create_search_parameters()

        solution = routing.SolveWithParameters(search_parameters)

        return self.decode_solution(solution=solution, routing=routing)

    def _add_distance_dimention(self, routing):

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

        demand_callback_index = routing.RegisterUnaryTransitCallback(self.demand_callback)

        dimension_name = 'Capacity'
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            self.couriers_capacities,  # vehicle maximum capacities
            True,  # start cumul to zero
            dimension_name)

        return routing

    def _create_search_parameters(self):

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()

        # distance search parameter
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # capacity search parameter
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)

        search_parameters.time_limit.FromSeconds(1)

        return search_parameters



