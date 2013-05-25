# -*-coding:utf-8-*-
"""
Reititysfunktiot käyttäjätoimintojen (rekisteröinti yms.) osalta.

"""

from application import app
from flask import request, g
import database as db
from utils import json
from auth import require_auth


@app.route("/register", methods=["POST"])
def register():
    """
    Rekisteröi uuden käyttäjän.

    TODO
    """
    username = request.form["username"]
    key = request.form["key"]

    # Validoidaan syötteet:
    if not username:
        return json("fail", {"username": "invalid username"})
    if not key or not (7 < len(key) < 500):
        return json("fail", {"key": "invalid key"})

    existing_user = db.get_user(username)
    if existing_user:
        return json("fail", {"username": "username taken"})

    uid = db.add_user(username, key)
    return json("success", {"id": str(uid)})


@app.route("/user", methods=["GET", "POST"])
@require_auth
def user():
    """
    Palauttaa käyttäjän tiedot.

    TODO
    """
    user = g.user
    return json("success", {"username": user["username"], "key": user["key"]})
