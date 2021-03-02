from flask import Flask, Response, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_required
from database_context import MCSTestContext

import sqlite3

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

conn = sqlite3.connect("databases/mcsservice.db")
context = MCSTestContext(conn)


class User(UserMixin):
    # proxy for a database of users
    user_database = {"JohnDoe": ("JohnDoe", "John"),
                     "JaneDoe": ("JaneDoe", "Jane")}

    def __init__(self, deviceID, password):
        self.id = deviceID
        self.password = password

    @classmethod
    def get(cls, id):
        return cls.user_database.get(id)


@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        deviceID, password = token.split(":")  # naive token
        user_entry = User.get(deviceID)
        if user_entry is not None:
            user = User(user_entry[0], user_entry[1])
            if user.password == password:
                return user
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['deviceID'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))

        #device_id = request.form['deviceID']
        #password = request.form['password']



    return render_template('login.html', error=error)


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.config["SECRET_KEY"] = "ITSASECRET"
    app.run(port=5000, debug=True)
