import sys
import logging

import aiohttp_cors
import aiohttp_jinja2
import jinja2
from aiohttp import web
import aiohttp
import pprint

from logistic import LogisticOptimizer
from logistic.ors import ORS

from utils import del_none

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

routes = web.RouteTableDef()


@routes.post("/")
async def main_page(request):
    """
    Main server for choosing stores set for delivery man

    """
    data = await request.json()
    data = del_none(data)
    print(data)

    model = LogisticOptimizer(central_store=data['central_store'],
                              stores=data['stores'],
                              couriers=data['couriers'],
                              routing_manager=ORS(request.app['ors_querer']),
                              approximation=False)
    pprint.pprint(model.road_to_weight)
    result = model.solve()

    return web.json_response(result)


@routes.get("/front")
@aiohttp_jinja2.template('index.html')
def front(request):
    return


def main():
    app = web.Application()
    app.add_routes(routes)
    app.add_routes([web.static('/static', 'static')])

    # routes.static('/static', 'static')
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    # Configure CORS on all routes.
    for route in list(app.router.routes()):
        cors.add(route)
    
    app['ors_querer'] = aiohttp.ClientSession()
    web.run_app(app)


if __name__ == '__main__':
    main()

