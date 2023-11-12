# SPDX-License-Identifier: AGPL-3.0-or-later
import argparse
import ast
import logging
import sys
import time

from . import EpsonPrinter, MODELS
from .. import usb

def int_(s):
    return int(ast.literal_eval(s))

def cli():

    c = argparse.ArgumentParser(
        prog="python -m reinkpy.epson",
        description="Probe the first USB Epson printer found",
        epilog="")
    c.add_argument('--rkey', type=int_,
                   help="""Model code needed for reading EEPROM.
                   If omitted, find it by brute force.""")
    c.add_argument('--dump-eeprom', type=int_, default=0x100,
                   help="(Upper address of) EEPROM range to dump")
    c.add_argument('--wkey', type=lambda s: bytes(s, 'ascii'),
                   help="""ASCII suffix key needed for writing.
                   If omitted, known keys are tried.""")
    c.add_argument('--try-keys-from', nargs='?', type=argparse.FileType('r'),
                   help="Try each line as wkey from file (- for stdin)")
    c.add_argument('--reset', type=lambda s:[int_(b) for b in s.split(',')],
                   help="""Comma-separated list of EEPROM addresses to reset.
                   You probably want to specify the range of waste ink pad counters.
                   If omitted, list known similar models if any.""")
    c.add_argument('--usb', action=argparse.BooleanOptionalAction, default=usb.AVAILABLE,
                   help="Use usb library")

    c.add_argument('--search-file', type=argparse.FileType('rb'),
                   help="""Instead of probing printer, search a traffic log file (like pcapng)
                   for read/write operations and (if extension is not .pcapng)
                   an "adjustment program" binary for potential keys.""")

    c.add_argument('--verbose', '-v', action='count', default=0)
    args = c.parse_args()

    if args.verbose > 1:
        print(args)
    logging.getLogger().setLevel(10 * (3 - args.verbose))


    if args.search_file is not None:
        for res in EpsonPrinter.search_bin(args.search_file.read(),
                                           yield_raw=not args.search_file.name.endswith('.pcapng')):
            print(res)
        return


    if args.usb:
        p = EpsonPrinter.from_usb()
    else:
        p = EpsonPrinter.from_file()


    with p:

        if args.rkey is not None:
            p.rkey = args.rkey
        else:
            print('Trying read keys...')
            if p.find_rkey():
                print('Now we can read!')
        print(f"Key for reading (model code): 0x{p.rkey:04X}")
        if args.dump_eeprom:
            print(f'EEPROM DUMP [0, {args.dump_eeprom}]:')
            print(', '.join(f'[0x{a:02x},0x{v:02x}]' for (a,v) in
                            p.read_eeprom(range(args.dump_eeprom)))) # 0x300


        if args.wkey is not None:
            p.wkey = args.wkey
            if p.find_wkey([args.wkey]):
                print('Now we can write!')
            else:
                print(f'Cannot write with key {args.wkey}!')
                return
        else:
            # Try known keys
            p.find_wkey([b'', *(m["wkey"] for m in MODELS.values() if 'wkey' in m)])

        if p.wkey is None and args.try_keys_from:
            print(f"Trying keys for writing, one per line from {args.try_keys_from}:")
            def ikeys():
                c = 0
                t0 = time.perf_counter()
                print('Start time', t0)
                for l in args.try_keys_from:
                    c += 1
                    if c % 1000 == 0:
                        print(l, '+%is' % int(time.perf_counter()-t0))
                    yield l
            p.find_wkey(k[:8].encode('ascii') for k in ikeys())
        print(f"Key for writing: {p.wkey}")

        if args.reset is not None:
            print(f"Resetting addresses {args.reset}...")
            p.reset(args.reset)
        else:
            print("Known models similar to this one: ",
                  [(k,v) for k,v in  MODELS.items() if
                   v.get('rkey') == p.rkey or v.get('wkey') == p.wkey])



if __name__ == '__main__':
    sys.exit(cli())
