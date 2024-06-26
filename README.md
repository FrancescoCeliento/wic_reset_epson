ReInkPy
=======
Waste ink counter resetter for some (EPSON) printers.

Free and open. Python code.


# Simple GUI usage

Download and execute the latest release as `.pyz` file.


# More advanced tasks and development

```
pip install -e git+https://codeberg.org/atufi/reinkpy#egg=reinkpy
```

Python API example:

```
from reinkpy import *

d = next(Device.ifind()).driver.configure()
assert d.specs.model # model is known
d.do_id()
d.do_reset_All_waste_counters_…() # dynamically generated methods
d.read_eeprom()
d.write_eeprom((address, value), …)
```

`python -m reinkpy.ui` launches the GUI.


# Requirements

- [python](https://python.org)
- (optional) some USB backend for [libusb](https://libusb.info)


# Warning

This is software. It won't actually replace pads.


# Similar projects

This was started as a port of [ReInk](https://github.com/lion-simba/reink/).
See also [epson_print_conf](https://github.com/Ircama/epson_print_conf).
