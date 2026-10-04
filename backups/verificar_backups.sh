#!/usr/bin/env bash
# Confere todos os backups listados em SHA256SUMS.
set -euo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$AQUI"
[ -f SHA256SUMS ] || { echo "não há SHA256SUMS em $AQUI"; exit 1; }
echo "Verificando $(grep -c . SHA256SUMS) arquivo(s)…"
sha256sum -c SHA256SUMS
echo
echo "Verificando bundles git…"
for f in *.bundle; do
    [ -f "$f" ] || continue
    git bundle verify "$f" >/dev/null && echo "  ok  $f"
done
echo
echo "Verificando tar.gz…"
for f in *.tar.gz; do
    [ -f "$f" ] || continue
    gzip -t "$f" && echo "  ok  $f"
done
echo
echo "TODOS OS BACKUPS ÍNTEGROS."
