from dotenv import dotenv_values
import requests
import ssl
import json
import sqlite3
from datetime import datetime

from app import db


def connect(baseUrl, params=dict()):
    # fetch secrets from .env
    try:
        config = dotenv_values(".env")
        params['key'] = config['TRELLO_KEY']
        params['token'] = config['TRELLO_TOKEN']
    except:
        return("Credentials file not found")


    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    response = requests.get(baseUrl, params=params)

    if not response:
        return response.status_code

    limits = dict()
    limits['X-Rate-Limit-Api-Key-Remaining'] = response.headers['X-Rate-Limit-Api-Key-Remaining']
    limits['X-Rate-Limit-Api-Token-Remaining'] = response.headers['X-Rate-Limit-Api-Key-Remaining']
    limits['X-Rate-Limit-Member-Remaining'] = response.headers['X-Rate-Limit-Member-Remaining']

    if ('0' in limits.values()):
        return "API Limit reached"

    print(limits)

    return response.json()


def createBoards(data):
    conn = db.initDb('data/new.sqlite3')
    cur = conn.cursor()

    boards = dict(db.getBoards(cur))

    for board in data:
        if board['name'] in boards.keys():
            board_id = boards[board['name']]
            # TODO: Update board if @modified is newer than db value
        else:
            board_id = db.insertBoard(
                conn=conn,
                name=board['name'],
                trello_id=board['id'],
                modified=timeToEpoch(board['dateLastActivity']),
                archived=board['closed'],
                starred=board['starred']
            )
            conn.commit()
        createLists(conn, board_id, board['id'])

    conn.close()
    return True


def createLists(conn, board_id, trello_id):
    cur = conn.cursor()
    lists = dict(db.getListsNew(cur, board_id))

    # id = db.getBoardTrelloId(cur, board_id)[0]
    baseUrl = 'https://api.trello.com/1/boards/'+trello_id+'/lists'
    params = {'cards': 'all'}
    res = connect(baseUrl, params)

    if res == []:
        return "No lists found. Skipping..."

    for list in res:
        if list['name'] in lists.keys():
            list_id = lists[list['name']]
        else:
            list_id = db.insertList(
                cur=cur,
                name=list['name'],
                trello_id=list['id'],
                closed=list['closed'],
                position=list['pos'],
                board_id=board_id
            )
            conn.commit()

        createCards(conn, list_id, list['cards'])

    return True


def createCards(conn, list_id, trello_cards):
    cur = conn.cursor()
    cards = dict(db.getCardsNew(cur, list_id))

    if trello_cards == []:
        return "No cards found."

    for card in trello_cards:
        if card['id'] in cards.keys():
            card_id = cards[card['id']]
            # TODO: updateCard when @modified is newer than db value
        else:
            card_id = db.insertCard(
                cur=cur,
                title=card['name'],
                trello_id=card['id'],
                closed=card['closed'],
                desc=card['desc'],
                position=card['pos'],
                modified=timeToEpoch(card['dateLastActivity']),
                due=timeToEpoch(card['due']),
                list_id=list_id
            )
        conn.commit()

    return card_id


def timeToEpoch(input_time):
    if input_time is None:
        return None

    # Convert time to since-epoch
    utc_time = datetime.strptime(input_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    return int((utc_time - datetime(1970, 1, 1)).total_seconds())
