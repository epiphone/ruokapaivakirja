# -*-coding:utf-8-*-
"""
Reititysfunktiot käyttäjätoimintojen (CRUD) osalta.

"""

from application import app
from flask import request, g
import database as db
from utils import require_auth, json


@app.route("/")
def index():
    return "Hello world!"


@app.route("/register", methods=["POST"])
def register():
    """
    Rekisteröi uuden käyttäjän.

    TODO
    """
    db.add_user(request.form["username"], request.form["key"])
    return "user %s added" % request.form["username"]


@app.route("/user", methods=["GET", "POST"])
@require_auth
def user():
    """
    Palauttaa käyttäjän tiedot.

    TODO
    """
    user = g.user
    return json("success", {"username": user["username"], "key": user["key"]})
