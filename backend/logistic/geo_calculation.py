import aiohttp
import os
import asyncio
import nest_asyncio
from typing import List, Tuple, Dict, Coroutine, Any

from openrouteservice.client import Client as ORSClient

from logistic.config import MAX_WEIGHT

nest_asyncio.apply()


class AsyncQuerying(object):

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
        self.api_client = ORSClient(key=os.environ.get("ORS_API_KEY"))

    async def fetch_distance_matrix(self,
                                    client: aiohttp.ClientSession,
                                    points: List[Tuple[float, float]]
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

        Returns
        -------
        dict
            Coroutine of Openroute Service API response

        """
        async with client.get(
                f'https://api.openrouteservice.org/matrix?api_key={s.environ.get("ORS_API_KEY")}&profile={self.mode}&locations={'|'.join([','.join([str(coord[1]), str(coord[0])]) for coord in coords])}') as resp:
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
        returns = asyncio.run(self.fetch_distance_matrix(points))
        durations = returns[i]['durations']
        points_dictionaries = {(points[i], points[j]): durations[i][j] if durations[i][j] else MAX_WEIGHT 
                                for j in range(len(points)) for i in range(len(points))}

        return points_dictionaries
