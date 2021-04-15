from app import trello, parser, deck


service = input('''Select service:
    [1] Import from Trello
    [2] Import from JSON
    [3] Authenticate with Deck
    [4] Export to Deck
''')

## Import data from Trello to SQLite Database
if (service == '1'):
    baseUrl = 'https://api.trello.com/1/members/me/boards'
    trello.createBoards(trello.connect(baseUrl))

if (service == '2'):
    data = parser.parseJson(input("type filename (default: data/trello.json):"))
    print(parser.getBoards(data))

if (service == '3'):
    print(deck.authenticate())

if (service == '4'):
    # deck.get_boards()
    deck.push_to_deck()
