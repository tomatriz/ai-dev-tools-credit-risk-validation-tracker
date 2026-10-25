$ErrorActionPreference = "Stop"
$token = if ($env:OPS_TOKEN) { $env:OPS_TOKEN } else { "local-demo-token" }
$headers = @{ "X-Ops-Token" = $token }
$sample = Join-Path $PSScriptRoot "..\sample-data\valid_portfolio.csv"

Write-Host "1. Enabling the reversible validation failure switch"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/ops/incident/enable" -Headers $headers | ConvertTo-Json

Write-Host "2. Sending a real user validation request that must fail"
try {
  Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/validations" -Form @{ file = Get-Item $sample }
  throw "Expected the incident request to fail"
} catch {
  Write-Host "Observed expected user-impact failure: $($_.Exception.Message)"
}

Write-Host "3. Waiting up to 30 seconds for Prometheus -> Alertmanager -> responder"
$verified = $false
for ($attempt = 0; $attempt -lt 15; $attempt++) {
  Start-Sleep -Seconds 2
  $latest = Invoke-RestMethod -Uri "http://localhost:8090/api/v1/remediations/latest"
  if ($latest -and $latest.verified) {
    $verified = $true
    $latest | ConvertTo-Json
    break
  }
}
if (-not $verified) { throw "Responder did not verify recovery within 30 seconds" }

Write-Host "4. Re-running the original validation after remediation"
$recovered = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/validations" -Form @{ file = Get-Item $sample }
$recovered | ConvertTo-Json -Depth 5
Write-Host "INCIDENT_DEMO_OK"

