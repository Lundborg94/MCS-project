import sqlite3
import json

from flask import Flask, render_template, redirect, url_for, request, session
from mcs_services import LoginService
from mcs_repositories import DeviceRepositoryTest

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
            service = LoginService(DeviceRepositoryTest(context))
            correct_password = service.get_user_password(device_id)

            if req_password == correct_password:
                user = service.get_user(device_id)

                add_user_to_session(user)

                return redirect(url_for('home'))
            else:
                error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)


@app.route('/')
def home():
    if not is_user_in_session():
        return redirect(url_for('login'))

    print("USER IN SESSION")
    print("===============")
    print(json.dumps(session["user"], indent=4))
    return render_template('home.html')


def is_user_in_session():
    return 'user' in session


def add_user_to_session(user):
    session['user'] = {
        'device': {
            'device_id': user.device.id,
            'device_name': user.device.name
        }
    }


if __name__ == '__main__':
    app.config["SECRET_KEY"] = "ITSASECRET"
    app.run(port=5000, debug=True)

