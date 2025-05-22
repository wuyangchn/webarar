"""
Import ararpy
"""
version = "202504011"
# import ararpy as ap                 # using Pip version
try:
    from .local_init import *
except ImportError:
    import ararpy_package.ararpy as ap    # local
