import sys

from twisted.python import log
from twisted.python.log import FileLogObserver


RESET_COLOR = '\033[0m'
RED_COLOR = '\033[91m'


class ColourfulLogObserver(FileLogObserver):

    def emit(self, eventDict):
        self.write(RESET_COLOR)

        if eventDict['isError']:
            self.write(RED_COLOR)
        FileLogObserver.emit(self, eventDict)


def logger():
    return ColourfulLogObserver(sys.stdout).emit


observer = ColourfulLogObserver(sys.stdout)
log.addObserver(observer.emit)
log.msg('Start')
log.msg('Log exception')

try:
    1 / 0
except ZeroDivisionError, e:
    log.err(e)


log.msg('End')
