"""
debater.py — "The Debater" / Devil's QC verification layer of the Hourglass.

This is the real 13-to-1 style bottleneck: every claim gathered by the
Learner must pass through here before it is allowed to reach the Teacher and
be taught out to the network. Verification is based on independent-source
corroboration, not on trusting a single source or an LLM's say-so.

Rules enforced:
  1. MIN_CORROBORATION independent domains must back a claim before it is
     marked VERIFIED. Fewer than that => NEEDS_MORE_SOURCES (purgatory, not
     taught yet). Independence is derived from each source's actual URL
     host, not from a self-reported domain label, and is normalized
     (case, trailing slash/whitespace, www.) before deduplication.
  2. Domain independence is verified against the URL itself. A source's
     declared "domain" field must match the host of its own "url" — a
     claim whose declared domain doesn't match its url's real host is
     rejected outright (REJECTED_CONFLICT), not silently trusted.
  3. Every VERIFIED claim carries a confidence score = number of independent
     source domains (not just number of links — 5 links from 1 domain is
     weaker evidence than 3 links from 3 domains).
  4. Safety-tagged claims (category containing "safety") require a strictly
     higher bar (MIN_CORROBORATION_SAFETY) before being marked verified,
     because a wrong safety instruction is more dangerous than a wrong spec.

  KNOWN LIMITATION (documented honestly, not fixed yet): numeric_range
  values are not currently cross-checked against per-source stated values,
  because sources are not structured to carry their own per-source number
  in this version of the schema. This is a real gap versus an earlier
  draft of this docstring that implied that check existed — flagged here
  rather than left as a false claim. See tests/redteam_debater.py Attack 4.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from urllib.parse import urlparse


MIN_CORROBORATION = 3
MIN_CORROBORATION_SAFETY = 5


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


def _normalize_host(host: str) -> str:
    """Lowercase, strip whitespace/trailing slash, drop a leading www. —
    so 'HDForums.com ', 'hdforums.com/', and 'www.hdforums.com' all
    collapse to the same 'hdforums.com', instead of being counted as 3
    different independent sources (see tests/redteam_debater.py Attack 1)."""
    h = (host or "").strip().lower().rstrip("/")
    if h.startswith("www."):
        h = h[4:]
    return h


def _url_host(url: str) -> str:
    try:
        return _normalize_host(urlparse(url).netloc)
    except Exception:
        return ""


def _independent_domains(sources: List[Dict[str, str]]) -> List[str]:
    """Returns the list of independent domains actually backing a claim,
    derived from each source's real URL host — never from the self-reported
    'domain' label alone (see tests/redteam_debater.py Attack 2). Sources
    whose declared domain label doesn't match their own URL's host are
    excluded entirely rather than trusted."""
    seen = []
    for s in sources:
        declared = _normalize_host(s.get("domain", ""))
        actual = _url_host(s.get("url", ""))
        if not actual:
            continue
        if declared and not _same_site(declared, actual):
            # Declared label doesn't match the real host of its own url (and
            # isn't a legitimate subdomain of it either) — do not trust the
            # label; this source contributes nothing.
            continue
        # Group by the shorter/root form so locale or forum subdomains of
        # the same publisher (es.scribd.com, www.hdforums.com) collapse into
        # one independent domain instead of counting as separate sources.
        canonical = declared if declared else actual
        if canonical not in seen:
            seen.append(canonical)
    return seen


def _same_site(declared: str, actual: str) -> bool:
    """True if declared and actual are the same site once normalized, or
    one is a subdomain of the other (e.g. declared 'scribd.com' legitimately
    covers actual 'es.scribd.com' — same publisher, just a locale subdomain).
    This is deliberately more lenient than exact-match so real regional/
    locale subdomains aren't false-flagged, while still catching genuinely
    unrelated domains like 'reuters.com' vs 'fake-blog.example'."""
    if not declared or not actual:
        return False
    if declared == actual:
        return True
    return actual.endswith("." + declared) or declared.endswith("." + actual)


def _has_domain_url_mismatch(sources: List[Dict[str, str]]) -> bool:
    for s in sources:
        declared = _normalize_host(s.get("domain", ""))
        actual = _url_host(s.get("url", ""))
        if declared and actual and not _same_site(declared, actual):
            return True
    return False


def _confidence_from_count(count: int, threshold: int) -> str:
    if count >= threshold + 2:
        return "HIGH"
    if count >= threshold:
        return "MEDIUM"
    return "LOW"


def verify_claim(claim: Dict[str, Any]) -> VerificationResult:
    sources = claim.get("sources", [])
    domains = _independent_domains(sources)
    is_safety = "safety" in claim.get("category", "")
    threshold = MIN_CORROBORATION_SAFETY if is_safety else MIN_CORROBORATION

    citations = [s.get("url", "") for s in sources]

    if _has_domain_url_mismatch(sources):
        status = "REJECTED_CONFLICT"
        notes = (
            "Rejected: at least one source's declared domain label does not match "
            "the actual host of its own url. A mismatched label is treated as untrustworthy "
            "self-reporting, not corroboration — fix the source data and resubmit."
        )
    elif len(domains) >= threshold:
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
        category=claim.get("category", ""),
        statement=claim.get("statement", ""),
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

    for i, claim in enumerate(claims):
        try:
            result = verify_claim(claim)
        except (KeyError, TypeError, AttributeError) as e:
            # A malformed claim (missing required field, wrong type, etc.)
            # must not take down the whole batch — isolate it as its own
            # pending record instead (see tests/redteam_debater.py Attack 5).
            pending.append({
                "fact_id": claim.get("fact_id", f"UNKNOWN_MALFORMED_CLAIM_{i}") if isinstance(claim, dict) else f"UNKNOWN_MALFORMED_CLAIM_{i}",
                "category": claim.get("category", "") if isinstance(claim, dict) else "",
                "statement": claim.get("statement", "") if isinstance(claim, dict) else "",
                "status": "MALFORMED_INPUT",
                "independent_domain_count": 0,
                "confidence": "LOW",
                "citations": [],
                "numeric_range": None,
                "notes": f"Skipped: claim at batch index {i} failed to process ({type(e).__name__}: {e}). "
                         f"Fix the source record; the rest of the batch was not affected.",
            })
            continue
        bucket = verified if result.status == "VERIFIED" else pending
        bucket.append(asdict(result))

    return {"verified": verified, "rejected_or_pending": pending}
