"""
Import ararpy
"""
version = "20260715"
import ararpy as ap                 # using Pip version

try:
    from .local_init import *       # local
except ImportError:
    pass
