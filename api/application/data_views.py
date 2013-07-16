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
import logging


BASIC_STATS = [
    ("kcal", "energia, laskennallinen"),
    ("carbs", u"hiilihydraatti imeytyvä"),
    ("protein", "proteiini"),
    ("fat", "rasva")]
DATEFORMAT = "%Y%m%d"
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"


### FOODS ###

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


### FAVS ###

@app.route("/api/json/user/favs")
@require_auth
def get_favs():
    """
    Palauttaa kirjautuneen käyttäjän suosikkielintarvikkeet.
    """
    logging.error("get_favs")
    favs = db.get_favs_by_user(g.user["_id"])
    return json(data=favs)


@app.route("/api/json/user/favs/<fid>", methods=[POST, DELETE])
@require_auth
def add_or_delete_fav(fid):
    """
    POST lisää kirjautuneelle käyttäjälle uuden suosikkielintarvikkeen.

    DELETE poistaa suosikkielintarvikkeen.
    """
    if request.method == DELETE:
        db.delete_fav_from_user(g.user["_id"], fid)
        return json()

    food = scraper.get_food(fid)
    if not food:
        return json("fail", {"fid": "food not found"})

    fav = {"fid": food["_id"], "name": food["name"]}
    db.add_fav_to_user(g.user["_id"], fav)
    return json()


### RECIPES ###

@app.route("/api/json/user/recipes")
@require_auth
def get_recipes():
    """
    Palauttaa kirjautuneen käyttäjän suosikkireseptit.
    """
    recipes = db.get_recipes_by_user(g.user["_id"])
    return json(data=recipes)


@app.route("/api/json/user/recipes/<rid>", methods=[POST, DELETE])
@require_auth
def add_or_delete_recipe(rid):
    """
    POST lisää kirjautuneelle käyttäjälle uuden suosikkireseptin.

    DELETE poistaa suosikkireseptin.
    """
    if request.method == DELETE:
        db.delete_recipe_from_user(g.user["_id"], rid)
        return json()

    recipe = db.get_recipe(rid)
    if not recipe:
        return json("fail", {"rid": "recipe not found"})

    recipe = {"rid": recipe["_id"], "name": recipe["name"]}
    db.add_fav_to_user(g.user["_id"], recipe)
    return json()


### DAYS ###

@app.route("/api/json/user/days")
@require_auth
def days():
    """
    Palauttaa käyttäjän päivät annetulta väliltä.

    URL-parametrit:
    - start: inklusiivinen alkupäivämäärä (YYYYmmdd)
    - end: inklusiivinen loppupäivämäärä (YYYYmmdd)

    Paluuarvo on muotoa [{date, count, kcal, carbs, fat, protein}]
    """
    start = request.args.get("start", None)
    end = request.args.get("end", None)
    try:
        if start:
            start = datetime.strptime(start, DATEFORMAT)
        if end:
            end = datetime.strptime(end, DATEFORMAT)
    except ValueError:
        return json("fail", {"parameters": "invalid date parameters"})

    return json(data=db.get_days_by_user(g.user["_id"], start, end))


### BITES ###

@app.route("/api/json/user/bites/<date>")
@require_auth
def bites_by_date(date):
    """
    Palauttaa kirjautuneen käyttäjän annokset valitulta päivältä.

    Parametrit:
    - date: päivämäärä muodossa YYYYmmdd
    """
    try:
        date = datetime.strptime(date, DATEFORMAT)
    except ValueError:
        return json("fail", {"parameters": "invalid date parameter"})

    return json(data=db.get_bites_by_user(g.user["_id"], date=date))


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
    - fid: elintarvikkeen id (ei pakollinen, jos rid on määritelty)
    - rid: reseptin nimi (ei pakollinen, jos fid on määritelty)
    - amount: määrä grammoissa
    - date: päivämäärä (YYYYmmdd)

    Huom! Jos sekä fid että rid ovat määritelty, käytetään fid:tä.
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

    # POST - lisätään annos:
    try:
        amount = int(request.form["amount"])
        bite = {
            "uid": g.user["_id"],
            "fid": request.form["fid"],
            "amount": amount,
            "date": datetime.strptime(request.form["date"], DATEFORMAT)
        }

        if "fid" in request.form:
            bite["fid"] = request.form["fid"]
        else:
            bite["rid"] = request.form["rid"]

    except KeyError:
        return json("fail", {"parameters": "missing parameters"})
    except ValueError:
        return json("fail", {"parameters": "invalid parameters"})

    if "fid" in bite:
        food = scraper.get_food(bite["fid"])
        if not food:
            return json("fail", {"fid": "food not found"})

        bite["name"] = food["name"]
        for p1, p2 in BASIC_STATS:
            bite[p1] = round(food["data"][p2][0] / 100.0 * amount)
    else:
        recipe = db.get_recipe(bite["rid"])
        if not recipe:
            return json("fail", {"rid": "recipe not found"})

        bite["name"] = recipe["name"]
        for p1, p2 in BASIC_STATS:
            bite[p1] = round(recipe[p1] / 100.0 * amount)

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
