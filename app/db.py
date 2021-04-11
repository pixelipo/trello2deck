import sqlite3


def initDb(dbName, reset=False):
    conn = sqlite3.connect(dbName)

    ## Initial setup
    if (reset is True):
        cur = conn.cursor()

        cur.executescript('''
            DROP TABLE IF EXISTS Boards;
            DROP TABLE IF EXISTS Lists;
            DROP TABLE IF EXISTS Cards;

            CREATE TABLE Boards (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                name TEXT UNIQUE,
                trello_id TEXT UNIQUE,
                deck_id INTEGER,
                starred INTEGER
            );

            CREATE TABLE Lists (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                name TEXT,
                trello_id TEXT UNIQUE,
                deck_id INTEGER,
                closed INTEGER,
                board_id INTEGER NOT NULL
            );

            CREATE TABLE Cards (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                trello_id TEXT UNIQUE,
                deck_id INTEGER,
                closed INTEGER,
                title TEXT,
                desc TEXT,
                due INTEGER,
                list_id INTEGER NOT NULL
            );
        ''')
        print("Database schema created")

    return(conn)

def insertBoard(conn, name, trello_id, starred):
    cur = conn.cursor()
    res = cur.execute(
        '''INSERT OR IGNORE INTO Boards (name, trello_id, starred) VALUES ( ?, ?, ? )''',
        ( name, trello_id, starred )
    )
    conn.commit()
    return res

def updateBoard(cur, name, deck_id):
    res = cur.execute(
        '''UPDATE Boards SET deck_id = ? WHERE name = ? ''',
        ( deck_id, name )
    )
    # conn.commit()
    return res

def insertList(cur, name, trello_id, closed, board_id):
    return cur.execute(
        '''INSERT OR IGNORE INTO Lists (name, trello_id, closed, board_id) VALUES ( ?, ?, ?, ? )''',
        ( name, trello_id, closed, board_id )
    )
    # return conn.commit()

def updateList(cur, name, deck_id):
    res = cur.execute(
        '''UPDATE Lists
           SET deck_id = ?,
           board_id=(SELECT id FROM Boards WHERE trello_id=Lists.board_id)
           WHERE name = ? ''',
        ( deck_id, name )
    )
    # conn.commit()
    return res

def insertCard(cur, trello_id, closed, title, desc, due, list_id):
    return cur.execute(
        '''INSERT OR IGNORE INTO Cards (trello_id, closed, title, desc, due, list_id) VALUES ( ?, ?, ?, ?, ?, ? )''',
        ( trello_id, closed, title, desc, due, list_id )
    )

def updateCard(cur, title, deck_id, list_id):
    res = cur.execute(
        '''UPDATE Cards SET deck_id = ?, list_id = ? WHERE title = ? ''',
        ( deck_id, list_id, title )
    )
    # conn.commit()
    return res

def getBoards(cur):
    return cur.execute('SELECT trello_id, name, deck_id FROM Boards;')

def getLists(cur, board_name):
    query = '''SELECT Lists.trello_id, Lists.name, Lists.deck_id FROM Lists JOIN Boards ON Lists.board_id = Boards.id WHERE Boards.name = ?
        '''
    return cur.execute(query, (board_name,))

def getCards(cur, list_id):
    return cur.execute(
        '''SELECT Cards.title, Cards.desc, Cards.due, Cards.deck_id, Lists.id
           FROM Cards JOIN Lists
           ON Cards.list_id=Lists.trello_id
           WHERE Lists.deck_id= ?
           ''', (list_id,))
