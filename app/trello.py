from dotenv import dotenv_values
import requests
import ssl
import json
import sqlite3

from app import db


def connect(baseUrl):
    # fetch secrets from .env
    params = dict()
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
        return response.status

    limits = dict()
    limits['X-Rate-Limit-Api-Key-Remaining'] = response.headers['X-Rate-Limit-Api-Key-Remaining']
    limits['X-Rate-Limit-Api-Token-Remaining'] = response.headers['X-Rate-Limit-Api-Key-Remaining']
    limits['X-Rate-Limit-Member-Remaining'] = response.headers['X-Rate-Limit-Member-Remaining']

    if ('0' in limits.values()):
        return "API Limit reached"

    print(limits)

    res = response.content
    return json.loads(res)


def createBoards(data):
    conn = db.initDb('data/db.sqlite3')

    for board in data:
        # board['dateLastActivity']
        # format = "%Y-/%m-%dT%H:%M:%S" #2016-08-28T12:09:14.623Z
        # modified = datetime.datetime(2012,4,1,0,0).timestamp()
        db.insertBoard(
            conn=conn,
            name=board['name'],
            trello_id=board['id'],
            # modified=modified,
            starred=board['starred']
        )

    return db.getBoards(conn)


def createLists():
    conn = db.initDb('data/db.sqlite3')
    cur = conn.cursor()
    boards = db.getBoards(cur).fetchall()

    for id, name in boards:
        baseUrl = 'https://api.trello.com/1/boards/'+id+'/lists?'
        res = connect(baseUrl)
        for line in res:
            db.insertList(
                cur=cur,
                name=line['name'],
                trello_id=line['id'],
                closed=line['closed'],
                board_id=id
            )
        conn.commit()

    return db.getLists(cur).fetchall()


def createCards():
    conn = db.initDb('data/db.sqlite3')
    cur = conn.cursor()

    lists = db.getLists(cur).fetchall()

    count = 0
    for id, name, boardName in lists:
        baseUrl = 'https://api.trello.com/1/lists/'+id+'/cards?'
        res = connect(baseUrl)
        count += len(res)

        for line in res:
            db.insertCard(
                cur=cur,
                trello_id=line['id'],
                closed=line['closed'],
                title=line['name'],
                desc=line['desc'],
                due=0,
                list_id=id
            )
        conn.commit()

    return count
