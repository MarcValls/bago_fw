#!/usr/bin/env pwsh
# BAGO Bootstrap — Arranque Fiable
# Detecta raíz, Python, Git, dependencias y arranca siempre igual

$ErrorActionPreference = 'Stop'

Write-Host "=== BAGO Bootstrap v4.0.0 ===" -ForegroundColor Cyan

# 1. Detectar raíz de BAGO
function Find-BagoRoot {
    $scriptPath = $MyInvocation.MyCommand.Path
    if (-not $scriptPath) {
        # Si no hay path, usar directorio actual
        return (Get-Location).Path
    }
    $current = Split-Path $scriptPath -Parent
    
    # Subir hasta encontrar .bago o bago_fw
    while ($current -ne (Split-Path $current -Parent)) {
        if ((Test-Path (Join-Path $current '.bago')) -or (Split-Path $current -Leaf -eq 'bago_fw')) {
            return $current
        }
        $current = Split-Path $current -Parent
    }
    
    # Fallback: directorio del script
    return Split-Path $scriptPath -Parent
}

$BAGO_ROOT = Find-BagoRoot
Write-Host "Raíz detectada: $BAGO_ROOT" -ForegroundColor Green
Set-Location $BAGO_ROOT

# 2. Detectar Python
Write-Host "`nVerificando Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Python: $pythonVersion" -ForegroundColor Green
    
    # Verificar versión mínima (3.10)
    $versionInfo = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $major, $minor = $versionInfo.Split('.')
    if ([int]$major -lt 3 -or ([int]$major -eq 3 -and [int]$minor -lt 10)) {
        Write-Host "  ERROR: Se requiere Python 3.10+ (encontrado: $versionInfo)" -ForegroundColor Red
        exit 1
    }
    Write-Host "  Versión OK (3.10+)" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python no encontrado" -ForegroundColor Red
    exit 1
}

# 3. Detectar Git (opcional)
Write-Host "`nVerificando Git..." -ForegroundColor Cyan
try {
    $gitVersion = git --version 2>&1
    Write-Host "  $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  Git no encontrado (opcional, continuando)" -ForegroundColor Yellow
}

# 4. Verificar estructura esencial
Write-Host "`nVerificando estructura..." -ForegroundColor Cyan
$requiredPaths = @(
    '.bago\core\cli.py',
    '.bago\config\config.json'
)

$allPresent = $true
foreach ($path in $requiredPaths) {
    $fullPath = Join-Path $BAGO_ROOT $path
    if (Test-Path $fullPath) {
        Write-Host "  [OK] $path" -ForegroundColor Green
    } else {
        Write-Host "  [FALTA] $path" -ForegroundColor Red
        $allPresent = $false
    }
}

if (-not $allPresent) {
    Write-Host "`nERROR: Estructura incompleta" -ForegroundColor Red
    exit 1
}

# 5. Verificar dependencias (si hay requirements.txt)
$requirementsPath = Join-Path $BAGO_ROOT 'requirements.txt'
if (Test-Path $requirementsPath) {
    Write-Host "`nVerificando dependencias..." -ForegroundColor Cyan
    try {
        python -c "import sys; sys.path.insert(0, '.'); import requirements" 2>$null
        Write-Host "  Dependencias: OK" -ForegroundColor Green
    } catch {
        Write-Host "  Instalando dependencias..." -ForegroundColor Yellow
        pip install -r $requirementsPath --quiet
        Write-Host "  Dependencias instaladas" -ForegroundColor Green
    }
}

# 6. Arrancar BAGO
Write-Host "`n=== Arrancando BAGO ===" -ForegroundColor Cyan
$cliPath = Join-Path $BAGO_ROOT '.bago\core\cli.py'

if ($args.Count -gt 0) {
    & python $cliPath @args
} else {
    Write-Host "`nUso: .\bootstrap.ps1 <comando> [args]" -ForegroundColor Yellow
    Write-Host "Comandos: start, status, nodes, connect, disconnect, exec, evidence, session, stop" -ForegroundColor Yellow
    Write-Host "`nEjemplo: .\bootstrap.ps1 start" -ForegroundColor Yellow
}

Write-Host "`n=== Bootstrap completado ===" -ForegroundColor Green
