# SPDX-License-Identifier: AGPL-3.0-or-later
import logging

FORMAT = "{levelname: <6} {name: <16} {message}"

logging.basicConfig(format=FORMAT, level=logging.INFO, style="{")
