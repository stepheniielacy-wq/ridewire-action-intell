"""
redteam_debater.py — IDART-style adversarial test harness for debater.py
(the Devil's QC / corroboration-verification layer of the Hourglass).

Modeled on Sandia's IDART methodology: don't theorize about weaknesses,
actually try to cause the failure and record whether the attack succeeds.
Each test below is a real attack attempt against the real verify_claim() /
run_devils_qc() functions — nothing here is simulated or hand-waved.

Run: python3 tests/redteam_debater.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from debater import verify_claim, run_devils_qc, MIN_CORROBORATION, MIN_CORROBORATION_SAFETY  # noqa: E402


RESULTS = []


def record(attack_id, description, passed_defense, evidence):
    """passed_defense=True means the system correctly resisted the attack.
    passed_defense=False means the attack succeeded (a real vulnerability)."""
    RESULTS.append({
        "attack_id": attack_id,
        "description": description,
        "defense_held": passed_defense,
        "evidence": evidence,
    })
    status = "DEFENSE HELD" if passed_defense else "ATTACK SUCCEEDED (VULNERABILITY)"
    print(f"[{attack_id}] {status}\n    {description}\n    Evidence: {evidence}\n")


# ---------------------------------------------------------------------------
# Attack 1: Same source repeated with trivial formatting variance
# (trailing slash, trailing space, case) — does dedup actually catch this,
# or does one real source get counted as 3 "independent" ones?
# ---------------------------------------------------------------------------
def attack_1_domain_formatting_variance():
    claim = {
        "fact_id": "RT1",
        "category": "spec",
        "statement": "Test claim for formatting-variance attack.",
        "sources": [
            {"domain": "hdforums.com", "url": "https://hdforums.com/a"},
            {"domain": "hdforums.com/", "url": "https://hdforums.com/b"},
            {"domain": "HDForums.com ", "url": "https://hdforums.com/c"},
        ],
    }
    result = verify_claim(claim)
    # This is ONE real site (hdforums.com) typed 3 slightly different ways.
    # A correct defense would collapse these to 1 independent domain and
    # return NEEDS_MORE_SOURCES. If it returns VERIFIED, the attack worked.
    attack_succeeded = result.status == "VERIFIED"
    record(
        "ATTACK-1",
        "Cite the same real domain 3x with trivial formatting differences "
        "(trailing slash, trailing space, case) to fake 3 independent sources.",
        passed_defense=not attack_succeeded,
        evidence=f"status={result.status}, independent_domain_count={result.independent_domain_count}",
    )


# ---------------------------------------------------------------------------
# Attack 2: "domain" field is never checked against the actual "url" field.
# Can we fabricate a claim by typing 3 trustworthy-sounding domain labels
# while the URLs point anywhere at all (even the same fake page)?
# ---------------------------------------------------------------------------
def attack_2_domain_url_mismatch():
    claim = {
        "fact_id": "RT2",
        "category": "spec",
        "statement": "Completely fabricated claim with fake trustworthy-sounding domain labels.",
        "sources": [
            {"domain": "reuters.com", "url": "https://fake-blog.example/made-up-page"},
            {"domain": "nytimes.com", "url": "https://fake-blog.example/made-up-page"},
            {"domain": "bbc.com", "url": "https://fake-blog.example/made-up-page"},
        ],
    }
    result = verify_claim(claim)
    # All 3 "sources" are actually the identical fake URL. If the system
    # only looks at the self-reported domain label (not the URL), this
    # fabricated claim will still pass as VERIFIED with HIGH-sounding
    # confidence, backed by nothing real.
    attack_succeeded = result.status == "VERIFIED"
    record(
        "ATTACK-2",
        "Type 3 trustworthy-sounding domain labels (reuters.com, nytimes.com, bbc.com) "
        "while every url actually points to the same fabricated page — domain label is "
        "never validated against the real url.",
        passed_defense=not attack_succeeded,
        evidence=f"status={result.status}, confidence={result.confidence}, "
                 f"independent_domain_count={result.independent_domain_count}, "
                 f"citations={result.citations}",
    )


# ---------------------------------------------------------------------------
# Attack 3: Safety-tagged claims are documented as needing a "strictly
# higher bar" than normal claims. Is MIN_CORROBORATION_SAFETY actually
# higher than MIN_CORROBORATION in the real code?
# ---------------------------------------------------------------------------
def attack_3_safety_bar_equivalence():
    is_actually_stricter = MIN_CORROBORATION_SAFETY > MIN_CORROBORATION
    claim = {
        "fact_id": "RT3",
        "category": "safety_and_diagnostic_rule",
        "statement": "A safety-critical instruction that should require a strictly higher bar.",
        "sources": [
            {"domain": "site-a.com", "url": "https://site-a.com/x"},
            {"domain": "site-b.com", "url": "https://site-b.com/x"},
            {"domain": "site-c.com", "url": "https://site-c.com/x"},
        ],
    }
    result = verify_claim(claim)
    # The docstring in debater.py explicitly claims safety claims need a
    # "strictly higher bar". If exactly 3 sources (the normal bar) still
    # verifies a safety claim, the documented behavior is false.
    record(
        "ATTACK-3",
        "debater.py's docstring claims safety-tagged claims require a 'strictly higher "
        "bar' (MIN_CORROBORATION_SAFETY). Check whether the constant is actually higher, "
        "and whether a safety claim with exactly the normal minimum (3 sources) still "
        "verifies.",
        passed_defense=is_actually_stricter,
        evidence=f"MIN_CORROBORATION={MIN_CORROBORATION}, MIN_CORROBORATION_SAFETY={MIN_CORROBORATION_SAFETY} "
                 f"-> safety claim with exactly {MIN_CORROBORATION} sources (the normal, non-safety bar) "
                 f"resulted in status={result.status} (should NOT verify if the safety bar is truly higher).",
    )


# ---------------------------------------------------------------------------
# Attack 4: docstring Rule 2 claims numeric_range consistency is enforced
# across corroborating sources ("no source contradicting the range
# outright"). Does any code path actually check this?
# ---------------------------------------------------------------------------
def attack_4_numeric_range_contradiction():
    claim = {
        "fact_id": "RT4",
        "category": "spec",
        "numeric_range": "12.5-13.0V at rest",
        "statement": "Battery resting voltage should read 12.5-13.0V (docstring claims contradicting "
                      "sources would be caught, but these 3 sources actually disagree wildly: one says "
                      "6V, one says 12.5-13.0V, one says 24V).",
        "sources": [
            {"domain": "site-a.com", "url": "https://site-a.com/says-6v"},
            {"domain": "site-b.com", "url": "https://site-b.com/says-12-13v"},
            {"domain": "site-c.com", "url": "https://site-c.com/says-24v"},
        ],
    }
    result = verify_claim(claim)
    # There is no field in `claim` capturing each source's own stated
    # number, and debater.py has zero logic referencing numeric_range at
    # all. So this will verify identically to a claim where sources agree,
    # even though the docstring documents a contradiction check that
    # doesn't exist in code.
    attack_succeeded = result.status == "VERIFIED"
    record(
        "ATTACK-4",
        "docstring Rule 2 claims sources contradicting a stated numeric_range are caught. "
        "No code in debater.py references numeric_range at all — verify a claim whose 3 "
        "sources wildly disagree (6V / 12-13V / 24V) and see if it still passes.",
        passed_defense=not attack_succeeded,
        evidence=f"status={result.status} despite sources disagreeing by a factor of 4x "
                 f"(6V vs 24V) — numeric_range='{result.numeric_range}' was never checked against "
                 f"per-source values because no such per-source field or check exists.",
    )


# ---------------------------------------------------------------------------
# Attack 5: malformed claim in a batch — does one bad record crash the
# entire QC run for every other (valid) claim in the batch?
# ---------------------------------------------------------------------------
def attack_5_malformed_claim_crashes_batch():
    good_claim_1 = {
        "fact_id": "RT5_GOOD_1", "category": "spec", "statement": "Fine claim one.",
        "sources": [{"domain": "a.com", "url": "https://a.com"}, {"domain": "b.com", "url": "https://b.com"},
                    {"domain": "c.com", "url": "https://c.com"}],
    }
    malformed_claim = {
        # missing "fact_id" entirely
        "category": "spec", "statement": "Malformed claim missing fact_id.",
        "sources": [{"domain": "d.com", "url": "https://d.com"}],
    }
    good_claim_2 = {
        "fact_id": "RT5_GOOD_2", "category": "spec", "statement": "Fine claim two.",
        "sources": [{"domain": "e.com", "url": "https://e.com"}, {"domain": "f.com", "url": "https://f.com"},
                    {"domain": "g.com", "url": "https://g.com"}],
    }
    batch = [good_claim_1, malformed_claim, good_claim_2]
    try:
        result = run_devils_qc(batch)
        crashed = False
        evidence = (f"run_devils_qc completed without crashing: "
                    f"{len(result['verified'])} verified, {len(result['rejected_or_pending'])} pending.")
    except Exception as e:
        crashed = True
        evidence = f"run_devils_qc RAISED {type(e).__name__}: {e} — entire batch of 3 claims " \
                   f"(including 2 otherwise-valid ones) failed to process because of 1 malformed record."
    record(
        "ATTACK-5",
        "Submit a batch of 3 claims where the middle one is missing required field 'fact_id'. "
        "A robust pipeline should skip/flag just that one record. Does the whole batch crash instead?",
        passed_defense=not crashed,
        evidence=evidence,
    )


def main():
    print("=" * 78)
    print("IDART-style red-team assessment of debater.py (Devil's QC corroboration layer)")
    print("Each attack below is executed for real against the live pipeline code.")
    print("=" * 78 + "\n")

    attack_1_domain_formatting_variance()
    attack_2_domain_url_mismatch()
    attack_3_safety_bar_equivalence()
    attack_4_numeric_range_contradiction()
    attack_5_malformed_claim_crashes_batch()

    held = sum(1 for r in RESULTS if r["defense_held"])
    total = len(RESULTS)
    print("=" * 78)
    print(f"SUMMARY: {held}/{total} defenses held, {total - held}/{total} attacks succeeded (real vulnerabilities).")
    print("=" * 78)

    out_path = os.path.join(os.path.dirname(__file__), "..", "output", "redteam_debater_findings.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"held": held, "total": total, "results": RESULTS}, f, indent=2)
    print(f"\nFull findings written to {out_path}")


if __name__ == "__main__":
    main()
