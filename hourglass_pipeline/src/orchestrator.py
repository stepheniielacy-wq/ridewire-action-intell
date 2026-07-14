"""
orchestrator.py — runs the real Gather -> Debate -> Teach pipeline end to end
for every domain file found in data/, and writes real output files.

Usage:
    python src/orchestrator.py

This is the "each one teach one" loop made concrete and auditable:
  1. Gatherer loads a domain's claim set (with real citations).
  2. Debater runs Devil's QC — corroboration-based verification.
  3. Teacher renders PRO and DIY reports from only the verified claims.
  4. Everything (including rejected/pending claims) is written to output/
     so nothing is silently dropped — you can see exactly what passed,
     what didn't, and why.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from gatherer import load_all_domains  # noqa: E402
from debater import run_devils_qc  # noqa: E402
from teacher import format_pro_report, format_diy_report  # noqa: E402


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    claim_sets = load_all_domains(DATA_DIR)

    if not claim_sets:
        print("No domain files found in data/. Nothing to run.")
        return

    for cs in claim_sets:
        print(f"\n=== HOURGLASS RUN: {cs.domain} ===")
        print(f"Gathered {len(cs.claims)} claims.")

        qc_result = run_devils_qc(cs.claims)
        verified = qc_result["verified"]
        pending = qc_result["rejected_or_pending"]

        print(f"Devil's QC: {len(verified)} VERIFIED, {len(pending)} NEEDS_MORE_SOURCES.")

        slug = cs.domain.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "-")
        slug = slug[:60]

        qc_path = os.path.join(OUTPUT_DIR, f"qc_result_{slug}.json")
        with open(qc_path, "w", encoding="utf-8") as f:
            json.dump(qc_result, f, indent=2)
        print(f"Wrote QC result -> {qc_path}")

        pro_report = format_pro_report(cs.domain, verified)
        pro_path = os.path.join(OUTPUT_DIR, f"pro_report_{slug}.md")
        with open(pro_path, "w", encoding="utf-8") as f:
            f.write(pro_report)
        print(f"Wrote PRO report -> {pro_path}")

        diy_report = format_diy_report(cs.domain, verified)
        diy_path = os.path.join(OUTPUT_DIR, f"diy_report_{slug}.md")
        with open(diy_path, "w", encoding="utf-8") as f:
            f.write(diy_report)
        print(f"Wrote DIY report -> {diy_path}")

        if pending:
            print("Claims still pending (need more independent sources before teaching):")
            for p in pending:
                print(f"  - {p['fact_id']}: {p['notes']}")


if __name__ == "__main__":
    main()
