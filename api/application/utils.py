# -*-coding:utf-8-*-
"""
Apufunktiota ym. työkaluja.

Aleksi Pekkala
"""

import urllib
from datetime import datetime, date


# Jsonify-moduuli ei oletuksena osaa muokata MongoDB:n ObjectId-olioita
# eikä datetime-olioita JSON-merkkijonoiksi, konffataan:
# (lähde: Fabrice Aneche github.com/akhenakh)
try:
    import simplejson as json_module
except ImportError:
    import json as json_module
from bson.objectid import ObjectId
from werkzeug import Response


class MongoJsonEncoder(json_module.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return unicode(obj)
        return json_module.JSONEncoder.default(self, obj)


def jsonify(*args, **kwargs):
    """
    Jsonify, joka tukee MongoDB:n ObjectId-olioita ja datetime-olioita.
    """
    return Response(json_module.dumps(dict(*args, **kwargs),
                    cls=MongoJsonEncoder), mimetype="application/json")


def json(status="success", data=None, message=None):
    """
    Palauttaa JSend-spesifikaation mukaisen JSON-merkkijonon.

    http://labs.omniti.com/labs/jsend
    """
    assert status in ["success", "fail", "error"]

    if status in ["success", "fail"]:
        return jsonify(dict(status=status, data=data))

    return jsonify(dict(status="error", message=data))


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
    assert isinstance(c, unicode)  # TODO debug
    c = c.lower().encode("utf-8")
    if c == "ä":
        return "%E4"
    elif c == "ö":
        return "%F6"
    elif c == "å":
        return "%E5"
    return urllib.quote_plus(c)


def objectify(oid):
    """
    Jos oid on merkkijono, muokataan se ObjectId-olioksi,
    jos oid on ObjectId-olio, palautetaan se muokkaamattomana.
    """
    return oid if isinstance(oid, ObjectId) else ObjectId(oid)
