# SPDX-License-Identifier: AGPL-3.0-or-later
__all__ = (
    'SNMPDevice',
)

from .core import Device

from pysnmp.hlapi import *
#import struct

OID_PRINTER = '1.3.6.1.2.1.43'
OID_ENTERPRISE = "1.3.6.1.4.1"
OID_EPSON = f"{OID_ENTERPRISE}.1248"
OID_CTRL = f"{OID_EPSON}.1.2.2.44.1.1.2.1"


class SNMPDevice(Device):

    @classmethod
    def ifind(cls):
        # ping ip range / broadcast snmp msg
        raise NotImplemented

    def __init__(self, ip, port=161, version='1', user='public'): # 'admin'
        self.ip = ip
        self.port = port
        assert version in ('1', '2c', '3')
        self.version = version
        self.user = user

    def __enter__(self):
        if self.version == '1':
            auth = CommunityData(self.user, mpModel=0)
        elif self.version == '2c':
            auth = CommunityData(self.user, mpModel=1)
        else:
            auth = UsmUserData(self.user)
        self._engine = SnmpEngine()
        self._iget = getCmd(
            self._engine,
            auth,
            UdpTransportTarget((self.ip, self.port)),
            ContextData(),
            ('system', None))
        if next(self._iget, None):
            return self
        else:
            logger.warn('Initializing SNMP failed')

    def __exit__(self, *exc):
        self._engine.unregisterTransportDispatcher()
        del self._iget

    def _get(self, oid):
        errIndication, errStatus, errIndex, varBinds = self._iget.send((oid, None))
        if errIndication:
            logger.warn(errIndication)
        elif errStatus:
            logger.warn('%s at %s' % (errStatus.prettyPrint(),
                                      varBinds[int(errIndex) - 1][0] if errIndex else '?'))
        else:
            return varBinds
            # for varBind in varBinds:
            #     print(' = '.join([x.prettyPrint() for x in varBind]))

    def ctrl(self, payload: bytes):
        # return '.'.join(OID_CTRL, *struct.unpack('B'*len(payload), payload))
        mib = '.'.join((OID_CTRL, *(str(int.from_bytes(b)) for b in payload)))
        return self._get(mib)
