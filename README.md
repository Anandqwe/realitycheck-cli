# ⚖️ RealityCheck CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Turn legal contracts into decision-grade risk intelligence — not summaries.**

RealityCheck CLI parses PDF agreements, classifies clause risk across 7 legal categories, detects power imbalance and ambiguity, and generates negotiation-ready outputs — all from your terminal.

> 🆕 **New here?** Jump straight to [`START_HERE.md`](START_HERE.md) for a 5-minute beginner walkthrough with sample PDFs.

---

## 🎯 Why It Matters

Most people sign contracts they can't fully parse. You skim 8 pages of dense legal text, worry about a clause or two, and sign anyway.

The gap between *"I read it"* and *"I understand the risk"* is where people get burned — unlimited liability, one-sided termination rights, overbroad IP assignments, missing payment protections.

**RealityCheck CLI makes the risk explicit, structured, and actionable before you sign.**

---

## ✨ Features

### 📄 PDF Parsing & Clause Extraction
- Text extraction via **pdfplumber** with automatic header/footer removal
- Smart clause segmentation by heading detection (numbered sections, ALL-CAPS headings)
- Page-anchored clauses so you can find them in the original document

### 🔍 Risk Analysis Engine
- **7 clause categories**: Non-Compete, IP Transfer, Liability, Termination, Financial Risk, Privacy, Neutral
- **4 risk levels**: Low, Medium, High, Critical
- Regex-driven heuristic classification — works fully offline, no API key needed
- Optional **Google Gemini LLM enrichment** for deeper analysis (signals merged with heuristics, never replaces them)

### 📊 Five Quantified Risk Metrics
| Metric | Range | What It Tells You |
|--------|-------|-------------------|
| **Overall Risk Score** | 1–100 | Weighted category average + penalties for vagueness and missing protections |
| **Power Imbalance** | 0–100 | How one-sided the obligations are (unilateral rights, asymmetric terms) |
| **Ambiguity Index** | 0–100 | Density of vague language ("sole discretion", "without notice", "as deemed necessary") |
| **Protection Coverage** | 0–100 | How many critical protections are present vs. missing |
| **Leverage Index™** | 0–100 | Your negotiation strength before signing (composite of all metrics) |

### 🚨 Signal Detection
- **Vague Language** — flags terms like "sole discretion", "at any time", "without cause"
- **One-Sided Rights** — detects unilateral obligations and asymmetric terms
- **Liability Expansion** — catches unlimited damages exposure or broad indemnification
- **Missing Protections** — scans for 6 critical protections:
  - Payment timeline
  - Termination notice period
  - Cure period (right to fix before termination)
  - Liability cap
  - Breach notification window
  - IP retention rights

### 📝 Negotiation-Ready Outputs
- **Auto-generated email drafts** — lists top-risk clauses with specific rewrite suggestions, ready to send
- **Clause rewrite suggestions** — category-specific rewrites (e.g., "narrow IP assignment to deliverables only")
- **Negotiation points** — contextual talking points based on detected signals

### 🔄 Contract Comparison
- **Smart clause matching** — 70% title similarity + 30% text similarity with 0.55 threshold
- **Delta analysis** — ADDED, REMOVED, MODIFIED, or UNCHANGED per clause
- **Domain-specific flags**:
  - `NEW_RISK` — new high-risk clause or risk increase ≥20 points
  - `EXPANDED_LIABILITY` — new liability expansion language detected
  - `EXTENDED_NON_COMPETE` — non-compete duration increase (parses days/months/years)

### 🖥️ Premium Terminal Output
- Color-coded Rich panels and tables (🔴 ≥80, 🟡 ≥60, 🟢 <60)
- Score cards, category breakdowns, leverage drivers, clause tables
- Negotiation email preview rendered in-terminal
- Full JSON artifact export for downstream workflows

---

## 🏗️ Architecture

```
PDF → [ingest] → [clauses] → [analysis] → [scoring] → [negotiation] → [output]
                                  ↕                                        ↕
                              [llm_client]                          [comparison]
```

### Project Structure

```
realitycheck_cli/
├── cli/              # Typer CLI app with analyze & compare commands
├── ingest/           # PDF extraction (pdfplumber) + header/footer removal
├── clauses/          # Clause segmentation + text normalization
├── analysis/         # Heuristic classifier + optional Gemini LLM enrichment
├── scoring/          # Weighted risk engine, power imbalance, leverage index
├── negotiation/      # Email drafts + clause rewrite suggestions
├── comparison/       # Smart clause matching + delta analysis + risk flags
├── output/           # Rich terminal rendering + JSON serialization
├── config/           # Environment-based settings
└── pipeline.py       # Orchestration layer wiring all modules together
```

### Design Decisions

- **Heuristic-first, LLM-optional** — Works fully offline with regex patterns. No API key needed. LLM only enriches, never replaces.
- **Weighted multi-factor scoring** — Not a single naive score. 5 complementary metrics with category-specific weights (Liability: 0.22, Financial Risk: 0.20, IP Transfer: 0.17, Non-Compete: 0.15, Termination: 0.12, Privacy: 0.09).
- **Pydantic schemas everywhere** — Type-safe, validated, serializable data models throughout.
- **Actionable by default** — Doesn't just flag risk. Generates email drafts and clause rewrites you can actually send.

---

## 📋 Requirements

- **Python 3.10+** recommended
- **Windows PowerShell** for the demo script (CLI works on any OS)

---

## 🚀 Installation

```powershell
git clone https://github.com/Anandqwe/realitycheck-cli.git
cd realitycheck-cli
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## ⚡ Quick Start

The repo includes sample PDFs at the root — `contract.pdf`, `baseline.pdf`, and `revised.pdf`. No setup beyond install needed.

```powershell
# Analyze a contract
python -m realitycheck_cli analyze .\contract.pdf

# Compare two contract versions
python -m realitycheck_cli compare .\baseline.pdf .\revised.pdf

# Export JSON artifacts
python -m realitycheck_cli analyze .\contract.pdf --json-output .\artifacts\contract.analysis.json
```

> 📘 For a complete beginner walkthrough with step-by-step instructions and tips on finding more PDFs to practice with, see [`START_HERE.md`](START_HERE.md).

---

## 🔧 Configuration

### Environment Variables (LLM is optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Required only when using `--use-llm` |
| `REALITYCHECK_GEMINI_MODEL` | `gemini-3-flash-preview` | Gemini model to use |
| `REALITYCHECK_HIGH_RISK_THRESHOLD` | `70` | Score threshold for high-risk classification |
| `REALITYCHECK_LLM_TIMEOUT` | `45` | LLM request timeout in seconds |

```powershell
$env:GEMINI_API_KEY = "your-key"
$env:REALITYCHECK_GEMINI_MODEL = "gemini-3-flash-preview"
$env:REALITYCHECK_HIGH_RISK_THRESHOLD = "70"
$env:REALITYCHECK_LLM_TIMEOUT = "45"
```

---

## 📖 Command Reference

### `analyze` — Analyze a Single Contract

```powershell
python -m realitycheck_cli analyze <pdf-path> [options]
```

| Option | Description |
|--------|-------------|
| `--json-output, -j` | Path to save JSON output file |
| `--use-llm` | Enable Gemini-based LLM enrichment |
| `--no-llm` | Disable LLM (default) |

**Examples:**
```powershell
python -m realitycheck_cli analyze .\contract.pdf
python -m realitycheck_cli analyze .\contract.pdf --json-output .\artifacts\contract.analysis.json
python -m realitycheck_cli analyze .\contract.pdf --use-llm
```

### `compare` — Compare Two Contract Versions

```powershell
python -m realitycheck_cli compare <baseline-pdf> <revised-pdf> [options]
```

| Option | Description |
|--------|-------------|
| `--json-output, -j` | Path to save JSON comparison output |
| `--use-llm` | Enable Gemini-based LLM enrichment |
| `--no-llm` | Disable LLM (default) |

**Examples:**
```powershell
python -m realitycheck_cli compare .\baseline.pdf .\revised.pdf
python -m realitycheck_cli compare .\baseline.pdf .\revised.pdf --json-output .\artifacts\comparison.json
python -m realitycheck_cli compare .\baseline.pdf .\revised.pdf --use-llm
```

### `demo.ps1` — Full Pipeline Demo Script

Runs analyze on both contracts, then compares them — all in one command.

```powershell
.\demo.ps1 -Baseline .\baseline.pdf -Revised .\revised.pdf
.\demo.ps1 -Baseline .\baseline.pdf -Revised .\revised.pdf -UseLLM
```

---

## 🖥️ Sample Output

### Analysis Output (`contract.pdf` — 19 clauses)

```
╭──────────────────────────── Analysis ────────────────────────────╮
│ RealityCheck CLI                                                 │
│ Contract: contract.pdf                                           │
│ Clauses analyzed: 19                                             │
╰──────────────────────────────────────────────────────────────────╯
╭─ Overall Risk Score ─╮ ╭─ Power Imbalance Score ─╮ ╭─ Leverage Index (TM) ─╮
│        40/100        │ │         41/100          │ │        54/100         │
╰──────────────────────╯ ╰─────────────────────────╯ ╰───────────────────────╯

              Category Risk Summary
┏━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Category       ┃ Score ┃ Weight ┃ Contribution ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━┩
│ IP_TRANSFER    │    57 │   0.17 │         9.69 │
│ TERMINATION    │    55 │   0.12 │         6.60 │
│ PRIVACY        │    52 │   0.09 │         4.68 │
│ NEUTRAL        │    36 │   0.05 │         1.80 │
└────────────────┴───────┴────────┴──────────────┘

╭──────────────── Missing Protections ─────────────────╮
│ - payment timeline                                    │
│ - cure period                                         │
│ - liability cap                                       │
│ - breach notification window                          │
│ - ip retained                                         │
╰──────────────────────────────────────────────────────╯

╭──────────── Negotiation Draft (Preview) ─────────────╮
│ Subject: Proposed revisions for contract              │
│                                                       │
│ Priority clauses to discuss:                          │
│ - Assignment (Transfer Of Contract Of Employment)     │
│   (C-008, risk 57/100): Narrow IP assignment to       │
│   deliverables created under this agreement.          │
│ - Probation (C-003, risk 55/100): Require written     │
│   notice and a cure period before termination.        │
│                                                       │
│ Additional protections requested:                     │
│ - Add explicit language for: payment timeline         │
│ - Add explicit language for: liability cap            │
│ - Add explicit language for: breach notification      │
╰──────────────────────────────────────────────────────╯
```

### Comparison Output

```
╭─────────────────── Comparison ───────────────────────╮
│ Baseline: baseline.pdf                                │
│ Revised: revised.pdf                                  │
╰──────────────────────────────────────────────────────╯
╭─ Baseline Risk ─╮ ╭─ Revised Risk ─╮ ╭─ Risk Delta ─╮
│       17        │ │       17       │ │      +0      │
╰─────────────────╯ ╰────────────────╯ ╰──────────────╯
╭─ Baseline Leverage ─╮ ╭─ Revised Leverage ─╮ ╭─ Leverage Delta ─╮
│         60          │ │         60         │ │        +0        │
╰─────────────────────╯ ╰────────────────────╯ ╰──────────────────╯
```

---

## 📦 Output Artifacts

JSON output defaults to `artifacts/` unless `--json-output` is provided. Each artifact includes:

- **Clause-level data** — category, risk score, risk level, benefits party, signals, rewrite suggestion, negotiation points
- **Summary metrics** — all 5 scores, category breakdowns, weighted contributions, missing protections
- **Negotiation email** — full draft ready to send
- **Comparison results** (when using `compare`) — per-clause deltas, risk flags, overall risk/leverage deltas

### JSON Structure (summary)

```json
{
  "contract_id": "contract",
  "source_path": "contract.pdf",
  "clauses": [ ... ],
  "summary": {
    "overall_risk_score": 40,
    "power_imbalance_score": 41,
    "ambiguity_index": 5,
    "protection_coverage_score": 15,
    "leverage_index": 54,
    "category_scores": { ... },
    "weighted_contributions": { ... },
    "high_risk_clause_ids": [],
    "missing_protections": [
      "payment_timeline",
      "cure_period",
      "liability_cap",
      "breach_notification_window",
      "ip_retained"
    ]
  },
  "negotiation_email": "Subject: Proposed revisions for contract..."
}
```

---

## 🧪 Demo Flow (Recommended)

1. **Analyze** the baseline contract to get risk scores and missing protections
2. **Review** the high-risk clause table and negotiation draft preview
3. **Re-run** with `--use-llm` to enrich classifications with structured LLM signals
4. **Export** JSON output for downstream workflows
5. **Compare** baseline vs revised drafts with `compare`
6. **Share** the negotiation email draft for redline discussions

---

## 🔬 Sample Walkthrough (Illustrative)

**Scenario:** 8-page consulting agreement between a client and contractor.

| Metric | Score | Interpretation |
|--------|-------|----------------|
| Overall Risk | **78/100** | High risk — review before signing |
| Power Imbalance | **72/100** | Heavily favors one party |
| Leverage Index | **38/100** | Weak negotiation position |

**High-Risk Clauses Detected:**
- 🔴 **Liability** — unlimited damages exposure
- 🔴 **Termination** — termination without notice
- 🔴 **IP Transfer** — broad assignment of all work product

**Missing Protections:**
- ❌ Payment timeline
- ❌ Liability cap
- ❌ Breach notification window

**Negotiation Outcomes:**
- ✉️ Email draft requests payment terms and a liability cap
- ✏️ Rewrite suggestions narrow IP assignment to deliverables only
- 🔄 Comparison flags reveal extended non-compete duration in revised draft

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| `No text extracted from PDF` | The PDF is likely scanned. Use a text-based PDF or OCR the document first |
| `GEMINI_API_KEY missing` | Only required when running with `--use-llm`. Core analysis works without it |
| `Slow responses` | Lower the contract size or run without `--use-llm` |
| `ModuleNotFoundError` | Ensure the venv is activated and `pip install -r requirements.txt` completed |

---

## 🧪 Tests

```powershell
python -m unittest discover -s tests
```

Tests cover the heuristic engine, scoring calculations, LLM client mocking, and comparison logic.

---

## 📰 Featured Article

📖 **[RealityCheck CLI — Turn Legal Contracts into Decision-Grade Risk Intelligence](https://dev.to/challenges/github-2026-01-21)**

Read the full story on Dev.to: architecture overview, live demos with real terminal output, comparison features, and how GitHub Copilot CLI accelerated the build.

---

## ⚠️ Disclaimer

This tool provides automated analysis and is **not legal advice**. Always consult a qualified legal professional for contract decisions.
