# -*-coding:utf-8-*-
"""
Räpellys API:n autorisoinnin testaamista varten.

"""

from flask import Flask, request
import time
import urllib
import base64
from hashlib import sha1
import hmac
from uuid import uuid4
import requests
import sys


try:
    API_URL = sys.argv[1]
    if not API_URL.startswith("http://"):
        API_URL = "http://" + API_URL
except IndexError:
    API_URL = "http://toimiiks.cloudapp.net"

PASSWORD_SALT = "djn12gsiugaieufe4f8fafh"
app = Flask(__name__)


def escape(text):
    """
    Palauttaa merkkijonon url-enkoodattuna.
    """
    return urllib.quote(text.encode("utf-8"), "")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    GET palauttaa rekisteröintilomakkeen,
    POST lisää uuden käyttäjän, palauttaa API:n vastauksen.
    """
    if request.method == "GET":
        return """
        <html><head></head><body>
        <h4>Register</h4>
        <form action="/register" method="POST">
        username: <input type="text" name="username">
        user key: <input type="text" name="key">
        <input type="submit" value="submit">
        </form></body></html>
        """
    # Hashataan salasana:
    key = sha1(request.form["key"].encode("utf-8") + PASSWORD_SALT).hexdigest()

    data = {"username": request.form["username"], "key": key}
    r = requests.post(API_URL + "/register", data=data)
    return r.text


@app.route("/", methods=["GET", "POST"])
def index():
    """
    GET palauttaa lomakkeen jonka kautta voi lähettää syötetyillä parametreillä
    autorisoituja HTTP-pyyntöjä API-palvelimelle.

    POST lähettää lomakkeen mukaisen pyynnön API-palvelimelle ja palauttaa API:n
    vastauksen.
    """
    if request.method == "GET":
        return """
        <html><head></head><body>
        <form action="/" method="POST">
        url: <input type="text" name="url" value="%s/api/json/" autofocus>
        data: <input type="text" name="data">
        appname: <input type="text" name="appname" value="sovelluksen nimi">
        app key: <input type="text" name="app_key" value="sovelluksen avain">
        username: <input type="text" name="username" value="aleksi">
        user key: <input type="text" name="user_key" value="aleksi">
        method: <select name="method"><option value="GET">GET</option>
        <option value="POST">POST</option>
        <option value="PUT">PUT</option>
        <option value="DELETE">DELETE</option></select>
        <input type="submit" value="submit">
        </form></body></html>
        """ % API_URL
    url = request.form["url"]
    method = request.form["method"]
    data_items = request.form["data"].split("&")
    if data_items and data_items != [""]:
        data = {k: v for k, v in [x.split("=") for x in data_items]}
    else:
        data = {}
    timestamp = str(time.time()).split(".")[0]
    params = {
        "username": request.form["username"],
        "client": request.form["appname"],
        "timestamp": timestamp,
    }

    # Nämä parametrit eivät tule Authorization-headeriin,
    # niitä käytetään vain allekirjoituksessa:
    signature_params = dict(params.items() + data.items())

    # Kääritään parametrit yhteen merkkijonoon:
    params_str = "&".join(
        ["%s=%s" % (escape(key), escape(signature_params[key]))
            for key in sorted(signature_params)])
    base_string = "&".join([method, escape(url),
                            escape(params_str)])

    # Luodaan allekirjoitus:
    user_key = sha1(request.form["user_key"].encode("utf-8") + PASSWORD_SALT).hexdigest()
    signing_key = request.form["app_key"] + "&" + user_key
    hashed = hmac.new(signing_key.encode("utf-8"), base_string.encode("utf-8"), sha1)

    # Lisätään allekirjoitus Authorization-headerin parametreihin:
    params["signature"] = base64.b64encode(hashed.hexdigest())

    # Kääritään Authorization-headerin parametrit:
    auth_header = ",".join(['%s="%s"' %
                  (escape(k), escape(v)) for k, v in params.items()])

    # Lähetetään pyyntö palvelimelle, palautetaan vastaus:
    headers = {"Authorization": auth_header}
    methods = {
        "GET": requests.get,
        "PUT": requests.put,
        "POST": requests.post,
        "DELETE": requests.delete
    }

    if method in ["GET", "DELETE"]:
        r = methods[method](url, params=data, headers=headers)
    else:
        r = methods[method](url, data=data, headers=headers)

    return "RESPONSE:<br>%s<br><br>BASE STRING:<br>%s<br><br>HEADERS:<br>%s" % (r.text, base_string, headers)
    # return r.text, r.status_code


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5001)
