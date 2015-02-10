from twisted.cred import checkers, portal
from twisted.internet import reactor
from twisted.words import service


worldRealm = service.InMemoryWordsRealm('example.com')
worldRealm.createGroupOnRequest = True

checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(user='pass')
portal = portal.Portal(worldRealm, [checker])

reactor.listenTCP(6667, service.IRCFactory(worldRealm, portal))
reactor.run()
