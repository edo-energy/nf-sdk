<#
.SYNOPSIS
    NF Gateway Test Harness startup script (Windows)
.DESCRIPTION
    Builds and starts the test harness Docker Compose stack
.PARAMETER ConfigFile
    Building configuration YAML file (from configs/ directory). Default: default.yml
.PARAMETER Acceleration
    Time acceleration factor (1-20). Default: 1
.PARAMETER Profile
    Docker Compose profile to activate (e.g., "tailscale"). Optional.
#>
param(
    [string]$ConfigFile = "default.yml",
    [int]$Acceleration = 1,
    [string]$Profile = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NF Gateway Test Harness" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Config:       $ConfigFile"
Write-Host "  Acceleration: ${Acceleration}x"
Write-Host ""

# Validate config
if (-not (Test-Path "configs\$ConfigFile")) {
    Write-Host "ERROR: Config file configs\$ConfigFile not found." -ForegroundColor Red
    Write-Host "Available configs:"
    Get-ChildItem configs\*.yml | ForEach-Object { Write-Host "  $($_.Name)" }
    exit 1
}

# Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# Set env vars
$env:BUILDING_CONFIG_FILE = $ConfigFile
$env:TIME_ACCELERATION = $Acceleration

# Build
Write-Host "Building containers..."
$profileArgs = if ($Profile) { @("--profile", $Profile) } else { @() }
docker compose @profileArgs build

# Start
Write-Host ""
Write-Host "Starting services..."
docker compose @profileArgs up -d

# Wait for health
Write-Host ""
Write-Host "Waiting for services to become healthy..."

# Wait for simulator
Write-Host -NoNewline "  Simulator: "
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:8100/api/state" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "ready" -ForegroundColor Green
        $ready = $true
        break
    } catch { Start-Sleep 2 }
}
if (-not $ready) { Write-Host "TIMEOUT" -ForegroundColor Yellow }

# Wait for NF
Write-Host -NoNewline "  NF Gateway: "
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/platform" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "ready" -ForegroundColor Green
        $ready = $true
        break
    } catch { Start-Sleep 2 }
}
if (-not $ready) { Write-Host "TIMEOUT - check: docker compose logs nf" -ForegroundColor Yellow }

# Wait for time controller
Write-Host -NoNewline "  Time Controller: "
$ready = $false
for ($i = 0; $i -lt 15; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:8200/api/time" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "ready" -ForegroundColor Green
        $ready = $true
        break
    } catch { Start-Sleep 2 }
}
if (-not $ready) { Write-Host "TIMEOUT" -ForegroundColor Yellow }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Services Available:" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  NF Console:        " -NoNewline; Write-Host "http://localhost:8080" -ForegroundColor Green
Write-Host "  Config UI:         " -NoNewline; Write-Host "http://localhost:3001" -ForegroundColor Green
Write-Host "  Sim Dashboard:     " -NoNewline; Write-Host "http://localhost:3002" -ForegroundColor Green
Write-Host "  Simulation API:    " -NoNewline; Write-Host "http://localhost:8100" -ForegroundColor Green
Write-Host "  Time Controller:   " -NoNewline; Write-Host "http://localhost:8200" -ForegroundColor Green
Write-Host "  edo-service:       " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "  Acceleration: ${Acceleration}x"
Write-Host ""
Write-Host "To stop:  docker compose down"
Write-Host "To logs:  docker compose logs -f [service]"
Write-Host "============================================" -ForegroundColor Cyan
