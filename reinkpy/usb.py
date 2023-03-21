# SPDX-License-Identifier: AGPL-3.0-or-later
__all__ = (
    'USBTransport',
    'iter_interfaces',
)

from .helpers import hexdump

import logging
_log = logging.getLogger(__name__)
del logging

try:
    import usb
    AVAILABLE = True
except ImportError as e:
    _log.warn(e)
    AVAILABLE = False


class USBTransport:

    def __init__(self, epIn, epOut, ifc, cfg, dev):
        self.epIn = epIn
        self.epOut = epOut
        self.ifc, self.cfg, self.dev = ifc, cfg, dev

    def write(self, data):
        # if len(data) > self.epOut.wMaxPacketSize: raise
        _log.debug('Writing...:\n%r', hexdump(data))
        return self.epOut.write(data)

    def read(self, size=None):
        res = self.epIn.read(size or self.epIn.wMaxPacketSize)
        _log.debug('Received %iB:\n%s', len(res), hexdump(res))
        return res

    def __str__(self):
        return 'USBTransport %s' % ((self.epIn, self.epOut),)
        # return 'USBTransport (IN:%s, OUT:%s)' % (
        #     hex(self.epIn.bEndpointAddress), hex(self.epOut.bEndpointAddress))

    def __enter__(self):
        dev, i = self.dev, self.ifc.index
        if dev.is_kernel_driver_active(i):
            dev.detach_kernel_driver(i)
            # ? .claim_interface
            self._detached_kernel_driver = i
        # _log.info('Setting configuration...')
        # try:
        #     dev.set_configuration(cfg)
        # except usb.USBError as e:
        #     _log.warning('Failed to configure device: %s, %s', dev, e)
        return self

    def __exit__(self, *exc):
        if hasattr(self, '_detached_kernel_driver'):
            try:
                self.dev.attach_kernel_driver(self._detached_kernel_driver)
                del self._detached_kernel_driver
            except usb.core.USBError as e:
                _log.error(e)
        # restore config?

    @classmethod
    def from_specs(cls, **specs):
        _log.info('Locating USB interface for %s...', specs)
        for (dev, cfg, ifc) in iter_interfaces(**specs):
            eps = get_bulk_io(ifc)
            if eps: break
        else:
            raise Exception('No USB interface found for %s' % specs)
        _log.info('Found device %s, interface %s.', dev, eps)

        # if dev.is_kernel_driver_active(ifc.index):
        #     dev.detach_kernel_driver(ifc.index)
        # try:
        #     dev.set_configuration(cfg)
        # except usb.USBError as e:
        #     _log.warning('Failed to configure device: %s, %s', specs, e)
        return cls(*eps, ifc, cfg, dev)


def iter_interfaces(bClass=0x07,  # match bDeviceClass or bInterfaceClass
                    **specs):
    devspecs = dict((k[7:], v) for (k,v) in specs.items() if k.startswith('device_'))
    ifacespecs = dict((k[6:], v) for (k,v) in specs.items() if k.startswith('iface_'))
    _log.debug('Looking for interfaces matching:\n  device specs: %s \n  interface specs: %s',
               devspecs, ifacespecs)
    m = is_bClass(bClass) if bClass is not None else None
    for dev in usb.core.find(True, custom_match=m, **devspecs):
        _log.debug(dev._str())
        for cfg in dev:
            _log.debug(cfg._str())
            for iface in usb.util.find_descriptor(cfg, True, **ifacespecs):
                _log.debug(iface._str())
                if bClass is None or (
                        dev.bDeviceClass == bClass or iface.bInterfaceClass == bClass):
                    yield (dev, cfg, iface)


def get_bulk_io(iface):
    i = usb.util.find_descriptor(iface, custom_match=lambda e: is_bulk(e) and is_in(e))
    o = usb.util.find_descriptor(iface, custom_match=lambda e: is_bulk(e) and is_out(e))
    return (i, o) if (i and o) else None

is_bulk = lambda e: usb.util.endpoint_type(e.bmAttributes) == usb.util.ENDPOINT_TYPE_BULK
is_in = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
is_out = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT

class is_bClass:
    def __init__(self, bClass):
        self.bClass = bClass
    def __call__(self, device):
        if device.bDeviceClass == self.bClass:
            return True
        for cfg in device: # if specified at interface
            if usb.util.find_descriptor(cfg, bInterfaceClass=self.bClass):
                return True
        return False
