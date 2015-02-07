import sys
from getpass import getpass

from twisted.conch.ssh import transport, connection, userauth, channel, common
from twisted.internet import defer, protocol, reactor
from twisted.python import log


class CommandChannel(channel.SSHChannel):
    name = 'session'

    def __init__(self, command, *args, **kwargs):
        channel.SSHChannel.__init__(self, *args, **kwargs)
        self.command = command

    def channelOpen(self, data):
        self.conn.sendRequest(self, 'exec', common.NS(self.command), wantReply=True).addCallback(self._gotResponse)

    def _gotResponse(self, result):
        self.conn.sendEOF(self)

    def dataReceived(self, data):
        log.msg(data)

    def closed(self):
        reactor.stop()


class ClientConnection(connection.SSHConnection):

    def __init__(self, command, *args, **kwargs):
        connection.SSHConnection.__init__(self)
        self.command = command

    def serviceStarted(self):
        command = CommandChannel(self.command, conn=self)
        self.openChannel(command)


class PasswordAuth(userauth.SSHUserAuthClient):

    def __init__(self, user, password, connection):
        userauth.SSHUserAuthClient.__init__(self, user, connection)
        self.password = password

    def getPassword(self, prompt=None):
        return defer.succeed(self.password)


class ClientCommandTransport(transport.SSHClientTransport):

    def __init__(self, username, password, command):
        self.username = username
        self.password = password
        self.command = command

    def verifyHostKey(self, public_key, fingerprint):
        '''Always accept for now'''
        return defer.succeed(True)

    def connectionSecure(self):
        connection = ClientConnection(self.command)
        password_auth = PasswordAuth(self.username, self.password, connection)
        self.requestService(password_auth)


class ClientCommandFactory(protocol.ClientFactory):

    def __init__(self, username, password, command):
        self.username = username
        self.password = password
        self.command = command

    def buildProtocol(self, address):
        protocol = ClientCommandTransport(self.username, self.password, self.command)
        return protocol


if __name__ == '__main__':
    server = 'localhost'
    command = sys.argv[1]
    username = raw_input('Username:')
    password = getpass('Password:')

    factory = ClientCommandFactory(username, password, command)
    reactor.connectTCP(server, 2222, factory)
    reactor.run()
