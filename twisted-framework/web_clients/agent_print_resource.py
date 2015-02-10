import sys

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent


class ResourcePrinter(Protocol):

    def __init__(self, finished):
        self.finished = finished

    def dataReceived(self, data):
        print data

    def connenctionLost(self, reason):
        self.finished.callback(None)


def printResource(response):
    finished = Deferred()
    response.deliverBody(ResourcePrinter(finished))
    return finished


def printError(failure):
    print >>sys.stderr, failure


if len(sys.argv) != 2:
    print >>sys.stderr, 'Usage: python agent_print_resource.py URL'
    exit(1)


agent = Agent(reactor)
url = sys.argv[1]
d = agent.request('GET', url)
d.addCallbacks(printResource, printError)
d.addBoth(lambda: reactor.stop())

reactor.run()
