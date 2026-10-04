#!/usr/bin/env bash
# Sobe a interface web do XAN.
#   ./ferramentas/servir.sh [porta]
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORTA="${1:-${XAN_PORTA:-8000}}"
cd "$RAIZ"
echo "XAN — interface web"
echo "  http://0.0.0.0:${PORTA}/   (Ctrl-C para parar)"
exec python3 motor/servidor/app.py --host 0.0.0.0 --porta "$PORTA"
