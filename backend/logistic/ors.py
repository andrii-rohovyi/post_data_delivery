import aiohttp
import os
import asyncio
import nest_asyncio
import itertools
from typing import List, Tuple, Dict, Coroutine, Any

from openrouteservice import convert

from logistic.config import MAX_WEIGHT

nest_asyncio.apply()


class ORS(object):

    def __init__(self, async_session: aiohttp.ClientSession):
        """
        Class for querying Google API

        Parameters
        ----------
        async_session: aiohttp.ClientSession
            Mode in which deliveryman moving
            There can be several modes that is supported: "driving-car", "foot-walking", "cycling-reglar"
        """
        self.session = async_session
        self.base_api_url = 'https://api.openrouteservice.org/v2/{}/{}'
        self.api_key = os.environ.get('ORS_API_KEY')

    async def fetch(self,
                    client: aiohttp.ClientSession,
                    points: List[Tuple[float, float]],
                    ref: str,
                    mode: str,
                    ) -> dict:
        """
        Fetch data from Openroute Service API
        Here you can find more detailed information about it: https://openrouteservice.org/dev/#/api-docs

        Parameters
        ----------
        client: aiohttp.ClientSession
            aiohttp client
        points: List[Tuple[float, float]]
            Points between each we need to query Openroute Service API
        ref: str
            Specifies a part of the API to call. Either 'matrix' or 'directions'. 
        mode: str
            Specifies a transport

        Returns
        -------
        dict
            With path from Openroute Service API and dropped nodes if there are any

        """
        if len(points) <= 1:
            return {'response': [], 'dropped_nodes': []}
        url = self.base_api_url.format(ref, mode)

        body = {}
        if ref == 'matrix':
            body = {"locations": points}
        elif ref == 'directions':
            body = {"coordinates": points}

        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': self.api_key,
            'Content-Type': 'application/json; charset=utf-8'
        }

        dropped_nodes = []
        async with client.post(url, json=body, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                return {'response': result, 'dropped_nodes': dropped_nodes}
            else:
                result = await resp.json()
                err = result['error']['message']
                idx_err = int(err.split(':')[0].split(' ')[-1])
                dropped_nodes.append(points[idx_err])
                del points[idx_err]
                if len(points) > 1:
                    updated_resp = await self.fetch(self.session, points, ref, mode)
                    dropped_nodes.extend(updated_resp['dropped_nodes'])
                    return {'response': updated_resp['response'], 'dropped_nodes': dropped_nodes}
                else:
                    return {'response': [], 'dropped_nodes': dropped_nodes}
            

    async def call_api(self,
                       points: Tuple[Tuple[float, float], Tuple[float, float]],
                       ref: str,
                       mode: str
                       ) -> Coroutine[Any, Any, Any]:
        """
        Querying Directions API in different sessions

        Parameters
        ----------
        points: Tuple[Tuple[float, float], Tuple[float, float]]
            Points between each we need to query Directions API
        ref: str
            Specifies a part of the API to call. Either 'matrix' or 'directions'. 
        mode: str
            Specifies a transport
        Returns
        -------

        """
        return await self.fetch(self.session, points, ref, mode)

    async def query(self,
                    points,
                    ref: str,
                    mode: str):
        """
        async method allowing us to await in the body of the function

        Parameters
        ----------
        points: List[Tuple[Tuple[float, float], Tuple[float, float]]]
            List of points tuples in (lat, lon) format between each we need to calculate duration of movement or directions.
            Examples:  1. [(30.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421),
                        (34.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421)]
                       2. [[(30.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421)], 
                            (30.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421)]]
        ref: str
            Specifies a part of the API to call. Either 'matrix' or 'directions'. 
        mode: str
            Specifies a transport

        Returns
        -------

        """
        returns = []
        if ref == 'matrix':
            returns = await asyncio.gather(self.call_api(points, ref, mode))
        elif ref == 'directions':
            returns = await asyncio.gather(*[self.call_api(point, ref, mode) if len(point) else [] for point in points])

        return returns

    def duration_calculation(self, points: List[Tuple[float, float]], mode: str) -> Dict[Tuple[float, float], float]:
        """
        Calculate duration for moving between points

        Parameters
        ----------
        points: List[List[float, float]]
            List of points tuples in (lat, lon) format between each we need to calculate duration of movement.
            Examples:  [(30.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421),
                        (34.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421)]
        mode: str
            Specifies a transport

        Returns
        -------
        Dict[Tuple[float, float], float]
            Dict with information about duration of movements between points
            Examples: {((30.302990054837696, 50.50609174896435),
                          (30.55375538507264, 50.55876662752421)): 9223372036854775807,
                         ((34.30299005483769, 50.50609174896435),
                          (30.55375538507264, 50.55876662752421)): 9223372036854775807]

        """
        ors_points = [[coord[1], coord[0]] for coord in points]
        returns = asyncio.run(self.query(ors_points, 'matrix', mode))

        durations = returns[0]['response']['durations']

        points_dictionaries = {(tuple(points[i]), tuple(points[j])): durations[i][j] if durations[i][j] else MAX_WEIGHT 
                                for j in range(len(points)) for i in range(len(points))}

        return points_dictionaries

    def directions_calculation(self, points: List[List[Tuple[float, float]]], mode: str) -> List[List[Tuple[float, float]]]:
        """
        Calculate direction for moving between points

        Parameters
        ----------
        points: List[List[float, float]]
            List of points tuples in (lat, lon) format between each we need to calculate duration of movement.
            Examples:  [(30.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421),
                        (34.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421)]
        mode: str
            Specifies a transport

        Returns
        -------
        List[List[List[float, float]]]
            List of list of coordinates 
            Examples:  [ 
                            [[50.5, 30.3],[50.55, 30.35], [50.6, 30.4]],
                            [[55.5, 35.3],[55.55, 35.35], [55.6, 35.4]]
                        ]

        """
        returns = asyncio.run(self.query(points, 'directions', mode))

        resps = [obj['response'] for obj in returns]
        dropped_nodes = list(itertools.chain.from_iterable([ret['dropped_nodes'] for ret in returns]))

        routes = [convert.decode_polyline(route['routes'][0]['geometry'])['coordinates'] if len(route) else [] for route in resps]
        routes = [[[coord[1], coord[0]] for coord in route] if len(route) else [] for route in routes ]

        return routes, dropped_nodes

