"""
PERSONAGEM + COMBATE + ESTADO PERSISTENTE.
Fórmulas fechadas — nada de improviso numérico.
"""
import json
import os
import secrets

from mundo import degrau, DEGRAUS
from regras import (ATRIBUTOS, CUSTO_MOD, ESTILOS, ORIGENS,
                    TECNICAS, PROF_FX, validar_criacao)


def _r(n):
    return secrets.randbelow(n) + 1


# ---------------------------------------------------------------- CRIAÇÃO
def criar(nome, origem, estilo, distribuicao, rank=1, tecnicas_iniciais=None):
    ok, gastos, erros = validar_criacao(distribuicao)
    if not ok:
        raise ValueError("; ".join(erros))
    if origem not in ORIGENS:
        raise ValueError(f"origem desconhecida: {origem}")
    if estilo not in ESTILOS:
        raise ValueError(f"estilo desconhecido: {estilo}")

    deg = degrau(rank)
    o = ORIGENS[origem]
    mod = dict(distribuicao)
    for a, b in o["bonus"].items():
        mod[a] += b

    tec = list(tecnicas_iniciais or [])
    if not tec:
        aptas = [n for n, t in TECNICAS.items() if t["rank"] <= rank]
        tec = aptas[:deg["tec_max"]]

    p = {
        "nome": nome, "origem": origem, "estilo": estilo,
        "rank": rank, "rank_nome": deg["nome"],
        "mod": mod,
        "qi_max": deg["qi"] + o["qi"] + max(0, mod["Vontade"]) * 2,
        "pv_max": deg["pv"] + o["pv"] + max(0, mod["Corpo"]),
        "tecnicas": {t: "Entrada" for t in tec},
        "fadiga": 0, "divida_do_ceu": 0, "estresse": 0,
        "inspiracao": 2,
        "arma": ESTILOS[estilo]["arma"],
        "dado_arma": ESTILOS[estilo]["dado"],
        "gancho_origem": o["gancho"],
    }
    p["qi"] = p["qi_max"]
    p["pv"] = p["pv_max"]
    return p


def aprender(p, tecnica, prof="Entrada"):
    """Teto de técnicas por degrau é regra dura. Retorna (ok, motivo)."""
    from regras import TECNICAS
    if tecnica not in TECNICAS:
        return False, "técnica inexistente"
    t = TECNICAS[tecnica]
    if t["rank"] > p["rank"] + 1:
        return False, f"exige degrau {t['rank']} acima do que você alcança aprender"
    if tecnica in p["tecnicas"]:
        return False, "você já a conhece"
    if len(p["tecnicas"]) >= degrau(p["rank"])["tec_max"]:
        return False, (f"teto do degrau {p['rank']} é {degrau(p['rank'])['tec_max']} técnicas "
                       f"— esqueça uma antes")
    p["tecnicas"][tecnica] = prof
    return True, "aprendida"


def defesas(p, ciente=True):
    """Defesa de Aparar (Corpo) e Defesa de Esquiva (Passo)."""
    m = p["mod"]
    half = p["rank"] // 2
    aparar = 10 + half + m["Corpo"] + (1 if p["estilo"] == "Espada" else 0)
    esquiva = 10 + half + m["Passo"]
    if not ciente:
        return {"aparar": 5 + m["Passo"], "esquiva": 5 + m["Passo"], "ciente": False}
    return {"aparar": aparar, "esquiva": esquiva, "ciente": True}


def rolar_dano(expr, bonus=0):
    """'2d8+1' + bonus -> (total, detalhe)."""
    expr = expr.strip().lower()
    mult = 1.0
    if "*" in expr:
        # o multiplicador SEMPRE vem no fim: "d10+2*2.0" = (d10+2) x 2.0
        base_expr, m = expr.rsplit("*", 1)
        mult = float(m)
        expr = base_expr
    partes = expr.split("+")
    dado = partes[0]
    fixo = int(partes[1]) if len(partes) > 1 else 0
    if "d" in dado:
        q, n = dado.split("d")
        q = int(q) if q.strip() else 1   # "d10" == "1d10"
        rols = [_r(int(n)) for _ in range(q)]
        base = sum(rols)
    else:
        rols = [int(dado)]
        base = int(dado)
    total = int(round((base + fixo + bonus) * mult))
    return max(0, total), f"{rols}+{fixo}+{bonus}" + (f" x{mult}" if mult != 1 else "")


# ---------------------------------------------------------------- COMBATE
def atacar(atk, alvo_tec=None, alvo_rank=1, defesa=None, alvo_def_type="aparar",
           prof=None, qi_gasto_extra=0, desvantagem=False, vantagem=False):
    """Resolve um golpe. Retorna dict com todos os números (para o mestre conferir)."""
    m = atk["mod"]
    tec = TECNICAS.get(alvo_tec) if alvo_tec else None
    rank_tec = tec["rank"] if tec else atk["rank"]
    pfx = PROF_FX[prof or (atk["tecnicas"].get(alvo_tec, "Entrada") if alvo_tec else "Entrada")]

    # Tábua II: técnica acima do seu degrau = desvantagem + estresse
    estresse_extra = 0
    if tec and tec["rank"] > atk["rank"]:
        desvantagem = True
        estresse_extra = 2

    d1 = _r(20)
    d2 = _r(20) if (vantagem or desvantagem) else None
    if vantagem and not desvantagem:
        dado = max(d1, d2)
    elif desvantagem and not vantagem:
        dado = min(d1, d2)
    else:
        dado = d1

    acerto = dado + m["Corpo"] + pfx["acerto"] + (atk["rank"] - alvo_rank) * 2
    nat20 = dado == 20
    nat1 = dado == 1
    acertou = nat20 or (not nat1 and acerto >= (defesa or 10))

    detalhe = {"d20": d1, "d20b": d2, "usado": dado, "acerto": acerto,
               "defesa_alvo": defesa, "acertou": acertou, "nat20": nat20, "nat1": nat1,
               "estresse_extra": estresse_extra}
    if not acertou:
        detalhe["dano"] = 0
        return detalhe

    # dano
    if tec and tec["dano"]:
        base = tec["dano"]
    else:
        base = f"1d{atk['dado_arma']}"
    bonus = m["Corpo"] // 2 + qi_gasto_extra
    # Tábua VI: 4+ degraus abaixo -> -6
    if alvo_rank - atk["rank"] >= 4:
        bonus -= 6
    dano, det = rolar_dano(f"{base}*{pfx['dano']}", bonus)
    if nat20:
        dano = int(round(dano * 1.5)) + 2
    detalhe["dano"] = dano
    detalhe["det_dano"] = det
    detalhe["nat20_aplicado"] = nat20
    return detalhe


def custo_qi(atk, nome_tecnica, prof=None):
    t = TECNICAS[nome_tecnica]
    prof = prof or atk["tecnicas"].get(nome_tecnica, "Entrada")
    custo = int(round(t["custo"] * PROF_FX[prof]["custo"]))
    if atk["estilo"] == "Palma" and t["tipo"] == "interno":
        custo = max(0, custo - 2)
    return max(0, custo)


def gastar_qi(p, qtd):
    """Tábua I: abaixo de 0 = Contragolpe, sem efeito."""
    p["qi"] -= qtd
    contragolpe = 0
    if p["qi"] < 0:
        contragolpe = _r(6)
        p["qi"] = 0
        p["pv"] -= contragolpe
    return contragolpe


def regenerar(p, modo):
    """modo: 'combate' | 'meditacao' | 'sono'"""
    m = p["mod"]
    if modo == "combate":
        p["qi"] = min(p["qi_max"], p["qi"] + _r(4) + max(0, m["Vontade"]))
    elif modo == "meditacao":
        p["qi"] = min(p["qi_max"], p["qi"] + _r(8) + 2 + max(0, m["Vontade"]))
    elif modo == "sono":
        p["qi"] = p["qi_max"]
        p["pv"] = min(p["pv_max"], p["pv"] + p["pv_max"] // 2)
        p["fadiga"] = 0
        p["estresse"] = 0
    return p


def subir_degrau(p):
    if p["rank"] >= 9:
        return None
    p["rank"] += 1
    d = degrau(p["rank"])
    p["rank_nome"] = d["nome"]
    p["qi_max"] += d["qi"] - degrau(p["rank"] - 1)["qi"]
    p["pv_max"] += d["pv"] - degrau(p["rank"] - 1)["pv"]
    p["qi"], p["pv"] = p["qi_max"], p["pv_max"]
    return d["nome"]


# ---------------------------------------------------------------- ESTADO PERSISTENTE
class Estado:
    ARQ = os.path.join(os.path.dirname(__file__), "estado.json")

    def __init__(self):
        self.d = {
            "caos": 5,
            "inspiracao": 2,
            "hora": "amanhecer",
            "clima": "chuva fina",
            "local": "Estrada do Sal Velho, Província da Chuva Verde",
            "personagem": None,
            "npcs_conhecidos": [],
            "tramas": [],
            "fatos": [],
            "sementes": [],
            "cena_atual": {"nome": None, "testes": 0},
        }

    def carregar(self):
        if os.path.exists(self.ARQ):
            with open(self.ARQ, encoding="utf-8") as fh:
                self.d.update(json.load(fh))
        return self

    def salvar(self):
        with open(self.ARQ, "w", encoding="utf-8") as fh:
            json.dump(self.d, fh, ensure_ascii=False, indent=2)
        return self.ARQ

    def ajustar_caos(self, delta):
        self.d["caos"] = max(1, min(9, self.d["caos"] + delta))
        return self.d["caos"]

    def ficha(self):
        d = self.d
        p = d.get("personagem")
        linhas = [
            f"LOCAL: {d['local']}  |  HORA: {d['hora']}  |  CLIMA: {d['clima']}",
            f"CAOS: {d['caos']}  |  INSPIRAÇÃO: {d['inspiracao']}",
        ]
        if p:
            linhas += [
                f"{p['nome']} — {p['rank_nome']} (rank {p['rank']}) | {p['origem']} | {p['estilo']}",
                f"PV {p['pv']}/{p['pv_max']}   Qi {p['qi']}/{p['qi_max']}   Fadiga {p['fadiga']}/10   Dívida {p['divida_do_ceu']}",
                f"Atributos: " + ", ".join(f"{a} {p['mod'][a]:+d}" for a in ATRIBUTOS),
                f"Técnicas: " + ", ".join(f"{t} ({pr})" for t, pr in p["tecnicas"].items()),
            ]
        if d["npcs_conhecidos"]:
            linhas.append("NPCs: " + "; ".join(d["npcs_conhecidos"]))
        if d["tramas"]:
            linhas.append("TRAMAS ABERTAS:")
            linhas += [f"  - {t}" for t in d["tramas"]]
        if d["sementes"]:
            linhas.append("SEMENTES (mudas por enquanto): " + "; ".join(d["sementes"]))
        return "\n".join(linhas)
