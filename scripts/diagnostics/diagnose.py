#!/usr/bin/env python3
"""
RideWire Diagnostic Engine (real version)
------------------------------------------
Looks up a real vehicle OBD-II Diagnostic Trouble Code (DTC) against the
standard, publicly documented SAE J2012 generic code list and produces a
plain-English diagnostic report.

This module does NOT invent numbers, confidence scores, or telemetry.
Everything it reports is either:
  1. Looked up directly from the real code database (dtc_codes.csv,
     sourced from https://github.com/todrobbins/dtcdb, MIT licensed, and
     spot-checked against AutoZone's published OBD-II code list; two
     isolated duplicate-row errors in the upstream file were manually
     corrected for codes P0110 and P0577), or
  2. A transparent, rule-based severity label derived from keywords in
     that real description (documented below, not a black box).

Usage:
    python3 diagnose.py P0300
    python3 diagnose.py P0300 --json
"""
import csv
import json
import sys
import argparse
import datetime
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "dtc_codes.csv")

# Transparent, keyword-based severity heuristic.
# This is NOT a machine-learning confidence score - it's a simple, documented
# rule so nobody can mistake it for a fabricated statistic.
HIGH_SEVERITY_KEYWORDS = ["misfire", "overheat", "knock", "loss of power",
                          "stall", "fuel injector", "airbag", "brake"]
MEDIUM_SEVERITY_KEYWORDS = ["circuit malfunction", "circuit low input",
                            "circuit high input", "efficiency below threshold",
                            "leak detected", "sensor circuit"]


def load_codes():
    codes = {}
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                code = row[0].strip().strip('"').upper()
                desc = row[1].strip().strip('"')
                codes[code] = desc
    return codes


def classify_severity(description: str) -> str:
    d = description.lower()
    if any(k in d for k in HIGH_SEVERITY_KEYWORDS):
        return "HIGH"
    if any(k in d for k in MEDIUM_SEVERITY_KEYWORDS):
        return "MEDIUM"
    return "LOW"


def diagnose(code: str, codes_db=None) -> dict:
    codes_db = codes_db or load_codes()
    code = code.strip().upper()
    description = codes_db.get(code)
    found = description is not None
    severity = classify_severity(description) if found else "UNKNOWN"
    return {
        "code": code,
        "found_in_database": found,
        "description": description or "Code not found in the standard SAE J2012 generic code database. This may be a manufacturer-specific code that requires a make/model-specific lookup.",
        "severity": severity,
        "severity_basis": "Rule-based keyword match against the real code description (see HIGH/MEDIUM keyword lists in this file). Not a machine-learning score.",
        "source": "SAE J2012 generic DTC list, sourced from github.com/todrobbins/dtcdb (MIT license) and spot-checked against AutoZone's published OBD-II code list; two isolated duplicate-row errors in the source file were manually corrected (P0110, P0577)",
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Look up a real OBD-II diagnostic trouble code.")
    parser.add_argument("code", help="e.g. P0300")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = diagnose(args.code)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Code: {result['code']}")
        print(f"Found in database: {result['found_in_database']}")
        print(f"Description: {result['description']}")
        print(f"Severity: {result['severity']} ({result['severity_basis']})")
        print(f"Source: {result['source']}")
