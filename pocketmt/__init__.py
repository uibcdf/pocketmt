"""
PocketMT
Short description
"""

# versioningit
from ._version import __version__

def __print_version__():
    print("PocketMT version " + __version__)

from . import config
config.setup_logging(level="WARNING", capture_warnings=True, simplify_warning_format=True)

from ._pyunitwizard import pyunitwizard

from .Topography import Topography
from .Pocket import Pocket
from .Mouth import Mouth
from . import alpha_spheres

from .get_alpha_spheres import get_alpha_spheres
from .get_pockets import get_pockets, show_pockets

from . import io

__all__ = []

