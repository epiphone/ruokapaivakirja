#-*-coding:utf-8-*-
"""
Ruokapäiväkirja API

author: Aleksi Pekkala (aleksipekkala@hotmail.com)
"""

from flask import Flask, request
from werkzeug.contrib.cache import SimpleCache


### SOVELLUKSEN ALUSTUS ###

app = Flask("application")
app.config.from_object("application.settings")
cache = SimpleCache()


@app.after_request
def after_request(response):
    """
    Kutsutaan jokaisen HTTP-pyynnön lopussa, juuri ennen vastausta.
    """
    response.headers["Access-Control-Allow-Origin"] = request.headers["Origin"]
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


### GLOBAALIT ###

API_URL = "http://130.234.180.42:5000"


### SIVUT (views) ###

from application import user_views, data_views
