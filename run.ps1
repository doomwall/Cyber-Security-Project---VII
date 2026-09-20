# Start the development server from a clean database (Windows PowerShell).
#
# The database is deleted and rebuilt on every start. That matters for the
# cryptography flaw: passwords are hashed with whichever algorithm is active
# in settings.py at the moment they are written, so toggling a flaw on or off
# and restarting with this script always leaves the stored data consistent
# with the code. Without the reset, old password hashes would be unreadable
# by the newly selected hasher and nobody could log in.
#
# Usage:
#   .\run.ps1                reset the database, seed it, run the server
#   .\run.ps1 -Keep          keep the existing database (no reset, no seed)
#   .\run.ps1 8080           run on a different port

param(
    [switch]$Keep,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ServerArgs
)

$ErrorActionPreference = 'Stop'

Set-Location (Join-Path $PSScriptRoot 'cyberproject')

$py = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

if (-not $Keep) {
    Write-Host '==> Removing old database'
    Remove-Item -Force -ErrorAction SilentlyContinue db.sqlite3

    Write-Host '==> Creating tables'
    & $py manage.py migrate --no-input

    Write-Host '==> Seeding demo users and notes'
    & $py manage.py seed
} else {
    Write-Host '==> Keeping existing database (-Keep)'
}

Write-Host '==> Active password hasher:'
& $py manage.py shell --no-imports -c "from django.conf import settings; print('    ' + settings.PASSWORD_HASHERS[0])"

Write-Host '==> Starting server on http://127.0.0.1:8000/  (Ctrl+C to stop)'
& $py manage.py runserver @ServerArgs
