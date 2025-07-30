#!/usr/bin/env bash
set -euo pipefail

# 1. Absoluten Pfad zum Projekt-Root ermitteln (eine Ebene über nc-macos-tests)
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"

# 2. Umgebungsvariablen aus .env für alle Scripts verfügbar machen
if [ -f "$BASE_DIR/.env" ]; then
  set -a
  . "$BASE_DIR/.env"
  set +a
  echo "🔄 .env aus $BASE_DIR/.env gesourced"
fi

# 3. Liste der Test-Skripte in der gewünschten Reihenfolge (absolut)
SCRIPTS=(
  #"$BASE_DIR/nc-macos-tests/TestplanHDNX/login-logout-flow-app.py"
  "$BASE_DIR/nc-macos-tests/TestplanHDNX/VersionCheck.py"
  "$BASE_DIR/nc-macos-tests/TestplanHDNX/test_settings_quota_display_check.py"
  "$BASE_DIR/nc-macos-tests/TestplanHDNX/TestLinkCheck.py"
)

# 4. Alle Skripte nacheinander ausführen, aber bei Fehlern nicht abbrechen
for script in "${SCRIPTS[@]}"; do
  echo
  echo "=== Running $script ==="
  if ! python3 "$script"; then
    echo "⚠️  $script failed, continue with next…"
  fi
done

echo
echo "✅ All scripts have run (errors were logged above if any)."
