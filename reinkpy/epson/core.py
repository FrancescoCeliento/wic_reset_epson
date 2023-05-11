# SPDX-License-Identifier: AGPL-3.0-or-later
from .. import core, d4

import re as _re
import struct as _struct


class EpsonPrinter(core.Printer):

    # EJL "Epson Job Language"
    CMD_ENTER_D4 = b'\x00\x00\x00\x1b\x01@EJL 1284.4\n@EJL\n@EJL\n' # "Exit packet mode"
    CMD_ENTER_D4_REPLY = b'\x00\x00\x00\x08\x01\x00\xc5\x00'

    # ctrl channel
    CMD_ID = 'di'               # get printer ID
    CMD_STATE = 'st'            #
    CMD_FIRMWARE = 'fl'         # before loading firmware, in recovery mode
    # Misc 2-letter commands / answers observed on an XP-830:
    # [0] cd:01:NA;
    # cx:00; ex:NA; ht:0000;
    # ia: @BDC PS\r\nIA:01;NAVL,NAVL,NAVL,NAVL,NAVL;
    # ii:NA; pc:\x01:NA; pm:@BDC... rj:NA;
    # [1] rs:01:OK; reset?
    # rw: @BDC PS rw:NA;
    # ti:NA; vi:01:NA;

    # "factory commands" (cls, cmd)
    CMD_EEPROM_READ = (0x7c, 0x41)  # (|,A)
    CMD_EEPROM_WRITE = (0x7c, 0x42) # (|,B)

    # USB-IF
    iManufacturer = "EPSON"
    idVendor = 0x04b8
    idProduct: int

    # 2-bytes model code, needed to read from EEPROM
    rkey: int = 0
    # 8-bytes, needed to write to EEPROM
    wkey: bytes = None
    # addresses of waste ink pads
    addr_waste: list[int] = ()

    def __init__(self, tsp, **kw):
        super().__init__(tsp, **kw)
        self.d4_link = d4.D4Link(self.tsp)

    def __enter__(self):
        super().__enter__()
        self._enter_d4()
        self.ctrl = self.d4_link.get_channel('EPSON-CTRL') # (0x02, 0x02)
        self.ctrl.protocol = self                          # encode/decode methods
        self._exit_stack.enter_context(self.ctrl)
        # self.data = self.d4_link.get_channel('EPSON-DATA') # (0x40, 0x40)
        # self.data.protocol = self
        # self._exit_stack.enter_context(self.data)
        return self

    def _enter_d4(self):
        self._log.info('Entering IEEE 1284.4 mode...')
        assert self.tsp.write(self.CMD_ENTER_D4)
        r = b''
        for i in range(5):
            r += self.tsp.read()
            if self.CMD_ENTER_D4_REPLY in r:
                break
        else:
            self._log.debug(r.hex())
            self._log.warning('Entering IEEE 1284.4 mode: no answer from device')
        self._exit_stack.enter_context(self.d4_link)


    def encode(self, cmd, payload=b''):
        payload = bytes(payload)
        if isinstance(cmd, bytes):
            return cmd
        elif isinstance(cmd, str) and len(cmd) == 2:
            return cmd.encode('ascii') + _struct.pack('<H', len(payload)) + payload
        elif cmd == 'read':
            cls_, cmd = self.CMD_EEPROM_READ
        elif cmd == 'write':
            cls_, cmd = self.CMD_EEPROM_WRITE
        h = _struct.pack('<BBHHBBB', cls_, cls_, len(payload) + 5, self.rkey,
                         cmd, ~cmd & 0xff, (cmd>>1 & 0x7f) | (cmd<<7 & 0x80))
        return h + payload

    # addresses are little endian; field values big endian (here 1-byte)
    @classmethod
    def decode(cls, b):
        # a = b.decode('ascii')
        # _re.match('@BDC', a)
        return b

    def read_eeprom(self, pos):
        if type(pos) is not int:
            return [self.read_eeprom(p) for p in pos]
        r = self.ctrl('read', _struct.pack('<H', pos))
        v = _re.match('.*?\sEE:([0-9a-fA-F]{6,6});', r.decode('ascii')) # '@BDC PS EE:ED0100;'
        if v:
            p, val = _struct.unpack('>HB', bytes.fromhex(v.group(1))) # big endian
            assert p == pos
            return (pos, val)

    def write_eeprom(self, pos, val, key=None, check_read=True):
        """Write to EEPROM

        key -- secret 54-bit / 8 ASCII chars suffix key as found on XP Series
        check_read -- read `pos` again to check that value was written
        Returns -- True on success
        """
        if key is None:
            key = self.wkey
        payload = _struct.pack('<HB', pos, val) + (key or b'')
        r = self.ctrl('write', payload)
        if r == b'||:42:OK;\x0c': #r.contains(':OK;')
            if check_read:
                return self.read_eeprom(pos) == (pos, val)
            return True

    def reset(self, addr, val=0x0):
        "Set addr range in EEPROM to val"
        r = True
        for pos in addr:
            self._log.info('Current value at %02X: %02X', *self.read_eeprom(pos))
            if not self.write_eeprom(pos, val):
                self._log.warning('Failed writing to %02x', pos)
                r = False
        return r

    def reset_waste(self):
        "Reset the waste ink counter"
        return self.reset(self.addr_waste) # + self.byte_confirm

    # ('Ink Information', b'\x0f\x13\x03(BBB)*', 'inkCartridgeName inkColor inkRemainCounter')

    def find_rkey(self, ikeys=range(0x0,0xffff)):
        "Find and set the 2-bytes read key / model code (brute force)"
        orig = self.rkey
        for c in ikeys:
            self._log.debug('Trying model code %04X', c)
            self.rkey = c
            if self.read_eeprom(0x00) is not None:
                self._log.info('Found model code: %04X', c)
                return c
        else:
            self.rkey = orig

    def find_wkey(self, ikeys=(b'',), addr=0x00):
        "Try each key in ikeys iterable to write to addr"
        val = self.read_eeprom(addr)[1]
        newval = val + 1
        # if ikeys is None:
        #     ikeys = [b'', *(m.wkey for m in MODELS)]
        for k in ikeys:
            self._log.info('Trying key %s', k)
            if self.write_eeprom(addr, newval, key=k, check_read=True):
                self._log.warn('>>>    !!! FOUND KEY !!!   %r   <<<', k)
                print(k)
                self.write_eeprom(addr, val, key=k)
                self.wkey = k
                return k


    @classmethod
    def decode_traffic(cls, packets):
        """Prints (some) decoded information from traffic dump.

        packets -- iterable of `bytes`"""
        for header, payload in d4.decode(packets):
            print('    Channel %s: %s' % (header.cid, cls.decode(payload)))


    @classmethod
    def search_bin(cls, bstr=b'', yield_raw=True):
        """Yields read/write operations found in bytes"""
        pat = b'\|\|(?P<length>..)(?P<rkey>..)(?P<cmd>A\xbe\xa0|B\xbd!)'
        for m in _re.finditer(pat, bstr):
            try:
                end = m.span()[1]
                payload = bstr[end:end + _struct.unpack('<H', m.group('length'))[0] - 5]
                rkey = _struct.unpack('<H', m.group('rkey'))[0]
                if m.group('cmd')[0] == 0x41:
                    addr = _struct.unpack('<H', payload[:2])[0]
                    yield f'rkey:{rkey:04x} READ addr:{addr:04x}'
                else:
                    a,v = _struct.unpack('<HB', payload[:3])
                    yield f'rkey:{rkey:04x} WRITE addr:{a:04x} val:{v:02x} wkey:{payload[3:]}'
            except Exception as e:
                print(e)
                yield 'INVALID %r' % m.group()
        if yield_raw: # any 8-chars strings
            for m in _re.finditer(b'([\x20-\x7E]{8})', bstr):
                yield m.group().decode('ascii')
