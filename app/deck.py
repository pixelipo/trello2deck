import os

from urllib import request, parse
from urllib.error import URLError, HTTPError
import requests
import ssl
import json
import base64
# import sqlite3

# from app import db


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


def connect():
    parms = dict()
    # fetch secrets from local file
    try:
        from env.conf import deck
        baseUrl = deck['domain']
        parms['username'] = deck['username']
        parms['password'] = deck['password']
    except:
        return("credentials file not found")


    basicAuthCredentials = (parms['username'], parms['password'])
    url = baseUrl + '/index.php/apps/deck/api/v1.0/boards/1'
    hdr = {
        'OCS-APIRequest' : 'true',
        'Content-Type': 'application/json'
    }
    # Send HTTP GET request to server and attempt to receive a response
    print(url)
    response = requests.get(url, auth=basicAuthCredentials, headers=hdr)

    # If the HTTP GET request can be served
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return dir(response)

    # baseUrl = 'https://api.trello.com/1/members/me/boards?'

    # url = baseUrl + parse.urlencode(parms)
    # print(username)

    # b64auth = base64.standard_b64encode('%s:%s' % (username, password))



    # req = request.Request(url)
    # req.add_header("OCS-APIRequest", "true")
    # req.add_header("Content-Type", "application/json")
    # print(req.full_url)
    # try:
    #     resp = request.urlopen(req, context=ctx).headers()
    #     return resp.read()
    # except HTTPError as e:
    #     return e



    # try:
    #
    #     print(requests.get(url, auth=(credentials['loginName'], credentials['appPassword'])).content, headers=hdr)
    #     # data = parse.urlencode(parms).encode()
    #     # req =  request.Request(deck['domain']+'/index.php/login/v2', data=data) # this will make the method "POST"
    #     # response = request.urlopen(req)
    #     # # req = request.Request(url, headers=hdr)
    #     # # print(req)
    #     # # response = request.urlopen(req, context=ctx)
    # except URLError as e:
    #     return e


    # data = connection.read()
    # limits = dict()
    # limits['X-Rate-Limit-Api-Key-Remaining'] = response.info()['X-Rate-Limit-Api-Key-Remaining']
    # limits['X-Rate-Limit-Api-Token-Remaining'] = response.info()['X-Rate-Limit-Api-Key-Remaining']
    # limits['X-Rate-Limit-Member-Remaining'] = response.info()['X-Rate-Limit-Member-Remaining']

    # if ('0' in limits.values()):
    #     return "API Limit reached"
    # print(limits)
    # res = response.read().decode()
    # return response
    # return json.loads(res)
