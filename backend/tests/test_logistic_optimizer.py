from unittest import TestCase
import time
from random import uniform, randrange

from logistic import LogisticOptimizer


class TestLogisticOptimizer(TestCase):

    def test_capacity_limits_and_result_changing(self):
        central_store = {'location': (50.45, 30.51)}

        locations = [{'location': (50.46, 30.49), "demand": 1}, {'location': (50.485212, 30.505732), "demand": 2},
                     {'location': (50.450190, 30.502826), "demand": 1}]

        model = LogisticOptimizer(central_store=central_store,
                                  stores=locations,
                                  couriers=[{'pid': i, 'transport': 'bicycling', 'capacity': 2} for i in range(2)],
                                  approximation=True)
        solution = model.solve()
        self.assertTrue([(50.45, 30.51), (50.485212, 30.505732)] in solution['routes'].values())
        self.assertTrue([(50.45, 30.51), (50.450190, 30.502826), (50.46, 30.49)] in solution['routes'].values())

    def test_nodes_dropping_demand_is_not_satisfied(self):
        central_store = {'location': (50.45, 30.51)}

        locations = [{'location': (50.46, 30.49), "demand": 1}, {'location': (50.485212, 30.505732), "demand": 3},
                     {'location': (50.450190, 30.502826), "demand": 1}]

        model = LogisticOptimizer(central_store=central_store,
                                  stores=locations,
                                  couriers=[{'pid': i, 'transport': 'bicycling', 'capacity': 2} for i in range(2)],
                                  approximation=True)
        solution = model.solve()
        self.assertTrue(solution['dropped_nodes'] == [(50.485212, 30.505732)])
        self.assertTrue(len(solution['routes'].keys()) == 1)

    def test_time_and_demand_constraints(self):
        central_store = {'location': (50.45, 30.51)}

        unix_time = int(time.time())

        locations = [{'location': (50.46, 30.49), "demand": 1, 'time_window': [unix_time, unix_time + 2000000]},
                     {'location': (50.485212, 30.505732), "demand": 3},
                     {'location': (50.450190, 30.502826), "demand": 1, 'time_window': [unix_time, unix_time + 60]}
                     ]

        model = LogisticOptimizer(central_store=central_store,
                                  stores=locations,
                                  couriers=[{'pid': i, 'transport': 'bicycling', 'capacity': i} for i in range(2)],
                                  approximation=True)
        solution = model.solve()
        self.assertTrue(solution['dropped_nodes'] == [(50.485212, 30.505732), (50.45019, 30.502826)])
        self.assertTrue(solution['routes'][1] == [(50.45, 30.51), (50.46, 30.49)])

    def test_time_constraint(self):
        central_store = {'location': (50.45, 30.51)}

        unix_time = int(time.time())

        locations = [{'location': (50.46, 30.49), "demand": 1, 'time_window': [unix_time, unix_time + 2000000]},
                     {'location': (50.485212, 30.505732)},
                     {'location': (50.450190, 30.502826), "demand": 1, 'time_window': [unix_time, unix_time + 60]}
                     ]

        model = LogisticOptimizer(central_store=central_store,
                                  stores=locations,
                                  couriers=[{'pid': i, 'transport': 'bicycling', 'capacity': i} for i in range(2)],
                                  approximation=True)
        solution = model.solve()
        self.assertTrue(solution['dropped_nodes'] == [(50.45019, 30.502826)])

    def test_correct_pids(self):
        central_store = {'location': (50.45, 30.51)}

        locations = [{'location': (50.46, 30.49), "demand": 3},
                     {'location': (50.485212, 30.505732), "demand": 2},
                     {'location': (50.450190, 30.502826), "demand": 1}
                     ]

        model = LogisticOptimizer(central_store=central_store,
                                  stores=locations,
                                  couriers=[{'pid': i, 'transport': 'bicycling', 'capacity': i} for i in range(4)],
                                  approximation=True)
        solution = model.solve()
        self.assertTrue(solution['routes'][1] == [(50.45, 30.51), (50.45019, 30.502826)])
        self.assertTrue(solution['routes'][2] == [(50.45, 30.51), (50.485212, 30.505732)])
        self.assertTrue(solution['routes'][3] == [(50.45, 30.51), (50.46, 30.49)])

    def test_complex_solution(self):
        central_store = {'location': (30.5029689, 50.4568971)}
        locations = [{'location': (30.479039892023273, 50.327305730848174)},
                     {'location': (30.62140862721199, 50.40379998051621)},
                     {'location': (30.65705362588355, 50.34996188580664)},
                     {'location': (30.858471191798756, 50.29299151372923)},
                     {'location': (30.21467812222614, 50.456185368592195)}]

        model = LogisticOptimizer(central_store=central_store,
                                  stores=locations,
                                  couriers=[{'pid': i, 'transport': 'driving'} for i in range(2)],
                                  approximation=True)
        model.road_to_weight = {(0, 0): 0,
                                (1, 1): 0,
                                (2, 2): 0,
                                (3, 3): 0,
                                (4, 4): 0,
                                (5, 5): 0,
                                (0, 1): 3056,
                                (1, 0): 2185,
                                (0, 2): 2827,
                                (2, 0): 2023,
                                (0, 3): 3149,
                                (3, 0): 2340,
                                (0, 4): 9223372036854775807,
                                (4, 0): 9223372036854775807,
                                (0, 5): 4074,
                                (5, 0): 4568,
                                (1, 2): 1934,
                                (2, 1): 1994,
                                (1, 3): 2059,
                                (3, 1): 2065,
                                (1, 4): 9223372036854775807,
                                (4, 1): 9223372036854775807,
                                (1, 5): 2877,
                                (5, 1): 2911,
                                (2, 3): 537,
                                (3, 2): 537,
                                (2, 4): 9223372036854775807,
                                (4, 2): 9223372036854775807,
                                (2, 5): 4871,
                                (5, 2): 4845,
                                (3, 4): 9223372036854775807,
                                (4, 3): 9223372036854775807,
                                (3, 5): 4942,
                                (5, 3): 4970,
                                (4, 5): 9223372036854775807,
                                (5, 4): 9223372036854775807}
        solution = model.solve()
        self.assertTrue(solution in [{'routes': {1: [(30.5029689, 50.4568971),
                                                     (30.62140862721199, 50.40379998051621),
                                                     (30.65705362588355, 50.34996188580664),
                                                     (30.479039892023273, 50.327305730848174),
                                                     (30.21467812222614, 50.456185368592195)]},
                                      'dropped_nodes': [(30.858471191798756, 50.29299151372923)]},
                                     {'routes': {0: [(30.5029689, 50.4568971),
                                                     (30.62140862721199, 50.40379998051621),
                                                     (30.65705362588355, 50.34996188580664),
                                                     (30.479039892023273, 50.327305730848174),
                                                     (30.21467812222614, 50.456185368592195)]},
                                      'dropped_nodes': [(30.858471191798756, 50.29299151372923)]}
                                     ])

    def test_edge_time_for_calculations(self):
        central_store = {'location': (30.19, 30.86)}

        locations = [{'location': (uniform(30.19, 30.86), uniform(50.2, 50.6))}
                     for x in range(40)]

        model = LogisticOptimizer(central_store=central_store,
                                  stores=locations,
                                  couriers=[{'pid': i, 'transport': 'bicycling', 'capacity': i} for i in range(10)],
                                  approximation=True)
        start_time = time.time()
        solution = model.solve()
        self.assertTrue(time.time() - start_time < 1.5)

    def test_edge_time_for_calculations_with_capacity_constraint(self):
        central_store = {'location': (30.19, 30.86)}

        locations = [{'location': (uniform(30.19, 30.86), uniform(50.2, 50.6)), "demand": randrange(0, 10)}
                     for x in range(40)]

        model = LogisticOptimizer(central_store=central_store,
                                  stores=locations,
                                  couriers=[{'pid': i, 'transport': 'bicycling', 'capacity': i} for i in range(10)],
                                  approximation=True)
        start_time = time.time()
        solution = model.solve()
        self.assertTrue(time.time() - start_time < 1.5)

    def test_edge_time_for_calculations_with_time_constraint(self):
        central_store = {'location': (30.19, 30.86)}
        unix_time = int(time.time())

        locations = [{'location': (uniform(30.19, 30.86), uniform(50.2, 50.6)),
                      "time_window": [unix_time, unix_time + randrange(0, 1000000)]}
                     for x in range(40)]

        model = LogisticOptimizer(central_store=central_store,
                                  stores=locations,
                                  couriers=[{'pid': i, 'transport': 'bicycling', 'capacity': i} for i in range(10)],
                                  approximation=True)
        start_time = time.time()
        solution = model.solve()
        self.assertTrue(time.time() - start_time < 1.5)
