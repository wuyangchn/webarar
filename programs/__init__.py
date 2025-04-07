"""
Import ararpy
"""
version = "2025/04/07"
try:
    from .local_init import *
    # import ararpy as ap                 # using Pip version
except ImportError:
    import ararpy_package.ararpy as ap    # local
