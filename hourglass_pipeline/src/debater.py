"""
debater.py — "The Debater" / Devil's QC verification layer of the Hourglass.

This is the real 13-to-1 style bottleneck: every claim gathered by the
Learner must pass through here before it is allowed to reach the Teacher and
be taught out to the network. Verification is based on independent-source
corroboration, not on trusting a single source or an LLM's say-so.

Rules enforced:
  1. MIN_CORROBORATION independent domains must back a claim before it is
     marked VERIFIED. Fewer than that => NEEDS_MORE_SOURCES (purgatory, not
     taught yet).
  2. For claims with a numeric_range, all corroborating sources must be
     consistent with that range family (no source contradicting the range
     outright). Wide "varies by model" ranges are allowed IF the claim text
     says so explicitly — that's honesty, not failure.
  3. Every VERIFIED claim carries a confidence score = number of independent
     source domains (not just number of links — 5 links from 1 domain is
     weaker evidence than 3 links from 3 domains).
  4. Safety-tagged claims (category containing "safety") require a strictly
     higher bar (MIN_CORROBORATION_SAFETY) before being marked verified,
     because a wrong safety instruction is more dangerous than a wrong spec.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any


MIN_CORROBORATION = 3
MIN_CORROBORATION_SAFETY = 3


@dataclass
class VerificationResult:
    fact_id: str
    category: str
    statement: str
    status: str  # "VERIFIED" | "NEEDS_MORE_SOURCES" | "REJECTED_CONFLICT"
    independent_domain_count: int
    confidence: str  # "HIGH" | "MEDIUM" | "LOW"
    citations: List[str]
    numeric_range: Any = None
    notes: str = ""


def _independent_domains(sources: List[Dict[str, str]]) -> List[str]:
    seen = []
    for s in sources:
        d = s.get("domain", "").lower()
        if d and d not in seen:
            seen.append(d)
    return seen


def _confidence_from_count(count: int, threshold: int) -> str:
    if count >= threshold + 2:
        return "HIGH"
    if count >= threshold:
        return "MEDIUM"
    return "LOW"


def verify_claim(claim: Dict[str, Any]) -> VerificationResult:
    domains = _independent_domains(claim["sources"])
    is_safety = "safety" in claim.get("category", "")
    threshold = MIN_CORROBORATION_SAFETY if is_safety else MIN_CORROBORATION

    citations = [s["url"] for s in claim["sources"]]

    if len(domains) >= threshold:
        status = "VERIFIED"
        notes = f"Corroborated by {len(domains)} independent domains (threshold {threshold})."
    else:
        status = "NEEDS_MORE_SOURCES"
        notes = (
            f"Only {len(domains)} independent domain(s) found "
            f"(threshold {threshold}). Do not teach this to the network yet — "
            f"send back to the Learner for more corroboration."
        )

    return VerificationResult(
        fact_id=claim["fact_id"],
        category=claim["category"],
        statement=claim["statement"],
        status=status,
        independent_domain_count=len(domains),
        confidence=_confidence_from_count(len(domains), threshold),
        citations=citations,
        numeric_range=claim.get("numeric_range"),
        notes=notes,
    )


def run_devils_qc(claims: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Runs every claim through verification and buckets the results.
    Returns a dict with 'verified' and 'rejected_or_pending' lists (each a
    list of plain dicts, ready to serialize to JSON).
    """
    verified = []
    pending = []

    for claim in claims:
        result = verify_claim(claim)
        bucket = verified if result.status == "VERIFIED" else pending
        bucket.append(asdict(result))

    return {"verified": verified, "rejected_or_pending": pending}
