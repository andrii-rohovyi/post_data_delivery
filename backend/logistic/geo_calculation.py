import aiohttp
import os
import asyncio
import nest_asyncio
from typing import List, Tuple, Dict, Coroutine, Any

from logistic.config import MAX_WEIGHT

nest_asyncio.apply()


class GoogleQuerying(object):

    def __init__(self, mode: str):
        """
        Class for querying Google API

        Parameters
        ----------
        mode: str
            Mode in which deliveryman moving
            There can be several modes that is supported: "driving", "walking", "bicycling", "transit", "haversine"
        """
        self.mode = mode
        self.session = aiohttp.ClientSession()

    async def fetch(self,
                    client: aiohttp.ClientSession,
                    points: Tuple[Tuple[float, float], Tuple[float, float]]
                    ) -> Coroutine[dict, Any, Any]:
        """
        Fetch data from Direction API
        Here you can find more detailed information about it: https://developers.google.com/maps/documentation/directions/overview

        Parameters
        ----------
        client: aiohttp.ClientSession
            aiohttp client
        points: Tuple[Tuple[float, float], Tuple[float, float]]
            Points between each we need to query Directions API

        Returns
        -------
        Coroutine[dict, Any, Any]
            Coroutine of directions API response

        """
        async with client.get(
                f'https://maps.googleapis.com/maps/api/directions/json?origin={points[0][0]},{points[0][1]}&destination={points[1][0]},{points[1][1]}&mode={self.mode}&transit_mode=bus|subway|train|tram|rail&key={os.environ.get("API_KEY")}') as resp:
            assert resp.status == 200
            return await resp.json()

    async def call_api(self,
                       points: Tuple[Tuple[float, float], Tuple[float, float]]
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
        return await self.fetch(self.session, points)

    async def query_google(self,
                           points_connections: List[Tuple[Tuple[float, float], Tuple[float, float]]]
                           ):
        """
        async ethod allowing us to await in the body of the functio

        Parameters
        ----------
        points_connections: List[Tuple[Tuple[float, float], Tuple[float, float]]]
            List of points tuples in (lat, lon) format between each we need to calculate duration of movement.
            Examples:  [((30.302990054837696, 50.50609174896435),
                          (30.55375538507264, 50.55876662752421)),
                                             ((34.302990054837696, 50.50609174896435),
                          (30.55375538507264, 50.55876662752421))]

        Returns
        -------

        """
        returns = await asyncio.gather(*[self.call_api(points) for points in points_connections])
        await self.session.close()

        return returns

    def duration_calculation(self, points_connections: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
        """
        Calculate duration for moving between points_connections list

        Parameters
        ----------
        points_connections: List[Tuple[float, float]]
            List of points tuples in (lat, lon) format between each we need to calculate duration of movement.
            Examples:  [((30.302990054837696, 50.50609174896435),
                          (30.55375538507264, 50.55876662752421)),
                                             ((34.302990054837696, 50.50609174896435),
                          (30.55375538507264, 50.55876662752421))]

        Returns
        -------
        Dict[Tuple[float, float], float]
            Dict with information about duration of movements between points
            Examples: {((30.302990054837696, 50.50609174896435),
                          (30.55375538507264, 50.55876662752421)): 9223372036854775807,
                         ((34.30299005483769, 50.50609174896435),
                          (30.55375538507264, 50.55876662752421)): 9223372036854775807]

        """
        returns = asyncio.run(self.query_google(points_connections))
        points_dictionaries = {points_connections[i]: returns[i]['routes'][0]['legs'][0]['duration']['value']
                               if returns[i]['routes'] != [] else MAX_WEIGHT
                               for i in range(len(points_connections))
                               }

        return points_dictionaries
