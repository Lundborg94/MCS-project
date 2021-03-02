import requests
import json


def get_configurations():
    with open("project_config_file.json", "r") as file:
        config = file.read()

    return json.loads(config)['cumulocity_config']


def get_location():
    config = get_configurations()

    username = config['username']
    password = config['password']

    payload = {'fragmentType': 'c8y_Position'}
    r = requests.get('https://{}.eu-latest.cumulocity.com/inventory/managedObjects'.format(username.lower()),
                     auth=(username, password), params=payload)

    response = r.json()

    managedObjects = response['managedObjects'][0]
    position = managedObjects['c8y_Position']

    return position
