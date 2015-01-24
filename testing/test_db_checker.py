from twisted.trial import unittest
from twisted.cred import credentials
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import reactor
from twisted.internet.defer import Deferred

from db_checker import DBCredentialsChecker


class DBCredentialsCheckerTestCase(unittest.TestCase):

    def setUp(self):
        self.creds = credentials.UsernameHashedPassword('user', 'pass')

    def test_requestAvatarId_with_good_credentials(self):
        def fakeRunQueryMatchingPassword(query, username):
            d = Deferred()
            reactor.callLater(0, d.callback, (('user', 'pass'),))
            return d

        def checkRequestAvatar_cb(result):
            self.assertEqual('user',  result)

        checker = DBCredentialsChecker(fakeRunQueryMatchingPassword, 'fake query')
        d = checker.requestAvatarId(self.creds)

        d.addCallback(checkRequestAvatar_cb)
        return d

    def test_requestAvatarId_with_bad_credentials(self):
        def fakeRunQueryBadCredentials(query, username):
            d = Deferred()
            reactor.callLater(0, d.callback, ())
            return d

        checker = DBCredentialsChecker(fakeRunQueryBadCredentials, 'fake query')
        d = checker.requestAvatarId(self.creds)

        def checkError(result):
            self.assertEqual('User not in database', result.message)
        return self.assertFailure(d, UnauthorizedLogin).addCallback(checkError)

    def test_requestAvatarId_with_bad_password(self):
        def fakeRunQueryBadPassword(query, username):
            d = Deferred()
            reactor.callLater(0, d.callback, (('user', 'badpw'),))
            return d

        checker = DBCredentialsChecker(fakeRunQueryBadPassword, 'fake query')
        d = checker.requestAvatarId(self.creds)

        def checkError(result):
            self.assertEqual('Password mismatch', result.message)
        return self.assertFailure(d, UnauthorizedLogin).addCallback(checkError)
