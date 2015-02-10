from twisted.internet import reactor
from twisted.enterprise import adbapi


dbpool = adbapi.ConnectionPool('sqlite3', 'users.db', check_same_thread=False)


def _createUsersTable(transaction, users):
    transaction.execute('CREATE TABLE IF NOT EXISTS users(email TEXT, name TEXT)')
    for email, name in users:
        transaction.execute('INSERT INTO users (email, name) VALUES(?, ?)', (email, name))


def createUsersTable(users):
    return dbpool.runInteraction(_createUsersTable, users)


def getName(email):
    return dbpool.runQuery('SELECT name FROM users WHERE email = ?', (email,))


def printResults(results):
    for item in results:
        print item


def finish():
    dbpool.close()
    reactor.stop()


users = [('foo@bar.com', 'Foo'), ('bar@foo.com', 'Bar')]
d = createUsersTable(users)
d.addCallback(lambda u: getName('foo@bar.com'))
d.addCallback(printResults)


reactor.callLater(1, finish)
reactor.run()
