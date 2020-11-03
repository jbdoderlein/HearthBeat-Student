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
    return render_template('user.html',user_id=user_id, **info)