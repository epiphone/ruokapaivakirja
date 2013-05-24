# -*-coding:utf-8-*-
"""
Reititysfunktiot datatoimintojen osalta.

"""

from application import app
from flask import request, g
from utils import require_auth, json
import database as db
from datetime import datetime


DATEFORMAT = "%Y%m%d"
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"


@app.route("/api/json/user/bites", methods=[GET, POST])
@require_auth
def bites():
    """
    GET Palauttaa kirjautuneen käyttäjän annokset annetulta aikaväliltä.

    URL-parametrit:
    - start: inklusiivinen alkupäivämäärä (YYYYmmdd)
    - end: inklusiivinen loppupäivämäärä (YYYYmmdd)


    POST lisää uuden annoksen.

    POST-parametrit:
    - fid: elintarvikkeen id
    - amount: määrä grammoissa
    - date: päivämäärä (YYYYmmdd)
    """
    if request.method == GET:
        try:
            start = datetime.strptime(request.args.get("start"), DATEFORMAT)
            end = datetime.strptime(request.args.get("end"), DATEFORMAT)
        except TypeError:
            return json("fail", {"parameters": "missing date parameters"})
        except ValueError:
            return json("fail", {"parameters": "invalid date parameters"})

        return json(data=db.get_bites_by_user(g.user["_id"], start, end))

    try:
        amount = int(request.form["amount"])
        bite = {
            "uid": g.user["_id"],
            "fid": request.form["fid"],
            "amount": amount,
            "date": datetime.strptime(request.form["date"], DATEFORMAT)
        }
    except KeyError:
        return json("fail", {"parameters": "missing parameters"})
    except ValueError:
        return json("fail", {"parameters": "invalid parameters"})

    food = db.get_food(request.form["fid"])
    if not food:
        return json("fail", {"fid": "food not found"})

    bite["name"] = food["name"]
    bite["kcal"] = round(food["energia, laskennallinen"][0]/100.0*amount)
    bite["carbs"] = round(food[u"hiilihydraatti imeytyvä"][0]/100.0*amount)
    bite["protein"] = round(food["proteiini"][0] / 100.0 * amount)
    bite["fat"] = round(food["rasva"][0] / 100.0 * amount)

    db.add_bite(bite)
    return json()


@app.route("/api/json/user/bites/<bid>", methods=[DELETE])
@require_auth
def delete_bite(bid):
    """
    Poistaa kirjautuneelta käyttäjältä määrätyn annoksen.
    """
    if request.method == DELETE:
        db.delete_bite(bid)
        return json()
