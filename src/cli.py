import os
import sys
from subprocess import Popen

try:
    import click
except ImportError:
    sys.exit(1)

from src.main import dotenv_values, get_key, set_key, unset_key, to_env
from src.version import __VERSION__ as __version__