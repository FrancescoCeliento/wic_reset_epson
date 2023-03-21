# SPDX-License-Identifier: AGPL-3.0-or-later
__all__ = ('Printer', 'FileTransport')

from contextlib import ExitStack as _ExitStack
import logging as _logging


class Printer:

    def __init__(self, tsp, **kw):
        self.tsp = tsp # transport, a binary-file-like object
        self._log = _logging.getLogger('{0.__module__}.{0.__class__.__name__}'.format(self))

    def __str__(self):
        return '{0.__class__.__name__!s}({0.tsp!s})'.format(self)

    def __enter__(self):
        self._log.info('vvv__enter__vvv')
        self._exit_stack = _ExitStack()
        self._exit_stack.enter_context(self.tsp)
        return self

    def __exit__(self, *exc):
        self._exit_stack.close()
        self._log.info('^^^__exit__^^^')

    @classmethod
    def from_file(cls, device_file='/dev/usb/lp0'):
        return cls(FileTransport(device_file))

    bClass = 0x07
    @classmethod
    def from_usb(cls, **kw):
        from .usb import USBTransport
        KEYS = ('bClass', 'iManufacturer', 'idVendor', 'iProduct', 'iSerialNumber',
                'bInterfaceNumber', 'bAlternateSetting')
        return cls(USBTransport.from_specs(**kw,
                                           **dict((k, getattr(cls, k)) for k in KEYS
                                                  if hasattr(cls, k) and k not in kw)))

    def make_report(self): raise NotImplemented
    def read_eeprom(self, pos): raise NotImplemented
    def write_eeprom(self, pos, val): raise NotImplemented
    def reset_ink(self): raise NotImplemented
    def reset_waste(self): raise NotImplemented


class FileTransport:

    def __init__(self, fname, mode='a+b'):
        self.fname = fname
        self.mode = mode
        self._nctx = 0

    def __enter__(self):
        if self._nctx == 0:
            self._f = open(self.fname, self.mode)
        self._nctx += 1
        assert not self._f.closed
        return self

    def __exit__(self, *exc):
        self._nctx -= 1
        if self._nctx == 0:
            self._f.close()

    def write(self, data):
        return self._f.write(data)

    def read(self, size=None):
        return self._f.read(size)

    def __str__(self):
        return '{0.__class__.__name__!s}({0.fname!r})'.format(self)
