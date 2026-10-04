#!/usr/bin/env bash
# =============================================================================
# XAN — criar backup
#
# Três camadas independentes:
#   1. git bundle  → o histórico completo, num arquivo só, clonável
#   2. tar.gz      → foto do diretório de trabalho (inclui o que não está no git)
#   3. SHA256SUMS  → verificação de integridade
#
# Uso:  ./backups/criar_backup.sh [rótulo]
# Saída: backups/<data>-<rótulo>.bundle, .tar.gz e SHA256SUMS atualizado
# =============================================================================
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

ROTULO="${1:-completo}"
ROTULO="$(printf '%s' "$ROTULO" | tr -c 'A-Za-z0-9._-' '-' | sed 's/--*/-/g;s/^-//;s/-$//')"
[ -z "$ROTULO" ] && ROTULO="completo"

DATA="$(date -u +%Y%m%dT%H%M%SZ)"
RAMO="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo sem-git)"
BASE="backups/${DATA}-${ROTULO}"

echo "XAN — criando backup"
echo "  repositório : $RAIZ"
echo "  ramo        : $RAMO"
echo "  rótulo      : $ROTULO"
echo "  data (UTC)  : $DATA"
echo

# --- 1. git bundle -----------------------------------------------------------
if git rev-parse --git-dir >/dev/null 2>&1; then
    echo "→ git bundle (todos os ramos + histórico completo)"
    git bundle create "${BASE}.bundle" --all
    git bundle verify "${BASE}.bundle" >/dev/null
    echo "  ok: $(du -h "${BASE}.bundle" | cut -f1)  ${BASE}.bundle"
else
    echo "→ git bundle: ignorado (não é um repositório git)"
fi

# --- 2. tar.gz do diretório de trabalho --------------------------------------
echo "→ tar.gz do diretório de trabalho"
EXCLUIR=(--exclude=.git --exclude='__pycache__' --exclude='*.pyc'
         --exclude=.mypy_cache --exclude='backups/*.tar.gz'
         --exclude='backups/*.bundle' --exclude=node_modules --exclude=.venv)
tar "${EXCLUIR[@]}" -czf "${BASE}.tar.gz" -C "$(dirname "$RAIZ")" "$(basename "$RAIZ")"
echo "  ok: $(du -h "${BASE}.tar.gz" | cut -f1)  ${BASE}.tar.gz"

# --- 3. somas SHA-256 --------------------------------------------------------
echo "→ SHA256SUMS"
# As somas usam só o nome do arquivo (sem o prefixo "backups/") para que
# ./verificar_backups.sh possa conferir de dentro da própria pasta.
(
    cd backups
    for f in "${BASE#backups/}.bundle" "${BASE#backups/}.tar.gz"; do
        [ -f "$f" ] && sha256sum "$f"
    done
) >> backups/SHA256SUMS
sort -u backups/SHA256SUMS -o backups/SHA256SUMS

# --- 4. manifesto legível ----------------------------------------------------
{
    echo "data_utc: $DATA"
    echo "rotulo: $ROTULO"
    echo "ramo: $RAMO"
    if git rev-parse --git-dir >/dev/null 2>&1; then
        echo "commit: $(git rev-parse HEAD 2>/dev/null || echo desconhecido)"
        echo "commits_no_historico: $(git rev-list --all --count 2>/dev/null || echo 0)"
    fi
    echo "arquivos_no_tar: $(tar -tzf "${BASE}.tar.gz" | wc -l)"
    echo "tamanho_total: $(du -ch "${BASE}".* 2>/dev/null | tail -1 | cut -f1)"
} > "${BASE}.MANIFESTO.txt"
cat "${BASE}.MANIFESTO.txt"

echo
echo "Backup criado."
echo "  IMPORTANTE: copie a pasta backups/ para FORA desta máquina."
echo "  Um backup no mesmo disco do original não é backup."
