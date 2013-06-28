# -*-coding:utf-8-*-
"""
Reititysfunktiot käyttäjätoimintojen (rekisteröinti yms.) osalta.

"""

from application import app
from flask import request, g
import database as db
from utils import json
from auth import require_auth


@app.route("/api/json/user/register", methods=["POST"])
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


@app.route("/api/json/user")
@require_auth
def user():
    """
    Palauttaa käyttäjän tiedot.

    Paluuarvossa avaimina username, goals, favs, id.
    """
    user = {
        "username": g.user["username"],
        "favs": g.user["favs"],
        "id": g.user["_id"],
        "goals": g.user["goals"] if "goals" in g.user else {}
    }
    return json("success", user)


@app.route("/api/json/user/goals", methods=["GET", "POST"])
@require_auth
def goals():
    """
    Palauttaa/asettaa käyttäjän päivittäiset ravintoainetavoitteet.
    Jos tavoitteita ei ole asetettu, palautetaan tyhjä olio.

    POST-parametrit (kaikki pakollisia):
    - kcal: päivittäinen energiatavoite kilokaloreina
    - carbs: päivittäinen hiilihydraattitavoite grammoina
    - fat: päivittäinen rasvatavoite grammoina
    - protein: päivittäinen proteiinitavoite grammoina
    """
    user = g.user

    if request.method == "GET":
        if not "goals" in user:
            return json("success", {})
        return json("success", user.goals)

    # POST
    try:
        for attr in ["kcal", "carbs", "fat", "protein"]:
            request.form[attr] = int(request.form[attr])
    except KeyError:
        return json("fail", {"missing parameter": attr})
    except ValueError:
        return json("fail", {"invalid parameter": attr})

    if db.set_user_goals(user["_id"], goals):
        return json("success")
    return json("error", "database update error")

