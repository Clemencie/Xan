#!/usr/bin/env bash
# Prepara uma sessão de jogo: diário, selo inicial e resumo do mundo.
#   ./ferramentas/nova_sessao.sh <semente-do-mundo> <nome-da-sessao>
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

SEMENTE="${1:?uso: nova_sessao.sh <semente-do-mundo> <nome-da-sessao>}"
SESSAO="${2:?uso: nova_sessao.sh <semente-do-mundo> <nome-da-sessao>}"
DIR="mundos/${SESSAO}"

mkdir -p "$DIR/auditoria" "$DIR/selos" "$DIR/personagens"

if [ ! -f "$DIR/mundo.json" ]; then
    echo "→ gerando o mundo de ${SESSAO} a partir da semente '${SEMENTE}'"
    ./xan mundo gerar --semente "$SEMENTE" --saida "$DIR" --npcs 8
fi

DIARIO="$DIR/auditoria/${SESSAO}.jsonl"
echo "→ diário: $DIARIO"
echo "→ role com:"
echo "    ./xan rolar \"1d20\" --ator \"Nome\" --diario $DIARIO"
echo
echo "→ ao fim da sessão, sele e guarde o selo FORA do repositório:"
echo "    ./xan auditoria selar --diario $DIARIO --saida $DIR/selos/$(date -u +%Y-%m-%d).txt"
echo "    ./xan auditoria verificar --diario $DIARIO"
