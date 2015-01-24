import sys

from twisted.python import log


log.startLogging(sys.stdout)
log.msg('Starting')

log.msg('Logging exception')

try:
    1 / 0
except ZeroDivisionError, e:
    log.err(e)

log.msg('End')
