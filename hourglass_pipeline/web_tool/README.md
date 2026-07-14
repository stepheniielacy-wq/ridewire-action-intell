# Hourglass Diagnostic Lookup — Web Tool (v1)

A static, no-build web page that renders the verified output of the Hourglass pipeline
(`../output/qc_result_*.json`) as a searchable diagnostic lookup tool, in two modes:

- **Pro** — every verified claim with category, confidence, independent-domain count, and full citation list. Pending/unverified claims are shown separately and clearly labeled — never mixed in with verified ones.
- **DIY** — the same verified data, reformatted as a plain-English, ordered roadside walkthrough (battery → stator → regulator).

## Why this exists
The pipeline was producing good verified JSON/Markdown, but nobody could actually use it without opening a repo and reading raw files. This turns it into something a mechanic could open on a phone and search. It is a direct, honest slice of the original "package it for pros first, get real feedback" plan — nothing more.

## What it is NOT
No AR, no 3D twin, no game layer, no AI-generated summarization. It reads the pipeline's own JSON output directly and renders it. If the data is wrong, the page shows the same wrong data — there is no smoothing-over layer.

## Files
- `index.html` / `style.css` / `app.js` — the page.
- `qc_data.json` — copy of the pipeline's QC output for the Harley charging-system pilot (`verified` + `rejected_or_pending`).
- `diy_data.json` — the DIY report's ordered steps, parsed out of `../output/diy_report_*.md`.

## Regenerating the data files after a new pipeline run
```bash
cp ../output/qc_result_<domain>.json qc_data.json
# and re-run the markdown parser used to build diy_data.json if the DIY report changed
```

## Running locally
No build step. Open `index.html` in a browser, or serve the folder with any static file server (`python3 -m http.server`) since `fetch()` needs http(s), not `file://`.
