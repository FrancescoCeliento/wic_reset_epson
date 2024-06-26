# SPDX-License-Identifier: AGPL-3.0-or-later
from .core import *
from .usb import *
from .epson import *

try:
    import importlib.metadata
    try:
        __version__ = importlib.metadata.version(__name__)
    except importlib.metadata.PackageNotFoundError:
        __version__ = None
    del importlib
except ImportError:
    __version__ = None


PREFACE = """Dear User,

ReInkPy is user-made, collaborative, free software.
It is offered to you with the sub-legal request that you will fight against
e-waste and planned obsolescence beyond fixing your own printer. Please

  + Report on how it works for specific devices;
  + Help others fix theirs;
  + Support #FreeSoftware and the #RightToRepair — vote, lobby, join, donate.

"""
