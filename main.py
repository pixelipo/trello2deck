from app import trello, parser, deck, db


service = input("Select service:\n[1] Import from Trello\n[2] Import from JSON\n[3] Export to Deck\n")

## Import data from Trello to SQLite Database
if (service == '1'):
    baseUrl = 'https://api.trello.com/1/members/me/boards?'
    trello.createBoards(trello.connect(baseUrl))
    print(trello.createLists())
    print(trello.createCards())

if (service == '2'):
    data = parser.parseJson(input("type filename (default: data/trello.json):"))
    print(parser.getBoards(data))

if (service == '3'):
    # print(deck.authenticate())
    # print(deck.connect())
    print(deck.postBoards())
    print(deck.postLists())
