#!/usr/bin/env bash
#
# Start the development server from a clean database.
#
# The database is deleted and rebuilt on every start. That matters for the
# cryptography flaw: passwords are hashed with whichever algorithm is active
# in settings.py at the moment they are written, so toggling a flaw on or off
# and restarting with this script always leaves the stored data consistent
# with the code. Without the reset, old password hashes would be unreadable
# by the newly selected hasher and nobody could log in.
#
# Usage:
#   ./run.sh                 reset the database, seed it, run the server
#   ./run.sh --keep          keep the existing database (no reset, no seed)
#   ./run.sh 8080            run on a different port
#
set -euo pipefail

cd "$(dirname "$0")/cyberproject"

PY="${PYTHON:-python3}"
command -v "$PY" >/dev/null 2>&1 || PY=python

RESET=1
ARGS=()
for arg in "$@"; do
    case "$arg" in
        --keep) RESET=0 ;;
        *) ARGS+=("$arg") ;;
    esac
done

if [ "$RESET" -eq 1 ]; then
    echo "==> Removing old database"
    rm -f db.sqlite3

    echo "==> Creating tables"
    "$PY" manage.py migrate --no-input

    echo "==> Seeding demo users and notes"
    "$PY" manage.py seed
else
    echo "==> Keeping existing database (--keep)"
fi

echo "==> Active password hasher:"
"$PY" manage.py shell --no-imports -c "from django.conf import settings; print('    ' + settings.PASSWORD_HASHERS[0])"

echo "==> Starting server on http://127.0.0.1:8000/  (Ctrl+C to stop)"
exec "$PY" manage.py runserver ${ARGS[@]+"${ARGS[@]}"}
