import os
import sys

from loguru import logger

from util import constants

LOG_LEVEL = os.environ.get("LOG_LEVEL").strip()
logger.add(sys.stderr, format="{level} - {name} - {message}", level=LOG_LEVEL)

if constants.EXTRA_LOGGING is True:
    pass


def get_logger():
    return logger
