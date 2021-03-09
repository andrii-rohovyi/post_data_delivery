import sys
import logging
from aiohttp import web
import aiohttp
import pprint
import asyncio

from logistic import LogisticOptimizer
from logistic.ors import ORS

routes = web.RouteTableDef()
logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


@routes.post("/")
async def main_page(request):
    """
    Main server for choosing stores set for delivery man

    """

    data = await request.json()
    model = LogisticOptimizer(central_store=data['central_store'],
                              stores=data['stores'],
                              couriers=data['couriers'],
                              routing_manager=ORS(request.app['ors_querer']),
                              approximation=False)
    pprint.pprint(model.road_to_weight)
    result = model.solve()

    return web.json_response(result)


def main():
    app = web.Application()
    app['ors_querer'] = aiohttp.ClientSession()
    app.add_routes(routes)
    web.run_app(app)


if __name__ == '__main__':
    asyncio.run(main())
