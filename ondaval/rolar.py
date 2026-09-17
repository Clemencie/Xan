#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rolar.py — dados oficiais da mesa de Ondaval (GURPS 4ª edição)

Aleatoriedade de verdade: usa secrets.SystemRandom(), que bebe direto da
fonte de entropia do sistema operacional (o mesmo gerador que alimenta
chaves criptográficas). Sem semente, sem previsão — tão perto de
"completamente aleatório" quanto uma máquina alcança.

Uso:
  python3 ondaval/rolar.py                    → 3d6 solto
  python3 ondaval/rolar.py 3d6                → 3d6 solto
  python3 ondaval/rolar.py 2d6+1              → expressão livre NdN±M
  python3 ondaval/rolar.py 3d6 12             → teste contra Habilidade 12
  python3 ondaval/rolar.py 3d6 12 14          → confronto rápido 12 × 14
  python3 ondaval/rolar.py 3d6 14 --n 4       → quatro testes seguidos
  python3 ondaval/rolar.py 1d100              → percentagem
"""

import argparse
import re
import secrets

RNG = secrets.SystemRandom()  # entropia do sistema operacional (urandom)
EXPR = re.compile(r"^\s*(\d*)\s*[dD]\s*(\d+)\s*([+-]\s*\d+)?\s*$")


def parse_expressao(texto):
    """Aceita '3d6', '2d10+1', 'd20', '4d6-2' e parecidos."""
    m = EXPR.match(texto)
    if not m:
        raise SystemExit(
            f"Expressão inválida: {texto!r} — use o formato NdN, ex.: 3d6, 2d10+1."
        )
    qtd = int(m.group(1)) if m.group(1) else 1
    lados = int(m.group(2))
    mod = int(m.group(3).replace(" ", "")) if m.group(3) else 0
    if not (1 <= qtd <= 100 and 2 <= lados <= 1000):
        raise SystemExit("Fora do razoável: de 1 a 100 dados, de 2 a 1000 lados.")
    return qtd, lados, mod


def jogar(qtd, lados, mod=0):
    """Rola os dados e devolve (lista de dados, total com modificador)."""
    dados = [RNG.randint(1, lados) for _ in range(qtd)]
    return dados, sum(dados) + mod


def julgar(total, alvo):
    """Regras GURPS 4e: margem importa; 3-4 crit; 18, 17 com alvo<16,
    ou falha por 10+ são falha crítica."""
    margem = alvo - total
    if total <= 4 or margem >= 10:
        return margem, "SUCESSO CRÍTICO"
    if total >= 18 or margem <= -10 or (total == 17 and alvo < 16):
        return margem, "FALHA CRÍTICA"
    return margem, "sucesso" if total <= alvo else "falha"


def linha_teste(alvo, qtd, lados, mod):
    dados, total = jogar(qtd, lados, mod)
    if (qtd, lados) != (3, 6):
        print(f"  (atenção: teste de habilidade se dá com 3d6; rolando {qtd}d{lados} mesmo assim)")
    margem, resultado = julgar(total, alvo)
    print(f"  🎲 3d6 → [{', '.join(map(str, dados))}] = {total}")
    if resultado.startswith("sucesso") or resultado.startswith("falha"):
        detalhe = f"por {margem}" if margem >= 0 else f"por {-margem}"
        print(f"  🎯 alvo {alvo} → {resultado.upper()} {detalhe}")
    else:
        print(f"  🎯 alvo {alvo} → {resultado}!")


def linha_confronto(hab_a, hab_b):
    """Confronto rápido GURPS; crítico vence sucesso comum (regra da casa)."""
    da, ta = jogar(3, 6)
    db, tb = jogar(3, 6)
    ra = julgar(ta, hab_a)[1]
    rb = julgar(tb, hab_b)[1]
    crit_a, crit_b = ra.endswith("CRÍTICO"), rb.endswith("CRÍTICO")

    print(f"  🅰️  alvo {hab_a} → [{', '.join(map(str, da))}] = {ta} ({ra})")
    print(f"  🅱️  alvo {hab_b} → [{', '.join(map(str, db))}] = {tb} ({rb})")

    def tem_sucesso(r, crit):
        return r.startswith("sucesso") or crit

    sa, sb = tem_sucesso(ra, crit_a), tem_sucesso(rb, crit_b)
    if sa and not sb:
        vencedor = "A"
    elif sb and not sa:
        vencedor = "B"
    elif sa and sb:
        if crit_a and not crit_b:
            vencedor = "A"
        elif crit_b and not crit_a:
            vencedor = "B"
        elif ta != tb:
            vencedor = "A" if ta < tb else "B"
        else:
            vencedor = None
    else:
        vencedor = None

    if vencedor:
        print(f"  ⚖️  VENCE {vencedor}")
    else:
        print("  ⚖️  EMPATE — ninguém vence desta vez")


def main():
    ap = argparse.ArgumentParser(
        description="Dados de Ondaval — GURPS 4e, aleatoriedade criptográfica.",
        epilog="Ex.: python3 ondaval/rolar.py 3d6 12  |  python3 ondaval/rolar.py 2d6+1 --n 3",
    )
    ap.add_argument("expressao", nargs="?", default="3d6", help="ex.: 3d6, 2d6+1, d100")
    ap.add_argument("alvos", nargs="*", type=int,
                    help="1 alvo = teste de habilidade; 2 alvos = confronto rápido")
    ap.add_argument("--n", type=int, default=1, help="repetições (padrão 1)")
    args = ap.parse_args()

    if args.n < 1 or args.n > 50:
        raise SystemExit("--n deve ficar entre 1 e 50.")
    if len(args.alvos) > 2:
        raise SystemExit("No máximo 2 alvos (teste ou confronto).")

    qtd, lados, mod = parse_expressao(args.expressao)

    for i in range(args.n):
        if args.n > 1:
            print(f"— rolagem {i + 1}/{args.n} —")
        if not args.alvos:
            dados, total = jogar(qtd, lados, mod)
            print(f"  🎲 {qtd}d{lados}{mod:+d} → [{', '.join(map(str, dados))}] = {total}")
        elif len(args.alvos) == 1:
            linha_teste(args.alvos[0], qtd, lados, mod)
        else:
            if (qtd, lados, mod) != (3, 6, 0):
                print("  (confronto rápido sempre usa 3d6; expressão ignorada)")
            linha_confronto(args.alvos[0], args.alvos[1])


if __name__ == "__main__":
    main()
