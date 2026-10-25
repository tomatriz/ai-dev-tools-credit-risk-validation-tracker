$ErrorActionPreference = "Stop"

$previousPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = (Resolve-Path (Join-Path $PSScriptRoot "..\backend")).Path
python -m pytest backend/tests
if ($LASTEXITCODE -ne 0) { throw "Backend tests failed" }

$env:PYTHONPATH = (Resolve-Path (Join-Path $PSScriptRoot "..\oncall")).Path
python -m pytest oncall/tests
if ($LASTEXITCODE -ne 0) { throw "On-call tests failed" }

npm --prefix frontend ci
if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed" }
npm --prefix frontend test -- --run
if ($LASTEXITCODE -ne 0) { throw "Frontend tests failed" }
npm --prefix frontend run build
if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }

$env:PYTHONPATH = $previousPythonPath

Write-Host "All unit, integration, and frontend checks passed."

