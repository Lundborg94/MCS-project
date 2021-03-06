import sqlite3
import json
import threading
import time
import re

from flask import Flask, render_template, redirect, url_for, request, session, make_response, jsonify
from flask.sessions import SecureCookieSessionInterface
from mcs_services import AccountService, AddUserDto, LocationService, DashboardService
from mcs_repositories import DeviceRepositoryTest, CumulocityRepository, LocationRepository, EmergencyRepositoryTest

app = Flask(__name__)
app.config["SECRET_KEY"] = "ITSASECRET"

session_serializer = SecureCookieSessionInterface().get_signing_serializer(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'GET' and is_user_in_session():
        # No login required
        return redirect(url_for('home'))

    elif request.method == 'POST':
        device_id = request.form['deviceID']
        req_password = request.form['password']

        with sqlite3.connect('deviceservice.db') as context:
            service = AccountService(DeviceRepositoryTest(context), CumulocityRepository(context))
            correct_password = service.get_user_password(device_id)

            if req_password == correct_password:
                user = service.get_user(device_id)

                add_user_to_session(user)

                session_cookie = session_serializer.dumps(dict(session))
                print(session_cookie)

                resp = make_response(redirect(url_for('home')))

                # Client code can access cookies
                resp.set_cookie('client_session', session_cookie)

                return resp
            else:
                error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'deviceName' in request.form and 'password' in request.form \
            and 'vehicle' in request.form and 'deviceid' in request.form:

        deviceid = request.form['deviceid']
        name = request.form['deviceName']
        password = request.form['password']
        vehicle = request.form['vehicle']
        cumulocity_name = request.form['cumulocityName']
        cumulocity_tenant_id = request.form['tenantId']
        cumulocity_password = request.form['cumulocityPassword']

        with sqlite3.connect('deviceservice.db') as context:
            account_service = AccountService(DeviceRepositoryTest(context), CumulocityRepository(context))

            account = account_service.get_user(deviceid)
            if account:
                msg = 'Account already exists !'
            elif not re.match(r'[A-Za-z0-9]+', name):
                msg = 'Username must contain only characters and numbers !'
            elif not name or not password or not deviceid or not vehicle or not cumulocity_name or not cumulocity_tenant_id or not cumulocity_password:
                msg = 'Please fill out the form !'
            else:
                account_service.add_user(AddUserDto(deviceid, name, password, cumulocity_name, cumulocity_tenant_id, cumulocity_password))
                msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/')
def home():
    if not is_user_in_session():
        return redirect(url_for('login'))

    print("USER IN SESSION")
    print("===============")
    print(json.dumps(session["user"], indent=4))
    return render_template('home.html')


@app.route('/api/location/current')
def get_current_location():

    if not is_user_in_session():
        return "Unauthorized", 401

    with sqlite3.connect('deviceservice.db') as context:
        service = LocationService(LocationRepository(context), CumulocityRepository(context))
        location = service.get_realtime_location(session["user"]["device"]["device_id"])
        print(location)

    return location


@app.route('/api/location/lastknown')
def get_last_known_location():

    if not is_user_in_session():
        return "Unauthorized", 401

    with sqlite3.connect('deviceservice.db') as context:
        service = LocationService(LocationRepository(context), CumulocityRepository(context))
        last_known_location = service.get_latest_location(session["user"]["device"]["device_id"])

        if not last_known_location:
            return "No location logs exists for this device.", 404

        return last_known_location


@app.route('/api/cumulocity/state/<state>')
def activate_cumulocity(state):

    if not is_user_in_session():
        return "Unauthorized", 401

    bit = None
    if state == "on":
        bit = True
    elif state == "off":
        bit = False
    else:
        return "Input was not valid", 400

    with sqlite3.connect('deviceservice.db') as context:
        service = LocationService(LocationRepository(context), CumulocityRepository(context))
        service.set_state(session["user"]["device"]["device_id"], bit)

        return "State is now {}".format(state)


@app.route('/api/device/ec')
def get_device_emergency_contacts():

    if not is_user_in_session():
        return "Unauthorized", 401

    with sqlite3.connect('deviceservice.db') as context:
        service = DashboardService(EmergencyRepositoryTest(context))
        emergency_contacts = service.get_ice_contacts_for_device(session["user"]["device"]["device_id"])

        return jsonify(emergency_contacts)


@app.route('/api/device/ec/<ec_id>', methods=['DELETE'])
def remove_device_emergency_contact(ec_id):

    if not is_user_in_session():
        return "Unauthorized", 401

    with sqlite3.connect('deviceservice.db') as context:
        service = DashboardService(EmergencyRepositoryTest(context))

        if service.remove_ice_contact_for_device(session["user"]["device"]["device_id"], ec_id):
            return "Successfully removed emergency contact.", 200

        return "The emergency contact does not exist for current device.", 404


@app.route('/api/device/ec', methods=['POST'])
def add_device_emergency_contact():

    if not is_user_in_session():
        return "Unauthorized", 401

    json_message = request.json

    with sqlite3.connect('deviceservice.db') as context:
        service = DashboardService(EmergencyRepositoryTest(context))

        ec_id = service.add_ice_contact_for_device(session["user"]["device"]["device_id"], json_message["phone_number"])

        return str(ec_id), 200


def is_user_in_session():
    return 'user' in session


def add_user_to_session(user):
    session['user'] = {
        'device': {
            'device_id': user.device.id,
            'device_name': user.device.name
        }
    }


def realtime_device_location_polling():
    """Polls locations of active devices forever"""
    i = 0
    while True:
        time.sleep(3)
        with sqlite3.connect('deviceservice.db') as context:
            service = LocationService(LocationRepository(context), CumulocityRepository(context))
            active_devices = service.get_active_cumulocity_devices()
            for ad in active_devices:
                location, status_code = service.get_realtime_location(ad[0])
                if not location:
                    print("[{}]: Something went wrong (status code: {})".format(i, status_code))
                    continue

                service.add_location(ad[0], location['lat'], location['lng'], location['alt'])
                print("[{}]: {}".format(i, location))
        i += 1


if __name__ == '__main__':
    # Start background processes
    x = threading.Thread(target=realtime_device_location_polling)
    x.start()

    # Start app
    app.run(port=5000, debug=False)
