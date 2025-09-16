ReInkPy
=======
Waste ink counter resetter for some (EPSON) printers.

Free and open. [Python](https://python.org) code.


# Getting started

```
pip install -e git+https://codeberg.org/atufi/reinkpy#egg=reinkpy[ui,usb,net]
```

`python -m reinkpy.ui` launches a GUI.

For debugging: `LOGLEVEL=DEBUG python -m reinkpy.ui`, then look at the log file
mentioned on the CLI.

Python API examples:

```
import reinkpy

for p in reinkpy.Device.find():
	print(p)
    print(p.info)

# Or get a specific device
p = reinkpy.Device.from_file('/dev/usb/lp0')
p = reinkpy.Device.from_usb(manufacturer='EPSON')
p = reinkpy.Device.from_ip('192.168.0.255')

e = p.epson # Epson driver
if not e.spec.model: # Either model is unknown or autoconfiguration failed
    # Some printers just don't advertise their model name cleanly, e.g.
	e.configure("XP-352")

print(e.read_eeprom())
# e.reset_waste()
# e.write_eeprom((address, value), …)
```

CLI one-liners:

`python -c 'import reinkpy;print(reinkpy.Device.from_usb().epson.read_eeprom(*range(256)))'`

`python -c 'import reinkpy;reinkpy.Device.from_ip("1.2.3.4").epson.reset_waste()'`


# Windows
There are a couple of steps to do to get things working on windows.
## Prerequisites
1. `libusb-1.0.dll` from [https://libusb.info/](https://libusb.info/).
2. [Zadig](https://zadig.akeo.ie/) to install a `libusb` compatible driver to your device.

## Steps
### Installing `libusb-1.0.dll`
1. Download the `libusb-1.0.dll` from [https://libusb.info/](https://libusb.info/). Go to Downloads > Latest Windows Binaries. This will download a zip file.
2. Open the zip and find the `libusb-1.0.dll`. It should be somewhere in `VS2022\MS64\dll`.
3. Copy the `libusb-1.0.dll` to your python install folder (Usually in `C:\Python3x`).

### Install `libusb` Compatible Driver
1. Open Zadig.
2. Select your device.
    > [!NOTE]
    > If you do not see your device, you might need to go to Options > List All Devices.
    >
    > You might see duplicates of your device especially if your devices have multiple functions (e.i. scanning, printing, etc.). For my ET-2800, I had to choose EPSON Utility.
3. Select the driver. `libusbK (v3.1.0.0)` worked for me, but you can always try other driver if it doesn't work.
4. Click Install Driver or Replace Driver.

## Windows Troubleshoot
### Invalid response reading addr ...
If you are getting an `Invalid response reading addr` error, it means you've selected a device over the network. The solution is to turn off the device Wifi network for now and connect the device to your computer via USB.

### NotImplementedError: Operation not supported or unimplemented on this platform
If you are getting the `NotImplementedError: Operation not supported or unimplemented on this platform` error, it means `libusb` couldn't find a device that has a `libusb` compatible driver. Use Zadig to install the driver to your device. You can always try the other driver available in Zadig.

# Warning

This is software. It won't actually replace pads.


# Similar projects

This was started as a port of [ReInk](https://github.com/lion-simba/reink/).
See also [epson_print_conf](https://github.com/Ircama/epson_print_conf).
