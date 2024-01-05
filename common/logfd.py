import threading

class LogFD:
    def __init__(self, bname):
        self._error_fd = open("agent.error-log." + bname, 'a')
        self._info_fd = open("agent.info-log." + bname, 'a')
        self._tlock = threading.Lock()

    def __del__(self):
        if self._error_fd: self._error_fd.close()
        if self._info_fd: self._info_fd.close()

    def close(self):
        if self._error_fd: self._error_fd.close()
        if self._info_fd: self._info_fd.close()

    def flush(self):
        if self._error_fd: self._error_fd.flush()
        if self._info_fd: self._info_fd.flush()

    def error_log(self, msg):
        self._tlock.acquire()
        self._error_fd.write(msg+'\n')
        self._tlock.release()

    def info_log(self, msg):
        self._tlock.acquire()
        self._info_fd.write(msg+'\n')
        self._tlock.release()

