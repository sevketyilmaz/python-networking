from twisted.internet import reactor, protocol
from twisted.python import log
from twisted.words.protocols import irc


class EchoBot(irc.IRCClient):
    nickname = 'echobotfortwiste'

    def signedOn(self):
        self.join(self.factory.channel)

    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

        log.msg(msg)
        if channel == self.nickname:
            log.msg('Sent PM')
            self.msg(user, msg)
        elif msg.startswith(self.nickname + ','):
            log.msg('Responded in channel')
            self.msg(channel, user + ':' + msg[len(self.nickname + ':'):])

    def action(self, user, channel, action):
        log.msg(action)
        log.msg('Imitated action')
        self.describe(channel, action)


class EchoBotFactory(protocol.ClientFactory):

    def __init__(self, channel):
        self.channel = channel

    def buildProtocol(self, addr):
        proto = EchoBot()
        proto.factory = self
        return proto

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()


network = 'irc.freenode.net'
port = 6667
channel = 'twisted-bot-test'
reactor.connectTCP(network, port, EchoBotFactory(channel))
reactor.run()
