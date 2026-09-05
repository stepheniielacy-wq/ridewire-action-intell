# RideWire Motorcycle Job Aids (real, source-cited)

Four real Harley-Davidson diagnostic trouble codes, researched from actual manufacturer
bulletins/manuals and owner/technical forums, then diagnosed by three independent AI
models (Claude Sonnet 5, GPT-5.6 Terra, Gemini 3.1 Pro) using a transparent
keyword-overlap "agreement" check. This is the same honest pipeline already proven on
the car code P0171 (see `../scripts/diagnostics/multi_ai_consensus.py`), extended to a
second industry: motorcycles/powersports.

## What's real here

- **Codes are real**, sourced from official Harley-Davidson TSBs, dealer diagnostic
  manuals, and NHTSA-hosted bulletins, cross-checked against independent owner/technician
  forum threads. Full source URLs and a confidence note are in each code's
  `consensus_report.json` and `job_aid.pdf`.
- **Consensus is real**: each of the 3 models was asked the same question independently;
  `raw_claude.json` / `raw_gpt.json` / `raw_gemini.json` are their verbatim answers.
  "Agreement" is literal keyword overlap on a single query - not a validated ML accuracy
  score, and it is explicitly labeled as such in every PDF.
- **Diagrams are generic reference schematics** (principle-level, matplotlib-generated) -
  NOT manufacturer-exact wiring diagrams. They teach how the circuit family works, not an
  as-built pinout for any specific model/year. Exact factory wiring diagrams require a
  licensed database (AllData, Mitchell1, or the OEM service manual), which this project
  does not have.

## What's NOT done yet

- This covers 4 codes on Harley-Davidson only. "100% of motorcycles" (all codes across
  Harley, Indian, Yamaha, Honda, etc.) is a large, multi-session research effort - this
  proves the pipeline works on a second industry, it is not full coverage.
- No John Deere / other industries yet - same pipeline, different research pass.

## Folder structure (per code)

```
<code>/job_aid.pdf         - the assembled, source-cited PDF job aid
<code>/schematic.png       - generic reference diagram
<code>/consensus_report.json - keyword-overlap agreement + all 3 raw model answers
<code>/raw_claude.json, raw_gpt.json, raw_gemini.json - each model's verbatim answer
```

Codes covered: `p0562` (charging system), `p0131` (front O2 sensor), `ckp` (crankshaft
position sensor, P0371/P0372/P0374), `abs` (wheel speed sensor circuit, C1032/C1034).

Underlying verified research: `moto_codes_verified.json` in this folder (copy of
`../scripts/diagnostics/moto_codes_verified.json`).
