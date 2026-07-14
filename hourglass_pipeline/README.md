# Hourglass Diagnostic Pipeline — v1 Pilot (Real, Working)

This is a real, running implementation of the Gather → Debate → Teach loop
described in the RideWire AI Hub planning sessions, scoped down to something
that actually works end to end today, with real data and real verification
logic — no simulated `asyncio.sleep()` stand-ins, no `return True` fake QC.

## What's real right now

- **`data/claims_harley_charging_system.json`** — 10 diagnostic claims about
  Harley-Davidson charging systems (battery / stator / voltage regulator),
  gathered from 16 independent live web sources (HD Forums threads spanning
  2008–2023, repair-shop guides, YouTube teardown videos, Reddit). Every
  claim carries its real source URLs — check them yourself.
- **`src/gatherer.py`** ("The Learner") — loads and schema-validates claim
  files. Rejects any claim with zero real source URLs. Includes an honestly
  unimplemented `LiveGatherer.fetch()` stub for wiring in a real search API
  later, rather than faking live gathering.
- **`src/debater.py`** ("The Devil's QC") — the actual verification bottleneck.
  A claim only becomes `VERIFIED` if it's corroborated by **3+ independent
  domains** (5+ for safety-tagged claims). Citing the same domain four times
  does not count as four sources — this is enforced in code, not asserted.
- **`src/teacher.py`** — renders two real output tiers (PRO technical /
  DIY roadside) from only the verified claims. Unverified claims never reach
  either report.
- **`src/orchestrator.py`** — runs the full pipeline and writes results to
  `output/`, including which claims did **not** clear QC and why.

## Actual results from the first real run

```
Gathered 10 claims.
Devil's QC: 7 VERIFIED, 3 NEEDS_MORE_SOURCES.
  - F6_STATOR_GROUND_TEST: only 2 independent domains (needs 1 more)
  - F7_REGULATOR_BLEED_BACK_TEST: only 2 independent domains (needs 1 more)
  - F10_GROUND_MIMICS_FAILURE: only 2 independent domains (needs 1 more)
```

That 7-out-of-10 pass rate is the point: the QC step is a real filter, not
theater. The 3 pending claims are still true (they match everything else
in the field) but haven't cleared the corroboration bar yet, so they are
correctly withheld from the PRO/DIY reports until more sources back them.

## How "Each One Teach One" actually works here (bounded, not an infinite swarm)

The early planning talked about agents "recruiting" arbitrary open-source
models indefinitely — that's not something that can be safely or honestly
built. What *is* real and useful from that idea:

1. Pick a new domain (a different Harley model line, a different
   manufacturer, a different vehicle system — motorcycle, car, big rig,
   tractor, off-road).
2. Research it for real (live search, service manuals, forums) and write a
   new `data/claims_<domain>.json` file in the exact schema used here, with
   real source URLs.
3. Drop it in `data/` and re-run `python src/orchestrator.py` — it picks up
   every domain file automatically and runs each one through the same
   Devil's QC bar.
4. Only verified claims get taught out into PRO/DIY reports. That's the
   propagation loop, made auditable instead of magical.

## What this is NOT (yet)

- Not AR. Not a 3D twin. Not a game engine. Those are a separate, large
  build (see the AR/WebXR device-compatibility notes from the prior
  message — Android/Chrome and Meta Quest are viable targets today, iOS
  Safari needs a fallback). This pipeline is the **data/verification
  backbone** those layers would eventually consume — building that backbone
  correctly first is what makes the flashy layers trustworthy later.
- Not NIST-audited. No self-declared compliance claim is made anywhere in
  this codebase. An actual NIST-alignment claim requires an external audit
  against a specific NIST framework (e.g. NIST 800-53 for the software
  security side) — that's a real, separate engagement, not something code
  can assert about itself.
- Not full Harley coverage (205 models). This is one system (charging) on
  one pilot domain, proving the loop works with real data before scaling
  breadth.

## Next concrete step

Pick the next domain to research for real (e.g. Harley ignition/starting
system, or a different make entirely) and I'll run the same Gather → Debate
→ Teach loop on it.
