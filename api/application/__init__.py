#-*-coding:utf-8-*-
"""
Ruokapäiväkirja API

author: Aleksi Pekkala (aleksipekkala@hotmail.com)
"""

from flask import Flask


### SOVELLUKSEN ALUSTUS ###

app = Flask("application")
app.config.from_object("application.settings")


### GLOBAALIT ###

API_URL = "http://130.234.180.42:5000"
TIMESTAMP_LIMIT = 5 * 60  # sekuntia
PASSWORD_SALT = "djn12gsiugaieufe4f8fafh"


### SIVUT (views) ###

import application.user_views
