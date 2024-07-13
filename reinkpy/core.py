# SPDX-License-Identifier: AGPL-3.0-or-later
__all__ = (
    'Device',
    'Driver',
    'FileDevice',
    'NetworkDevice'
)

import functools, glob, logging, pathlib

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format="{levelname: <6} {name: <16} {message}", level=logging.INFO, style="{")


class Driver:
    """Base Driver class"""

    @classmethod
    def supports(cls, device) -> bool:
        pass


class Device:

    brand: str|None = None
    model: str|None = None
    serial_number: str|None = None

    @classmethod
    def ifind(cls):
        "Yield available printer devices"
        for c in cls.__subclasses__():
            yield from c.ifind()

    @functools.cached_property
    def driver(self):
        "Best matching driver for this device"
        s = sorted(((c.supports(self), c) for c in Driver.__subclasses__()), key=lambda t: -t[0])
        if s: return s[0][1](self)

    ieee1284_device_id: str
    def _parse_device_id(self, str):
        "Parse IEEE 1284 device id string"
        return dict((k, v.split(',')) for (k,s,v) in
                    (kv.partition(':') for kv in r[9:].split(';') if kv))



class FileDevice(Device):

    @classmethod
    def ifind(cls, globs=('/dev/lp?', '/dev/usb/lp?')):
        for g in globs:
            for p in glob.iglob(g):
                p = pathlib.Path(p)
                if p.is_char_device():
                    # TODO: probe?
                    #status = read()
                    yield cls(p)

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

    def __eq__(self, o):
        return (self.__class__ is o.__class__ and self.fname == o.fname and self.mode == o.mode)

    def __str__(self):
        return '{0.__class__.__name__} [{0.fname}]'.format(self)

    # def probe(self):
    #     with self:
    #         # IEEE 1284.1 RDC Request Summary cmd
    #         # self.write(b'\xa5'       # START-PACKET
    #         #            b'\x00\x03'   # PAYLOAD-LENGTH:>H
    #         #            b'\x50'       # FLAG:component&reply
    #         #            b'\x01\x00')  # RDC RS
    #         r = self.read()
    #     return r


class NetworkDevice(Device):
    # IPP? SNMP?

    @classmethod
    def ifind(cls):
        # ping ip range / broadcast snmp msg
        PORTS = (515, 631)      # printer, ipp, snmp
        return ()

    def __init__(self, ip):
        self.ip = ip
