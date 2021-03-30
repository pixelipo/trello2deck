import os

import urllib.request
from urllib.error import URLError
import  urllib.parse
import ssl
import json
import sqlite3

from app import db


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def connect(baseUrl):
    parms = dict()
    # fetch secrets from local file
    try:
        from env.conf import trello
        parms['key'] = trello['key']
        parms['token'] = trello['token']
    except:
        return("credentials file not found")


    # baseUrl = 'https://api.trello.com/1/members/me/boards?'
    url = baseUrl + urllib.parse.urlencode(parms)

    try:
        response = urllib.request.urlopen(url, context=ctx)
    except URLError as e:
        return e

    # data = connection.read()
    limits = dict()
    limits['X-Rate-Limit-Api-Key-Remaining'] = response.info()['X-Rate-Limit-Api-Key-Remaining']
    limits['X-Rate-Limit-Api-Token-Remaining'] = response.info()['X-Rate-Limit-Api-Key-Remaining']
    limits['X-Rate-Limit-Member-Remaining'] = response.info()['X-Rate-Limit-Member-Remaining']

    if ('0' in limits.values()):
        return "API Limit reached"
    print(limits)
    res = response.read().decode()
    return json.loads(res)

def createBoards(data):
    conn = db.initDb('data/db.sqlite3')

    # boards = dict()
    for board in data:
        # boards.__setitem__(board['id'],board['name'])
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
    cur=conn.cursor()
    boards = db.getBoards(cur).fetchall()
    # lists = list()
    for id, name in boards:
        # print(id, name)
        baseUrl = 'https://api.trello.com/1/boards/'+id+'/lists?'
        res = connect(baseUrl)
        for line in res:
            # print(line)
            db.insertList(
                cur=cur,
                name=line['name'],
                trello_id=line['id'],
                closed=line['closed'],
                board_id=id
            )
        conn.commit()
            # conn.close()
            # lists.append({'listId': line['id'], 'listTitle': line['name'], 'boardId': id, 'boardName': name})

    return db.getLists(cur).fetchall()


def createCards():
    conn = db.initDb('data/db.sqlite3')
    cur=conn.cursor()

    lists = db.getLists(cur).fetchall()
    # print(lists)
    count = 0
    for id, name, boardName in lists:
        baseUrl = 'https://api.trello.com/1/lists/'+id+'/cards?'
        res = connect(baseUrl)
        count += len(res)
        for line in res:
            # print(line)
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
