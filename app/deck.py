from dotenv import dotenv_values
from time import sleep
import requests

from app import db, helpers


def authenticate():
    # fetch secrets from local file
    try:
        config = dotenv_values(".env")
    except:
        return("Credentials file not found")

    url = config['NC_DOMAIN'] + '/index.php/login/v2'

    response = requests.get(url)

    if not response:
        return response.status_code

    res = response.json()

    params = {
        'token': res['poll']['token']
    }

    print('Open', res['login'], 'in a browser')
    e = None
    while e != 200:
        sleep(5) # wait 5 seconds before subsequent request queries
        req = requests.post(res['poll']['endpoint'], params=params)
        e = req.status_code

    # TODO: auto-save DECK_USERNAME/DECK_PASSWORD pair to .env file
    return req.json()


def connect(endpoint, data=None):
    # fetch secrets from local file
    try:
        config = dotenv_values(".env")
        credentials = (config['DECK_USERNAME'], config['DECK_PASSWORD'])
    except:
        return("Credentials not found")

    # compose request
    url = config['NC_DOMAIN'] + endpoint
    hdr = {
        'OCS-APIRequest' : 'true',
        'Content-Type': 'application/json'
    }

    if data:
        response = requests.post(url, auth=credentials, headers=hdr, json=data)
    else:
        response = requests.get(url, auth=credentials, headers=hdr)

    if not response:
        return response.status_code

    return response.json()


# Get Cards from Deck
def get_cards(conn, stack_id, cards):
    cur = conn.cursor()
    result = [db.updateCard(cur, card['title'], card['id'], stack_id) for card in cards]
    conn.commit()
    if result:
        print('Cards updated for stack', stack_id)

    return True


# Get Stacks from Deck
def get_stacks(conn, deck_id):
    cur = conn.cursor()
    endpoint = f"/index.php/apps/deck/api/v1.0/boards/{deck_id}/stacks"
    data = connect(endpoint)
    try:
        stacks = [db.updateList(cur, stack['title'], stack['id'], deck_id) for stack in data]
    except:
        print("Hello")
    conn.commit()

    try:
        cards = [get_cards(conn, stack['id'], stack['cards']) for stack in data]
    except:
        print('No Cards found')

    return stacks


# Get Boards from Deck
def get_boards():
    conn = db.initDb('data/new.sqlite3')
    cur = conn.cursor()
    endpoint = f"/index.php/apps/deck/api/v1.0/boards"
    boards = [db.updateBoard(cur, board['title'], board['id']) for board in connect(endpoint)]
    conn.commit()

    stacks = [get_stacks(conn, deck_id) for deck_id in boards]

    conn.close()

    return boards


# Push to Deck
def push_to_deck():
    conn = db.initDb('data/new.sqlite3')
    cur = conn.cursor()

    res = [create_board(cur, board) for board in db.getBoardsDeck(cur)]

    conn.commit()

    return res


def create_board(cur, board):
    endpoint = f"/index.php/apps/deck/api/v1.0/boards/"

    name = board[0]
    id = board[1]
    try:
        deck_id = board[2]
    except:
        data = {"title": name, "color": helpers.randomColor()}
        deck_id = db.updateBoard(cur, id, connect(endpoint, data))

    return [create_stack(cur, stack, deck_id) for stack in db.getListsData(cur, deck_id)]


# Push Stack to Deck
def create_stack(cur, stack, deck_id):
    endpoint = f"/index.php/apps/deck/api/v1.0/boards/{deck_id}/stacks"

    try:
        stack_id = stack[3]
    except:
        data = {"title": stack[0], "order": stack[2]}
        try:
            stack_id = connect(endpoint, data).json()['id']
            db.updateList(cur, stack['0'], stack_id, deck_id)
        except:
            stack_id = None
            return (f"Importing {stack[0]} failed")

    return [create_card(cur, card, stack_id, endpoint) for card in db.getCards(cur, stack_id)]


# Push Card to Deck
def create_card(cur, card, stack_id, endpoint):
    endpoint += str(stack_id)

    try:
        deck_id = card[3]
    except:
        data = {
            'title': card[0],
            'type': 'plain',
            'order': card[4],
            'description': card[1],
            'duedate': card[2]
        }
        card = connect(endpoint, data)
        try:
            deck_id = card.json()['id']
        except:
            return card

    return deck_id
