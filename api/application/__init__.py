#-*-coding:utf-8-*-
"""
Ruokapäiväkirja API

author: Aleksi Pekkala (aleksipekkala@hotmail.com)
"""

from flask import Flask, request
from werkzeug.contrib.cache import SimpleCache
import logging


### SOVELLUKSEN ALUSTUS ###

app = Flask("application")
app.config.from_object("application.settings")
cache = SimpleCache()


# TODO debug
@app.before_request
def before_request():
    logging.error("BEFORE REQUEST: URL=%s\n IS_XHR=%s\n HEADERS=%s" % (request.url, str(request.is_xhr), str(request.headers)))


@app.after_request
def after_request(response):
    """
    Kutsutaan jokaisen HTTP-pyynnön lopussa, juuri ennen vastausta.

    Laitetaan palvelin tukemaan CORSia, eli asiakas voi tehdä AJAX-pyyntöjä
    domainin ulkopuolelta. TODO debug
    """
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response


### GLOBAALIT ###

API_URL = "http://130.234.180.42:5000"


### SIVUT (views) ###

from application import user_views, data_views
