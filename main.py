from app import trello, parser, deck, db


service = input("Select service([1] Fetch from Trello [2] Fetch from JSON [3] Export to Deck:")

## Connect to Trello via API
if (service == '1'):
    # baseUrl = 'https://api.trello.com/1/members/me/boards?'
    # res = trello.createBoards(trello.connect(baseUrl))
    # if res:
        # print(res)
    # print(trello.createLists())
    # print(trello.createCards())
    conn = db.initDb('data/db.sqlite3')
    cur=conn.cursor()
    print(db.getCards(cur).fetchall())

if (service == '2'):
    data = parser.parseJson(input("type filename (default: data/trello.json):"))
    print(parser.getBoards(data))

if (service == '3'):
    # print(deck.authenticate())
    print(deck.connect())
