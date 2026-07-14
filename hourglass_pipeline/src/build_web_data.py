"""
build_web_data.py — generates the multi-domain data files consumed by the
web_tool/ front end (qc_data_<slug>.json, diy_data_<slug>.json, domains.json)
directly from the pipeline's own verified output/ + data/ files.

This keeps the web tool honest: it never hand-edits or duplicates data, it
just reshapes the same qc_result_*.json (Devil's QC output) and the domain's
diy_order/diy_titles into the shape the front end expects.

Usage:
    python3 src/build_web_data.py
Run this after src/orchestrator.py any time a domain's claims change.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from gatherer import load_all_domains  # noqa: E402
from teacher import format_diy_report  # noqa: E402
from debater import run_devils_qc  # noqa: E402


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
WEB_TOOL_DIR = os.path.join(ROOT_DIR, "web_tool")
STANDALONE_WEB_TOOL_DIR = "/home/user/workspace/ridewire_diagnostic_tool"

# Short, URL/file-safe slug + friendly label per domain, keyed by the exact
# domain string used in the claims_*.json "domain" field. Add an entry here
# whenever a new domain file is created.
DOMAIN_META = {
    "Harley-Davidson Charging System Diagnostics (Battery / Stator / Voltage Regulator-Rectifier)": {
        "slug": "charging",
        "label": "Charging System",
        "sublabel": "Battery / Stator / Voltage Regulator-Rectifier",
    },
    "Harley-Davidson Ignition & Starting System Diagnostics (No-Crank / No-Start Troubleshooting)": {
        "slug": "ignition",
        "label": "Ignition & Starting System",
        "sublabel": "No-Crank / No-Start Troubleshooting",
    },
}


def build_diy_steps(verified, diy_order, diy_titles):
    """Reuses teacher.py's ordering logic, then parses its own markdown output
    back into structured steps — this guarantees the web tool's DIY steps are
    always in the exact same order as the shipped diy_report_*.md, with zero
    duplicated ordering logic."""
    md = format_diy_report("DOMAIN", verified, diy_order=diy_order, diy_titles=diy_titles)
    steps = []
    current = None
    for line in md.splitlines():
        if line.startswith("### Step "):
            if current:
                steps.append(current)
            # "### Step 3: Title text"
            rest = line[len("### Step "):]
            num_str, title = rest.split(":", 1)
            current = {"step": int(num_str.strip()), "title": title.strip(), "body": ""}
        elif current is not None and line.strip():
            current["body"] = (current["body"] + " " + line.strip()).strip()
    if current:
        steps.append(current)
    return steps


def main():
    claim_sets = load_all_domains(DATA_DIR)
    if not claim_sets:
        print("No domain files found. Nothing to build.")
        return

    manifest = []
    os.makedirs(WEB_TOOL_DIR, exist_ok=True)

    for cs in claim_sets:
        meta = DOMAIN_META.get(cs.domain)
        if not meta:
            print(f"WARNING: no DOMAIN_META entry for '{cs.domain}' — skipping web data build for it. "
                  f"Add an entry to DOMAIN_META in build_web_data.py.")
            continue

        slug = meta["slug"]
        qc_result = run_devils_qc(cs.claims)
        verified = qc_result["verified"]
        pending = qc_result["rejected_or_pending"]

        qc_data = {"verified": verified, "rejected_or_pending": pending}
        diy_steps = build_diy_steps(verified, cs.diy_order, cs.diy_titles)
        diy_data = {
            "intro": "If you're stuck on the side of the road: read this top to bottom, in order. You'll need a basic multimeter.",
            "steps": diy_steps,
        }

        for target_dir in (WEB_TOOL_DIR, STANDALONE_WEB_TOOL_DIR):
            os.makedirs(target_dir, exist_ok=True)
            with open(os.path.join(target_dir, f"qc_data_{slug}.json"), "w", encoding="utf-8") as f:
                json.dump(qc_data, f, indent=2)
            with open(os.path.join(target_dir, f"diy_data_{slug}.json"), "w", encoding="utf-8") as f:
                json.dump(diy_data, f, indent=2)

        manifest.append({
            "id": slug,
            "label": meta["label"],
            "sublabel": meta["sublabel"],
            "qc_file": f"qc_data_{slug}.json",
            "diy_file": f"diy_data_{slug}.json",
            "verified_count": len(verified),
            "pending_count": len(pending),
        })
        print(f"Built web data for '{cs.domain}' -> qc_data_{slug}.json / diy_data_{slug}.json "
              f"({len(verified)} verified, {len(pending)} pending)")

    for target_dir in (WEB_TOOL_DIR, STANDALONE_WEB_TOOL_DIR):
        with open(os.path.join(target_dir, "domains.json"), "w", encoding="utf-8") as f:
            json.dump({"domains": manifest}, f, indent=2)
    print(f"Wrote domains.json manifest with {len(manifest)} domain(s).")


if __name__ == "__main__":
    main()
