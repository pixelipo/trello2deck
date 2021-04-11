from app import trello, parser, deck, db


service = input('''Select service:
    [1] Import from Trello
    [2] Import from JSON
    [3] Export to Deck
    [4] Authenticate with Deck
''')

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
    # print(deck.createBoard('lastTest'))
    print(deck.postBoards())

if (service == '4'):
    print(deck.authenticate())
