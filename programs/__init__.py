"""
Import ararpy
"""
version = "20250604"
# import ararpy as ap                 # using Pip version
try:
    from .local_init import *
except ImportError:
    import ararpy_package.ararpy as ap    # local
