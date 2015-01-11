from twisted.internet.defer import Deferred


def callback(result):
    print result


d = Deferred()
d.addCallback(callback)
d.callback('something')
