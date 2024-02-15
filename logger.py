import logging
from logging.handlers import RotatingFileHandler


def setup_logger(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Create a rotating file handler
    handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=1)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
