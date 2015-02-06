from os.path import expanduser
import base64
import sys

from twisted.conch import error
from twisted.conch.ssh import keys, factory
from twisted.cred import checkers, credentials, portal
from twisted.internet import reactor
from twisted.python import failure, log
from zope.interface import implements

from password_server import SSHRealm, get_RSA_keys


class PublicKeyCreditentialsChecker:
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.ISSHPrivateKey,)

    def __init__(self, authorized_keys):
        self.authorizedKeys = authorized_keys

    def requestAvatarId(self, credentials):
        log.msg(credentials)
        user_key_string = self.authorizedKeys.get(credentials.username)
        if not user_key_string:
            return failure.Failure(error.ConchError('No such user'))

        # strip ssh-rsa type before decoding
        decoded_string = base64.decodestring(user_key_string.split(' ')[1])
        if decoded_string != credentials.blob:
            raise failure.Failure(error.ConchError('I don\'t recognize this key'))

        if not credentials.signature:
            raise error.ValidPublicKey()

        user_key = keys.Key.fromString(data=user_key_string)
        if user_key.verify(credentials.signature, credentials.sigData):
            return credentials.username
        else:
            log.err('Signature check failed!')
            return failure.Failure(error.ConchError('Incorrect signature'))


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    factory = factory.SSHFactory()
    realm = SSHRealm()
    factory.portal = portal.Portal(realm)

    public_key, private_key = get_RSA_keys()
    factory.publicKeys = {'ssh-rsa': public_key}
    factory.privateKeys = {'ssh-rsa': private_key}

    admin_key_path = expanduser('~/.ssh/id_rsa.pub')
    with open(admin_key_path) as f:
        admin_key = f.read()
    authorized_keys = {'admin': admin_key}
    checker = PublicKeyCreditentialsChecker(authorized_keys)
    factory.portal.registerChecker(checker)

    reactor.listenTCP(2222, factory)
    reactor.run()
