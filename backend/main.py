import sys
import logging
from aiohttp import web
import pprint

from logistic import LogisticOptimizer

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
                              approximation=False)
    pprint.pprint(model.road_to_weight)
    result = model.solve()

    return web.json_response(result)


if __name__ == '__main__':
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)
