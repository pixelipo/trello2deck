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
        response = requests.post(url, auth=credentials, headers=hdr, json=data)
        if response.status_code != 200:
            return response.text

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
        boards.__setitem__(board['title'], board['id'])

    for id, name in trello:
        if name in boards.keys():
            print(name, 'found; skipping')
        else:
            connect(endpoint, {"title": name, "color": randomColor()})
            print('Added', name)

        postLists(boards[name], name)

    return True

def postCards(endpoint, list):
    conn = db.initDb('data/db.sqlite3')
    cur=conn.cursor()

    deck = connect(endpoint)

    stacks = dict()
    for stack in json.loads(deck):
        stacks[stack['title']] = stack['id']

    cards = db.getCards(conn, list).fetchall()
    for index, card in enumerate(cards):
        url = endpoint + '/' + str(stacks[card[3]]) + '/cards'
        data = {
            'title': card[0],
            'type': 'plain',
            'order': index,
            'description': card[1]#,
            # 'duedate': card[2]
        }
        res = connect(url, data)
        if res == 200:
            print(card[0], 'added')
        else:
            print('Error importing', card[0], '\n', res)


def postLists(board_id, board_name):
    conn = db.initDb('data/db.sqlite3')
    cur=conn.cursor()
    trello = db.getLists(conn, board_name).fetchall()

    endpoint = '/index.php/apps/deck/api/v1.0/boards/' + str(board_id) + '/stacks'

    deck = connect(endpoint)

    stacks = dict()
    if len(deck) != 0:
        for stack in json.loads(deck):
            stacks[stack['title']] = stack['id']

    for index, l in enumerate(trello):
        if l[1] in stacks.keys():
            print(l[1], 'found; skipping')
        else:
            res = connect(endpoint, {"title": l[1], "order": index})

            if res == 200:
                print(l[1], 'added to', board_id)
            else:
                print('Error importing', l[1])

        postCards(endpoint, l[0])

    return True


def randomColor():
    r = lambda: randint(0,255)
    return ('%02X%02X%02X' % (r(),r(),r()))
