import requests
import json


def get_configurations():
    with open("project_config_file.json", "r") as file:
        config = file.read()

    return json.loads(config)['cumulocity_config']


def get_location(username, tenant_id, password):
    config = get_configurations()

    tenant_id = tenant_id
    username = username
    password = password

    payload = {'fragmentType': 'c8y_Position'}
    resp = requests.get('https://{}.eu-latest.cumulocity.com/inventory/managedObjects'.format(tenant_id),
                     auth=(username, password), params=payload)

    response = resp.json()

    managedObjects = response['managedObjects'][0]
    position = managedObjects['c8y_Position']

    return position