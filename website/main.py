from flask import Flask, render_template
import requests
import json
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<int:guild_id>/<int:user_id>')
def get_user(guild_id, user_id):
    info = requests.get(f"http://localhost:7500/user/{guild_id}/{user_id}").json()
    return render_template('user.html', user_id=user_id, **info)

@app.route('/users/<int:guild_id>')
def get_users(guild_id):
    info = requests.get(f"http://localhost:7500/users/{guild_id}").json()
    return render_template('users.html', guild_id=guild_id, info=info)

""" TODO
@app.route('/appel/<int:guild_id>/<int:appel_id>')
def get_users(guild_id, appel_id):
    data = requests.get(f"http://localhost:7500/appel/{guild_id}/{appel_id}").json()
    return render_template('appel.html', head=data['head'], body=data['body'])
"""