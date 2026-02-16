# Start Here: Try RealityCheck CLI with PDFs

If you're new, use this quick flow.

## 1) Setup (Windows PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Run with sample PDFs already in this repo
You already have test files in the project root:
- `baseline.pdf`
- `revised.pdf`

Single-file analysis:
```powershell
python -m realitycheck_cli analyze .\baseline.pdf
```

Compare two versions:
```powershell
python -m realitycheck_cli compare .\baseline.pdf .\revised.pdf
```

Save JSON output:
```powershell
python -m realitycheck_cli analyze .\baseline.pdf --json-output .\artifacts\baseline.analysis.json
```

## 3) Optional: Enable LLM mode
```powershell
$env:GEMINI_API_KEY = "your-key"
python -m realitycheck_cli analyze .\baseline.pdf --use-llm
```

## 4) Where to get more PDFs to practice
Use legal/document templates that are publicly available and safe to share:
- SEC EDGAR filings (real public contracts): https://www.sec.gov/edgar/search/
- OneNDA (free NDA templates): https://onenda.org/
- Docracy legal docs archive: https://www.docracy.com/
- LawInsider sample clauses/contracts: https://www.lawinsider.com/contracts
- Government procurement/contract portals in your country (public records)

Tip: Prefer text-based PDFs (not scanned images) for best extraction quality.

## 5) Common issue
- If output says no text extracted, the PDF is likely scanned. Try a text-based PDF or OCR first.
