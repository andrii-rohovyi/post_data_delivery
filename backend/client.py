import requests
import json
import pprint


def main():
    
    url = "http://0.0.0.0:8080/"

    with open('example.json') as f:
        data = json.load(f)

    results = requests.post(url, json=data)

    pprint.pprint(results.json())


if __name__ == '__main__':
    main()
