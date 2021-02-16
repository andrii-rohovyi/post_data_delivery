import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from logistic import LogisticOptimizer

app = Flask(__name__)
CORS(app)
logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


@app.route("/", methods=["POST"])
@cross_origin(origins=['http://localhost:3000', 'localhost', '0.0.0.0:3000', '0.0.0.0'])
def main_page():
    """
    Main server for choosing stores set for delivery man

    """
    print(request.get_json(force=True))

    data = request.get_json(force=True)
    model = LogisticOptimizer(central_store=tuple(data['head_location']),
                              locations=[(x[0], x[1]) for x in data['stores_locations']],
                              amount_of_delivery_man=data['deliveryman_cnt'],
                              mode='haversine')
    result = model.solve_delivery_problem()['routes']
    result = [list(x) for x in result]
    print(result)
    print(len(result[0]), len(result[1]))
    r = [[{'lat': p[0], 'lng': p[1]} for p in points] for points in result]
    print(r)

    return jsonify(r)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
