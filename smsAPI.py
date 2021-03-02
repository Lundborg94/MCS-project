from twilio.rest import Client
import json


def get_sms_config():
    with open("project_config_file.json", "r") as file:
        config = file.read()

    return json.loads(config)['sms_config']


def send_msg(phone_number, msg):
    config = get_sms_config()
    account_sid = config['account_sid']
    auth_token = config['auth_token']
    fromNumber = config['from_number']
    client = Client(account_sid, auth_token)

    # sending message
    message = client.messages.create(
        body=msg,
        from_=fromNumber,
        to=phone_number)
    # printing the sid after success
    print(message.sid)


if __name__ == '__main__':
    send_msg('+46733933020', 'hej hej')
