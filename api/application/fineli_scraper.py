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
STATS = ["energia", "hh", "rasva", "proteiini", "alkoholi", "hapot",
         "tärkkelys", "sokerit", "sakkaroosi", "laktoosi", "fruktoosi",
         "sokerialkoholi", "kuitu, kokonais-", "kuitu liukenematon",
         "polysakkaridi", "glukoosi", "maltoosi", "galaktoosi",
         "rasva yht tag", "rasva yht", "rasva tyyd", "rasva cis",
         "rasva monityyd", "rasva trans", "linolihappo", "alfalinoleenihappo",
         "epa", "dha", "kolesteroli", "sterolit", "natrium", "suola", "kalium",
         "magnesium", "kalsium", "fosfori", "rauta", "sinkki", "jodi",
         "seleeni", "tryptofaani", "a", "d", "e", "k", "c", "hplc", "ne",
         "niasiini", "b2", "b1", "b12", "vetykloridi", "karotenoidit"]


def search_foods(query):
    """
    Palauttaa hakuehtoja vastaavat elintarvikkeet + id:t.
    """
    query = re.sub("\s+", " ", query).strip()

    stored = db.get_search(query)
    if stored:
        return stored

    url = URL_ROOT + "/foodsearch.php?name=" + escape(query)

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
    url = URL_ROOT + "/food.php?foodid=" + fid

    root = html.parse(url)

    food = {}
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

        food[name] = (value, unit)

    return food


def test(query="a"):
    fids = [fid for (fid, food) in search_foods(query)]
    for fid in fids:
        food = get_food(fid)
        print len(food), fid
