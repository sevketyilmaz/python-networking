from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver


class ChatProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.name = None
        self.state = 'REGISTER'

    def connectionMade(self):
        self.sendLine('What\'s your name?')

    def connectionLost(self):
        if self.name in self.factory.users:
            del self.factory.users[self.name]
            self.broadcastMessage('{0} has left the channel.'.format(self.name))

    def lineReceived(self, line):
        if self.state == 'REGISTER':
            self.handleREGISTER(line)
        else:
            self.handleCHAT(line)

    def handleREGISTER(self, name):
        if name in self.factory.users:
            self.sendLine('Name taken.')
            return
        self.sendLine('Welcome {0}.'.format(name))
        self.broadcastMessage('{0} has joined the channel.'.format(name))
        self.name = name
        self.factory.users[name] = self
        self.state = 'CHAT'

    def handleCHAT(self, message):
        message = '<{0}> {1}'.format(self.name, message)
        self.broadcastMessage(message)

    def broadcastMessage(self, message):
        for protocol_ in self.factory.users.values():
            if protocol_ != self:
                protocol_.sendLine(message)


class ChatFactory(protocol.Factory):

    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return ChatProtocol(self)


if __name__ == '__main__':
    reactor.listenTCP(8000, ChatFactory())
    reactor.run()
