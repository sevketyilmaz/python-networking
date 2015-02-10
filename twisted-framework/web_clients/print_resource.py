import sys

from twisted.internet import reactor
from twisted.web.client import getPage


def printPage(page):
    print page


def printError(failure):
    print >>sys.stderr, failure


def stop(result):
    reactor.stop()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        printError('Usage python print_resource.py <URL>')
        sys.exit(1)

    url = sys.argv[1]
    d = getPage(url, method='POST')
    d.addCallbacks(printPage, printError)
    d.addBoth(stop)

    reactor.run()
