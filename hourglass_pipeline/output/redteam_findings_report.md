# Red-Team Findings Report: Hourglass Corroboration Logic (`debater.py`)

**Methodology:** IDART-style adversarial testing (modeled on [Sandia National Labs' Information Design Assurance Red Team](https://casa.sandia.gov/idart/) approach) — every attack below was executed for real against the live `verify_claim()` / `run_devils_qc()` code in `src/debater.py`, not theorized about. Test harness: `tests/redteam_debater.py`.

**Scope:** The Devil's QC corroboration layer only — the code that decides whether a claim has enough independent, trustworthy source agreement to be marked `VERIFIED` before it reaches a Pro or DIY report.

## Bottom line

Round 1 (before any fixes): **5 of 5 attacks succeeded.** Every defense that mattered — deduplication, domain/URL trust, the safety bar, numeric contradiction checking, and crash isolation — failed on first attempt.

Round 2 (after fixes): **4 of 5 defenses now hold.** One (numeric-range cross-checking) is a real, still-open gap that requires a schema change, not a quick patch — it is documented as a known limitation rather than silently claimed as fixed.

The real production dataset (20 claims across 2 domains, shipped before this test) was separately audited against all 5 exploits and found clean — none of these vulnerabilities had actually been exploited in the data published so far. But two real claims *did* legitimately change status once the honest fixes were applied (see "Real-data consequences" below) — this is the system correctly getting stricter, not a bug.

## The 5 attacks

| # | Attack | Round 1 | Round 2 (post-fix) |
|---|--------|---------|---------------------|
| 1 | Cite the same real domain 3x with trivial formatting differences (trailing slash, trailing space, case) to fake 3 independent sources | **Succeeded** — counted as 3 independent domains, VERIFIED | **Defense held** — normalizes host casing/whitespace/trailing slash/`www.` before dedup; correctly counted as 1 domain, `NEEDS_MORE_SOURCES` |
| 2 | Label 3 sources as `reuters.com`, `nytimes.com`, `bbc.com` while every actual `url` points to the same fabricated page | **Succeeded** — `VERIFIED`, MEDIUM confidence; the `domain` field was never checked against the real `url` | **Defense held** — new `_has_domain_url_mismatch()` check parses the real host from each `url` and rejects the claim outright (`REJECTED_CONFLICT`) when a declared label doesn't match reality |
| 3 | Docstring claims safety-tagged claims need a "strictly higher bar." Check whether `MIN_CORROBORATION_SAFETY` is actually higher, and whether a safety claim with only the normal minimum (3 sources) still verifies | **Succeeded** — the constant was silently equal to the normal bar (3 == 3); false documentation | **Defense held** — raised to 5; a safety claim with 3 sources now correctly returns `NEEDS_MORE_SOURCES` |
| 4 | Docstring claims sources that disagree on `numeric_range` are caught. Submit 3 sources disagreeing by 4x (6V vs 24V) | **Succeeded** — `VERIFIED` anyway; no code anywhere ever reads `numeric_range` against per-source values | **Still open.** No fix applied this round. The claims schema has no field for "what value did *this specific source* state" — only one shared `numeric_range` for the whole claim. A real fix needs a schema change (each source needs its own reported value), not just new logic. Documented as a known limitation in the code's docstring rather than papered over. |
| 5 | Submit a 3-claim batch where the middle claim is missing the required `fact_id` field | **Succeeded** — uncaught `KeyError` crashed `run_devils_qc()`, taking down 2 otherwise-valid claims with it | **Defense held** — each claim is now processed in its own try/except; a malformed claim is isolated as a `MALFORMED_INPUT` record with a note explaining what broke, and the rest of the batch (verified or pending) is unaffected |

## Fixes applied to `debater.py`

- Rewrote the module docstring to state the real rules, including the one honestly-unfixed limitation (attack 4), instead of describing behavior the code didn't actually have.
- `_independent_domains()` rewritten to derive identity from the real URL host (parsed via `urllib.parse.urlparse`), normalized for case/whitespace/trailing slash/`www.`, rather than trusting a free-text `domain` label.
- New `_same_site()` helper treats a legitimate subdomain of the declared domain as the same source (e.g. `es.scribd.com` under a declared `scribd.com` is Scribd's own Spanish-locale subdomain, not a different, independent publisher) — this was added *after* the first version of the fix produced a false positive on real data (see below); an overly strict exact-host-match would have wrongly rejected a real, legitimate source.
- New `_has_domain_url_mismatch()` flags sources whose declared label and real URL host are unrelated sites entirely (the actual fabrication case in attack 2) without over-flagging legitimate subdomains.
- `verify_claim()` now checks for a domain/URL mismatch first and returns `REJECTED_CONFLICT` (a status value the type annotation already allowed for, previously unused) instead of silently trusting labels.
- `MIN_CORROBORATION_SAFETY` raised from 3 to 5 so it is actually stricter than the normal bar of 3, matching what the docstring always claimed.
- `run_devils_qc()` now wraps each claim's verification in a per-claim `try/except`, so one malformed record can't take the whole batch down; it's reported as `MALFORMED_INPUT` with an explanatory note.

## Real-data consequences (the honest part)

Re-running the full pipeline on the actual 20-claim dataset after the fixes changed 2 real outcomes — both are correct, not bugs:

- **`F10_GROUND_MIMICS_FAILURE`** (charging system, category `safety_and_diagnostic_rule`) had 3 independent domains. Under the old, broken safety bar (3 == 3) it was `VERIFIED`. Under the real bar of 5, it correctly drops to `NEEDS_MORE_SOURCES`.
- **`F8_SAFETY_INTERLOCK_REQUIREMENTS`** (ignition system, same category) also had 3 independent domains and drops the same way. Notably, this claim's own data file already carried a manually-written `pilot_note` flagging that one of its 3 sources was another official Harley-Davidson domain and not fully independent in spirit — the stricter automated bar now catches exactly the weakness a human reviewer had already spotted by hand.

Both claims remain visible on the site labeled "pending" — not deleted, not silently downgraded — and are excluded from the Pro/DIY reports until more independent sources are added, exactly as the (now-accurate) site copy describes.

One near-miss worth recording: the first version of the domain/URL match fix produced a **false positive** on a real, legitimate source (`F4_VOLTAGE_DROP_CRANK_TEST`'s Scribd citation, declared as `scribd.com` but linked via its `es.scribd.com` Spanish-locale subdomain). This was caught before shipping by checking real data against the fix, not assumed to be correct — the subdomain-aware `_same_site()` logic was added specifically to resolve it, and `F4` is confirmed back to `VERIFIED` after that correction.

## What's still not fixed

Attack 4 (numeric-range cross-checking) remains a real, open gap. Fixing it properly would require the claims schema to capture what value each individual source actually stated (not just one shared `numeric_range` for the whole claim), then a comparison step in `debater.py` to flag claims where sources materially disagree. That's a data-model change, not a one-line patch, and is flagged here rather than quietly left undocumented.

## Files changed this round

- `hourglass_pipeline/src/debater.py` — core fixes described above
- `hourglass_pipeline/tests/redteam_debater.py` — the 5-attack harness (new)
- `hourglass_pipeline/output/redteam_debater_findings.json` — machine-readable findings from the final (post-fix) run
- `hourglass_pipeline/output/qc_result_*.json`, `pro_report_*.md`, `diy_report_*.md` — regenerated for both domains to reflect the 2 status changes above
- `hourglass_pipeline/web_tool/*.json` and `ridewire_diagnostic_tool/*.json` — regenerated web data
- `ridewire_diagnostic_tool/index.html`, `app.js` — copy corrected to describe the real tiered threshold (3+/5+) instead of a flat "3+"
