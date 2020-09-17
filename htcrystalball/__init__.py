"""HTCrystalBall - A crystal ball that lets you peek into the future."""

import logging

from os.path import expanduser, join as opj

from htcrystalball._version import __version__

SLOTS_CONFIGURATION = opj(expanduser('~'), '.htcrystalball')

# External (root level) logging level
logging.basicConfig(level=logging.ERROR)

# Internal logging level
LOGGER = logging.getLogger('crystal_balls')
LOGGER.setLevel(level=logging.DEBUG)

__all__ = [
    '__version__',
    'SLOTS_CONFIGURATION',
    'LOGGER'
]
