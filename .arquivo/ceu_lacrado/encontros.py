"""
GERADOR DE ENCONTRO com FILTRO DE COERÊNCIA.

O sorteio é limitado três vezes:
  1. TERRENO  — só entra o que existe naquele lugar;
  2. HORA/CLIMA — noite e chuva mexem nos pesos e cancelam encontros impossíveis;
  3. FORMA — rank (0,0) não tem corpo: é ambiente, nunca vira "NPC com segredo".

E cada encontro carrega uma ÂNCORA: o gancho de trama a que pertence.
Se não der para ancorar em nada estabelecido, o encontro entra MUDO —
vira detalhe ambiental e semente, nunca "pizza, abacaxi, hambúrguer".
"""
import secrets


def _r(n):
    return secrets.randbelow(n) + 1


def _pick(l):
    return l[_r(len(l)) - 1]


def _ponderado(itens, ajustes=None):
    pesos = []
    for it in itens:
        p = it["peso"]
        if ajustes:
            p = int(round(p * ajustes.get(it["que"], 1)))
        pesos.append(max(0, p))
    total = sum(pesos)
    if total == 0:
        return itens[0]
    alvo = secrets.randbelow(total) + 1
    acum = 0
    for it, p in zip(itens, pesos):
        acum += p
        if alvo <= acum:
            return it
    return itens[-1]


AJUSTES_HORA = {
    "amanhecer": {"Uma monja do Sino, calada, seguindo alguém": 1.5,
                  "Névoa que não se move contra o vento": 2.0,
                  "Névoa que devolve o som atrasado": 2.0,
                  "Deslizamento / trilha destruída": 1.3},
    "dia":       {"Patrulha da guarnição de Vau de Pedra Verde": 1.5,
                  "Guardas do portão exigindo taxa": 1.5,
                  "Mercador de jade com uma peça que não devia existir": 1.5,
                  "Duelo de honra marcado na praça": 1.5},
    "entardecer": {"Duelo de honra marcado na praça": 1.5,
                   "Bandidos de folga, bêbados, do Passo da Garoa": 1.5,
                   "Procissão funerária de alguém importante": 1.5},
    "noite":     {"Cães selvagens descendo da serra": 2.0,
                  "Gás de pântano acendendo sozinho": 2.5,
                  "Ladões de túmulos com um selo de jade": 2.0,
                  "Cobrador do Portão Carmesim": 2.0,
                  "Cobrador do Portão Carmesim disfarçado de estivador": 2.0,
                  "Um forasteiro que não tira o chapéu": 1.5},
}

CANCELADOS_POR_CHUVA_FORTE = {
    "Névoa que não se move contra o vento",
    "Névoa que devolve o som atrasado",
}


def encontrar(terreno, hora="dia", chuva=True, rank_grupo=None, peso_narrativo=None,
              rotulo_ambiente=None):
    """Sorteia UM encontro coerente e devolve dict pronto para narrar."""
    from mundo import ENCONTROS, FACCOES
    from npc import gerar_npc, gerar_grupo, tier_por_peso

    terreno = terreno if terreno in ENCONTROS else "estrada"
    itens = [dict(x) for x in ENCONTROS[terreno]]

    ajustes = dict(AJUSTES_HORA.get(hora, {}))
    if chuva:
        for k in CANCELADOS_POR_CHUVA_FORTE:
            ajustes[k] = 0
    sorteado = _ponderado(itens, ajustes)

    lo, hi = sorteado["rank"]
    ambiente = (lo == 0 and hi == 0)

    # FORMA manda no teto de profundidade
    if ambiente or sorteado.get("forma") == "sem_forma":
        forma = "sem_forma"
    elif sorteado.get("forma") == "nao_humano":
        forma = "fera"
    else:
        forma = "humano"

    # tier: dado pelo peso narrativo da cena, mas limitado pelo encontro E pela forma
    if peso_narrativo is None:
        peso_narrativo = _r(10)
    tier = min(tier_por_peso(peso_narrativo), sorteado["tier"])

    rank = None
    npcs = []
    if not ambiente:
        rank = rank_grupo or (lo if lo == hi else lo + _r(hi - lo + 1) - 1)
        qlo, qhi = sorteado["qtd"]
        qtd = qlo if qlo == qhi else qlo + _r(qhi - qlo + 1) - 1
        rotulo = sorteado["que"] if forma != "humano" else None
        ctx = f"Encontrado em {terreno}, {hora}."
        if qtd == 1 or forma != "humano":
            npcs.append(gerar_npc(sorteado["faccao"] or "errante", tier, rank=rank,
                                  contexto=ctx, forma=forma, rotulo=rotulo,
                                  rank_min=lo, rank_max=hi, mortal=(rank == 0)))
            qtd = 1
        else:
            npcs = gerar_grupo(sorteado["faccao"] or "errante", qtd,
                               tier_lider=min(tier, 3), rank_lider=rank,
                               contexto=ctx, forma=forma, rank_min=lo, rank_max=hi)
    else:
        qtd = 1
        # ambiente ganha uma linha de presença; vira semente, não ficha
        from npc import O_QUE_FAZ_SEM_FORMA
        npcs.append({
            "forma": "sem_forma", "tier": 0, "tier_nome": "Decoração",
            "mortal": True, "rank": 0, "rank_nome": "sem forma — não cultiva",
            "nome": None, "rotulo": sorteado["que"], "faccao": "nenhuma",
            "o_que_faz": _pick(O_QUE_FAZ_SEM_FORMA) if sorteado["tier"] == 0
                         else "Isso não é coincidência. A terra lembrou.",
            "por_que_esta_aqui": f"Ambiente em {terreno}, {hora}.",
        })

    return {
        "o_que": sorteado["que"],
        "forma": forma,
        "ambiental": ambiente,
        "terreno": terreno,
        "hora": hora,
        "quantidade": qtd,
        "rank_faixa": (lo, hi),
        "tier": tier if not ambiente else 0,
        "ancora": sorteado["ancora"],
        "faccao": (FACCOES.get(sorteado["faccao"], {}).get("nome") if sorteado["faccao"] else "nenhuma"),
        "npcs": npcs,
        "peso_narrativo": peso_narrativo,
    }


def faísca(tema=None):
    """Foco + Ação + Assunto, ancorados. Cru, para o jogador virar cena."""
    from mundo import FOCO_EVENTO, ACAO_EVENTO, ASSUNTO_EVENTO
    return {"foco": _pick(FOCO_EVENTO), "acao": _pick(ACAO_EVENTO),
            "assunto": _pick(ASSUNTO_EVENTO), "tema": tema}
