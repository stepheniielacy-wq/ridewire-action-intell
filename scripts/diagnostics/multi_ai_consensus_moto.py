#!/usr/bin/env python3
"""
RideWire Multi-AI Consensus Engine - Motorcycle codes (REAL implementation)

Same honest method as multi_ai_consensus.py (used for car code P0171),
applied to 4 real Harley-Davidson DTCs researched in moto_codes_verified.json.

Honesty notes (read this before trusting any number this script prints):
- Three genuinely distinct, independent AI models (Claude Sonnet 5, GPT-5.6
  Terra, Gemini 3.1 Pro) were each asked the SAME real diagnostic question
  per code. Each model's raw answer is saved verbatim in consensus_runs/moto/.
- "Agreement" below is a plain keyword-overlap check on each model's own
  stated primary_root_cause and urgency - NOT a machine-learning confidence
  score and NOT validated against real-world repair outcomes. It answers the
  narrow question "did the three models say the same thing on this one
  query," nothing more.
- There is no validated accuracy percentage anywhere in this codebase.
  Producing one would require running many codes against known, verified
  repair outcomes and comparing - that dataset does not exist yet.
- DTC descriptions/causes/first-checks/sources come from moto_codes_verified.json
  (real Harley-Davidson bulletins, manuals, and owner/technical forum threads -
  see that file's "sources" and "confidence_note" fields per code).
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

DIAG_DIR = os.path.dirname(__file__)
MOTO_DIR = os.path.join(DIAG_DIR, "consensus_runs", "moto")
VERIFIED_CODES_PATH = os.path.join(DIAG_DIR, "moto_codes_verified.json")

MODEL_FILES = {
    "Claude Sonnet 5": "claude.json",
    "GPT-5.6 Terra": "gpt.json",
    "Gemini 3.1 Pro": "gemini.json",
}

# maps short internal key -> DTC code string as it appears in moto_codes_verified.json
CODE_KEY_TO_DTC = {
    "p0562": "P0562",
    "p0131": "P0131",
    "ckp": "P0371 / P0372 / P0374",
    "abs": "C1032 / C1034",
}


def normalize(text):
    return re.sub(r"[^a-z ]", "", text.lower())


def keyword_agreement(diagnoses, field):
    stopwords = {"the", "a", "an", "or", "and", "of", "in", "on", "to", "for"}
    word_sets = []
    for model_name, d in diagnoses.items():
        words = {w for w in normalize(d[field]).split() if w not in stopwords and len(w) > 2}
        word_sets.append(words)
    shared = set.intersection(*word_sets) if word_sets else set()
    return shared


def load_diagnoses(code_key):
    diagnoses = {}
    for model_name, suffix in MODEL_FILES.items():
        path = os.path.join(MOTO_DIR, f"{code_key}_{suffix}")
        with open(path) as f:
            diagnoses[model_name] = json.load(f)
    return diagnoses


def load_verified_code(dtc_code):
    with open(VERIFIED_CODES_PATH) as f:
        data = json.load(f)
    for entry in data["codes"]:
        if entry["code"] == dtc_code:
            return entry
    raise KeyError(f"{dtc_code} not found in moto_codes_verified.json")


def build_report(code_key):
    dtc_code = CODE_KEY_TO_DTC[code_key]
    verified = load_verified_code(dtc_code)
    diagnoses = load_diagnoses(code_key)

    shared_cause_words = keyword_agreement(diagnoses, "primary_root_cause")
    urgencies = [d["urgency"] for d in diagnoses.values()]
    urgency_agreement = len(set(urgencies)) == 1
    n_models = len(diagnoses)
    cause_agreement_count = n_models if shared_cause_words else 0

    report = {
        "code": dtc_code,
        "platform": verified["platform"],
        "code_description": verified["description"],
        "family": verified["family"],
        "verified_likely_causes": verified["likely_causes"],
        "verified_first_check": verified["first_check"],
        "verified_sources": verified["sources"],
        "verified_confidence_note": verified["confidence_note"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "models_queried": list(diagnoses.keys()),
        "per_model_diagnosis": diagnoses,
        "shared_root_cause_keywords": sorted(shared_cause_words),
        "root_cause_agreement": (
            f"{cause_agreement_count} of {n_models} models shared the keyword(s) "
            f"{sorted(shared_cause_words)} in their primary root cause"
            if shared_cause_words
            else f"0 of {n_models} models used overlapping words for primary root cause - no agreement detected"
        ),
        "urgency_values": urgencies,
        "urgency_agreement": urgency_agreement,
        "honesty_note": "Agreement figures above are literal keyword overlap on this single query, not a validated accuracy score.",
    }
    return report


if __name__ == "__main__":
    keys = sys.argv[1:] if len(sys.argv) > 1 else list(CODE_KEY_TO_DTC.keys())
    for code_key in keys:
        report = build_report(code_key)
        out_path = os.path.join(MOTO_DIR, f"report_{code_key}.json")
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"saved {out_path} - root_cause_agreement: {report['root_cause_agreement']}")
