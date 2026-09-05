#!/usr/bin/env python3
"""
RideWire Natural Resource Monitor (real version)
--------------------------------------------------
Pulls REAL, live, free, no-API-key-required public government data feeds.
No simulated telemetry, no invented satellites, no placeholder GeoDataFrames.

Sources used (both confirmed live and working as of this build):
  1. USGS Earthquake Hazards Program feed (global, updates continuously)
     https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson
  2. USGS National Water Information System - Instantaneous Values service
     for a real New Mexico gauge: Rio Grande at Albuquerque, NM (site 08330000)
     https://waterservices.usgs.gov/nwis/iv/

Known limits (stated honestly, not hidden):
  - Oil/gas production data (e.g. EIA) requires a free API key signup at
    https://www.eia.gov/opendata/register.php - not wired up yet because no
    key has been provided. This script does NOT fabricate oil/gas numbers
    in the meantime.
  - This is real-time public monitoring data, not a proprietary "Earth
    mapping" or predictive model. It is exactly what it looks like: a live
    read of public USGS feeds.

Usage:
    python3 natural_resources.py --json
"""
import json
import argparse
import datetime
import urllib.request

EARTHQUAKE_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
WATER_URL = "https://waterservices.usgs.gov/nwis/iv/?format=json&sites=08330000&parameterCd=00060,00065&siteStatus=all"


def fetch_json(url, timeout=15):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def get_earthquake_summary():
    try:
        data = fetch_json(EARTHQUAKE_URL)
        count = data["metadata"]["count"]
        top = sorted(data["features"], key=lambda f: f["properties"]["mag"] or 0, reverse=True)[:3]
        events = [
            {
                "place": f["properties"]["place"],
                "magnitude": f["properties"]["mag"],
                "time_utc": datetime.datetime.fromtimestamp(f["properties"]["time"] / 1000, tz=datetime.timezone.utc).isoformat(),
            }
            for f in top
        ]
        return {"ok": True, "count_last_2_5_days": count, "top_events": events, "source": EARTHQUAKE_URL}
    except Exception as e:
        return {"ok": False, "error": str(e), "source": EARTHQUAKE_URL}


def get_rio_grande_water():
    try:
        data = fetch_json(WATER_URL)
        series = data["value"]["timeSeries"]
        readings = []
        for t in series:
            site = t["sourceInfo"]["siteName"]
            var = t["variable"]["variableName"]
            vals = t["values"][0]["value"]
            if vals:
                latest = vals[-1]
                readings.append({
                    "site": site,
                    "variable": var,
                    "value": latest["value"],
                    "measured_at": latest["dateTime"],
                })
        return {"ok": True, "readings": readings, "source": WATER_URL}
    except Exception as e:
        return {"ok": False, "error": str(e), "source": WATER_URL}


def build_report():
    return {
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "earthquake_activity": get_earthquake_summary(),
        "rio_grande_albuquerque": get_rio_grande_water(),
        "oil_gas_data": {
            "ok": False,
            "note": "Not implemented - requires a free EIA API key (https://www.eia.gov/opendata/register.php). No fabricated data shown.",
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(json.dumps(report, indent=2))
