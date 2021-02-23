from twilio.rest import Client
import json

def get_SMS_config():
    with open("SMS_config.json", "r") as file:
        config = file.read()

    return json.loads(config)

def send_msg(phoneNumber, msg):
    config = get_SMS_config()
    account_sid = config['account_sid']
    auth_token = config['auth_token']
    fromNumber =  config['from_number']
    client = Client(account_sid, auth_token)

    # sending message
    message = client.messages.create(
    body=msg, 
    from_= fromNumber, 
    to = phoneNumber)
    # printing the sid after success
    print(message.sid)
