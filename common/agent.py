
class Agent:
    def __init__(self, output, log_fd):
        self._output = output
        self._log_fd = log_fd

    def flush_log(self):
        self._log_fd.flush()

    def write_info_log(self, msg):
        self._log_fd.info_log(msg)

    def write_error_log(self, msg):
        self._log_fd.error_log(msg)

