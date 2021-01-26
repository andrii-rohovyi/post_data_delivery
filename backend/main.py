import sys
import logging
from flask import Flask, request, jsonify

from backend.logistic import LogisticOptimizer

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


@app.route("/", methods=["POST"])
def main_page():
    """
    Main page for

    Returns
    -------

    """

    data = request.get_json(force=True)
    model = LogisticOptimizer(central_store=tuple(data['head_location']),
                              locations=[(x[0], x[1]) for x in data['stores_locations']],
                              amount_of_delivery_man=data['deliveryman_cnt'])
    result = model.solve_delivery_problem()
    result = [list(x) for x in result]

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
