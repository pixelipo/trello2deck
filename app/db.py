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
                starred INTEGER,
                archived INTEGER,
                modified INTEGER
            );

            CREATE TABLE Lists (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                name TEXT,
                trello_id TEXT UNIQUE,
                deck_id INTEGER,
                closed INTEGER,
                position INTEGER,
                board_id INTEGER NOT NULL
            );

            CREATE TABLE Cards (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                trello_id TEXT UNIQUE,
                deck_id INTEGER,
                closed INTEGER,
                position INTEGER,
                title TEXT,
                desc TEXT,
                due INTEGER,
                list_id INTEGER NOT NULL,
                modified INTEGER
            );
        ''')
        print("Database schema created")

    return(conn)


def insertBoard(conn, name, trello_id, modified, starred, archived):
    cur = conn.cursor()
    res = cur.execute(
        '''INSERT OR IGNORE INTO Boards (name, trello_id, modified, starred, archived) VALUES ( ?, ?, ?, ?, ? )''',
        ( name, trello_id, modified, starred, archived )
    )
    return cur.lastrowid


def updateBoard(cur, name, deck_id):
    res = cur.execute(
        '''UPDATE Boards SET deck_id = ? WHERE name = ? ''',
        ( deck_id, name )
    )
    # conn.commit()
    return res


def insertList(cur, name, trello_id, closed, position, board_id):
    cur.execute(
        '''INSERT OR IGNORE INTO Lists (name, trello_id, closed, position, board_id) VALUES ( ?, ?, ?, ?, ? )''',
        ( name, trello_id, closed, position, board_id )
    )
    return cur.lastrowid


def insertCard(cur, title, trello_id, closed, desc, position, modified, due, list_id):
    cur.execute(
        '''INSERT OR IGNORE INTO Cards (
            title,
            trello_id,
            closed,
            desc,
            position,
            modified,
            due,
            list_id
        ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ? )''',
        ( title, trello_id, closed, desc, position, modified, due, list_id )
    )
    return cur.lastrowid


def updateList(cur, name, deck_id):
    res = cur.execute(
        '''UPDATE Lists
           SET deck_id = ?
           WHERE name = ? ''',
        ( deck_id, name )
    )
    # conn.commit()
    return res


def updateCard(cur, title, deck_id, list_id):
    res = cur.execute(
        '''UPDATE Cards SET deck_id = ?, list_id = ? WHERE title = ? ''',
        ( deck_id, list_id, title )
    )
    # conn.commit()
    return res

def getBoards(cur):
    cur.execute('SELECT name, id FROM Boards;')
    return cur.fetchall()

def getBoardTrelloId(cur, board_id):
    cur.execute('SELECT trello_id FROM Boards WHERE id = ?;', (board_id,))
    return cur.fetchone()

def getListsNew(cur, board_id):
    cur.execute('SELECT name, id FROM Lists WHERE board_id = ?', (board_id,))
    return cur.fetchall()


def getLists(cur, board_name):
    query = '''SELECT Lists.trello_id, Lists.name, Lists.deck_id FROM Lists JOIN Boards ON Lists.board_id = Boards.id WHERE Boards.name = ?
        '''
    return cur.execute(query, (board_name,))

def getCardsNew(cur, list_id):
    cur.execute('SELECT trello_id, id FROM Cards WHERE list_id = ?', (list_id,))
    return cur.fetchall()

def getCards(cur, list_id):
    return cur.execute(
        '''SELECT Cards.title, Cards.desc, Cards.due, Cards.deck_id, Lists.id
           FROM Cards JOIN Lists
           ON Cards.list_id=Lists.trello_id
           WHERE Lists.deck_id= ?
           ''', (list_id,))
