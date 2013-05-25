#-*-coding:utf-8-*-
"""
Ruokapäiväkirja API

author: Aleksi Pekkala (aleksipekkala@hotmail.com)
"""

from flask import Flask
from werkzeug.contrib.cache import SimpleCache


### SOVELLUKSEN ALUSTUS ###

app = Flask("application")
app.config.from_object("application.settings")
cache = SimpleCache()

### GLOBAALIT ###

API_URL = "http://130.234.180.42:5000"


### SIVUT (views) ###

from application import user_views, data_views
