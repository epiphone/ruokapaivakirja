# -*-coding:utf-8-*-
"""
Käynnistää API-palvelimen.

"""

from application import app
import sys

try:
    port = int(sys.argv[1])
except KeyError, ValueError:
    port = 5000

app.run(host="0.0.0.0", port=5000)
