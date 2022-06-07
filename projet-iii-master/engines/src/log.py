import logging

from logging.handlers import TimedRotatingFileHandler

root = logging.getLogger()

def setLogger(log_prefix, ID, release=True):

    handlers = []

    if release:
        root.setLevel(logging.INFO)
        handlers.append(TimedRotatingFileHandler(log_prefix,
                                                 when="D",
                                                 interval=1,
                                                 backupCount=60))
    else:
        root.setLevel(logging.DEBUG)

    # Useful for Docker!
    handlers.append(logging.StreamHandler())

    fmt = f"[engine-{ID}] %(levelname)-8s %(asctime)s - %(message)s"
    formatter = logging.Formatter(fmt)

    for h in handlers:
        h.setFormatter(formatter)
        root.addHandler(h)

def without_logging(func):

    """
    Disable all logging when calling `func()`
    """

    def wrapper(*args, **kwargs):
        try:
            logging.disable(logging.CRITICAL)
            return func(*args, **kwargs)
        finally:
            logging.disable(logging.NOTSET)

    return wrapper
