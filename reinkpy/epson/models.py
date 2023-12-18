# SPDX-License-Identifier: AGPL-3.0-or-later
"""Known Epson models"""

# TODO: this should probably be keyed by wkey/rkey rather than by advertised model name
MODELS = {

    "ET-2720": dict(
        rkey = 0x0797,
        wkey = b'Nbsjcbzb', # Maribaya
        addr_waste = range(0x2f,0x38), # + (0x1c,)
        # range(0x0120, 0x012a), range(0x0727,0x072c), range(0x07f4,0x07fe),
        # range(0x02f,0x034), range(0x0644,0x064e)
    ),

    "L355": dict(
        rkey = 0x0941,
    ),

    "L4160": dict(
        rkey = 0x0849,
        wkey = b'Bsboujgp', # Arantifo
    ),

    "SX400": dict(
        rkey = 0x0649,
    ),

    "XP-205": dict(
        rkey = 0x0719,
        wkey = b'Xblbupcj',
        addr_waste = range(0x18,0x1b),
    ),

    "XP-315": dict(
        rkey = 0x0881,
        wkey = b'Xblbupcj', # Wakatobi
    ),

    "XP-422": dict(
        rkey = 0x0555,
        wkey = b'Nvtdbsj/', # Muscari.
    ),

    "XP-435": dict(
        rkey = 0x0585,
        wkey = b'Qpmzyfob', # Polyxena
    ),

    "XP-510": dict(
        rkey = 0x0479,
        wkey = b'Hpttzqjv', # Gossypiu
    ),

    "XP-530": dict(
        rkey = 0x0928,
        wkey = b'Jsjthbsn', # Irisgarm
    ),

    "XP-540": dict(
         rkey = 0x0414,
         wkey = b'Gjsnjbob', # Firmiana
         addr_waste = range(0x10,0x16),
     ),

    "XP-610": dict(
        rkey = 0x0479,
        wkey = b'Hpttzqjv', # Gossypiu
    ),

    "XP-620": dict(
        rkey = 0x0539,
        wkey = b'Bmuibfb/' # Althaea.
    ),

    "XP-630": dict(
        rkey = 0x0928,
        wkey = b'Jsjthbsn', # Irisgarm
    ),

    "XP-700": dict(
        rkey = 0x0028,
    ),

    "XP-760": dict(
        rkey = 0x0557,
    ),

    "XP-830": dict(
        rkey = 0x0928,
        wkey = b'Jsjthbsn', # Irisgarm (Iris graminea with typo?)
        addr_waste = (
            0x10, 0x11, # '>H' "main pad counter" Max: 0x2102 (8450)
            0x06,
            0x14, 0x15,
            0x12, 0x13, # '>H' "platen pad counter" Max: 0x0d2a (3370)
            0x06
        ),# or 0x08?
        idProduct = 0x110b,
    ),

    "XP-850": dict(
        rkey = 0x0028,
        wkey = b'Ijcjtdvt', # Hibiscus
    ),

    "XP-2150": dict(
        rkey = 0x0950,
        wkey = b'Cjebebsj', # Bidadari
        addr_waste = range(0x0150,0x0159), # and 0x1c
    ),

    "XP-7100": dict(
        rkey = 0x0528,
        wkey = b'Mfvdpkvn', # Leucojum
        addr_waste = range(0x10,0x16),
    ),

}
