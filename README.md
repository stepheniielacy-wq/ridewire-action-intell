# RideWire

RideWire is Stephenie Lacy's AI-assisted vehicle diagnostics project, based in
Albuquerque, NM. This repo holds the real, working parts of it — not a pitch deck.

## What's actually built and proven (start here)

**Motorcycle job aids** — `/job_aids/motorcycle/`
Four real Harley-Davidson diagnostic codes (P0562, P0131, P0371/P0372/P0374,
C1032/C1034), each researched from manufacturer bulletins and independent
technician/owner forums, run through three independent AI models (Claude, GPT,
Gemini) with a disclosed keyword-overlap agreement check, and assembled into a
source-cited shop job-aid PDF with a generic reference schematic. Store listing
copy for these is in `job_aids/motorcycle/GUMROAD_LISTINGS.md`.

**Diagnostic pipeline scripts** — `/scripts/diagnostics/`
- `diagnose.py` — a real 469-code OBD-II lookup database
- `multi_ai_consensus.py` / `multi_ai_consensus_moto.py` — the 3-model consensus engine
- `build_moto_diagrams.py`, `build_moto_job_aids.py` — the PDF assembly pipeline

Every claim in these outputs is either sourced (with a URL) or explicitly labeled as a
disclosed methodology limitation. No manufactured accuracy percentages, no fictional
hardware, no invented compliance certifications.

## What's real about the business (also no hype)

- RIDE WIRE LLC, registered in Albuquerque, NM
- $0 current revenue; a documented pipeline of projected/unclosed leads — not cash in hand
- 420 mechanic survey responses (location of the raw data still needs to be confirmed)
- The 4 motorcycle job aids above, ready to list for sale

## What is NOT built yet

- Full DTC code coverage across motorcycle brands (only 4 Harley-Davidson codes exist)
- Any other industry (John Deere / farm equipment is the next target, not started)
- Any hardware product, field-service crew, AR overlay, or satellite/aerospace product
- A live storefront — listing copy exists, no store account has been created yet

## Repo housekeeping note

`/archive/pre-2026-09-audit/` holds ~65 older strategy/pitch files that predate this
README and made claims (e.g. "production-ready," "launch-ready SaaS") that were not
true at the time they were written. They're kept for history only — do not treat
anything in that folder as current or verified. Several other directories in this repo
(`campaigns/`, `frontend/`, `indian-motorcycle-partnership/`, etc.) also predate this
audit and have not yet been individually verified — treat them the same way until
checked.

## Working principle for everything added going forward

If a number, capability, or claim isn't backed by a real source URL, real working code,
or a real test result sitting next to it in this repo, it doesn't go in — draft it as a
clearly-labeled proposal instead.
