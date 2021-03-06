import requests
import json


def get_configurations():
    with open("project_config_file.json", "r") as file:
        config = file.read()

    return json.loads(config)['cumulocity_config']


def get_location(username, tenant_id, password):
    tenant_id = tenant_id
    username = username
    password = password

    payload = {'fragmentType': 'c8y_Position'}
    resp = requests.get(f'https://{tenant_id}.eu-latest.cumulocity.com/inventory/managedObjects',
                        auth=(username, password), params=payload)

    if resp.status_code != 200:
        return None, resp.status_code

    response = resp.json()

    managed_objects = response['managedObjects'][0]
    position = managed_objects['c8y_Position']

    return position, resp.status_code
