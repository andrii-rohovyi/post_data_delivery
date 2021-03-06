import aiohttp
import os
import asyncio
import nest_asyncio
from typing import List, Tuple, Dict, Coroutine, Any

from openrouteservice import convert

from logistic.config import MAX_WEIGHT

nest_asyncio.apply()


class ORS(object):

    def __init__(self, mode: str):
        """
        Class for querying Google API

        Parameters
        ----------
        mode: str
            Mode in which deliveryman moving
            There can be several modes that is supported: "driving-car", "foot-walking", "cycling-reglar"
        """
        self.mode = mode
        self.session = aiohttp.ClientSession()
        self.base_api_url = 'https://api.openrouteservice.org/v2/{}/{}'
        self.api_key = os.environ.get('ORS_API_KEY')

    async def fetch(self,
                    client: aiohttp.ClientSession,
                    points: List[Tuple[float, float]],
                    ref: str
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

        Returns
        -------
        dict
            Coroutine of Openroute Service API response

        """
        url = self.base_api_url.format(ref, self.mode)

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

        async with client.post(url, json=body, headers=headers) as resp:
            assert resp.status == 200
            return await resp.json()

    async def call_api(self,
                       points: Tuple[Tuple[float, float], Tuple[float, float]],
                       ref
                       ) -> Coroutine[Any, Any, Any]:
        """
        Querying Directions API in different sessions

        Parameters
        ----------
        points: Tuple[Tuple[float, float], Tuple[float, float]]
            Points between each we need to query Directions API
        Returns
        -------

        """
        return await self.fetch(self.session, points, ref)

    async def query(self,
                    points,
                    ref: str
                    ):
        """
        async ethod allowing us to await in the body of the functio

        Parameters
        ----------
        points: List[Tuple[Tuple[float, float], Tuple[float, float]]]
            List of points tuples in (lat, lon) format between each we need to calculate duration of movement.
            Examples:  1. [(30.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421),
                        (34.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421)]
                       2. [[(30.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421)], 
                            (30.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421)]]
        ref: str
            Specifies a part of the API to call. Either 'matrix' or 'directions'. 

        Returns
        -------

        """
        returns = []
        if ref == 'matrix':
            returns = await asyncio.gather(self.call_api(points, ref))
        elif ref == 'directions':
            returns = await asyncio.gather(*[self.call_api(points, ref) for points in points_connections])
        await self.session.close()

        return returns

    def duration_calculation(self, points: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
        """
        Calculate duration for moving between points_connections list

        Parameters
        ----------
        points: List[Tuple[float, float]]
            List of points tuples in (lat, lon) format between each we need to calculate duration of movement.
            Examples:  [(30.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421),
                        (34.302990054837696, 50.50609174896435),(30.55375538507264, 50.55876662752421)]

        Returns
        -------
        Dict[Tuple[float, float], float]
            Dict with information about duration of movements between points
            Examples: {((30.302990054837696, 50.50609174896435),
                          (30.55375538507264, 50.55876662752421)): 9223372036854775807,
                         ((34.30299005483769, 50.50609174896435),
                          (30.55375538507264, 50.55876662752421)): 9223372036854775807]

        """
        
        returns = asyncio.run(self.query(points, 'matrix'))

        durations = returns[0]['durations']

        points_dictionaries = {(tuple(points[i]), tuple(points[j])): durations[i][j] if durations[i][j] else MAX_WEIGHT 
                                for j in range(len(points)) for i in range(len(points))}

        return points_dictionaries

    def directions_calculation(self, point):
        returns = asyncio.run(self.query(points, 'directions'))
        routes = [convert.decode_polyline(route['routes'][0]['geometry']) for route in returns]

        return routes

