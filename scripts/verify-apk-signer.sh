#!/usr/bin/env bash
set -euo pipefail

APK="${1:?Ange APK-fil}"
EXPECTED="84:3B:F9:FA:2B:80:42:D6:CB:F3:1A:A6:50:F1:D8:F4:34:97:57:06:D7:56:DC:DC:39:27:C0:06:AA:D4:A1:7A"
ACTUAL=$(keytool -printcert -jarfile "$APK" 2>/dev/null | awk '/SHA256:/{sub(/^[[:space:]]*SHA256:[[:space:]]*/,""); print; exit}')

if [[ "${ACTUAL^^}" != "$EXPECTED" ]]; then
  echo "Fel signeringscertifikat: ${ACTUAL:-<saknas>}" >&2
  echo "Förväntat: $EXPECTED" >&2
  exit 1
fi

echo "Signeringen är korrekt: $ACTUAL"
