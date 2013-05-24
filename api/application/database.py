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
    return db.users.insert({"username": username, "key": key})


def get_user(username=None):
    """
    Palauttaa käyttäjänimeä vastaavan käyttäjän, tai kaikki käyttäjät jos nimeä
    ei ole määritelty.
    """
    if username:
        return db.users.find_one({"username": username})
    return db.users.find()


### DATA ###

# Elintarvikehaku:
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


# Yksittäinen elintarvike:
def get_food(fid):
    """
    Palauttaa id:tä vastaavan elintarvikkeen tiedot.
    """
    return db.foods.find_one(fid)


def add_food(food):
    """
    Tallentaa elintarvikkeen.
    """
    return db.foods.insert(food)


# Käyttäjän annokset:
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
    return db.bites.remove(bid)["n"]


# Käyttäjän suosikkielintarvikkeet:
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
    return db.users.update(uid, {"$addToSet": {"favs": fav}})


def delete_fav_from_user(uid, fid):
    """
    Poistaa käyttäjältä suosikkielintarvikkeen.
    """
    uid = objectify(uid)
    return db.users.update(uid, {"$pull": {"favs": fid}})


# Käyttäjän reseptit:
def get_recipes_by_user(uid):
    """
    Palauttaa käyttäjän reseptit.
    """
    raise NotImplementedError


def add_recipe_to_user(uid, rid):
    """
    Lisää käyttäjälle reseptin.
    """
    raise NotImplementedError


def delete_recipe_from_user(uid, rid):
    """
    Poistaa käyttäjältä reseptin.
    """
    raise NotImplementedError
