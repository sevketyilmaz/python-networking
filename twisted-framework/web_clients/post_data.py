import sys

from twisted.internet import reactor
from twisted.internet.defer import Deferred, succeed
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.iweb import IBodyProducer
from zope.interface import implements


class StringProducer:
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class ResourcePrinter(Protocol):

    def __init__(self, finished):
        self.finished = finished

    def dataReceived(self, data):
        print data

    def connectionLost(self, reason):
        self.finished.callback(None)


def printResource(response):
    finished = Deferred()
    response.deliverBody(ResourcePrinter(finished))
    return finished


def printError(failure):
    print >>sys.stderr, failure


if len(sys.argv) != 3:
    printError("Usage: python post_resource.py URL 'POST DATA'")
    exit(1)

agent = Agent(reactor)
url = sys.argv[1]
data = sys.argv[2]
body = StringProducer(data)
d = agent.request('POST', url, bodyProducer=body)
d.addCallbacks(printResource, printError)
d.addBoth(lambda: reactor.stop())
reactor.run()
