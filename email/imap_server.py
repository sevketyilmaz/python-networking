from StringIO import StringIO
import email
import os
import random
import sys

from twisted.cred import checkers, portal
from twisted.internet import reactor, protocol
from twisted.mail import imap4, maildir
from twisted.python import log
from zope.interface import implements


class IMAPUserAccount:
    implements(imap4.IAccount)

    def __init__(self, user_dir, avatar_id):
        self.dir = user_dir
        self.avatar_id = avatar_id

    def _getMailbox(self, path):
        full_path = os.path.join(self.dir, path)
        if not os.path.exists(full_path):
            raise KeyError('No such mailbox')
        return IMAPMailbox(full_path)

    def listMailboxes(self, ref, wildcard):
        for box in os.listdir(self.dir):
            yield box, self._getMailbox(box)

    def select(self, path, readwrite=False):
        return self._getMailbox(path)


class ExtendedMailDir(maildir.MaildirMailbox):

    def __iter__(self):
        return iter(self.list)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]


class IMAPMailbox:
    implements(imap4.IMailbox)

    def __init__(self, path):
        self.maildir = ExtendedMailDir(path)
        self.listeners = []
        self.uniqueValidityIdentifier = random.randint(1000000, 9999999)

    def getHierarchicalDelimiter(self):
        return '.'

    def getFlags(self):
        return []

    def getMessageCount(self):
        return len(self.maildir)

    def getRecentCount(self):
        return 0

    def isWriteable(self):
        return False

    def getUIDValidity(self):
        return self.uniqueValidityIdentifier

    def _seqMessageSetToSeqDict(self, message_set):
        if not message_set.last:
            message_set.last = self.getMessageCount()

        seq_map = {}
        message_count = self.getMessageCount()
        for message_num in message_set:
            if message_num >= 0 and message_num <= message_count:
                seq_map[message_num] = self.maildir[message_num - 1]
        return seq_map

    def fetch(self, messages, uid):
        if uid:
            raise NotImplementedError('This server only supports lookup by sequence number.')

        messages_to_fetch = self._seqMessageSetToSeqDict(messages)
        for seq, filename in messages_to_fetch.items():
            with open(filename) as f:
                message_content = f.read()
            yield seq, MailDirMessage(message_content)

    def addListener(self, listener):
        self.listeners.append(listener)

    def removeListener(self, listener):
        self.listeners.remove(listener)


class MailDirMessage:
    implements(imap4.IMessage)

    def __init__(self, message_data):
        self.message = email.message_from_string(message_data)

    def getHeaders(self, negate, *names):
        if not names:
            names = self.message.keys()

        headers = {}
        if negate:
            for header in self.message.keys():
                if header.upper() not in names:
                    headers[header.lower()] = self.message.get(header, '')
        else:
            for name in names:
                headers[name.lower()] = self.message.get(name, '')
        return headers

    def getBodyFile(self):
        return StringIO(self.message.get_payload())

    def isMultipart(self):
        return self.message.is_multipart()


class MailUserRealm:
    implements(portal.IRealm)

    def __init__(self, base_dir):
        self.baseDir = base_dir

    def requestAvatar(self, avatarId, mind, *interfaces):
        if imap4.IAccount not in interfaces:
            raise NotImplementedError('This realm only supports imap4.IAccount interfaces.')

        user_dir = os.path.join(self.baseDir, avatarId)
        avatar = IMAPUserAccount(user_dir, avatarId)
        return imap4.IAccount, avatar, lambda: None


class IMAPServerProtocol(imap4.IMAP4Server):

    def lineReceived(self, line):
        log.msg('Client: {0}'.format(line))
        imap4.IMAP4Server.lineReceived(self, line)

    def sendLine(self, line):
        imap4.IMAP4Server.sendLine(self, line)
        log.msg('Server: {0}'.format(line))


class IMAPFactory(protocol.Factory):

    def __init__(self, portal):
        self.portal = portal

    def buildProtocol(self, addr):
        proto = IMAPServerProtocol()
        proto.portal = self.portal
        return proto


log.startLogging(sys.stdout)

data_dir = '/tmp/mail'
portal = portal.Portal(MailUserRealm(data_dir))
checker = checkers.FilePasswordDB(os.path.join(data_dir, 'passwords.txt'))
portal.registerChecker(checker)

reactor.listenTCP(1430, IMAPFactory(portal))
reactor.run()
