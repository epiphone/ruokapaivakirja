# -*-coding:utf-8-*-
"""
Tietokantafunktiot.

"""

from pymongo import MongoClient


client = MongoClient()
db = client.rpk


### AUTH ###

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


def get_food():
    pass


def get_favourites_by_user(user_id):
    """
    Palauttaa käyttäjän suosikkiruoat.
    """
    raise NotImplementedError


def get_recipes_by_user(user_id):
    """
    Palauttaa käyttäjän reseptit.
    """
    raise NotImplementedError


def add_favourite_to_user(user_id, favourite):
    """
    Lisää käyttäjälle suosikkiruoan.
    """
    raise NotImplementedError


def add_recipe_to_user(user_id, recipe):
    """
    Lisää käyttäjälle reseptin.
    """
    raise NotImplementedError
