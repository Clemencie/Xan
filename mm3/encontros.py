"""
GERADOR DE ENCONTRO com FILTRO DE COERÊNCIA.

O sorteio passa por três filtros antes de virar cena:
  1. TERRENO — 9 tabelas, só entra o que existe naquele lugar;
  2. HORA — noite e madrugada mexem nos pesos (patrulha, contrabando, Coro);
  3. FORMA — ambiente não vira ficha, animal não vira gente, objeto não fala.

Cada encontro carrega uma ÂNCORA: o gancho de trama ao qual pertence.
Se a âncora não tocar nada já estabelecido, o encontro entra MUDO —
vira detalhe de cenário e semente. Nunca "pizza, abacaxi, hambúrguer".
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
    "manha":  {"Multidão filmando alguém com poder em pânico": 1.5,
               "Turista e camelô, dia normal, ninguém olha para o mar": 2.0,
               "Herói do Panteão fazendo aparição patrocinada": 1.5},
    "tarde":  {"Patrulha da AEGIS conferindo registros": 1.5,
               "Herói do Panteão gravando comercial na areia": 2.0,
               "Carro da Delegacia de Ocorrências Especiais": 1.5},
    "noite":  {"Assalto em andamento — três, sem poder": 2.0,
               "Estivadores da Linha Vermelha movendo contêiner sem etiqueta": 2.0,
               "Contrabando desembarcando na Praia do Naufrágio": 2.0,
               "Alguém cantando baixinho na esquina": 2.0,
               "Fuga por cima dos prédios": 1.5},
    "madrugada": {"Gente do Coro parada na arrebentação, de roupa, sem sair": 2.5,
                  "O Coro em procissão, descalço, cantando": 2.5,
                  "Água subindo pelo cais fora do horário de maré": 2.0,
                  "Maré subindo fora de hora, sem lua e sem vento": 2.0,
                  "Alguém cantando dentro de um contêiner fechado": 2.0,
                  "Assalto em andamento — três, sem poder": 1.5},
}


def encontrar(terreno, hora="noite", peso_narrativo=None):
    """Sorteia UM encontro coerente e devolve o dict pronto para narrar."""
    from mundo import ENCONTROS, FACCOES
    from heroi_npc import gerar, gerar_grupo, tier_por_peso

    terreno = terreno if terreno in ENCONTROS else "rua"
    itens = [dict(x) for x in ENCONTROS[terreno]]
    sorteado = _ponderado(itens, dict(AJUSTES_HORA.get(hora, {})))

    lo, hi = sorteado["np"]
    forma = sorteado["forma"]
    ambiental = (lo == 0 and hi == 0) or forma == "ambiente"

    if peso_narrativo is None:
        peso_narrativo = _r(10)
    tier = min(tier_por_peso(peso_narrativo), sorteado["tier"])

    ctx = f"Encontrado em {terreno}, {hora}."
    npcs = []

    if forma == "ambiente" or (ambiental and forma != "objeto"):
        # ambiente: nem ficha. Uma linha e uma semente.
        npcs.append({
            "forma": "ambiente", "tier": 0, "tier_nome": "Decoração",
            "nome": None, "rotulo": sorteado["que"], "faccao": "nenhuma", "np": 0,
            "o_que_acontece": "Isso não é coincidência. A cidade está contando alguma coisa.",
            "por_que_esta_aqui": ctx,
        })
        qtd = 1
    elif forma in ("objeto", "animal"):
        rotulo = sorteado["que"]
        n = gerar(sorteado["faccao"] or "civil", tier, np=None, forma=forma,
                  contexto=ctx, rotulo=rotulo,
                  np_min=lo if lo else 1, np_max=hi if hi else 20)
        n["rotulo"] = rotulo
        npcs.append(n)
        qtd = 1
    else:
        qlo, qhi = sorteado["qtd"]
        qtd = qlo if qlo == qhi else qlo + _r(qhi - qlo + 1) - 1
        if qtd == 1:
            npcs.append(gerar(sorteado["faccao"] or "civil", tier, np=None,
                              contexto=ctx, np_min=lo, np_max=hi))
        else:
            npcs = gerar_grupo(sorteado["faccao"] or "civil", qtd,
                               tier_lider=min(tier, 3), np_lider=None,
                               contexto=ctx, np_min=lo, np_max=hi)

    return {
        "o_que": sorteado["que"],
        "forma": forma,
        "ambiental": forma == "ambiente",
        "terreno": terreno,
        "hora": hora,
        "quantidade": qtd,
        "np_faixa": (lo, hi),
        "tier": tier if not (forma == "ambiente") else 0,
        "ancora": sorteado["ancora"],
        "faccao": (FACCOES.get(sorteado["faccao"], {}).get("nome")
                   if sorteado["faccao"] else "nenhuma"),
        "npcs": npcs,
        "peso_narrativo": peso_narrativo,
    }


def faísca():
    """Foco + Ação + Assunto, ancorados. Cru, para o jogador virar cena."""
    from mundo import FOCO_EVENTO, ACAO_EVENTO, ASSUNTO_EVENTO
    return {"foco": _pick(FOCO_EVENTO), "acao": _pick(ACAO_EVENTO),
            "assunto": _pick(ASSUNTO_EVENTO)}
