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
                starred INTEGER
            );

            CREATE TABLE Lists (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                name TEXT,
                trello_id TEXT UNIQUE,
                closed INTEGER,
                board_id INTEGER NOT NULL
            );

            CREATE TABLE Cards (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                trello_id TEXT UNIQUE,
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

def insertList(cur, name, trello_id, closed, board_id):
    return cur.execute(
        '''INSERT OR IGNORE INTO Lists (name, trello_id, closed, board_id) VALUES ( ?, ?, ?, ? )''',
        ( name, trello_id, closed, board_id )
    )
    # return conn.commit()


def insertCard(cur, trello_id, closed, title, desc, due, list_id):
    return cur.execute(
        '''INSERT OR IGNORE INTO Cards (trello_id, closed, title, desc, due, list_id) VALUES ( ?, ?, ?, ?, ?, ? )''',
        ( trello_id, closed, title, desc, due, list_id )
    )

def getBoards(cur):
    return cur.execute('SELECT trello_id, name FROM Boards;')

def getLists(cur):
    return cur.execute('SELECT Lists.trello_id, Lists.name, Boards.name FROM Lists JOIN Boards ON Lists.board_id = Boards.trello_id')

def getCards(cur):
    return cur.execute('SELECT Cards.title, Lists.name, Boards.name FROM Cards JOIN Lists JOIN Boards ON Cards.list_id=Lists.trello_id AND Lists.board_id=Boards.trello_id')
