"""
Import ararpy
"""
import pathlib
from django.conf import settings
import ararpy as ap                 # using Pip version

try:
    from .local_init import *       # local
except ImportError:
    pass

version_file = pathlib.Path(settings.BASE_DIR) / "VERSION"
try:
    version = version_file.read_text(encoding="ascii").strip()
except (OSError, UnicodeError):
    version = "0.0.0-dev"

