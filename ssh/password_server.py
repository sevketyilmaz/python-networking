from os.path import expanduser
import sys

from twisted.conch import avatar, recvline
from twisted.conch.insults import insults
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import factory, keys, session
from twisted.cred import portal, checkers
from twisted.internet import reactor
from twisted.python import log
from zope.interface import implements


class SSHProtocol(recvline.HistoricRecvLine):

    def __init__(self, user):
        self.user = user
        self.username = self.user.username

    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        log.msg('{0} logged in'.format(self.username))
        self.terminal.write('Welcome! {0}'.format(self.username))
        self.terminal.nextLine()
        self.do_help()
        self.show_prompt()

    def show_prompt(self):
        self.terminal.write('$ ')

    def get_command_function(self, cmd):
        return getattr(self, 'do_' + cmd, None)

    def lineReceived(self, line):
        line = line.strip()
        if line:
            cmd_and_args = line.split()
            cmd = cmd_and_args[0]
            args = cmd_and_args[1:]
            function = self.get_command_function(cmd)
            if function:
                try:
                    function(*args)
                    log.msg('{0} executed command {1}.'.format(self.username, function.func_name))
                except Exception as e:
                    log.err('{0} failed to execute command {1}.'.format(self.username, function.func_name))
                    self.terminal.write('Error: {0}'.format(e))
                    self.terminal.nextLine()
            else:
                log.err('{0} tried to execute a non-existing command.')
                self.terminal.write('No such command.')
                self.terminal.nextLine()
        self.show_prompt()

    def do_help(self):
        public_methods = [function_name for function_name in dir(self) if function_name.startswith('do_')]
        commands = [cmd.replace('do_', '', 1) for cmd in public_methods]
        self.terminal.write('Commands: ' + ' '.join(commands))
        self.terminal.nextLine()

    def do_echo(self, *args):
        self.terminal.write(' '.join(args))
        self.terminal.nextLine()

    def do_whoami(self):
        self.terminal.write(self.user.username)
        self.terminal.nextLine()

    def do_quit(self):
        self.terminal.write('Bye!')
        self.terminal.nextLine()
        self.terminal.loseConnection()

    def do_clear(self):
        self.terminal.reset()


class SSHAvatar(avatar.ConchUser):
    implements(ISession)

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})

    def openShell(self, protocol):
        server_protocol = insults.ServerProtocol(SSHProtocol, self)
        server_protocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(server_protocol))

    def getPty(self, terminal, window_size, attrs):
        return None

    def execCommand(self, protocol, cmd):
        raise NotImplementedError

    def closed(self):
        pass


class SSHRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser not in interfaces:
            raise NotImplementedError('No supported interfaces found.')
        return interfaces[0], SSHAvatar(avatarId), lambda: None


def get_key(path):
    with open(path) as f:
        contents = f.read()
    return keys.Key.fromString(data=contents)


def get_RSA_keys():
    ssh_folder = expanduser('~/.ssh/')
    public_key = get_key(ssh_folder + 'id_rsa.pub')
    private_key = get_key(ssh_folder + 'id_rsa')
    return public_key, private_key


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    factory = factory.SSHFactory()
    factory.portal = portal.Portal(SSHRealm())

    users = {'admin': 'aaa', 'guest': 'bbb'}
    factory.portal.registerChecker(
        checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))

    public_key, private_key = get_RSA_keys()
    factory.publicKeys = {'ssh-rsa': public_key}
    factory.privateKeys = {'ssh-rsa': private_key}

    reactor.listenTCP(2222, factory)
    reactor.run()
