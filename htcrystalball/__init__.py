from ._version import __version__
import logging

SLOTS_CONFIGURATION = "config/slots.json"

# External (root level) logging level
logging.basicConfig(level=logging.ERROR)

# Internal logging level
logger = logging.getLogger('crystal_balls')
logger.setLevel(level=logging.DEBUG)