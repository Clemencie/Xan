"""
GERADOR DE NPC — profundidade DOSADA e FORMA CONSCIENTE.

Regra 1 — ninguém gasta pensamento em obstáculo.
O tier de profundidade é decidido por dado (peso narrativo), não por capricho:

  T0 DECORAÇÃO   -> sem nome, sem desejo, 1 linha. Bandido nº3, cão, névoa.
  T1 OBSTÁCULO   -> nome + 1 traço + 1 desejo trivial. Bandido de estrada, guarda.
  T2 COADJUVANTE -> nome + 2 traços + desejo + 1-2 técnicas + gancho curto.
  T3 PEÇA-CHAVE  -> nome + 3 traços + desejo profundo + segredo + 2-4 técnicas.
  T4 ÂNCORA      -> tudo acima + como pensa + o que esconde de si + ponta de trama.

Regra 2 — a FORMA manda no que existe:
  humano     -> nome, desejo, segredo (conforme o tier).
  fera       -> instinto no lugar de desejo. Sem nome, sem segredo, nunca acima de T1.
  sem forma  -> nem nome, nem desejo, nem técnica decorada: só o que faz. Nunca acima de T0.

Regra 3 — a FACÇÃO manda no repertório. Um discípulo da Garça Branca não usa
"Corte Sujo" de bandido: ele usa as artes da própria casa, e só as que o
degrau dele já alcança.
"""
import secrets


def _r(n):
    return secrets.randbelow(n) + 1


def _pick(l):
    return l[_r(len(l)) - 1]


def _picks(l, qtd):
    pool = list(l)
    out = []
    for _ in range(min(qtd, len(pool))):
        out.append(pool.pop(_r(len(pool)) - 1))
    return out


def tier_por_peso(peso_narrativo):
    """peso_narrativo é um d10 rolado pela ferramenta.
    1-2 = T0 | 3-4 = T1 | 5-7 = T2 | 8-9 = T3 | 10 = T4."""
    if peso_narrativo <= 2:
        return 0
    if peso_narrativo <= 4:
        return 1
    if peso_narrativo <= 7:
        return 2
    if peso_narrativo <= 9:
        return 3
    return 4


# teto de tier por forma: o dado decide, mas o mundo limita
TETO_FORMA = {"humano": 4, "fera": 1, "sem_forma": 0}

INSTINTOS = {
    "fera": ["fome", "defender a cria", "fugir do fogo", "marcar território", "caçar o mais lento"],
    "sem_forma": ["repetir o último gesto que viu alguém fazer ali", "impedir que se leve algo",
                  "apagar o que for escrito no local", "esperar"],
}

O_QUE_FAZ_SEM_FORMA = [
    "Toma a forma de quem morreu ali e repete os últimos passos.",
    "Não ataca: empurra. Cada toque desloca ar de um lugar onde não há ninguém.",
    "Cobra Qi: quem gasta Qi perto dele alimenta o que ele é.",
    "Devolve, atrasado, todo som feito naquele círculo.",
    "Faz as feridas antigas de quem entra abrirem de novo, na mesma ordem.",
]


def gerar_npc(faccao, tier, rank=None, papel=None, contexto=None, forma="humano",
              rotulo=None, rank_min=1, rank_max=9, mortal=False,
              evitar_tracos=()):
    """Retorna dict do NPC na profundidade que o tier pede — e só nela."""
    from mundo import FACCOES, degrau as _deg
    from regras import TECNICAS, PROFICIENCIAS

    f = FACCOES.get(faccao) or FACCOES["errante"]

    # o dado decide o tier; a forma impõe o teto
    if tier == "auto":
        tier = tier_por_peso(_r(10))
    tier = max(0, min(4, tier))
    tier = min(tier, TETO_FORMA.get(forma, 4))

    if rank is None:
        base = f.get("degrau_lider") or 1
        rank = base - _r(3) + 1
    rank = max(rank_min, min(rank_max, rank))
    deg = _deg(rank)
    if rank == 0:
        mortal = True

    # bicho e coisa sem forma não pertencem a facção nenhuma
    nome_faccao = "nenhuma" if forma in ("fera", "sem_forma") else f["nome"]
    npc = {
        "forma": forma,
        "mortal": mortal,
        "tier": tier,
        "tier_nome": ["Decoração", "Obstáculo", "Coadjuvante", "Peça-chave", "Âncora"][tier],
        "rotulo": rotulo,
        "nome": None,
        "faccao": nome_faccao,
        "papel": papel or f["tipo"],
        "rank": rank,
        "rank_nome": deg["nome"],
        "qi": deg["qi"] if tier >= 2 else max(1, deg["qi"] // 2),
        "pv": deg["pv"] if tier >= 2 else max(1, deg["pv"] // 2),
    }

    # ---------- SEM FORMA: nada de identidade. Só o que faz.
    if forma == "sem_forma":
        npc["o_que_faz"] = _pick(O_QUE_FAZ_SEM_FORMA)
        npc["nome"] = rotulo
        npc["rank_nome"] = "sem forma — não cultiva"
        npc["rank"] = 0
        npc["qi"] = 0
        npc["perigo"] = f"equivalente a um praticante de rank {rank} para quem gastar Qi perto"
        if contexto:
            npc["por_que_esta_aqui"] = contexto
        return npc

    # ---------- FERA: instinto, sem nome, sem segredo
    if forma == "fera":
        # fera não cultiva: o "rank" aqui é só o tamanho do perigo
        npc["nome"] = rotulo
        npc["rank_nome"] = rotulo or "fera de Qi"
        npc["instinto"] = _pick(INSTINTOS["fera"])
        npc["ataque_natural"] = rotulo or "garras e dentes"
        npc["dano_fera"] = f"1d{4 + 2 * min(4, max(1, rank))}"
        npc["pv"] = max(3, 2 * max(1, rank) + _r(4))
        if contexto:
            npc["por_que_esta_aqui"] = contexto
        return npc

    # ---------- HUMANO
    if mortal:
        # mortal comum: sem cultivo. Obstáculo de verdade, não de mentira.
        npc["rank_nome"] = "Mortal (sem cultivo)"
        npc["qi"] = 0
        npc["pv"] = max(2, 4 + _r(4))
        npc["dano_mortal"] = "1d6"
        if tier >= 1:
            npc["nome"] = f"{_pick(f['nomes'])} {_pick(f['sobrenomes'])}"
            npc["tracos"] = _picks(f["traços"], 1)
            npc["desejo"] = _pick(f["desejos"]["trivial"])
        npc["nota_mortal"] = "Não tem Qi nem técnica. Só tem faca, número e pressa."
        if contexto:
            npc["por_que_esta_aqui"] = contexto
        return npc

    # nome: só T1+
    if tier >= 1:
        npc["nome"] = f"{_pick(f['nomes'])} {_pick(f['sobrenomes'])}"

    # traços
    n_tracos = [0, 1, 2, 3, 4][tier]
    if n_tracos:
        # dois homens do mesmo bando não podem ter a mesma cara
        disponiveis = [t for t in f["traços"] if t not in evitar_tracos]
        if disponiveis:
            npc["tracos"] = _picks(disponiveis, n_tracos)
        else:
            # o repertório de caras do bando acabou: este vira rosto comum
            npc["tracos_esgotados"] = True
            npc["tracos"] = ["rosto comum — nada nele gruda na memória"]

    # técnicas: repertório da facção, filtrado pelo degrau
    n_tec = [0, 1, 2, 3, 4][tier]
    if n_tec:
        from regras import genericas as _genericas
        if faccao == "errante":
            # sem bandeira: o que sabe, aprendeu de alguém — mistura tudo que o degrau alcança
            pool = [n for n, t in TECNICAS.items()
                    if t["rank"] <= rank and t["raridade"] != "proibida"]
        else:
            da_casa = [a for a in f["artes"]
                       if a in TECNICAS and TECNICAS[a]["rank"] <= rank]
            pool = da_casa or _genericas(rank)
        escolhidas = _picks(pool, n_tec)
        npc["tecnicas"] = escolhidas
        if faccao == "errante":
            npc["nota_tecnica"] = "Sem casa: cada técnica dele veio de um lugar diferente."
        elif not [a for a in f["artes"] if a in TECNICAS and TECNICAS[a]["rank"] <= rank]:
            npc["nota_tecnica"] = "Sem arte da casa no degrau dele: improvisa o básico que qualquer um aprende."
        elif tier == 1:
            npc["nota_tecnica"] = "Uma técnica só, gasta, repetida até gastar mais ainda."
        if tier >= 2:
            teto = [0, 0, 1, 2, 3][tier]
            npc["proficiencia"] = {t: PROFICIENCIAS[min(teto, _r(teto + 1) - 1)] for t in escolhidas}

    # desejo: trivial em T1, da facção em T2, profundo em T3+
    if tier == 1:
        npc["desejo"] = _pick(f["desejos"]["trivial"])
    elif tier == 2:
        npc["desejo"] = _pick(f["desejos"]["trivial"] + f["desejos"]["profundo"])
    elif tier >= 3:
        npc["desejo"] = _pick(f["desejos"]["profundo"])

    # segredo: SÓ T3+
    if tier >= 3:
        npc["segredo"] = f["segredo"] or _pick([
            "vendeu alguém da própria facção e ainda recebe por isso",
            "já foi discípulo do lado oposto",
            "sabe onde está uma Tábua falsa — porque ajudou a fazer",
        ])
        alvo = "alguém sem bandeira" if faccao == "errante" else f["nome"]
        npc["gancho1"] = f"Se alguém puxar o assunto '{f['quer'].rstrip('.').lower()}', ele mente mal."
        npc["gancho2"] = f"Deve algo a {alvo} e o prazo está acabando."

    # T4: interioridade + ponta de trama
    if tier == 4:
        npc["como_pensa"] = _pick([
            "Acredita que a ordem vale mais que as pessoas, e já pagou caro por essa crença.",
            "Trata crueldade como contabilidade: sem raiva, só números.",
            "Coleciona gentilezas que fez e cobra cada uma no momento pior.",
            "Já escolheu o lado que vai perder e vai até o fim por teimosia, não por fé.",
        ])
        npc["esconde_de_si"] = _pick([
            "que quer ser perdoado por alguém que já morreu",
            "que continua lutando porque não sabe fazer mais nada",
            "que tem medo do que vai encontrar se vencer",
            "que já foi exatamente igual a você, e perdeu",
        ])
        npc["ponta_de_trama"] = (
            f"{f['nome']}: {f['quer']} — e {f['segredo']}" if f["segredo"]
            else f"{f['nome']}: {f['quer']}"
        )

    if contexto:
        npc["por_que_esta_aqui"] = contexto
    return npc


def gerar_grupo(faccao, qtd, tier_lider=None, rank_lider=None, contexto=None,
                forma="humano", rank_min=1, rank_max=9):
    """Grupo coerente: o líder carrega o tier alto; capangas são T0/T1 (obstáculo puro).
    rank_min/rank_max travam o grupo dentro da faixa que o encontro declarou."""
    from mundo import FACCOES
    f = FACCOES.get(faccao) or FACCOES["errante"]
    base = rank_lider or max(rank_min, min(rank_max, (f.get("degrau_lider") or 2) - _r(2) + 1))
    grupo = []
    vistos = []          # traços já usados: nenhum capanga é xerox do outro
    nomes = []           # e nenhum tem o mesmo nome
    if tier_lider is not None and tier_lider > 0:
        lid = gerar_npc(faccao, tier_lider, rank=base, papel="líder",
                        contexto=contexto, forma=forma,
                        rank_min=rank_min, rank_max=rank_max)
        vistos += lid.get("tracos", [])
        if lid.get("nome"):
            nomes.append(lid["nome"])
        grupo.append(lid)
    for i in range(max(0, qtd - (1 if grupo else 0))):
        rank_cap = max(rank_min, min(rank_max, base - _r(2)))
        n = gerar_npc(faccao, _r(2) - 1, rank=rank_cap,
                      papel="capanga", contexto=contexto, forma=forma,
                      rank_min=rank_min, rank_max=rank_max,
                      mortal=(rank_cap == 0), evitar_tracos=vistos)
        # nome repetido dentro do mesmo bando? sorteia outro
        for _ in range(6):
            if not n.get("nome") or n["nome"] not in nomes:
                break
            n = gerar_npc(faccao, n["tier"], rank=rank_cap, papel="capanga",
                          contexto=contexto, forma=forma, rank_min=rank_min,
                          rank_max=rank_max, mortal=(rank_cap == 0),
                          evitar_tracos=vistos)
        vistos += [t for t in n.get("tracos", []) if not n.get("tracos_esgotados")]
        if n.get("nome"):
            nomes.append(n["nome"])
        grupo.append(n)
    return grupo
