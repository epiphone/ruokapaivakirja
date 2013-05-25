# -*-coding:utf-8-*-
"""
Skreippaa elintarviketietoja Fineli-sivustolta.

Aleksi Pekkala
"""

from lxml import html
from utils import fin_escape as escape
import re
import logging
import database as db


### GLOBALS ###

URL_ROOT = "http://www.fineli.fi"


def search_foods(query):
    """
    Palauttaa hakuehtoja vastaavat elintarvikkeet + id:t.

    Paluuarvona lista, jossa arvot tyyppiä [id, nimi].
    """
    query = re.sub("\s+", " ", query).strip()

    stored = db.get_search(query)
    if stored:
        return stored

    url = URL_ROOT + "/foodsearch.php?name=" + escape(query)
    print "url=", url
    root = html.parse(url)

    foods = []
    rows = root.xpath("/html/body/div/table[2]/tr[1]/td[2]/ul/li/a")
    for row in rows:
        try:
            fid = row.attrib["href"].split("=")[1].split("&")[0]
        except IndexError:
            logging.error("Scraping food ID failed: " + query)
            continue

        foods.append((fid, row.text.strip()))

    db.add_search({"query": query, "results": foods})
    return foods


def get_food(fid):
    """
    Palauttaa id:tä vastaavan elintarvikkeen ravintotiedot.
    """
    stored = db.get_food(fid)
    if stored:
        return stored

    url = URL_ROOT + "/food.php?foodid=" + fid
    root = html.parse(url)

    # Elintarvikkeen id (Finelin käyttämä) ja nimi:
    food = {"_id": fid, "data": {}}
    fname = root.xpath("/html/body/div/table[2]//h1")[0].text.strip().lower()
    food["name"] = fname

    # Ravintoarvot:
    rows = root.xpath(
        "/html/body/div/table[2]/tr/td[2]/table/tr[3]/td/table/tr")
    for row in rows:
        if row.attrib["class"] in ["header", "subheader"]:
            continue
        tds = row.iterchildren()
        name = tds.next()[0].text.strip()

        value = tds.next().text.strip()
        if "(" in value:
            value = float(value.split()[-1][1:-1])
        elif "<" in value:
            value = 0.0
        else:
            value = float(value)

        unit = tds.next().text.strip()
        if "(" in unit:
            unit = unit.split()[-1][1:-1]

        food["data"][name] = (value, unit)

    db.add_food(food)
    return food
