param(
    [int]$BackendPort = 8888,
    [int]$FrontendPort = 3000,
    [int]$ReflexBackendPort = 8010
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "Backend"
$frontendDir = Join-Path $root "internship_portal"

if (-not (Test-Path $backendDir)) {
    throw "Backend directory not found: $backendDir"
}
if (-not (Test-Path $frontendDir)) {
    throw "Frontend directory not found: $frontendDir"
}

Write-Host "Starting Internship Portal dev environment..." -ForegroundColor Cyan
Write-Host "Backend directory:  $backendDir"
Write-Host "Frontend directory: $frontendDir"

$backendCmd = "Set-Location -LiteralPath '$backendDir'; python -m uvicorn app:app --host 127.0.0.1 --port $BackendPort"
$reflexCmd = "Set-Location -LiteralPath '$frontendDir'; reflex run --frontend-port $FrontendPort --backend-port $ReflexBackendPort"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd | Out-Null
Start-Process powershell -ArgumentList "-NoExit", "-Command", $reflexCmd | Out-Null

Write-Host ""
Write-Host "Dev servers launched in two new PowerShell windows." -ForegroundColor Green
Write-Host "Frontend:       http://localhost:$FrontendPort"
Write-Host "Reflex Backend: http://127.0.0.1:$ReflexBackendPort"
Write-Host "FastAPI:        http://127.0.0.1:$BackendPort"
Write-Host "Health:         http://127.0.0.1:$BackendPort/health"
Write-Host ""
Write-Host "Tip: stop servers by closing those two spawned PowerShell windows."
