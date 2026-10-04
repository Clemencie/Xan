#!/usr/bin/env bash
# Roda tudo: testes unitários, invariantes do motor e uma bateria curta de justiça.
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

echo "=============================================================="
echo "1/3  testes unitários (260)"
echo "=============================================================="
( cd motor && python3 -m unittest discover -s testes -t . )

echo
echo "=============================================================="
echo "2/3  invariantes do motor"
echo "=============================================================="
./xan motor autoteste

echo
echo "=============================================================="
echo "3/3  bateria curta de imparcialidade"
echo "=============================================================="
./xan justica --amostras 4000 --leves 2000

echo
echo "TUDO VERDE."
