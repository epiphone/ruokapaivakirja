# -*-coding:utf-8-*-
"""
Reititysfunktiot käyttäjätoimintojen (CRUD) osalta.

"""

from application import app
from flask import request, jsonify, g
import database as db
from utils import require_auth, json


@app.route("/")
def index():
    return "Hello world!"


@app.route("/register", methods=["POST"])
def register():
    db.add_user(request.form["username"], request.form["key"])
    return "user %s added" % request.form["username"]


@app.route("/test", methods=["GET", "POST", "PUT", "DELETE"])
def test():
    auth_header = None
    if "Authorization" in request.headers:
        auth_header = request.headers["Authorization"]

    args = {}
    for k, v in request.args.iteritems():
        args[k] = v

    form = {}
    for k, v in request.form.iteritems():
        form[k] = v

    return jsonify({
        "auth_header": auth_header,
        "form": form,
        "args": args
    })


@app.route("/user", methods=["GET", "POST"])
@require_auth
def user():
    # if not "Authorization" in request.headers:
    #     return json_fail({"authorization": "authorization header is required"})

    # # Poimitaan Authorization-headerin parametrit:
    # auth_header = request.headers["Authorization"]
    # auth_params = [param.split("=") for param in auth_header.split(",")]
    # auth_dict = {k: v[1:-1] for k, v in auth_params}

    # # Tarkastetaan timestamp:
    # if time.time() - float(auth_dict["timestamp"]) > TIMESTAMP_LIMIT:
    #     return json_fail({"timestamp": "old timestamp"})

    # # Tarkastetaan käyttäjä:
    # user = db.get_user(unquote(auth_dict["username"]))
    # if not user:
    #     return json_fail({"username": "user not found"})

    # # Poimitaan pyynnön data:
    # method = request.method
    # if method in ["GET", "POST"]:
    #     data_src = request.args
    # else:
    #     data_src = request.form
    # data = {escape(k): escape(v) for k, v in data_src.iteritems()}

    # # Kerätään parametrit allekirjoitusta varten:
    # params = {
    #     "username": auth_dict["username"],
    #     "client": auth_dict["client"],
    #     "timestamp": auth_dict["timestamp"],
    # }

    # signature_params = dict(params.items() + data.items())
    # # Kääritään parametrit yhteen merkkijonoon:
    # params_str = "&".join(
    #     ["%s=%s" % (key, signature_params[key])
    #         for key in sorted(signature_params)])
    # url = request.url.split("?")[0]
    # if not url.startswith("http://"):
    #     url = "http://" + url
    # base_string = "&".join([method, escape(url),
    #                         escape(params_str)])

    # # Luodaan allekirjoitus:
    # signing_key = APP_KEY + "&" + user["key"]
    # hashed = hmac.new(signing_key.encode("utf-8"), base_string.encode("utf-8"), sha1)
    # signature = escape(base64.b64encode(hashed.digest()))

    # if signature != auth_dict["signature"]:
    #     return json_fail({"signature": "incorrect signature"})
    user = g.user
    return json("success", {"username": user["username"], "key": user["key"]})
