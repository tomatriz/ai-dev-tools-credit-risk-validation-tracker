$ErrorActionPreference = "Stop"
$token = if ($env:OPS_TOKEN) { $env:OPS_TOKEN } else { "local-demo-token" }
$headers = @{ "X-Ops-Token" = $token }
$sample = Join-Path $PSScriptRoot "..\sample-data\valid_portfolio.csv"
$backendPort = if ($env:CRVT_BACKEND_PORT) { $env:CRVT_BACKEND_PORT } else { "8000" }
$oncallPort = if ($env:CRVT_ONCALL_PORT) { $env:CRVT_ONCALL_PORT } else { "8090" }
$backendUrl = "http://localhost:$backendPort"
$oncallUrl = "http://localhost:$oncallPort"

Write-Host "1. Enabling the reversible validation failure switch"
$previousCompletion = $null
try {
  $previous = Invoke-RestMethod -Uri "$oncallUrl/api/v1/remediations/latest"
  if ($previous) { $previousCompletion = $previous.completed_at }
} catch {
  # A fresh responder legitimately has no prior result.
}
Invoke-RestMethod -Method Post -Uri "$backendUrl/api/v1/ops/incident/enable" -Headers $headers | ConvertTo-Json

Write-Host "2. Sending a real user validation request that must fail"
try {
  Invoke-RestMethod -Method Post -Uri "$backendUrl/api/v1/validations" -Form @{ file = Get-Item $sample }
  throw "Expected the incident request to fail"
} catch {
  Write-Host "Observed expected user-impact failure: $($_.Exception.Message)"
}

Write-Host "3. Waiting up to 30 seconds for Prometheus -> Alertmanager -> responder"
$verified = $false
for ($attempt = 0; $attempt -lt 15; $attempt++) {
  Start-Sleep -Seconds 2
  $latest = Invoke-RestMethod -Uri "$oncallUrl/api/v1/remediations/latest"
  if ($latest -and $latest.verified -and $latest.completed_at -ne $previousCompletion) {
    $verified = $true
    $latest | ConvertTo-Json
    break
  }
}
if (-not $verified) { throw "Responder did not verify recovery within 30 seconds" }

Write-Host "4. Re-running the original validation after remediation"
$recovered = Invoke-RestMethod -Method Post -Uri "$backendUrl/api/v1/validations" -Form @{ file = Get-Item $sample }
$recovered | ConvertTo-Json -Depth 5
Write-Host "INCIDENT_DEMO_OK"

