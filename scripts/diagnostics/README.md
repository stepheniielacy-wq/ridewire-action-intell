# RideWire Real Data Pipeline (v1)

This folder is a deliberately small, honest counterpart to the aspirational
"17 Canonical Node" architecture described in other RideWire notebooks. Every
number and fact produced here is either:

1. Looked up from a real, cited, public dataset, or
2. Fetched live from a real, public, free API, with no API key required.

Nothing here invents telemetry, satellites, payment transactions, or
confidence scores. Where a capability isn't real yet (e.g. oil/gas data),
the code says so explicitly instead of faking a number.

## Modules

### `diagnose.py` - Vehicle Diagnostic Trouble Code lookup
- Looks up a real OBD-II code (e.g. `P0300`) against a verified 469-code
  reference table.
- Source: [todrobbins/dtcdb](https://github.com/todrobbins/dtcdb) (MIT
  license), spot-checked against [AutoZone's published OBD-II code
  list](https://www.autozone.com/diy/diagnostic-trouble-codes/obd-2-code-list).
  Two isolated duplicate-row errors in the upstream file were found and
  manually corrected (codes P0110 and P0577).
- Severity is a transparent keyword-based rule (documented in the file),
  not a machine-learning confidence score.
- Usage: `python3 diagnose.py P0300 --json`

### `natural_resources.py` - Live public natural resource data
- Pulls real-time data from two free, keyless, public U.S. government feeds:
  - [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson) (global, updates continuously)
  - [USGS National Water Information System](https://waterservices.usgs.gov/nwis/iv/) - live streamflow/gage height for the Rio Grande at Albuquerque, NM (site 08330000)
- Oil/gas data is explicitly marked as not implemented - it would require a
  free [EIA API key](https://www.eia.gov/opendata/register.php) that hasn't
  been provided yet. No placeholder numbers are shown in its place.
- Usage: `python3 natural_resources.py --json`

## Live proof (first real run, Sept 5 2026)

- Real Google Sheet: https://docs.google.com/spreadsheets/d/1FD9VgikN6CcNFSu2J2z_ije2wiacpUKFG5cJMANzras/edit
  - `Diagnostics` tab: real P0300 lookup logged with timestamp
  - `Natural Resources` tab: real live earthquake + Rio Grande water readings logged with timestamps
- A real confirmation email was sent to the account owner via Gmail with the
  diagnostic result and a link to the sheet.

## What this is NOT (yet)

- Not connected to any real vehicle, sensor, or satellite - `diagnose.py`
  takes a code as input; it doesn't read a live OBD-II port.
- Not a payment system - no Stripe/PayPal/Novo Bank integration exists here.
- Not an Earth-mapping or treasure-finding tool - it reads two real public
  monitoring feeds, nothing more.
- Diagrams module - not yet built; scope to be defined (see project notes).

## Next real steps (not yet done)
- Wire a real OBD-II Bluetooth/USB adapter as an input source (real hardware
  read instead of manual code entry).
- Register a free EIA API key to add real oil/gas production data.
- Define what "diagrams" tab should contain (real wiring reference diagrams
  vs. AI-generated illustrative diagrams) before building it.
