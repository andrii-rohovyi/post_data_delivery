import sys
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
import pprint
from logistic import LogisticOptimizer


app = Flask(__name__)
CORS(app)

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)


@cross_origin(origins=['http://localhost:3000', 'localhost', '0.0.0.0:3000', '0.0.0.0'])
@app.route("/", methods=["POST"])
def main_page():
    """
    Main server for choosing stores set for delivery man

    """

    data = request.get_json(force=True)
    model = LogisticOptimizer(central_store=data['central_store'],
                              stores=data['stores'],
                              couriers=data['couriers'],
                              approximation=False)
    print(model.mode)
    pprint.pprint(model.road_to_weight)
    result = model.solve()
    # print(result)
    # r = {
    #     'routes': [[{'lat': p[0], 'lng': p[1]} for p in point] for point in result.get('routes', [])],
    #     'dropped_nodes': [{'lat': p[0], 'lng': p[1]} for p in result.get('dropped_nodes', [])]
    # }
    # print(r)
    # {'routes': [[{'lat': 50.4486941427873, 'lng': 30.52272858686755}, {'lat': 50.443182537581635, 'lng': 30.537797837451716}, {'lat': 50.43837215321555, 'lng': 30.511361985400935}]]

    return jsonify(result)


@app.route('/front')
def front():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
