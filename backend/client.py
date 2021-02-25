import requests
import json


def main():
    
    url = "http://0.0.0.0:8080/"

    with open('example.json') as f:
        data = json.load(f)

    results = requests.post(url, json=data)

    print(results.text)


if __name__ == '__main__':
    main()
