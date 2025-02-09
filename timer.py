import time

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    __slots__ = ['_start_time']
    def __init__(self):
        self._start_time = None

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()
    def get_lapsed(self):
        if self._start_time is not None:
            elapsed_time = (time.perf_counter() - self._start_time) *1000
        else:
            elapsed_time = -1
        return elapsed_time
    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
    def reset(self):
        """Reset the timer"""
        self.stop()
        self.start()