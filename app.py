import sqlite3
import json
import threading
import time
import re

from flask import Flask, render_template, redirect, url_for, request, session
from mcs_services import AccountService, AddUserDto, LocationService
from mcs_repositories import DeviceRepositoryTest, CumulocityRepository, LocationRepository

app = Flask(__name__)


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

                return redirect(url_for('home'))
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
            # elif not re.match(r'[^@]+@[^@]+\.[^@]+', mail):
            #     msg = 'Invalid email address !'
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


@app.route('/location/<device_id>')
def get_current_location(device_id):
    with sqlite3.connect('deviceservice.db') as context:
        service = LocationService(LocationRepository(context), CumulocityRepository(context))
        location = service.get_realtime_location(device_id)
        print(location)

    return location


def service_worker():
    i = 0
    while True:
        time.sleep(3)
        with sqlite3.connect('deviceservice.db') as context:
            service = LocationService(LocationRepository(context), CumulocityRepository(context))
            active_devices = service.get_active_cumulocity_devices()
            for ad in active_devices:
                realtime_location = service.get_realtime_location(ad[0])
                service.add_location(ad[0], realtime_location['lat'], realtime_location['lng'], realtime_location['alt'])
                print("[{}]: {}".format(i, realtime_location))
        i += 1


@app.route('/location/getlastknown/<device_id>')
def get_last_known_location(device_id):
    with sqlite3.connect('deviceservice.db') as context:
        service = LocationService(LocationRepository(context), CumulocityRepository(context))
        last_known_location = service.get_latest_location(device_id)

        if not last_known_location:
            return "No location logs exists for this device.", 404

        return last_known_location


def is_user_in_session():
    return 'user' in session


def add_user_to_session(user):
    session['user'] = {
        'device': {
            'device_id': user.device.id,
            'device_name': user.device.name
        }
    }

x = threading.Thread(target=service_worker)
x.start()

if __name__ == '__main__':

    app.config["SECRET_KEY"] = "ITSASECRET"
    app.run(port=5000, debug=True)
