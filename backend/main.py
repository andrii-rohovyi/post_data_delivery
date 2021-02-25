import sys
import logging
from flask import Flask, request, jsonify
import pprint

from logistic import LogisticOptimizer
from utils import del_none


app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


@app.route("/", methods=["POST"])
def main_page():
    """
    Main server for choosing stores set for delivery man

    """

    data = del_none(request.get_json(force=True))
    model = LogisticOptimizer(central_store=data['central_store'],
                              stores=data['stores'],
                              couriers=data['couriers'],
                              approximation=True)
    print(model.mode)
    pprint.pprint(model.road_to_weight)
    result = model.solve()

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
