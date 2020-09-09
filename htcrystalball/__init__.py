"""HTCrystalBall - A crystal ball that lets you peek into the future."""

from ._version import __version__
import logging
from os.path import expanduser, join as opj

SLOTS_CONFIGURATION = opj(expanduser('~'), '.htcrystalball')

# External (root level) logging level
logging.basicConfig(level=logging.ERROR)

# Internal logging level
logger = logging.getLogger('crystal_balls')
logger.setLevel(level=logging.DEBUG)

__all__ = [
    '__version__',
    'SLOTS_CONFIGURATION',
    'logger'
]
