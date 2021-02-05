import sys
import logging
from flask import Flask, request, jsonify

from logistic import LogisticOptimizer

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


@app.route("/", methods=["POST"])
def main_page():
    """
    Main server for choosing stores set for delivery man

    """

    data = request.get_json(force=True)
    model = LogisticOptimizer(central_store=tuple(data['head_location']),
                              locations=[(x[0], x[1]) for x in data['stores_locations']],
                              stores_demands=data['stores_demands'],
                              amount_of_couriers=data['amount_of_couriers'],
                              couriers_capacities=data['couriers_capacities'],
                              time_windows=data['time_windows'],
                              mode='haversine')
    result = model.solve()['routes']
    result = [list(x) for x in result]

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
