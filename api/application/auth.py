# -*-coding:utf-8-*-
"""
API:n autorisointi.

TODO
- ohjeet asiakkaalle tai ohjaus toteutukseen?
- loggaukset pois

Autorisointimenetelmän lähde: Riyad Kalla
thebuzzmedia.com/designing-a-secure-rest-api-without-oauth-authentication/
"""


import database as db
from utils import escape, json

from functools import wraps
from flask import g, request, redirect
import time
import base64
from hashlib import sha1
import hmac
from uuid import uuid4
import urllib
import logging


### GLOBAALIT ###

TIMESTAMP_LIMIT = 5 * 60  # sekuntia
PASSWORD_SALT = "djn12gsiugaieufe4f8fafh"  # TODO erillisestä tiedostosta


def require_auth(f):
    """
    Dekoraattori, joka palauttaa virheilmoituksen jos HTTP-pyynnön autorisointi
    on virheellinen. Onnistuneen autorisoinnin tapauksessa kohdefunktio
    käsitellään normaalisti.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        logging.error("\nNEW REQUEST:")
        if not "Authorization" in request.headers:
            logging.error("Authorization header missing")
            return json("fail", {"authorization": "authorization header is required"})

        # Poimitaan Authorization-headerin parametrit:
        auth_header = request.headers["Authorization"]
        auth_params = [param.split("=") for param in auth_header.split(",")]
        auth_dict = {k: v[1:-1] for k, v in auth_params}

        # Tarkastetaan timestamp:
        if time.time() - float(auth_dict["timestamp"]) > TIMESTAMP_LIMIT:
            logging.error("Old timestamp")
            return json("fail", {"timestamp": "old timestamp"})

        # Etsitään käyttäjä tietokannasta:
        user = db.get_user(urllib.unquote(auth_dict["username"]))
        if not user:
            logging.error("User not found")
            return json("fail", {"username": "user not found"})

        # Etsitään asiakassovellus tietokannasta:
        client = db.get_client(urllib.unquote(auth_dict["client"]))
        if not client:
            logging.error("Client not found")
            return json("fail", {"client": "client not found"})

        # Poimitaan pyynnön data:
        method = request.method
        if method in ["GET", "DELETE"]:
            data_src = request.args
        else:
            data_src = request.form
        data = {escape(k): escape(v) for k, v in data_src.iteritems()}
        logging.error("DATA=" + str(data))

        # Kerätään parametrit allekirjoitusta varten:
        params = {
            "username": auth_dict["username"],
            "client": auth_dict["client"],
            "timestamp": auth_dict["timestamp"],
        }
        signature_params = dict(params.items() + data.items())

        # Kääritään parametrit yhteen merkkijonoon:
        root_url = request.url.split("?")[0]
        if not root_url.startswith("http://"):
            root_url = "http://" + root_url

        params_str = "&".join(["%s=%s" % (key, signature_params[key])
            for key in sorted(signature_params)])

        base_string = "&".join([method, escape(root_url), escape(params_str)])
        logging.error("BASE_STR=" + base_string)

        # Luodaan allekirjoitus:
        signing_key = client["key"] + "&" + user["key"]
        hashed = hmac.new(signing_key.encode("utf-8"), base_string.encode("utf-8"), sha1)
        signature = escape(base64.b64encode(hashed.hexdigest()))

        # Tarkastetaan vastaako luotu allekirjoitus pyynnön allekirjoitusta:
        if signature != auth_dict["signature"]:
            logging.error("Incorrect signature, base_string=" + base_string)
            return json("fail", {"signature": "incorrect signature"})

        # Allekirjoitus oikein -> autorisointi onnistui:
        logging.error("Auth success")
        g.user = user
        return f(*args, **kwargs)

    return decorator
