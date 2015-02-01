from twisted.internet import reactor
from twisted.enterprise import adbapi


dbpool = adbapi.ConnectionPool('sqlite3', 'users.db', check_same_thread=False)


def getName(email):
    return dbpool.runQuery('SELECT name FROM users WHERE email = ?', (email,))


def printResults(results):
    for item in results:
        print item


def finish():
    dbpool.close()
    reactor.stop()


d = getName('foo@bar.com')
d.addCallback(printResults)

reactor.callLater(1, finish)
reactor.run()
