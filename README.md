ReInkPy
=======
Waste ink counter resetter for some (EPSON) printers.

Free and open. Python code. Drawing heavily on [ReInk](https://github.com/lion-simba/reink/).


# DISCLAIMER



# CLI usage

Probing a printer:
```
python3 -m reinkpy.epson -v | tee report-with-eeprom-backup.log
```

Searching for keys:
```
python3 -m reinkpy.epson --search-file some-reset-session.pcapng
```
or
```
python3 -m reinkpy.epson --search-file some-adjprog.exe | sort -u >potential-keys
```

Trying many potential keys:
```
python3 -m reinkpy.epson --try-keys-from wordlists/wikidata-taxons.csv.alnum.words.Keys8
```

Specifying a write key once it's known:
```
python3 -m reinkpy.epson -v --wkey 'Thekey//'
```
(Then please share it!)

Resetting a waste ink pad counter with known EEPROM addresses:
```
python3 -m reinkpy.epson -v --reset [addresses]
```

To set other values, see the python API.
