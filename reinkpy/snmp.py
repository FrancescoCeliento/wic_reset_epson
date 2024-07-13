# SPDX-License-Identifier: AGPL-3.0-or-later
__all__ = (
    'SNMPLink',
)

# from .core import NetworkDevice

import contextlib
from pysnmp.hlapi import *
import logging
_log = logging.getLogger(__name__)
del logging


class SNMPLink(contextlib.nullcontext):

    OID_PRINTER = '1.3.6.1.2.1.43'
    OID_ENTERPRISE = '1.3.6.1.4.1'

    def __init__(self, target: 'NetworkDevice', port=161, version='1', user='public'): # 'admin'
        self.target = target
        self.port = port
        assert version in ('1', '2c', '3')
        self.version = version
        self.user = user
        # self._nctx = 0

    def _do_get(self, oid):
        if self.version == '1':
            auth = CommunityData(self.user, mpModel=0)
        elif self.version == '2c':
            auth = CommunityData(self.user, mpModel=1)
        else:
            auth = UsmUserData(self.user)
        engine = SnmpEngine()
        return getCmd(
            engine,
            auth,
            UdpTransportTarget((self.target.ip, self.port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid), None),
            lookupMib=True
        )
    # def _init(self):
    #     if not self._iget:
    #         _log.warn('Initializing SNMP failed')
    #         ObjectType(ObjectIdentity('SNMPv2-MIB', 'system'))# ('system', None)

    # def __enter__(self):
    #     if self._nctx == 0:
    #         if self.version == '1':
    #             auth = CommunityData(self.user, mpModel=0)
    #         elif self.version == '2c':
    #             auth = CommunityData(self.user, mpModel=1)
    #         else:
    #             auth = UsmUserData(self.user)
    #         self._engine = SnmpEngine()
    #         self._iget = getCmd(
    #             self._engine,
    #             auth,
    #             UdpTransportTarget((self.target.ip, self.port)),
    #             ContextData(),
    #             ObjectType(ObjectIdentity('SNMPv2-MIB', 'system'))# ('system', None)
    #         )
    #         if not self._iget:
    #             _log.warn('Initializing SNMP failed')
    #     self._nctx += 1
    #     return self

    # def __exit__(self, *exc):
    #     self._nctx -= 1
    #     if self._nctx == 0:
    #         self._engine.unregisterTransportDispatcher()
    #         del self._iget

    def get(self, oid):
        eInd, eStat, eIdx, varBinds = self._do_get(oid) #_iget.send((oid, None))
        if eInd:
            _log.warn(eInd)
        elif eStat:
            _log.warn('%s at %s', eStat.prettyPrint(), varBinds[int(eIdx) - 1][0] if eIdx else '?')
        else:
            _log.info('\n'.join((v.prettyPrint() for v in varBinds)))
            return varBinds

    def get_channel(self, prefix):
        return Channel(self, prefix)


class Channel(contextlib.nullcontext):

    def __init__(self, link, prefix):
        super().__init__(self)
        self.link = link
        self.prefix = prefix

    # def __enter__(self):
    #     self.link.__enter__()
    #     return self
    # def __exit__(self, *exc):
    #     self.link.__exit__(*exc)

    def __call__(self, payload: bytes):
        # *struct.unpack('B'*len(payload), payload)
        mib = '.'.join((self.prefix, *(str(b) for b in payload)))
        return self.link.get(mib)
