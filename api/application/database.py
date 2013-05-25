# -*-coding:utf-8-*-
"""
Tietokantafunktiot.

"""

from pymongo import MongoClient
from utils import objectify


client = MongoClient()
db = client.rpk


### AUTH & KÄYTTÄJÄT ###

def get_client(client):
    """
    Palauttaa nimeä vastaavan asiakassovelluksen.
    """
    return db.clients.find_one({"client": client})


def add_user(username, key):
    """
    Lisää käyttäjän tietokantaan.
    """
    return db.users.insert({
        "username": username, "key": key, "favs": [], "recipes": []})


def get_user(username=None):
    """
    Palauttaa käyttäjänimeä vastaavan käyttäjän, tai kaikki käyttäjät jos nimeä
    ei ole määritelty.
    """
    if username:
        return db.users.find_one({"username": username})
    return db.users.find()


### ELINTARVIKEHAKU ###

def get_search(query):
    """
    Palauttaa Finelin elintarvikehaun tulokset annetulle hakusanalle.
    """
    search = db.searches.find_one({"query": query})
    return search["results"] if search else None


def add_search(search):
    """
    Lisää haku-tulokset-parin tietokantaan.
    """
    return db.searches.insert(search)


### YKSITTÄINEN ELINTARVIKE ###

def get_food(fid):
    """
    Palauttaa id:tä vastaavan elintarvikkeen.
    """
    return db.foods.find_one(fid)


def add_food(food):
    """
    Tallentaa elintarvikkeen.
    """
    return db.foods.insert(food)


### YKSITTÄINEN RESEPTI ###

def get_recipe(rid):
    """
    Palauttaa id:tä vastaavan reseptin.
    """
    rid = objectify(rid)
    return db.recipes.find_one(rid)


def add_recipe(recipe):
    """
    Lisää reseptin.
    """
    for food in recipe["foods"]:
        food["fid"] = objectify(food["fid"])
    recipe["user"]["uid"] = objectify(recipe["user"]["uid"])
    return db.recipes.insert(recipe)


def delete_recipe(rid):
    """
    Poistaa reseptin, palauttaa poistojen lukumäärän.
    """
    rid = objectify(rid)
    return db.recipes.remove({"_id": rid})["n"]


### KÄYTTÄJÄN ANNOKSET ###

def get_bites_by_user(uid, start_date, end_date):
    """
    Palauttaa käyttäjän annokset annetulta aikaväliltä, järjestettynä
    päivämäärän (kasvava) mukaan.

    Päivämääräparametrit ovat inklusiivisia.
    """
    bites = db.bites.find({
        "uid": objectify(uid),
        "date": {"$gte": start_date, "$lte": end_date}
    }).sort("date")

    return list(bites) if bites else bites


def add_bite(bite):
    """
    Lisää annoksen.
    """
    return db.bites.insert(bite)


def delete_bite(bid):
    """
    Poistaa annoksen, palauttaa poistojen lukumäärän.
    """
    bid = objectify(bid)
    return db.bites.remove({"_id": bid})["n"]


### KÄYTTÄJÄN SUOSIKIT ###

def get_favs_by_user(uid):
    """
    Palauttaa listan käyttäjän suosikkielintarvikkeista,
    tai None, jos käyttäjää ei löydy tai käyttäjällä ei ole suosikkeja.
    """
    uid = objectify(uid)
    user = db.users.find_one(uid, ["favs"])
    return None if not user else user["favs"]


def add_fav_to_user(uid, fav):
    """
    Lisää käyttäjälle suosikkielintarvikkeen.
    """
    uid = objectify(uid)
    return db.users.update({"_id": uid}, {"$addToSet": {"favs": fav}})


def delete_fav_from_user(uid, fid):
    """
    Poistaa käyttäjältä suosikkielintarvikkeen.
    """
    uid = objectify(uid)
    return db.users.update({"_id": uid}, {"$pull": {"favs": {"fid": fid}}})


### KÄYTTÄJÄN RESEPTIT ###

def get_recipes_by_user(uid):
    """
    Palauttaa käyttäjän reseptit.
    """
    uid = objectify(uid)
    user = db.users.find_one(uid, ["recipes"])
    return user["recipes"] if user else None


def add_recipe_to_user(uid, recipe):
    """
    Lisää käyttäjälle reseptin.
    """
    uid = objectify(uid)
    return db.users.update({"_id": uid}, {"$addToSet": {"recipes": recipe}})


def delete_recipe_from_user(uid, rid):
    """
    Poistaa käyttäjältä reseptin.
    """
    uid, rid = objectify(uid), objectify(rid)
    return db.users.update({"_id": uid}, {"$pull": {"recipes": {"rid": rid}}})


### TOP-RESEPTIT JA TOP-ELINTARVIKKEET ###

def get_top_recipes(limit=10):
    """
    Palauttaa listan suosituimmista resepteistä.
    """
    return db.users.aggregate([
        {"$project": {"favs": 1}},
        {"$unwind": "$favs"},
        {"$group": {"_id": "$favs", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {"fid": "$_id.fid", "name": "$_id.name", "count": 1}}
    ])


def get_top_foods(limit=10):
    """
    Palauttaa listan suosituimmista elintarvikkeista.
    """
    return db.users.aggregate([
        {"$project": {"favs": 1}},
        {"$unwind": "$favs"},
        {"$group": {"_id": "$favs", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$project": {"fid": "$_id.fid", "name": "$_id.name", "count": 1}}
    ])
