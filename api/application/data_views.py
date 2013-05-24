# -*-coding:utf-8-*-
"""
Reititysfunktiot datatoimintojen osalta.

"""

from application import app
from utils import json
from auth import require_auth
import fineli_scraper as scraper
from flask import request, g
import database as db
from datetime import datetime


DATEFORMAT = "%Y%m%d"
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"


@app.route("/api/json/foods/<fid>")
# @require_auth
def food(fid):
    """
    Palauttaa yksittäisen elintarvikkeen tiedot.
    """
    food = scraper.get_food(fid)
    if not food:
        return json("fail", {"fid": "food not found"})

    return json(data=food)


@app.route("/api/json/foods")
# @require_auth
def search_foods():
    """
    Palauttaa elintarvikehaun tulokset annetulla hakusanalla.

    URL-parametrit:
    - q: hakusana
    """
    query = request.args.get("q")
    if not query:
        return json("fail", {"q": "invalid query"})

    results = scraper.search_foods(query)
    return json(data=results)


@app.route("/api/json/user/favs")
@require_auth
def get_favs():
    """
    Palauttaa kirjautuneen käyttäjän suosikkielintarvikkeet.
    """
    favs = db.get_favs_by_user(g.user["_id"])
    return json(data=favs)


@app.route("/api/json/user/favs/<fid>")
@require_auth
def add_or_delete_bite(fid):
    """
    POST lisää kirjautuneelle käyttäjälle uuden suosikkielintarvikkeen.

    DELETE poistaa suosikkielintarvikkeen.
    """
    if request.method == DELETE:
        db.delete_fav_from_user(g.user["_id"], fid)
        return json()

    food = db.get_food(fid)
    if not food:
        return json("fail", {"fid": "food not found"})

    fav = {"fid": food["_id"], "name": food["name"]}
    db.add_fav_to_user(g.user["_id"], fav)
    return json()


@app.route("/api/json/user/bites", methods=[GET, POST])
@require_auth
def bites():
    """
    GET palauttaa kirjautuneen käyttäjän annokset annetulta aikaväliltä.

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
