from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

import time
import uuid
import json


def main():
    print('Hello World!')


def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))


def on_connection_interrupted(connection, error, **kwargs):
    print('Connection interrupted. error: {}'.format(error))


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print('Connection resumed. return_code: {} session_present: {}'.format(return_code, session_present))


def get_mqtt_config():
    with open("project_config_file.json", "r") as file:
        config = file.read()

    return json.loads(config)['mqtt_config']


def begin_resources():
    config = get_mqtt_config()

    endpoint = config["endpoint"]
    client_id = config["client_id"]
    topic = config["topic"]

    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    credentials_provider = auth.AwsCredentialsProvider.new_default_chain(client_bootstrap)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint = endpoint,
        cert_filepath = config["cert_filepath"],
        pri_key_filepath = config["pri_key_filepath"],
        client_bootstrap = client_bootstrap,
        ca_filepath = config["ca_filepath"],
        on_connection_interrupted = on_connection_interrupted,
        on_connection_resumed = on_connection_resumed,
        client_id = client_id,
        clean_session = config["clean_session"],
        keep_alive_secs = config["keep_alive_secs"]
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
        
        message = "test"
        print("Publishing message to topic '{}': {}".format(topic, message))
        mqtt_connection.publish(
            topic=topic,
            payload=message,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        
        time.sleep(5)


if __name__ == '__main__':
    begin_resources()
