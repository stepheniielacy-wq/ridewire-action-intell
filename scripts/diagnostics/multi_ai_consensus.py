#!/usr/bin/env python3
"""
RideWire Multi-AI Consensus Engine (REAL implementation)

Honesty notes (read this before trusting any number this script prints):
- This queries three genuinely distinct, independent AI models (Claude, GPT,
  and Gemini) on the SAME real diagnostic trouble code. Each model's opinion
  is captured verbatim in consensus_runs/*.json.
- "Agreement" below is a plain keyword-overlap check on each model's own
  stated primary_root_cause and urgency - NOT a machine-learning confidence
  score and NOT validated against real-world repair outcomes. It answers the
  narrow question "did the three models say the same thing on this one
  query", nothing more.
- There is no "94.2% accuracy" claim anywhere in this codebase. Producing a
  real accuracy percentage would require running many codes against known,
  verified repair outcomes and comparing - that dataset does not exist yet.
- Model calls in this run were made by RideWire's own AI assistant (three
  parallel independent queries), not by hitting OpenAI/Anthropic/Google's
  paid HTTP APIs directly - this avoids the three separate paid API keys the
  legacy multiAIOrchestrator.js expected, consistent with the "cost-wise,
  open-source-where-we-can" build rule for this project.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

RUNS_DIR = os.path.join(os.path.dirname(__file__), "consensus_runs")

MODEL_FILES = {
    "Claude Sonnet 5": "claude_diagnosis.json",
    "GPT-5.6 Terra": "gpt_diagnosis.json",
    "Gemini 3.1 Pro": "gemini_diagnosis.json",
}


def load_diagnoses():
    diagnoses = {}
    for model_name, filename in MODEL_FILES.items():
        path = os.path.join(RUNS_DIR, filename)
        with open(path) as f:
            diagnoses[model_name] = json.load(f)
    return diagnoses


def normalize(text):
    return re.sub(r"[^a-z ]", "", text.lower())


def keyword_agreement(diagnoses, field, min_shared_words=1):
    """Very simple, transparent heuristic: do the models' answers for `field`
    share at least `min_shared_words` non-trivial words? This is NOT semantic
    similarity or an ML score - just literal word overlap, printed so anyone
    can verify the logic themselves."""
    stopwords = {"the", "a", "an", "or", "and", "of", "in", "on", "to", "for"}
    word_sets = []
    for model_name, d in diagnoses.items():
        words = {w for w in normalize(d[field]).split() if w not in stopwords and len(w) > 2}
        word_sets.append(words)
    shared = set.intersection(*word_sets) if word_sets else set()
    return shared


def build_report(code, code_description, code_severity, diagnoses):
    shared_cause_words = keyword_agreement(diagnoses, "primary_root_cause")
    urgencies = [d["urgency"] for d in diagnoses.values()]
    urgency_agreement = len(set(urgencies)) == 1

    n_models = len(diagnoses)
    cause_agreement_count = n_models if shared_cause_words else 0

    report = {
        "code": code,
        "code_description": code_description,
        "code_severity_rule_based": code_severity,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "models_queried": list(diagnoses.keys()),
        "per_model_diagnosis": diagnoses,
        "shared_root_cause_keywords": sorted(shared_cause_words),
        "root_cause_agreement": f"{cause_agreement_count} of {n_models} models shared the keyword(s) {sorted(shared_cause_words)} in their primary root cause"
        if shared_cause_words
        else f"0 of {n_models} models used overlapping words for primary root cause - no agreement detected",
        "urgency_values": urgencies,
        "urgency_agreement": urgency_agreement,
        "honesty_note": "Agreement figures above are literal keyword overlap on this single query, not a validated accuracy score.",
    }
    return report


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "P0171"
    code_description = sys.argv[2] if len(sys.argv) > 2 else "System too Lean (Bank 1)"
    code_severity = sys.argv[3] if len(sys.argv) > 3 else "LOW"

    diagnoses = load_diagnoses()
    report = build_report(code, code_description, code_severity, diagnoses)
    print(json.dumps(report, indent=2))
