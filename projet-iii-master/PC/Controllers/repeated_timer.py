"""
This class repeats function every n interval of seconds.
"""
import time
from threading import Event, Thread

class RepeatedTimer:
    def __init__(self, interval, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.start = time.time()
        self.event = Event()
        self.thread = Thread(target=self.target)
        self.thread.start()

    def target(self):
        """Call function every n seconds."""
        while not self.event.wait(self.time):
            self.function(*self.args, **self.kwargs)

    @property
    def time(self):
        """Calculate time passed between executions of function."""
        return self.interval - ((time.time() - self.start) % self.interval)

    def stop(self):
        """Stop execution of function every n seconds."""
        self.event.set()
        self.thread.join()
