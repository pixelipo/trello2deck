from dotenv import dotenv_values
from random import randint

from urllib import request, parse
from urllib.error import URLError, HTTPError
import requests
import ssl
import json

from app import db


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def authenticate():
    # fetch secrets from local file
    try:
        config = dotenv_values(".env")
    except:
        return("Credentials file not found")

    try:
        req =  request.Request(config['NC_DOMAIN']+'/index.php/login/v2') # this will make the method "POST"
        response = request.urlopen(req)
    except URLError as e:
        return e

    res = json.loads(response.read().decode())

    data = {'token': res['poll']['token']}
    data = parse.urlencode(data).encode()

    e = 1
    print('Open', res['login'], 'in a browser')
    while e != 200:
        try:
            #TODO convert to requests library
            req = request.Request(res['poll']['endpoint'], data=data)
            res = request.urlopen(req, context=ctx)
            e = res.getcode()
        except HTTPError as err:
            e = err.code

    res = json.loads(res.read().decode())
    return res


def connect(endpoint, data=None):
    # fetch secrets from local file
    try:
        config = dotenv_values(".env")
    except:
        return("Credentials file not found")

    # compose request
    url = config['NC_DOMAIN'] + endpoint
    hdr = {
        'OCS-APIRequest' : 'true',
        'Content-Type': 'application/json'
    }
    credentials = (config['DECK_USERNAME'], config['DECK_PASSWORD'])

    if data:
        # print(url, credentials, data)
        response = requests.post(url, auth=credentials, headers=hdr, json=data)
        # print(response.text)
        return response.status_code

    response = requests.get(url, auth=credentials, headers=hdr)

    # If the HTTP GET request can be served
    if response.status_code != 200:
        return response

    return response.text


def postBoards():
    conn = db.initDb('data/db.sqlite3')
    cur=conn.cursor()
    trello = db.getBoards(conn).fetchall()
    endpoint = '/index.php/apps/deck/api/v1.0/boards'
    deck = connect(endpoint)

    boards = dict()
    for board in json.loads(deck):
        boards.__setitem__(board['id'], board['title'])

    for id, name in trello:
        if name in deck.values():
            print(name, 'found; skipping')
            continue

        connect(endpoint, {"title": name, "color": randomColor()})
    return True


def postLists():
    conn = db.initDb('data/db.sqlite3')
    cur=conn.cursor()
    trello = db.getLists(conn).fetchall()
    endpoint = '/index.php/apps/deck/api/v1.0/boards'
    deck = connect(endpoint)

    boards = dict()
    for board in json.loads(deck):
        boards.__setitem__(board['title'], board['id'])

    count = 1
    for l in trello:
        boardId = str(boards.get(l[2]))
        url = endpoint + '/' + boardId + '/stacks'

        res = connect(url, {"title": l[1], "order": count})
        # print(res)
        if res == 200:
            print(l[1], 'added')
            count += 1
        else:
            print('list', l[1], 'found in', l[2])

    return count


def randomColor():
    r = lambda: randint(0,255)
    return ('%02X%02X%02X' % (r(),r(),r()))
