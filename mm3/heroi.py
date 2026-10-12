"""
HERÓI — criação, validação de Nível de Poder, combate e estado.

Todas as fórmulas vêm do livro (pontos de poder, custo de características,
os cinco limites de NP, testes, graus, condições). Nada de casa.
"""
import json
import os
import secrets

from regras import (MOTIVACOES, COMPLICACOES, HABILIDADES, DEFESAS, PERICIAS, VANTAGENS, EFEITOS,
                    CUSTO_HABILIDADE, CUSTO_DEFESA, CUSTO_PERICIA, CUSTO_VANTAGEM,
                    pontos_iniciais, limites_np, custo_poder, graus, medida)


def _r(n):
    return secrets.randbelow(n) + 1


def d20():
    return _r(20)


# ============================================================ CRIAÇÃO
def criar(nome, np=10, habilidades=None, defesas=None, pericias=None,
          vantagens=None, poderes=None, complicacoes=None, motivacao=None,
          codinome=None, origem=None):
    """Monta o herói e VALIDA contra os limites de Nível de Poder.
    Levanta ValueError listando tudo que estourou — não deixa passar meia regra."""
    habilidades = habilidades or {}
    defesas = defesas or {}
    pericias = pericias or {}
    vantagens = vantagens or {}
    poderes = poderes or {}

    erros = []
    for h in habilidades:
        if h not in HABILIDADES:
            erros.append(f"habilidade inexistente: {h}")
        elif not (-5 <= habilidades[h] <= 20):
            erros.append(f"{h} {habilidades[h]} fora da faixa -5..20")
    for d in defesas:
        if d not in DEFESAS:
            erros.append(f"defesa inexistente: {d}")
    for p in pericias:
        if p not in PERICIAS and not p.startswith("Especialidade"):
            erros.append(f"perícia inexistente: {p}")
    for v in vantagens:
        if v not in VANTAGENS:
            erros.append(f"vantagem inexistente: {v}")
    for nome_pw, pw in poderes.items():
        if pw["efeito"] not in EFEITOS:
            erros.append(f"efeito inexistente em '{nome_pw}': {pw['efeito']}")

    if len(complicacoes or []) < 2:
        erros.append("o livro exige pelo menos 2 complicações, sendo uma a Motivação")
    if not motivacao:
        erros.append("falta a Motivação (é obrigatória)")
    elif motivacao not in MOTIVACOES:
        erros.append(f"Motivação inexistente: {motivacao}; use uma de {MOTIVACOES}")
    for c in complicacoes or []:
        if c not in COMPLICACOES and c != motivacao:
            erros.append(f"complicação inexistente: {c}; use uma de {COMPLICACOES}")

    heroi = {
        "nome": nome, "codinome": codinome or nome, "np": np,
        "origem": origem, "motivacao": motivacao,
        "complicacoes": list(complicacoes or []),
        "habilidades": {h: habilidades.get(h, 0) for h in HABILIDADES},
        "defesas": dict(defesas),
        "pericias": dict(pericias),
        "vantagens": dict(vantagens),
        "poderes": poderes,
        "pontos_heroicos": 1,          # o livro: começa a sessão com 1
        "condicoes": [],
        "fatiga": 0,
    }

    # ---- defesas derivadas
    der = {}
    for nome_def, info in DEFESAS.items():
        base = heroi["habilidades"][info["base"]]
        der[nome_def] = base + heroi["defesas"].get(nome_def, 0)
    heroi["defesas_totais"] = der
    heroi["iniciativa"] = heroi["habilidades"]["Prontidão"] + heroi["defesas"].get("Iniciativa", 0)

    # ---- pontos de poder gastos
    gastos = {"habilidades": 0, "defesas": 0, "pericias": 0.0, "vantagens": 0, "poderes": 0}
    for h, g in heroi["habilidades"].items():
        gastos["habilidades"] += g * CUSTO_HABILIDADE
    for d, extra in heroi["defesas"].items():
        if d in DEFESAS:
            gastos["defesas"] += extra * CUSTO_DEFESA
    for p, g in heroi["pericias"].items():
        gastos["pericias"] += g * CUSTO_PERICIA
    for v, g in heroi["vantagens"].items():
        gastos["vantagens"] += (g if isinstance(g, int) else 1) * CUSTO_VANTAGEM
    for pw in heroi["poderes"].values():
        gastos["poderes"] += custo_poder(pw["efeito"], pw["grad"],
                                         pw.get("extras", 0), pw.get("falhas", 0))
    total = int(sum(gastos.values()))
    orcamento = pontos_iniciais(np)
    heroi["pontos_gastos"] = total
    heroi["pontos_orcamento"] = orcamento
    heroi["gastos_detalhados"] = gastos

    if total > orcamento:
        erros.append(f"orçamento estourado: {total}/{orcamento} pontos de poder")

    # ---- os cinco limites de Nível de Poder
    lim = limites_np(np)
    heroi["limites_np"] = lim

    # 1) perícia: habilidade + graduações + vantagem não pode passar de NP + 10
    for p, g in heroi["pericias"].items():
        base_nome = "Especialidade" if p.startswith("Especialidade") else p
        if base_nome not in PERICIAS:
            erros.append(f"perícia inexistente no cálculo de teto: {p}")
            continue
        hab = PERICIAS[base_nome]["hab"]
        total_p = heroi["habilidades"][hab] + g
        if total_p > lim["pericia_max"]:
            erros.append(f"perícia {p}: {total_p} excede o teto NP+10 = {lim['pericia_max']}")

    # 2) ataque + efeito <= 2*NP
    for nome_pw, pw in heroi["poderes"].items():
        info = EFEITOS[pw["efeito"]]
        atq = pw.get("ataque")
        if atq is not None:
            if atq + pw["grad"] > lim["ataque_efeito_max"]:
                erros.append(f"{nome_pw}: ataque {atq} + efeito {pw['grad']} = "
                             f"{atq + pw['grad']} excede 2xNP = {lim['ataque_efeito_max']}")
        elif info["salvamento"] and pw["grad"] > lim["efeito_sem_ataque_max"]:
            erros.append(f"{nome_pw}: efeito {pw['grad']} sem teste de ataque excede NP = "
                         f"{lim['efeito_sem_ataque_max']}")

    # 3/4/5) pares de defesas
    d = heroi["defesas_totais"]
    pares = [("Esquiva", "Resistência", "esquiva_resistencia_max"),
             ("Aparar", "Resistência", "aparar_resistencia_max"),
             ("Fortitude", "Vontade", "fortitude_vontade_max")]
    for a, b, chave in pares:
        if d[a] + d[b] > lim[chave]:
            erros.append(f"{a} {d[a]} + {b} {d[b]} = {d[a] + d[b]} excede 2xNP = {lim[chave]}")

    heroi["erros"] = erros
    if erros:
        raise ValueError("Ficha recusada — " + " | ".join(erros))
    return heroi


# ============================================================ PERÍCIAS E TESTES
def mod_pericia(heroi, pericia):
    # "Especialidade (História da Maré)" conta como Especialidade
    base_nome = "Especialidade" if pericia.startswith("Especialidade") else pericia
    if base_nome not in PERICIAS:
        raise ValueError(f"perícia inexistente: {pericia}")
    hab = PERICIAS[base_nome]["hab"]
    return heroi["habilidades"][hab] + heroi["pericias"].get(pericia, 0)


def teste(heroi, caracteristica, cd, circunstancia=0, rotina=False):
    """Teste = d20 + modificador vs CD. 20 natural = sucesso crítico (+1 grau).
    rotina=True usa 10 em vez de rolar (sem pressão, como manda o livro)."""
    if caracteristica in heroi["habilidades"]:
        mod = heroi["habilidades"][caracteristica]
    elif caracteristica in PERICIAS or caracteristica.startswith("Especialidade"):
        mod = mod_pericia(heroi, caracteristica)
    elif caracteristica in heroi["defesas_totais"]:
        mod = heroi["defesas_totais"][caracteristica]
    else:
        raise ValueError(f"característica desconhecida: {caracteristica}")

    mod += circunstancia
    penalidade = 0
    if "Desabilitado" in heroi["condicoes"]:
        penalidade -= 5
    elif "Prejudicado" in heroi["condicoes"]:
        penalidade -= 2
    mod += penalidade

    dado = 10 if rotina else d20()
    total = dado + mod
    g = graus(total, cd)
    if dado == 20 and not rotina:
        g += 1                     # sucesso crítico soma um passo
    return {"d20": dado, "mod": mod, "total": total, "cd": cd,
            "graus": g, "sucesso": g > 0, "critico": dado == 20 and not rotina,
            "rotina": rotina}


def salvamento(heroi, defesa, cd, circunstancia=0):
    return teste(heroi, defesa, cd, circunstancia)


# ============================================================ COMBATE
def ataque(heroi, nome_poder=None, arma=None, defesa_alvo=10, circunstancia=0,
           esforco_extra=None, alvo_vulneravel=False, alvo_indefeso=False):
    """Teste de ataque = d20 + bônus de ataque vs defesa do alvo.
    20 natural é sempre acerto; 1 natural é sempre falha."""
    if nome_poder and isinstance(heroi["poderes"], dict) and nome_poder in heroi["poderes"]:
        pw = heroi["poderes"][nome_poder]
        atq = pw.get("ataque", 0)
        dano_grad = pw["grad"]
        efeito = pw["efeito"]
    else:
        atq = heroi["habilidades"]["Luta"] + heroi["pericias"].get("Combate Corpo-a-Corpo", 0)
        dano_grad = max(0, heroi["habilidades"]["Força"])
        efeito = "Dano"

    bonus = 0
    if esforco_extra == "bonus":
        bonus += 2
    if "Ataque Imprudente" in heroi["vantagens"]:
        bonus += 2

    if alvo_indefeso:
        # atacante pode usar teste de rotina; todo acerto é crítico
        r = teste(heroi, "Luta", defesa_alvo, circunstancia + bonus, rotina=True)
        r["critico"] = True
        r["dano_grad"] = dano_grad + 1
        r["efeito"] = efeito
        return r

    if alvo_vulneravel:
        defesa_alvo = -(-defesa_alvo // 2)     # metade, arredondando para cima

    d = d20()
    total = d + atq + bonus + circunstancia
    acertou = (d == 20) or (d != 1 and total >= defesa_alvo)
    g = graus(total, defesa_alvo) if acertou else graus(total, defesa_alvo)
    if d == 20:
        g += 1
    if esforco_extra == "poder":
        dano_grad += 1
    return {"d20": d, "ataque": atq + bonus + circunstancia, "total": total,
            "defesa_alvo": defesa_alvo, "acertou": acertou, "graus": g,
            "critico": d == 20, "falha_critica": d == 1,
            "dano_grad": dano_grad, "efeito": efeito}


def resistencia_alvo(resistencia, dano_grad, graus_ataque=1):
    """Resistência a Dano: CD 15 + graduações de dano. (Cap. 8, ADENDO)
    Grau da falha define a condição — tabela de Resistência a Dano."""
    cd = 15 + dano_grad
    d = d20()
    total = d + resistencia
    g = graus(total, cd)
    if g > 0:
        return {"cd": cd, "d20": d, "total": total, "resultado": "sem efeito",
                "condicoes": [], "graus": g}
    falha = -g
    # tabela de resistência a dano (ADENDO, pág. 217 não extraída)
    if falha >= 3:
        cond = ["Incapacitado"]
    elif falha == 2:
        cond = ["Atordoado", "Abatido"]
    else:
        cond = ["Abatido"]
    return {"cd": cd, "d20": d, "total": total, "graus": g,
            "resultado": " ".join(cond), "condicoes": cond}


def esforco_extra(heroi, beneficio):
    """Esforço extra: no início do turno seguinte o herói fica fatigado.
    Fatigado -> exausto; exausto -> incapacitado. (Cap. 1, lido no PDF)"""
    beneficio = beneficio.lower()
    validos = ["acao", "bonus", "poder", "facanha", "salvamento", "velocidade", "forca"]
    if beneficio not in validos:
        raise ValueError(f"benefício inválido; use um de {validos}")
    if "Incapacitado" in heroi["condicoes"]:
        return {"ok": False, "motivo": "já está incapacitado"}
    if "Exausto" in heroi["condicoes"]:
        heroi["condicoes"].append("Incapacitado")
        return {"ok": True, "beneficio": beneficio, "consequencia": "Incapacitado"}
    if "Fatigado" in heroi["condicoes"]:
        heroi["condicoes"].remove("Fatigado")
        heroi["condicoes"].append("Exausto")
        return {"ok": True, "beneficio": beneficio, "consequencia": "Exausto"}
    heroi["condicoes"].append("Fatigado")
    return {"ok": True, "beneficio": beneficio, "consequencia": "Fatigado"}


def gastar_ponto_heroico(heroi, uso):
    """Usos do livro: editar cena, feito heroico, melhorar rolagem, inspiração,
    repelir instantaneamente, recuperar-se."""
    usos = ["editar_cena", "feito_heroico", "melhorar_rolagem", "inspiracao",
            "repelir", "recuperar"]
    if uso not in usos:
        raise ValueError(f"uso inválido; use um de {usos}")
    if heroi["pontos_heroicos"] <= 0:
        return {"ok": False, "motivo": "sem pontos heroicos"}
    heroi["pontos_heroicos"] -= 1
    if uso == "recuperar":
        # remove TODAS as ocorrências: esforço extra pode ter acumulado a mesma condição
        for c in ("Tonto", "Fatigado", "Atordoado"):
            heroi["condicoes"] = [x for x in heroi["condicoes"] if x != c]
        if "Exausto" in heroi["condicoes"]:
            heroi["condicoes"] = [x for x in heroi["condicoes"] if x != "Exausto"]
            heroi["condicoes"].append("Fatigado")
    return {"ok": True, "uso": uso, "restam": heroi["pontos_heroicos"]}


def ganhar_ponto_heroico(heroi, motivo):
    """O mestre dá o ponto quando uma complicação aparece, por heroísmo ou interpretação."""
    heroi["pontos_heroicos"] += 1
    heroi.setdefault("pontos_ganhos", []).append(motivo)
    return heroi["pontos_heroicos"]


def moribundo(heroi):
    """Teste de Fortitude CD 15 a cada rodada. 2 graus = estabilizado.
    3 graus de falha no total = morte. (Cap. 1, lido no PDF)"""
    heroi["condicoes"].append("Moribundo")
    heroi["graus_falha_morte"] = heroi.get("graus_falha_morte", 0)
    r = salvamento(heroi, "Fortitude", 15)
    if r["graus"] >= 2:
        heroi["condicoes"].remove("Moribundo")
        return {"estado": "estabilizado", "teste": r}
    if r["graus"] < 0:
        heroi["graus_falha_morte"] += -r["graus"]
    if heroi["graus_falha_morte"] >= 3:
        return {"estado": "morreu", "teste": r}
    return {"estado": "moribundo", "teste": r, "acumulado": heroi["graus_falha_morte"]}


# ============================================================ ESTADO
class Estado:
    ARQ = os.path.join(os.path.dirname(__file__), "estado.json")

    def __init__(self):
        self.d = {
            "caos": 5,
            "hora": "noite",
            "clima": "madrugada úmida, maré subindo fora de hora",
            "local": "Baía de Santa Clara",
            "heroi": None,
            "npdms": [],
            "tramas": [],
            "fatos": [],
            "sementes": [],
            "cena": {"nome": None, "testes": 0},
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
        h = d.get("heroi")
        linhas = [f"LOCAL: {d['local']} | HORA: {d['hora']} | CLIMA: {d['clima']}",
                  f"CAOS: {d['caos']}"]
        if h:
            der = h["defesas_totais"]
            linhas += [
                f"{h['codinome']} ({h['nome']}) — NP {h['np']} | {h['origem']}",
                f"Motivação: {h['motivacao']}  |  Pontos heroicos: {h['pontos_heroicos']}",
                "Habilidades: " + ", ".join(f"{k[:3].upper()} {v:+d}" for k, v in h["habilidades"].items()),
                f"Defesas: Esq {der['Esquiva']} · Apa {der['Aparar']} · For {der['Fortitude']} · "
                f"Von {der['Vontade']} · Res {der['Resistência']}",
                f"Poderes: " + ", ".join(
                    f"{n} ({p['efeito']} {p['grad']})" for n, p in h["poderes"].items()),
                f"Condições: {', '.join(h['condicoes']) or 'normal'}",
                f"Pontos de poder: {h['pontos_gastos']}/{h['pontos_orcamento']}",
            ]
            if h["complicacoes"]:
                linhas.append("Complicações: " + "; ".join(h["complicacoes"]))
        if d["npdms"]:
            linhas.append("PdMs conhecidos: " + "; ".join(d["npdms"]))
        if d["tramas"]:
            linhas.append("TRAMAS ABERTAS:")
            linhas += [f"  - {t}" for t in d["tramas"]]
        if d["sementes"]:
            linhas.append("SEMENTES (mudas por enquanto): " + "; ".join(d["sementes"]))
        return "\n".join(linhas)
