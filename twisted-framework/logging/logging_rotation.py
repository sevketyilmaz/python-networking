from twisted.python import log, logfile


f = logfile .LogFile('test.log', '/tmp', rotateLength=100)
log.startLogging(f)

log.msg('First!')
f.rotate()


for i in range(5):
    log.msg('Message', i)


log.msg('Last!')
