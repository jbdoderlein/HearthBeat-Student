from flask import Flask, render_template, abort
import requests
import json
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<int:guild_id>/<int:user_id>')
def get_user(guild_id, user_id):
    r = requests.get(f"http://localhost:8887/user/{guild_id}/{user_id}")
    if r.status_code == 404:
        abort(404)
    info = r.json()
    return render_template('user.html', user_id=user_id, **info)

@app.route('/users/<int:guild_id>')
def get_users(guild_id):
    r = requests.get(f"http://localhost:8887/users/{guild_id}")
    if r.status_code == 404:
        abort(404)
    info = r.json()
    return render_template('users.html', guild_id=guild_id, info=info)

@app.route('/appel/<int:guild_id>/<string:matiere>/<int:role_id>')
def get_appel(guild_id, matiere, role_id):
    r = requests.get(f"http://localhost:8887/appel/{guild_id}/{matiere}/{role_id}")
    if r.status_code == 404:
        abort(404)
    info = r.json()
    return render_template('appel.html', guild_id=guild_id, matiere=matiere, role=info['role'], data=info['data'])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6789)
