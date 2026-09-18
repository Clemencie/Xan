#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rolar.py — dados oficiais da mesa (Warhammer 40K: a Grande Cruzada)

Aleatoriedade de verdade: secrets.SystemRandom(), que bebe direto da fonte
de entropia do sistema operacional — a mesma classe de gerador que alimenta
chaves criptográficas. Sem semente, sem previsão.

Modos:
  python3 imperium/rolar.py 1d100 55      → teste d100 contra 55 (graus a cada 10)
  python3 imperium/rolar.py 1d100 55 40   → teste oposto 55 × 40 (vence o melhor grau)
  python3 imperium/rolar.py 8d6 --wng     → pool Wrath & Glory (com Dado de Fúria)
  python3 imperium/rolar.py 2d10+10       → expressão livre NdN±M (dano etc.)
  python3 imperium/rolar.py 3d10 --n 4    → repetições
  python3 imperium/rolar.py 1d100         → d100 solto
"""

import argparse
import re
import secrets

RNG = secrets.SystemRandom()  # entropia do sistema operacional (urandom)
EXPR = re.compile(r"^\s*(\d*)\s*[dD]\s*(\d+)\s*([+-]\s*\d+)?\s*$")


def parse_expressao(texto):
    """Aceita '1d100', '2d10+10', 'd6', '4d6-2' e parecidos."""
    m = EXPR.match(texto)
    if not m:
        raise SystemExit(
            f"Expressão inválida: {texto!r} — use o formato NdN, ex.: 1d100, 2d10+10."
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


def julgar_d100(total, alvo):
    """Regras FFG (Deathwatch & família): d100 ≤ alvo; +1 grau a cada 10
    completos abaixo; 100 natural falha sempre."""
    if total == 100:
        return 0, "FALHA (100 natural — falha sempre)"
    if total <= alvo:
        graus = 1 + (alvo - total) // 10
        return graus, f"SUCESSO — {graus} grau{'s' if graus > 1 else ''}"
    excesso = total - alvo
    graus = 1 + (excesso - 1) // 10
    return -graus, f"falha — {graus} grau{'s' if graus > 1 else ''} de falha"


def linha_teste_d100(alvo):
    dados, total = jogar(1, 100)
    graus, texto = julgar_d100(total, alvo)
    print(f"  🎲 d100 → {total} (alvo {alvo}) → {texto}")


def linha_oposto(alvo_a, alvo_b):
    da, ta = jogar(1, 100)
    db, tb = jogar(1, 100)
    ga, xa = julgar_d100(ta, alvo_a)
    gb, xb = julgar_d100(tb, alvo_b)
    print(f"  🅰️  alvo {alvo_a} → {ta} → {xa}")
    print(f"  🅱️  alvo {alvo_b} → {tb} → {xb}")
    if ga > 0 and gb > 0:
        vencedor = "A" if ga > gb else "B" if gb > ga else None
    elif ga > 0:
        vencedor = "A"
    elif gb > 0:
        vencedor = "B"
    else:
        vencedor = None
    if vencedor:
        print(f"  ⚖️  VENCE {vencedor}")
    else:
        print("  ⚖️  NINGUÉM vence (empate de falhas)")


def linha_wng(qtd, dn):
    if qtd < 1:
        raise SystemExit("Pool precisa de ao menos 1 dado.")
    dados, _ = jogar(qtd, 6)
    furia = dados[0]
    icones = sum(2 if d == 6 else 1 if d >= 4 else 0 for d in dados)
    marcas = " ".join(f"[{d}]" if i == 0 else str(d) for i, d in enumerate(dados))
    print(f"  🎲 {qtd}d6 → {marcas}   (o dado entre colchetes é o Dado de Fúria)")
    print(f"  ✳️  Ícones: {icones} (4–5 = 1 ícone; 6 = 2 ícones) — DN {dn}")
    if icones >= dn:
        print("  🏆 SUCESSO")
    else:
        print("  💀 FALHA")
    if furia == 6:
        print("  🔥 Fúria 6: GLÓRIA ao grupo!")
    elif furia == 1:
        print("  ⚠️  Fúria 1: COMPLICAÇÃO na cena!")


def main():
    ap = argparse.ArgumentParser(
        description="Dados da mesa — Warhammer 40K (Grande Cruzada), entropia criptográfica.",
        epilog="Ex.: python3 imperium/rolar.py 1d100 55 | python3 imperium/rolar.py 8d6 --wng",
    )
    ap.add_argument("expressao", nargs="?", default="1d100",
                    help="ex.: 1d100, 2d10+10, 8d6")
    ap.add_argument("alvos", nargs="*", type=int,
                    help="1 alvo = teste d100; 2 alvos = teste oposto")
    ap.add_argument("--n", type=int, default=1, help="repetições (padrão 1)")
    ap.add_argument("--wng", action="store_true",
                    help="modo Wrath & Glory: pool de d6, ícones e Dado de Fúria")
    ap.add_argument("--dn", type=int, default=3, help="DN do teste W&G (padrão 3)")
    args = ap.parse_args()

    if args.n < 1 or args.n > 50:
        raise SystemExit("--n deve ficar entre 1 e 50.")
    if len(args.alvos) > 2:
        raise SystemExit("No máximo 2 alvos (teste ou oposto).")

    qtd, lados, mod = parse_expressao(args.expressao)

    for i in range(args.n):
        if args.n > 1:
            print(f"— rolagem {i + 1}/{args.n} —")
        if args.wng:
            if lados != 6:
                print("  (modo W&G usa d6; rolando d6 e ignorando a expressão)")
            linha_wng(qtd, args.dn)
        elif len(args.alvos) == 1:
            if (qtd, lados) != (1, 100):
                print("  (teste de alvo usa 1d100; rolando 1d100 mesmo assim)")
            linha_teste_d100(args.alvos[0])
        elif len(args.alvos) == 2:
            if (qtd, lados) != (1, 100):
                print("  (teste oposto usa 1d100; rolando 1d100 mesmo assim)")
            linha_oposto(args.alvos[0], args.alvos[1])
        else:
            dados, total = jogar(qtd, lados, mod)
            print(f"  🎲 {qtd}d{lados}{mod:+d} → [{', '.join(map(str, dados))}] = {total}")


if __name__ == "__main__":
    main()
