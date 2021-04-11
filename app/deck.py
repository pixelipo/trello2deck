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
    else:
        response = requests.get(url, auth=credentials, headers=hdr)

    return response


def postBoards():
    conn = db.initDb('data/db.sqlite3')
    cur=conn.cursor()
    trello = db.getBoards(conn).fetchall()

    endpoint = '/index.php/apps/deck/api/v1.0/boards'

    for trello_id, name, deck_id in trello:
        if deck_id is None:
            res = connect(endpoint, {"title": name, "color": randomColor()})
            if res.status_code == 200:
                # print(res.json())
                deck_id = res.json()['id']
                db.updateBoard(cur, name, deck_id)
                conn.commit()
                # TODO: Update board's lists board_id with Boards.id
                print('Added', name)
            else:
                print(res.status_code, res)
        else:
            print(name, 'found. Skipping...')

        postLists(deck_id, name)

    return True


def postLists(board_id, board_name):
    # Get Lists by @board_name
    conn = db.initDb('data/db.sqlite3')
    cur=conn.cursor()
    trello = db.getLists(conn, board_name).fetchall()

    if len(trello) == 0:
        # No lists found for a given board
        print('No lists found for ' + board_name + '; skipping...')
        return False

    endpoint = '/index.php/apps/deck/api/v1.0/boards/' + str(board_id) + '/stacks'

    for index, list in enumerate(trello):
        trello_id = list[0]
        name = list[1]
        deck_id = list[2]


        if deck_id is None:
            res = connect(endpoint, {"title": name, "order": index})
            if res.status_code == 200:
                # print(res.json())
                deck_id = res.json()['id']
                db.updateList(cur, name, deck_id)
                conn.commit()
                print('Imported', name)
            else:
                print('Error importing', name, ':\n', res.status_code, res)
        else:
            print(name, 'found; skipping...')

        postCards(endpoint, deck_id)

    return True


def postCards(endpoint, list_id):
    conn = db.initDb('data/db.sqlite3')
    cur=conn.cursor()

    url = endpoint + '/' + str(list_id)
    getCards = connect(url)
    if getCards.status_code == 200:
        try:
            cards = getCards.json()['cards']
            deck_cards = dict()
            for card in cards:
                deck_cards[card['title']] = card['id']
        except:
            deck_cards = dict()

    cards = db.getCards(conn, list_id).fetchall()
    url += '/cards'
    # print(enumerate(cards))
    for index, card in enumerate(cards):
        title = card[0]
        desc = card[1]
        # due = card[2] # TODO: handle duedate
        card_id = card[3]

        if title in deck_cards.keys():
            print('Card found. Skipping...')
            continue

        data = {
            'title': title,
            'type': 'plain',
            'order': index,
            'description': desc#,
            # 'duedate': card[2]
        }
        res = connect(url, data)
        if res.status_code == 200:
            db.updateCard(cur, title, res.json()['id'], list_id)
            conn.commit()
            print(title, 'added')
        else:
            print('Error importing', title, '\n', res)

    return True


def randomColor():
    r = lambda: randint(0,255)
    return ('%02X%02X%02X' % (r(),r(),r()))


# def createBoard(board_name):
#     endpoint = '/index.php/apps/deck/api/v1.0/boards'
#
#     res = connect(endpoint, {"title": board_name, "color": randomColor()})
#     if res.status_code == 200:
#         conn = db.initDb('data/db.sqlite3')
#         cur=conn.cursor()
#         res = db.updateBoard(cur, board_name, res.json()[0]['id'])
#         conn.commit()
#         conn.close()
#         return res
#     else:
#         return res.status_code
