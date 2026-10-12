# dados.py — motor de dados do RPG solo (aleatoriedade real, criptográfica)
#
# USO:
#   python3 dados.py oraculo 70 [caos]        oráculo sim/não (d100)
#   python3 dados.py cena [caos]              teste de cena (d10 vs Caos)
#   python3 dados.py peso                     d10 de peso narrativo (dosa o PdM)
#   python3 dados.py encontro <terreno> [hora]
#   python3 dados.py faísca                   Foco + Ação + Assunto
#   python3 dados.py cd                       tabela de dificuldades do livro
#
# Terrenos: rua telhado porto morro laboratorio zona_quarentena praia hospital quartel
# Horas:    manha tarde noite madrugada
import secrets
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mm3"))


def d(n):
    """Rola 1dN (1..n) com entropia criptográfica."""
    return secrets.randbelow(n) + 1


def pick(lista):
    return lista[d(len(lista)) - 1]


def rol(n, qtd=1, mod=0):
    rols = [d(n) for _ in range(qtd)]
    return rols, sum(rols) + mod


def d20(mod=0, adv=None):
    if adv is None:
        r = d(20)
    else:
        a, b = d(20), d(20)
        r = max(a, b) if adv else min(a, b)
    crit = "nat20" if r == 20 else ("nat1" if r == 1 else None)
    return r, r + mod, crit


def oraculo(limiar_base, caos=5):
    """Oráculo sim/não. limiar final = base + (caos-5)*3, preso em 1..99."""
    limiar = max(1, min(99, limiar_base + (caos - 5) * 3))
    r = d(100)
    extremo = max(1, limiar // 5)
    if r <= extremo:
        resp = "SIM, E COM FORÇA"
    elif r <= limiar:
        resp = "SIM"
    elif r <= limiar + 5:
        resp = "NÃO, MAS..."
    elif r <= limiar + 10:
        resp = "NÃO"
    else:
        resp = "NÃO, E PIROU"
    digito = r // 11 if (r % 11 == 0 and r > 0) else None
    dupla = digito is not None and digito <= caos
    return {"limiar": limiar, "rolagem": r, "resposta": resp,
            "dupla": dupla, "dupla_valor": r if dupla else None}


def cena(caos=5):
    r = d(10)
    if r > caos:
        res = "ESPERADA"
    elif r % 2 == 1:
        res = "ALTERADA"
    else:
        res = "INTERROMPIDA"
    return {"dado": r, "caos": caos, "resultado": res}


def peso_narrativo():
    """d10 que DOSA a profundidade de um PdM.
    1-2 T0 decoração | 3-4 T1 obstáculo | 5-7 T2 coadjuvante | 8-9 T3 peça-chave | 10 T4 âncora."""
    r = d(10)
    t = 0 if r <= 2 else 1 if r <= 4 else 2 if r <= 7 else 3 if r <= 9 else 4
    return {"d10": r, "tier": t,
            "tier_nome": ["Decoração", "Obstáculo", "Coadjuvante", "Peça-chave", "Âncora"][t]}


def _fmt_pdm(n, ident="  "):
    nome = n.get("nome") or n.get("rotulo") or "(sem nome)"
    cab = f"{ident}[T{n['tier']} {n['tier_nome']}] {nome} — {n.get('faccao', 'nenhuma')}"
    if n.get("np"):
        cab += f" — NP {n['np']}"
    linhas = [cab]
    ordem = [("o_que_acontece", "o que acontece"), ("o_que_faz", "o que faz"),
             ("guarda", "guarda"), ("instinto", "instinto"),
             ("nota", "nota"), ("nota_poder", "nota"),
             ("tracos", "traços"), ("equipamento", "equipamento"),
             ("poderes", "poderes"), ("ataque", "ataque"),
             ("np_efetivo", "NP efetivo"), ("defesas", "defesas"),
             ("dano", "dano"), ("esquiva", "esquiva"), ("resistencia", "resistência"),
             ("desejo", "quer"), ("segredo", "segredo"),
             ("complicacoes", "complicações"),
             ("gancho1", "gancho 1"), ("gancho2", "gancho 2"),
             ("como_pensa", "como pensa"), ("esconde_de_si", "esconde de si"),
             ("ponta_de_trama", "ponta de trama"),
             ("por_que_esta_aqui", "por que está aqui")]
    for k, rot in ordem:
        v = n.get(k)
        if not v:
            continue
        if k == "poderes":
            v = ", ".join(f"{p['rotulo']} ({p['efeito']} {p['grad']})" for p in v)
        elif k == "defesas":
            v = " ".join(f"{a[:3]} {b}" for a, b in v.items())
        elif isinstance(v, list):
            v = ", ".join(v)
        linhas.append(f"{ident}  {rot}: {v}")
    return "\n".join(linhas)


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "peso"

    if cmd == "oraculo":
        base = int(args[1]) if len(args) > 1 else 50
        caos = int(args[2]) if len(args) > 2 else 5
        print(oraculo(base, caos))
    elif cmd == "cena":
        print(cena(int(args[1]) if len(args) > 1 else 5))
    elif cmd == "peso":
        print(peso_narrativo())
    elif cmd == "faísca" or cmd == "faisca":
        from encontros import faísca
        print(faísca())
    elif cmd == "cd":
        from regras import TABELA_CD
        for cd, nome, ex in TABELA_CD:
            print(f"  CD {cd:2}  {nome:18} ex.: {ex}")
    elif cmd == "encontro":
        from encontros import encontrar
        enc = encontrar(args[1] if len(args) > 1 else "rua",
                        args[2] if len(args) > 2 else "noite")
        print(f"ENCONTRO: {enc['o_que']}  (x{enc['quantidade']}, NP {enc['np_faixa']}, "
              f"tier {enc['tier']}, {enc['hora']}, {enc['terreno']})")
        print(f"  facção: {enc['faccao']}  |  ÂNCORA DE TRAMA: {enc['ancora']}")
        for n in enc["npcs"]:
            print(_fmt_pdm(n))
    else:
        print("comandos: oraculo <base> [caos] | cena [caos] | peso | "
              "encontro <terreno> [hora] | faísca | cd")
