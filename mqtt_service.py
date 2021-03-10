from awscrt import io, mqtt, auth
from awsiot import mqtt_connection_builder

import time
import json
import smsAPI
import pyodbc

from mcs_repositories import EmergencyRepository, LocationRepository, CumulocityRepository
from mcs_services import DashboardService, LocationService

message_template = """
    A person that has made you his or her emergency contact has crashed at the following location:
    long {} lat {}
    Please make sure that they are alright or contact the emergency services!
"""

db_connection_string = None


def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    message = json.loads(payload.decode('utf-8'))

    if message['event'] == 'crash':
        with pyodbc.connect(db_connection_string) as context:
            dashboard_service = DashboardService(EmergencyRepository(context))
            ice_contacts = dashboard_service.get_ice_contacts_for_device(message['device_id'])
            for contact in ice_contacts:

                phone_number = contact['phone_number']
                print(phone_number)
                device_service = LocationService(LocationRepository(context),
                                                 CumulocityRepository(context))
                gps_location = device_service.get_latest_location(message['device_id'])
                if gps_location:
                    try:
                        msg = message_template.format(gps_location['longitude'], gps_location['latitude'])
                        smsAPI.send_msg(phone_number, msg)
                        print("Sent message to: " + phone_number, '\n', msg)
                    except Exception as e:
                        print('Could not send message due to an exception: ')
                        print(e)
                else:
                    print('Could not find GPS location')
    elif message['event'] == 'on_off_switch':
        bit = None
        if message['state'] == "on":
            bit = True
        elif message['state'] == "off":
            bit = False
        else:
            return "Input was not valid", 400

        with pyodbc.connect(db_connection_string) as context:
            service = LocationService(LocationRepository(context), CumulocityRepository(context))
            service.set_state(message['device_id'], bit)

            print("State is now {}".format(message['state']))
    else:
        print('Invalid event type')


def on_connection_interrupted(connection, error, **kwargs):
    print('Connection interrupted. error: {}'.format(error))


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print('Connection resumed. return_code: {} session_present: {}'.format(return_code, session_present))


def get_mqtt_config():
    with open("project_config_file.json", "r") as file:
        config = file.read()

    return json.loads(config)['mqtt_config']


def begin_resources(db_connection_str):
    global db_connection_string
    db_connection_string = db_connection_str

    config = get_mqtt_config()

    endpoint = config["endpoint"]
    client_id = config["client_id"]
    topic = config["topic"]

    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    credentials_provider = auth.AwsCredentialsProvider.new_default_chain(client_bootstrap)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=config["cert_filepath"],
        pri_key_filepath=config["pri_key_filepath"],
        client_bootstrap=client_bootstrap,
        ca_filepath=config["ca_filepath"],
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id,
        clean_session=config["clean_session"],
        keep_alive_secs=config["keep_alive_secs"]
    )

    print('Connecting to {} with client ID "{}"...'.format(endpoint, client_id))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'".format(topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received
    )

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    while True:
        time.sleep(5)


if __name__ == '__main__':
    begin_resources()
