import os
from random import randint

from urllib import request, parse
from urllib.error import URLError, HTTPError
import requests, logging
import ssl
import json
import base64
# import sqlite3

from app import db


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def authenticate():
    parms = dict()
    # fetch secrets from local file
    try:
        from env.conf import deck
        baseUrl = deck['domain'] + '/index.php/apps/deck/api/v1.0/boards/1'
        username = deck['username']
        # password = deck['password']
    #     parms['key'] = trello['key']
    #     parms['token'] = trello['token']
    except:
        return("Nexcloud domain not found")

    data = parse.urlencode(parms).encode()
    try:
        req =  request.Request(deck['domain']+'/index.php/login/v2', data=data) # this will make the method "POST"
        response = request.urlopen(req)
    except URLError as e:
        return e

    res = json.loads(response.read().decode())
    # print(res)
    token = res['poll']['token']
    data = {'token': token}
    data = parse.urlencode(data).encode()
    #
    e = 1
    print('Open', res['login'], 'in a browser')
    while e != 200:
        try:
            req = request.Request(res['poll']['endpoint'], data=data)
            res = request.urlopen(req, context=ctx)
            e = res.getcode()
        except HTTPError as err:
            e = err.code

    res = json.loads(res.read().decode())
    return res


def connect(data=None):
    # Fetch secrets locally
    try:
        from env.conf import deck
        baseUrl = deck['domain']
        credentials = (deck['username'], deck['password'])
    except:
        # TODO: populate env.conf using authenticate() function
        return("Credentials not found")

    url = baseUrl + '/index.php/apps/deck/api/v1.0/boards'
    hdr = {
        'OCS-APIRequest' : 'true',
        'Content-Type': 'application/json'
    }
    if data:
        response = requests.post(url, auth=credentials, headers=hdr, json=data)
        print(response)
        return response.status_code

    response = requests.get(url, auth=credentials, headers=hdr)


    # If the HTTP GET request can be served
    if response.status_code != 200:
        return response

    boards = dict()
    for board in json.loads(response.text):
        boards.__setitem__(board['id'], board['title'])

    return boards

def postBoards():
    conn = db.initDb('data/db.sqlite3')
    cur=conn.cursor()
    trello = db.getBoards(conn).fetchall()
    deck = connect()

    for id, name in trello:
        if name in deck.values():
            print(name, 'found; skipping')
            continue

        connect({"title": name, "color": randomColor()})
    return True


def randomColor():
    r = lambda: randint(0,255)
    return ('%02X%02X%02X' % (r(),r(),r()))
