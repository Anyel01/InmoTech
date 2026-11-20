Set-Location $PSScriptRoot

Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "No se encontró el entorno virtual .venv" -ForegroundColor Red
    exit 1
}

& ".venv\Scripts\Activate.ps1"

python run.py