# RealityCheck CLI

RealityCheck CLI turns legal contracts into decision-grade risk intelligence, not summaries.
It parses PDF agreements, classifies clause risk, detects power imbalance and ambiguity, and generates negotiation-ready outputs.

## Why it matters
Most people sign agreements they cannot fully parse. RealityCheck CLI makes the risk explicit, structured, and actionable before you sign.

## Features
- PDF parsing with **pdfplumber** and clause segmentation with page anchors.
- Clause classification + risk scoring (1-100) with power imbalance detection.
- Ambiguity detection (vague terms like "sole discretion" or "without notice").
- Missing protections detection (payment timeline, liability cap, etc.).
- Negotiation email drafts and clause rewrite suggestions.
- Contract comparison (new risks, expanded liability, extended non-compete).
- Leverage Index (TM) showing negotiation strength before signing.
- Premium **Rich** terminal output + JSON artifacts.

## Concepts (scores you will see)
- **Clause Severity (1-10)**: derived from clause risk score (risk/10).
- **Overall Risk Score (1-100)**: weighted category average plus penalties.
- **Power Imbalance (0-100)**: higher means more one-sided obligations.
- **Ambiguity Index (0-100)**: higher means more vague language.
- **Protection Coverage (0-100)**: higher means more missing protections covered.
- **Leverage Index (0-100)**: higher means stronger negotiation position.

## Requirements
- Python 3.10+ recommended.
- Windows PowerShell for the demo script.

## Installation
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Environment variables (LLM optional)
```powershell
$env:GEMINI_API_KEY = "your-key"
$env:REALITYCHECK_GEMINI_MODEL = "gemini-1.5-flash"
$env:REALITYCHECK_HIGH_RISK_THRESHOLD = "70"
$env:REALITYCHECK_LLM_TIMEOUT = "45"
```

## Command reference

### Analyze a single contract
```powershell
python -m realitycheck_cli analyze .\contract.pdf
python -m realitycheck_cli analyze .\contract.pdf --json-output .\artifacts\contract.analysis.json
python -m realitycheck_cli analyze .\contract.pdf --use-llm
```
Options:
- `--json-output, -j`: path to JSON output file.
- `--use-llm/--no-llm`: enable or disable Gemini-based classification.

### Compare two contract versions
```powershell
python -m realitycheck_cli compare .\baseline.pdf .\revised.pdf
python -m realitycheck_cli compare .\baseline.pdf .\revised.pdf --json-output .\artifacts\comparison.json
python -m realitycheck_cli compare .\baseline.pdf .\revised.pdf --use-llm
```
Options:
- `--json-output, -j`: path to JSON output file.
- `--use-llm/--no-llm`: enable or disable Gemini-based classification.

## Demo flow (recommended)
1. Run `analyze` on the baseline contract to get risk scores and missing protections.
2. Review the high-risk clause table and negotiation draft preview.
3. Re-run with `--use-llm` to enrich classifications with structured LLM signals.
4. Export JSON output for downstream workflows.
5. Compare baseline vs revised drafts with `compare`.
6. Share the negotiation email draft for redline discussions.

### Demo script
```powershell
.\demo.ps1 -Baseline .\baseline.pdf -Revised .\revised.pdf
.\demo.ps1 -Baseline .\baseline.pdf -Revised .\revised.pdf -UseLLM
```
Sample PDFs are included at the repo root: `baseline.pdf` and `revised.pdf`.

## Output artifacts
- JSON output defaults to `artifacts\` unless `--json-output` is provided.
- JSON includes clauses, per-clause signals, summary metrics, negotiation draft, and comparison results.

### JSON fields (summary)
```json
{
  "summary": {
    "overall_risk_score": 78,
    "power_imbalance_score": 72,
    "ambiguity_index": 40,
    "protection_coverage_score": 55,
    "leverage_index": 38
  }
}
```

## Sample contract walkthrough (illustrative)
Scenario: 8-page consulting agreement between a client and contractor.

**Observed output highlights**
- Overall Risk: **78/100** | Power Imbalance: **72/100**
- Leverage Index: **38/100** (weak negotiation position)
- High-risk clauses:
  - Liability: unlimited damages exposure
  - Termination: termination without notice
  - IP Transfer: broad assignment of all work product
- Missing protections:
  - payment timeline
  - liability cap
  - breach notification window

**Negotiation outcomes**
- Email draft requests payment terms and a liability cap.
- Rewrite suggestions narrow IP assignment to deliverables only.
- Comparison flags reveal extended non-compete duration in revised draft.

## Troubleshooting
- **No text extracted from PDF**: the PDF may be scanned; try OCR or use a text-based PDF.
- **`GEMINI_API_KEY` missing**: required only when running with `--use-llm`.
- **Slow responses**: lower the contract size or avoid `--use-llm`.

## Tests
```powershell
python -m unittest discover -s tests
```

## Disclaimer
This tool provides automated analysis and is not legal advice.
