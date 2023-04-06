# SPDX-License-Identifier: AGPL-3.0-or-later
from . import core, epson, logger

try:
    import importlib.metadata
    try:
        __version__ = importlib.metadata.version(__name__)
    except importlib.metadata.PackageNotFoundError:
        pass
    del importlib
except:
    __version__ = None
