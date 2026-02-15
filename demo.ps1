param(
    [Parameter(Mandatory = $true)]
    [string]$Baseline,
    [Parameter(Mandatory = $true)]
    [string]$Revised,
    [string]$OutputDir = "artifacts",
    [switch]$UseLLM
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -Path $Baseline)) {
    throw "Baseline file not found: $Baseline"
}
if (-not (Test-Path -Path $Revised)) {
    throw "Revised file not found: $Revised"
}

New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null

$llmFlag = if ($UseLLM) { "--use-llm" } else { "--no-llm" }

Write-Host "RealityCheck CLI demo starting..." -ForegroundColor Cyan
Write-Host "Baseline: $Baseline"
Write-Host "Revised:  $Revised"
Write-Host "Output:   $OutputDir" -ForegroundColor DarkGray

Write-Host "`nStep 1: Analyze baseline contract" -ForegroundColor Yellow
python -m realitycheck_cli analyze $Baseline --json-output "$OutputDir\baseline.analysis.json" $llmFlag

Write-Host "`nStep 2: Analyze revised contract" -ForegroundColor Yellow
python -m realitycheck_cli analyze $Revised --json-output "$OutputDir\revised.analysis.json" $llmFlag

Write-Host "`nStep 3: Compare contracts" -ForegroundColor Yellow
python -m realitycheck_cli compare $Baseline $Revised --json-output "$OutputDir\baseline_vs_revised.comparison.json" $llmFlag

Write-Host "`nDemo complete. JSON artifacts saved to $OutputDir." -ForegroundColor Green
