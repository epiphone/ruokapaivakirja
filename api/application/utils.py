# -*-coding:utf-8-*-
"""
Apufunktiota ym. työkaluja.

Aleksi Pekkala
"""

import urllib
from functools import wraps
from flask import g, request, redirect, jsonify
import time
import base64
from hashlib import sha1
import hmac
from uuid import uuid4
import urllib
from application import TIMESTAMP_LIMIT, PASSWORD_SALT
import database as db


def json(status="success", data=None, message=None):
    """
    Palauttaa JSend-spesifikaation mukaisen JSON-merkkijonon.

    http://labs.omniti.com/labs/jsend
    """
    assert status in ["success", "fail", "error"]

    if status in ["success", "fail"]:
        return jsonify(dict(status=status, data=data))

    return jsonify(dict(status="error", message=message))


def escape(text):
    """
    Palauttaa merkkijonon url-enkoodattuna.
    """
    return urllib.quote(text.encode("utf-8"), "")


def fin_escape(s):
    """
    Palauttaa merkkijonon josta ääkköset URL-enkoodattu.

    Huom! enkoodaus eroaa escape-funktion enkoodauksesta.

    >>> fin_escape("MÄMMI")
    'm%E4mmi'
    """
    return "".join([escape_char(c) for c in s])


def escape_char(c):
    """
    Palauttaa merkin URL-enkoodattuna, lowercaseen muokattuna.

    >>> escape_char("ä")
    '%E4'
    """
    c = c.lower()
    if c == "ä":
        return "%E4"
    elif c == "ö":
        return "%F6"
    elif c == "å":
        return "%E5"
    return c


def require_auth(f):
    """
    Dekoraattori, joka palauttaa virheilmoituksen jos HTTP-pyynnön autorisointi
    on virheellinen. Onnistuneen autorisoinnin tapauksessa kohdefunktio
    käsitellään normaalisti.

    TODO ohjeet asiakkaalle tai ohjaus toteutukseen?

    Autorisointimenetelmän lähde: Riyad Kalla
    thebuzzmedia.com/designing-a-secure-rest-api-without-oauth-authentication/
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        if not "Authorization" in request.headers:
            return json("fail", {"authorization": "authorization header is required"})

        # Poimitaan Authorization-headerin parametrit:
        auth_header = request.headers["Authorization"]
        auth_params = [param.split("=") for param in auth_header.split(",")]
        auth_dict = {k: v[1:-1] for k, v in auth_params}

        # Tarkastetaan timestamp:
        if time.time() - float(auth_dict["timestamp"]) > TIMESTAMP_LIMIT:
            return json("fail", {"timestamp": "old timestamp"})

        # Etsitään käyttäjä tietokannasta:
        user = db.get_user(urllib.unquote(auth_dict["username"]))
        if not user:
            return json("fail", {"username": "user not found"})

        # Etsitään asiakassovellus tietokannasta:
        client = db.get_client(urllib.unquote(auth_dict["client"]))
        if not client:
            return json("fail", {"client": "client not found"})

        # Poimitaan pyynnön data:
        method = request.method
        if method in ["GET", "POST"]:
            data_src = request.args
        else:
            data_src = request.form
        data = {escape(k): escape(v) for k, v in data_src.iteritems()}

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

        # Luodaan allekirjoitus:
        signing_key = client["key"] + "&" + user["key"]
        hashed = hmac.new(signing_key.encode("utf-8"), base_string.encode("utf-8"), sha1)
        signature = escape(base64.b64encode(hashed.digest()))

        # Tarkastetaan vastaako luotu allekirjoitus pyynnön allekirjoitusta:
        if signature != auth_dict["signature"]:
            return json("fail", {"signature": "incorrect signature"})

        # Allekirjoitus oikein -> autorisointi onnistui:
        g.user = user
        return f(*args, **kwargs)

    return decorator
