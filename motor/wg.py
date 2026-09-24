"""Motor de dados da mesa — Wrath & Glory adaptado para 30K.

Regras implementadas (ver sistema/01-regras-wrath-glory.md):
- Parada de d6s: 1-3 falha, 4-5 = 1 icone, 6 = 2 icones (exaltado).
- 1 dado de Wrath por teste: 1 = complicacao, 6 = +1 Gloria (+critico se ataque com sucesso).
- Shifts: 6s excedentes (sem fazer falta p/ bater o DN) viram dano extra/qualidade/Gloria.
- Dano: base + ED (4-5 = +1, 6 = +2) vs Resilience; soak via Determination (Toughness, sem Wrath).

Uso:
    python3 -m motor.wg teste --pool 8 --dn 3 --rotulo "BS+Agi vs cultista"
    python3 -m motor.wg teste --pool 8 --dn 3 --ataque --dn-alvo-defesa
    python3 -m motor.wg dano --base 10 --ed 2 --res 8 --tough 4 --ap 1
    python3 -m motor.wg derivados --tier 2 --tough 4 --init 4 --will 3 --armadura 3
    python3 -m motor.wg selftest
"""

from __future__ import annotations

import argparse
import random
import sys


# --------------------------------------------------------------------------- #
# Núcleo
# --------------------------------------------------------------------------- #
def rolar_d6(qtd: int, rng: random.Random) -> list[int]:
    return [rng.randint(1, 6) for _ in range(qtd)]


def icones(dados: list[int]) -> tuple[int, int]:
    """Retorna (total_de_icones, qtd_exaltados)."""
    total = 0
    exaltados = 0
    for d in dados:
        if d in (4, 5):
            total += 1
        elif d == 6:
            total += 2
            exaltados += 1
    return total, exaltados


def max_shifts(total_icones: int, exaltados: int, dn: int) -> int:
    """Quantos 6s podem ser shiftados sem deixar de bater o DN."""
    if total_icones < dn:
        return 0
    return min(exaltados, (total_icones - dn) // 2)


def teste(
    pool: int,
    dn: int,
    wrath: int = 1,
    ataque: bool = False,
    rng: random.Random | None = None,
) -> dict:
    """Executa um teste completo e devolve o resultado estruturado."""
    rng = rng or random.Random()
    if pool < 1:
        raise ValueError("pool deve ser >= 1 (o dado de Wrath conta na parada)")
    wrath = min(wrath, pool)
    dados_wrath = rolar_d6(wrath, rng)
    dados_normais = rolar_d6(pool - wrath, rng)

    todos = dados_wrath + dados_normais
    total, exaltados = icones(todos)
    sucesso = total >= dn
    complicacao = 1 in dados_wrath
    gloria = sum(1 for d in dados_wrath if d == 6)
    critico = bool(ataque and sucesso and gloria > 0)
    shifts = max_shifts(total, exaltados, dn)

    return {
        "pool": pool,
        "dn": dn,
        "dados_wrath": dados_wrath,
        "dados_normais": dados_normais,
        "icones": total,
        "exaltados": exaltados,
        "sucesso": sucesso,
        "margem": total - dn,
        "complicacao": complicacao,
        "gloria_ganha": gloria,
        "critico": critico,
        "shifts_max": shifts,
    }


def dano(
    base: int,
    ed: int = 0,
    res: int = 0,
    ap: int = 0,
    tough: int = 0,
    soak: bool = True,
    mortal: int = 0,
    rng: random.Random | None = None,
) -> dict:
    """Resolve dano contra Resilience, com soak opcional de Determination."""
    rng = rng or random.Random()
    dados_ed = rolar_d6(ed, rng)
    bonus, _ = icones(dados_ed)
    res_efetiva = max(0, res - ap)
    total = base + bonus
    if total < res_efetiva:
        wounds, shock = 0, 0
    elif total == res_efetiva:
        wounds, shock = 0, 1
    else:
        wounds, shock = total - res_efetiva, 0

    convertidos = 0
    dados_soak: list[int] = []
    if soak and wounds > 0 and tough > 0:
        dados_soak = rolar_d6(tough, rng)  # Determination: sem dado de Wrath
        ic, _ = icones(dados_soak)
        convertidos = min(ic, wounds)
        wounds -= convertidos
        shock += convertidos
    wounds += mortal  # Mortal Wounds: direto, sem soak

    return {
        "base": base,
        "dados_ed": dados_ed,
        "bonus_ed": bonus,
        "dano_total": total,
        "res_efetiva": res_efetiva,
        "wounds": wounds,
        "shock": shock,
        "dados_soak": dados_soak,
        "convertidos": convertidos,
    }


def derivados(tier: int, tough: int, init: int, will: int, armadura: int = 0) -> dict:
    return {
        "defence": init - 1,
        "resilience": tough + armadura,
        "wounds_max": tough + tier,
        "shock_max": will + tier,
        "determination": tough,
    }


# --------------------------------------------------------------------------- #
# Formatação (bloco padrão do protocolo da mesa)
# --------------------------------------------------------------------------- #
def fmt_teste(r: dict, rotulo: str = "") -> str:
    def fmt_dado(d: int, wrath: bool = False) -> str:
        s = f"⚡{d}!" if wrath and d in (1, 6) else (f"⚡{d}" if wrath else str(d))
        return s

    dados = [fmt_dado(d, True) for d in r["dados_wrath"]]
    dados += [fmt_dado(d) for d in r["dados_normais"]]
    titulo = f"Teste: {rotulo} — " if rotulo else "Teste: "
    linhas = [
        f"🎲 {titulo}{r['pool']}d6 vs DN {r['dn']}",
        f"   Dados: [{'] ['.join(dados)}]",
        f"   Ícones: {r['icones']} (exaltados: {r['exaltados']}) vs DN {r['dn']} → "
        f"{'SUCESSO' if r['sucesso'] else 'FALHA'} (margem {r['margem']:+d})",
    ]
    if r["complicacao"]:
        linhas.append("   ⚡1 → COMPLICAÇÃO! Algo dá errado mesmo se passou.")
    if r["gloria_ganha"]:
        linhas.append(f"   ⚡6! → +{r['gloria_ganha']} Glória ao grupo"
                      + (" + CRÍTICO!" if r["critico"] else ""))
    if r["sucesso"] and r["shifts_max"]:
        linhas.append(f"   Shifts disponíveis: {r['shifts_max']} "
                      f"(ex.: +{r['shifts_max']} ED de dano)")
    return "\n".join(linhas)


def fmt_dano(r: dict) -> str:
    linhas = [
        "💥 Dano:",
        f"   Base {r['base']} + ED {r['dados_ed'] or '—'} (+{r['bonus_ed']}) "
        f"= {r['dano_total']} vs Resilience {r['res_efetiva']}",
    ]
    if r["dados_soak"]:
        linhas.append(f"   Soak (Determination): {r['dados_soak']} → "
                      f"{r['convertidos']} Wound(s) convertida(s) em Shock")
    linhas.append(f"   Resultado: {r['wounds']} Wound(s), {r['shock']} Shock")
    return "\n".join(linhas)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wg", description="Motor de dados W&G 30K")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("teste", help="Executa um teste com dado de Wrath")
    t.add_argument("--pool", type=int, required=True, help="Total de d6s (inclui Wrath)")
    t.add_argument("--dn", type=int, required=True, help="Dificuldade")
    t.add_argument("--wrath", type=int, default=1, help="Dados de Wrath (padrão 1)")
    t.add_argument("--ataque", action="store_true", help="É ataque (habilita crítico)")
    t.add_argument("--rotulo", default="", help="Descrição do teste")
    t.add_argument("--seed", type=int, default=None, help="Seed p/ reprodutibilidade")

    d = sub.add_parser("dano", help="Resolve dano contra Resilience")
    d.add_argument("--base", type=int, required=True)
    d.add_argument("--ed", type=int, default=0)
    d.add_argument("--res", type=int, required=True)
    d.add_argument("--ap", type=int, default=0)
    d.add_argument("--tough", type=int, default=0, help="Determination p/ soak (0 = sem soak)")
    d.add_argument("--sem-soak", action="store_true")
    d.add_argument("--mortal", type=int, default=0)
    d.add_argument("--seed", type=int, default=None)

    v = sub.add_parser("derivados", help="Calcula traços derivados")
    v.add_argument("--tier", type=int, required=True)
    v.add_argument("--tough", type=int, required=True)
    v.add_argument("--init", type=int, required=True)
    v.add_argument("--will", type=int, required=True)
    v.add_argument("--armadura", type=int, default=0)

    sub.add_parser("selftest", help="Verifica o motor (determinístico)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "teste":
        rng = random.Random(args.seed)
        r = teste(args.pool, args.dn, args.wrath, args.ataque, rng)
        print(fmt_teste(r, args.rotulo))
    elif args.cmd == "dano":
        rng = random.Random(args.seed)
        r = dano(args.base, args.ed, args.res, args.ap, args.tough,
                 soak=not args.sem_soak, mortal=args.mortal, rng=rng)
        print(fmt_dano(r))
    elif args.cmd == "derivados":
        for k, v in derivados(args.tier, args.tough, args.init, args.will,
                              args.armadura).items():
            print(f"{k}: {v}")
    elif args.cmd == "selftest":
        return 0 if selftest() else 1
    return 0


def selftest() -> bool:
    """Bateria determinística: falha levanta AssertionError."""
    # icones / exaltados
    assert icones([1, 2, 3, 4, 5, 6]) == (4, 1)
    assert icones([6, 6, 6]) == (6, 3)
    assert icones([1, 1, 1]) == (0, 0)
    # shifts: só o excedente
    assert max_shifts(6, 2, 3) == 1   # 6-2=4 >= 3 ok; 6-4=2 < 3 não
    assert max_shifts(8, 3, 3) == 2
    assert max_shifts(2, 0, 3) == 0   # falhou: sem shift
    # determinismo com seed
    r1 = teste(8, 3, rng=random.Random(42))
    r2 = teste(8, 3, rng=random.Random(42))
    assert r1 == r2 and len(r1["dados_wrath"]) == 1
    assert len(r1["dados_normais"]) == 7
    # dano: sem ED, base abaixo/igual/acima
    assert dano(5, 0, res=8, soak=False)["wounds"] == 0
    d_igual = dano(8, 0, res=8, soak=False)
    assert (d_igual["wounds"], d_igual["shock"]) == (0, 1)
    d_acima = dano(11, 0, res=8, soak=False)
    assert d_acima["wounds"] == 3
    # soak nunca gera soak negativo e mortal sempre soma
    d_soak = dano(12, 0, res=8, tough=4, mortal=1, rng=random.Random(7))
    assert d_soak["wounds"] >= 1
    # derivados
    assert derivados(2, 4, 4, 3, 3) == {"defence": 3, "resilience": 7,
                                       "wounds_max": 6, "shock_max": 5,
                                       "determination": 4}
    print("selftest: OK — 13 verificações passaram.")
    return True


if __name__ == "__main__":
    sys.exit(main())
