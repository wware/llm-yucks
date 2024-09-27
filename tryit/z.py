import logging
from x import *

logger = logging.getLogger()
# logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)
logger.info("hello")


def configure_logging():
    # Check if the DEBUG environment variable is set and has a truthy value
    if boolean_env_var('DEBUG'):
        logger.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
    else:
        # If not, keep the logger at its default INFO level
        pass


configure_logging()
logger.info("This is an info message")
logger.debug("This is a debug message that will only be logged if DEBUG environment variable is set")
