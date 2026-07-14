"""
gatherer.py — "The Learner" / gathering layer of the Hourglass pipeline.

REAL, HONEST STATUS:
This module loads claim sets that were gathered by a human-directed research
pass (live web search across independent sources) and stored as structured
JSON in data/. It does NOT autonomously "recruit open-source models from the
internet" or scrape arbitrary sites at runtime — that framing from early
brainstorming was aspirational language, not a working system.

What this module *actually* does, today:
  1. Loads a claims file (one vehicle system/domain per file) from data/.
  2. Validates the schema (every claim must cite at least one real source URL).
  3. Returns a normalized in-memory representation for the Debater to verify.

How to extend it ("Each One Teach One" in a real, controllable form):
  - To add a new domain (e.g. a different Harley model line, a different
    manufacturer, or a different vehicle system), create a new
    data/claims_<domain>.json file following the same schema, populated with
    real claims + real source URLs (gathered via actual research, e.g.
    Perplexity search, service manuals, forums). Drop it in data/ and the
    orchestrator will pick it up.
  - A live-fetch backend (calling a real search/API) can be wired in later by
    implementing LiveGatherer.fetch() below — it is intentionally left
    unimplemented rather than faked, because a fake implementation would
    silently produce unverifiable data, which defeats the entire point of
    the Devil's QC step.
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any


REQUIRED_CLAIM_FIELDS = {"fact_id", "category", "statement", "sources"}


@dataclass
class ClaimSet:
    domain: str
    pilot_note: str
    claims: List[Dict[str, Any]] = field(default_factory=list)


class SchemaError(ValueError):
    """Raised when a claims file does not meet the minimum data-integrity bar."""


def load_claims_file(path: str) -> ClaimSet:
    """Load and validate a single claims JSON file from disk."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Claims file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    domain = raw.get("domain")
    if not domain:
        raise SchemaError(f"{path}: missing required 'domain' field")

    claims = raw.get("claims", [])
    if not claims:
        raise SchemaError(f"{path}: no claims found — an empty domain teaches nothing")

    for i, claim in enumerate(claims):
        missing = REQUIRED_CLAIM_FIELDS - set(claim.keys())
        if missing:
            raise SchemaError(f"{path}: claim #{i} ({claim.get('fact_id', '?')}) missing fields: {missing}")
        if not claim["sources"]:
            raise SchemaError(
                f"{path}: claim {claim['fact_id']} has zero sources — "
                f"an uncited claim cannot enter the Hourglass"
            )
        for src in claim["sources"]:
            if "url" not in src or not src["url"].startswith("http"):
                raise SchemaError(f"{path}: claim {claim['fact_id']} has an invalid source entry: {src}")

    return ClaimSet(domain=domain, pilot_note=raw.get("pilot_note", ""), claims=claims)


def load_all_domains(data_dir: str) -> List[ClaimSet]:
    """Load every claims_*.json file in the data directory."""
    claim_sets = []
    for fname in sorted(os.listdir(data_dir)):
        if fname.startswith("claims_") and fname.endswith(".json"):
            claim_sets.append(load_claims_file(os.path.join(data_dir, fname)))
    return claim_sets


class LiveGatherer:
    """
    Placeholder for a real live-search backend.

    Intentionally NOT implemented with fake/mocked data. To make this real,
    wire in an actual search API (e.g. via the custom-credentials flow) and
    have `fetch()` return claims in the exact schema validated above —
    including real source URLs that a human or the Debater can re-check.
    """

    def fetch(self, topic: str, min_sources: int = 3):
        raise NotImplementedError(
            "LiveGatherer.fetch() is not implemented. Add a real search/API "
            "integration here rather than mocking a result — mocked gather "
            "data would defeat the Debater's ability to verify anything real."
        )
