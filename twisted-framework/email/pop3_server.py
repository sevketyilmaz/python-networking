import os
import sys

from zope.interface import implements
from twisted.cred import checkers, portal
from twisted.internet import protocol, reactor
from twisted.mail import maildir, pop3
from twisted.python import log


class UserInbox(maildir.MaildirMailbox):

    def __init__(self, user_dir):
        inbox_dir = os.path.join(user_dir, 'Inbox')
        maildir.MaildirMailbox.__init__(self, inbox_dir)


class POP3ServerProtocol(pop3.POP3):

    def lineReceived(self, line):
        log.msg('CLIENT: {0}'.format(line))
        pop3.POP3.lineReceived(self, line)

    def sendLine(self, line):
        log.msg('SERVER: {0}'.format(line))
        pop3.POP3.sendLine(self, line)


class POP3Factory(protocol.Factory):

    def __init__(self, portal):
        self.portal = portal

    def buildProtocol(self, addr):
        proto = POP3ServerProtocol()
        proto.portal = self.portal
        return proto


class MailUserRealm:
    implements(portal.IRealm)

    def __init__(self, base_dir):
        self.baseDir = base_dir

    def requestAvatar(self, avatarId, mind, *interfaces):
        if pop3.IMailbox not in interfaces:
            log.err('Invalid interface used')
            raise NotImplementedError('This realm only supports pop3.IMailbox interfaces.')

        user_dir = os.path.join(self.baseDir, avatarId)
        avatar = UserInbox(user_dir)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return pop3.IMailbox, avatar, lambda: None


log.startLogging(sys.stdout)
data_dir = '/tmp/mail'

realm = MailUserRealm(data_dir)
portal = portal.Portal(realm)
checker = checkers.FilePasswordDB(os.path.join(data_dir, 'passwords.txt'))
portal.registerChecker(checker)

reactor.listenTCP(1100, POP3Factory(portal))
reactor.run()
