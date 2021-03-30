import json

def parseJson(file):
    file = 'data/trello.json'
    try:
        inp = open(file)
    except:
        return("File " + file + " not found")

    data = json.load(inp)
    return data['boards']

def getBoards(data):
    boards = dict()
    for board in data:
        print(board)
        # boards.__setitem__(board['id'],board['name'])
    return boards

# def
