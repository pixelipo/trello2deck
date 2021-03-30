import os

import urllib.request, urllib.parse
from urllib.error import URLError
import ssl
import json
import base64
# import sqlite3

# from app import db


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def connect():
    parms = dict()
    # fetch secrets from local file
    try:
        from env.conf import deck
        baseUrl = deck['domain'] + '/index.php/apps/deck/api/v1.0/boards/1'
        username = deck['username']
        password = deck['password']
    #     parms['key'] = trello['key']
    #     parms['token'] = trello['token']
    except:
        return("Nexcloud domain not found")


    # baseUrl = 'https://api.trello.com/1/members/me/boards?'
    url = baseUrl + urllib.parse.urlencode(parms)
    print(username)
    b64auth = base64.standard_b64encode('%s:%s' % (username, password))
    hdr = {
        'OCS-APIRequest' : 'true',
        'Content-Type': 'application/json',
        'Authorization': 'Basic %s' % b64auth
    }

    # request.add_header("Authorization", "Basic %s" % b64auth)
    # print(url)
    try:
        req = urllib.request.Request(url, headers=hdr)
        print(req)
        response = urllib.request.urlopen(req, context=ctx)
    except URLError as e:
        return e


    # data = connection.read()
    # limits = dict()
    # limits['X-Rate-Limit-Api-Key-Remaining'] = response.info()['X-Rate-Limit-Api-Key-Remaining']
    # limits['X-Rate-Limit-Api-Token-Remaining'] = response.info()['X-Rate-Limit-Api-Key-Remaining']
    # limits['X-Rate-Limit-Member-Remaining'] = response.info()['X-Rate-Limit-Member-Remaining']

    # if ('0' in limits.values()):
    #     return "API Limit reached"
    # print(limits)
    res = response.read().decode()
    return json.loads(res)
