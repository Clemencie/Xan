#!/usr/bin/env bash
# =============================================================================
# XAN — restaurar backup
#
#   ./backups/restaurar_backup.sh -l                    lista os backups
#   ./backups/restaurar_backup.sh -v <arquivo>          verifica a integridade
#   ./backups/restaurar_backup.sh -c <bundle> <dir>     clona o histórico git
#   ./backups/restaurar_backup.sh -x <tar.gz> <dir>     extrai a foto do trabalho
# =============================================================================
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

uso() {
    sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

lista() {
    echo "Backups em $AQUI:"
    ls -1 "$AQUI"/*.bundle "$AQUI"/*.tar.gz 2>/dev/null | while read -r f; do
        printf '  %-52s %8s  %s\n' "$(basename "$f")" "$(du -h "$f" | cut -f1)" \
            "$(date -r "$f" -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo '?')"
    done
    [ -f "$AQUI/SHA256SUMS" ] && echo && echo "SHA256SUMS:" && cat "$AQUI/SHA256SUMS"
}

verifica() {
    [ -f "$1" ] || { echo "arquivo não encontrado: $1"; exit 1; }
    cd "$AQUI"
    if grep -F "$(basename "$1")" SHA256SUMS >/dev/null 2>&1; then
        grep -F "$(basename "$1")" SHA256SUMS | sha256sum -c -
    else
        echo "aviso: $1 não consta no SHA256SUMS; calculando a soma atual:"
        sha256sum "$1"
    fi
    case "$1" in
        *.bundle) git bundle verify "$1" && echo "bundle íntegro." ;;
        *.tar.gz) gzip -t "$1" && echo "gzip íntegro." ;;
    esac
}

[ $# -lt 1 ] && uso 1
case "$1" in
    -l|--lista)  lista ;;
    -v|--verifica) [ $# -ge 2 ] || uso 1; verifica "$2" ;;
    -c|--clona)
        [ $# -ge 3 ] || uso 1
        git clone "$2" "$3"
        echo "Histórico restaurado em $3."
        echo "Confira com: cd $3 && git log --oneline && python3 -m unittest discover -s motor/testes -t motor"
        ;;
    -x|--extrai)
        [ $# -ge 3 ] || uso 1
        mkdir -p "$3"
        tar -xzf "$2" -C "$3"
        echo "Foto de trabalho extraída em $3."
        ;;
    -h|--help) uso 0 ;;
    *) echo "opção desconhecida: $1"; uso 1 ;;
esac
