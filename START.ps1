# Run from this project directory after the README installation steps.
$ErrorActionPreference = 'Stop'
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) { throw 'Create .venv and install requirements-lock.txt first. See README.md.' }
Push-Location $PSScriptRoot
try {
    & $projectPython manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
    & $projectPython manage.py collectstatic --noinput
    if ($LASTEXITCODE -ne 0) { throw 'Static collection failed.' }
    & $projectPython manage.py runserver 127.0.0.1:8000
} finally { Pop-Location }
