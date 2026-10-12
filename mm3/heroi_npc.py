"""
GERADOR DE PdM — profundidade DOSADA, agora sobre Mutantes & Malfeitores.

Regra 1 — ninguém gasta pensamento em obstáculo.
O d10 de Peso Narrativo decide o tier, e o mundo impõe o teto:

  T0 DECORAÇÃO   -> sem nome, sem desejo, sem ficha. "O terceiro capanga."
  T1 OBSTÁCULO   -> nome + 1 traço + 1 desejo trivial + 1 poder simples (se tiver poder).
  T2 COADJUVANTE -> nome + 2 traços + desejo + poderes + equipamento.
  T3 PEÇA-CHAVE  -> + desejo profundo + SEGREDO + complicações + 2 ganchos.
  T4 ÂNCORA      -> + como pensa + o que esconde de si + ponta de trama.

Regra 2 — a FORMA manda no que existe:
  humano   -> nome, desejo, segredo (conforme o tier).
  animal   -> teto T1. Instinto no lugar de desejo. Sem nome, sem segredo.
  objeto   -> teto T0. Sem nome, sem desejo. Só o que faz e o que guarda.
  ambiente -> teto T0. Nem isso: só o que acontece.

Regra 3 — o livro manda: PdM NÃO é limitado pelo Nível de Poder da série e não
precisa somar pontos. O NP efetivo dele é (ataque + efeito) / 2. Isso é o que a
ferramenta calcula e mostra.

Regra 4 — a FAÇÃO manda no repertório. Agente da AEGIS não anda com frasco de
água do mar; gente do Coro não anda com colete balístico.
"""
import secrets

from regras import EFEITOS, np_efetivo_pdM
import mundo


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
    """1-2 = T0 | 3-4 = T1 | 5-7 = T2 | 8-9 = T3 | 10 = T4."""
    if peso_narrativo <= 2:
        return 0
    if peso_narrativo <= 4:
        return 1
    if peso_narrativo <= 7:
        return 2
    if peso_narrativo <= 9:
        return 3
    return 4


TETO_FORMA = {"humano": 4, "animal": 1, "objeto": 0, "ambiente": 0}

INSTINTOS = ["fome", "defender o território", "fugir do barulho", "proteger a cria",
             "seguir o cheiro de sangue", "marcar passagem"]

# poderes plausíveis por facção — o repertório é da casa, não do mundo
PODERES_POR_FACCAO = {
    "aegis": [("Dano", "pistola de contenção"), ("Aflição", "algema de contenção"),
              ("Sentidos", "visor de varredura"), ("Proteção", "colete balístico"),
              ("Movimento", "tirolesa")],
    "panteao": [("Dano", "rajada"), ("Voo", "voo"), ("Proteção", "campo pessoal"),
                ("Aumentar Característica", "força aumentada"), ("Sentidos", "visão ampliada"),
                ("Ilusão", "glamour de câmera")],
    "ressaca": [("Dano", "o que tiver na mão"), ("Movimento", "escalar parede"),
                ("Aumentar Característica", "corpo fechado"), ("Sentidos", "ouvido de morro"),
                ("Cura", "benzedeira"), ("Ilusão", "despiste")],
    "coro": [("Aflição", "a letra da música"), ("Comunicação", "falar com a água"),
             ("Ilusão", "a maré que não está lá"), ("Sentidos", "ouvir o que vem do mar"),
             ("Cura", "mão salgada"), ("Ambiente", "a água sobe")],
    "linha_vermelha": [("Dano", "arma de fogo"), ("Enfraquecer", "dose de poeira"),
                       ("Aumentar Característica", "poeira queimando"),
                       ("Proteção", "chapa de contêiner"), ("Sentidos", "olho de negociador")],
    "delegacia": [("Dano", "revólver de serviço"), ("Sentidos", "olhar de interrogatório"),
                  ("Proteção", "colete"), ("Aflição", "algema")],
    "instituto": [("Sentidos", "instrumentação"), ("Compreender", "ler o dado da Maré"),
                  ("Criar", "campo de contenção"), ("Dano", "descarga de laboratório")],
    "civil": [("Aumentar Característica", "adrenalina"), ("Dano", "pau de vassoura")],
}

DESEJOS_TRIVIAIS_PADRAO = ["chegar em casa inteiro", "não se meter nisso", "terminar o turno"]


def _deriva_defesas(pdm, np, poderes):
    """Defesas derivadas das habilidades base, como no livro.

    Esquiva <- Agilidade, Aparar <- Luta, Fortitude <- Vigor,
    Vontade <- Presença, Resistência <- Vigor + graduações de Proteção.
    """
    prot = max((pw["grad"] for pw in poderes if pw["efeito"] == "Proteção"), default=0)
    pdm["agilidade"] = np // 2
    pdm["luta"] = np // 2
    pdm["vigor"] = np // 3
    pdm["presenca"] = np // 3
    pdm["defesas"] = {"Esquiva": 10 + pdm["agilidade"],
                      "Aparar": 10 + pdm["luta"],
                      "Fortitude": 10 + pdm["vigor"],
                      "Vontade": 10 + pdm["presenca"],
                      "Resistência": 10 + pdm["vigor"] + prot}


def gerar(faccao, tier, np=None, forma="humano", papel=None, contexto=None,
          rotulo=None, np_min=0, np_max=20, evitar_tracos=()):
    """Retorna o PdM na profundidade que o tier pede — e só nela."""
    from mundo import FACCOES
    f = FACCOES.get(faccao) or FACCOES["civil"]

    if tier == "auto":
        tier = tier_por_peso(_r(10))
    tier = max(0, min(4, tier))
    tier = min(tier, TETO_FORMA.get(forma, 4))

    if np is None:
        base = f.get("np_lider") or 2
        np = max(1, base - _r(3) + 1)
    np = max(np_min, min(np_max, np))

    # bicho, objeto e ambiente não pertencem a facção nenhuma
    nome_faccao = f["nome"] if forma == "humano" else "nenhuma"
    pdm = {
        "forma": forma,
        "tier": tier,
        "tier_nome": ["Decoração", "Obstáculo", "Coadjuvante", "Peça-chave", "Âncora"][tier],
        "rotulo": rotulo,
        "nome": None,
        "faccao": nome_faccao,
        "papel": papel or f["tipo"],
        "np": np,
        "tem_poder": faccao not in ("civil",) and np >= 5,
    }

    # ---------- AMBIENTE: nem ficha tem. Só o que acontece.
    if forma == "ambiente":
        pdm["np"] = 0
        pdm["o_que_acontece"] = _pick([
            "Alguma coisa cede, cai, ou abre — e há gente embaixo.",
            "O som some por dois segundos. Depois volta dobrado.",
            "A água sobe onde não devia subir.",
            "Uma luz acende num lugar que está sem energia há anos.",
            "O chão está molhado e ninguém derramou nada.",
        ])
        if contexto:
            pdm["por_que_esta_aqui"] = contexto
        return pdm

    # ---------- OBJETO: sem nome, sem desejo. Só o que faz e o que guarda.
    if forma == "objeto":
        pdm["o_que_faz"] = _pick([
            "Continua funcionando depois que tudo em volta parou.",
            "Registra. Alguém vai querer esse registro.",
            "Está ligado a alguma coisa que ainda está ligada.",
            "Não devia estar aqui. Foi trazido.",
        ])
        pdm["guarda"] = _pick([
            "a prova de que alguém mentiu", "um número que não bate",
            "o nome de alguém que ainda está vivo", "uma gravação de quinze anos atrás",
            "a dose que mantém alguém de pé",
        ])
        # objeto não tem nome próprio e não tem NP — é cenário que reage
        pdm["rotulo"] = rotulo or _pick(mundo.OBJETOS_LOCAL)
        pdm["np"] = 0
        if contexto:
            pdm["por_que_esta_aqui"] = contexto
        return pdm

    # ---------- ANIMAL: instinto, sem nome, sem segredo.
    if forma == "animal":
        # bicho não tem nome próprio — o rótulo é a espécie, e fica no campo rotulo
        pdm["rotulo"] = rotulo or _pick(mundo.ANIMAIS_LOCAL)
        pdm["instinto"] = _pick(INSTINTOS)
        pdm["dano"] = max(1, np // 2)
        pdm["esquiva"] = 10 + np // 2
        pdm["resistencia"] = 10 + np // 3
        if contexto:
            pdm["por_que_esta_aqui"] = contexto
        return pdm

    # ---------- HUMANO
    if tier >= 1:
        pdm["nome"] = f"{_pick(f['nomes'])} {_pick(f['sobrenomes'])}"

    n_tracos = [0, 1, 2, 3, 4][tier]
    if n_tracos:
        disp = [t for t in f["tracos"] if t not in evitar_tracos]
        if disp:
            pdm["tracos"] = _picks(disp, n_tracos)
        else:
            pdm["tracos_esgotados"] = True
            pdm["tracos"] = ["rosto comum — nada nele gruda na memória"]

    # poderes: repertório da facção, dimensionado pelo NP
    n_pod = [0, 1, 1, 2, 3][tier]
    if n_pod and pdm["tem_poder"]:
        rep = PODERES_POR_FACCAO.get(faccao, [("Dano", "o que tiver na mão")])
        escolhidos = _picks(rep, n_pod)
        pdm["poderes"] = [
            {"efeito": e, "rotulo": r,
             "grad": max(1, np - _r(3) + 1) if e == "Dano" else max(1, np - _r(4) + 1)}
            for e, r in escolhidos
        ]
        atq = max(2, np - _r(4) + 2)
        dano = max(1, pdm["poderes"][0]["grad"])
        pdm["ataque"] = atq
        pdm["np_efetivo"] = round(np_efetivo_pdM(atq, dano), 1)
        # Regra do livro: Esquiva e Aparar vêm de Agilidade/Luta, Fortitude de Vigor,
        # Vontade de Presença e Resistência de Vigor + graduações de Proteção.
        _deriva_defesas(pdm, np, pdm["poderes"])
        if tier <= 1:
            pdm["nota_poder"] = "Um poder só, usado sempre do mesmo jeito."
    elif n_pod and not pdm["tem_poder"]:
        pdm["sem_poder"] = True
        pdm["nota"] = "Sem poder nenhum. Tem ferramenta, número e pressa."
        pdm["equipamento"] = _picks(f["recursos"], min(2, len(f["recursos"])))
        pdm["ataque"] = max(1, np)
        pdm["np_efetivo"] = round(np_efetivo_pdM(pdm["ataque"], max(1, np // 2)), 1)
        _deriva_defesas(pdm, np, [])

    # desejo: trivial em T1, da facção em T2, profundo em T3+
    if tier == 1:
        pdm["desejo"] = _pick(f["desejos"]["trivial"] or DESEJOS_TRIVIAIS_PADRAO)
    elif tier == 2:
        pdm["desejo"] = _pick(f["desejos"]["trivial"] + f["desejos"]["profundo"])
    elif tier >= 3:
        pdm["desejo"] = _pick(f["desejos"]["profundo"])

    # segredo: SÓ T3+
    if tier >= 3:
        pdm["segredo"] = f["segredo"] or _pick([
            "vendeu alguém da própria organização e ainda recebe por isso",
            "já esteve do outro lado",
            "sabe quem vazou a lista",
        ])
        pdm["complicacoes"] = _picks([
            "Identidade", "Inimigo", "Responsabilidade", "Segredo", "Reputação",
            "Relacionamento", "Obsessão", "Honra", "Fraqueza", "Vício",
        ], 2)
        pdm["gancho1"] = f"Se alguém puxar '{f['quer'].rstrip('.').lower()}', ele mente mal."
        alvo = "alguém de fora" if faccao == "civil" else f["nome"]
        pdm["gancho2"] = f"Deve algo a {alvo} e o prazo está acabando."

    # T4: interioridade + ponta de trama
    if tier == 4:
        pdm["como_pensa"] = _pick([
            "Acredita que a ordem vale mais que as pessoas — e já pagou por isso.",
            "Trata crueldade como contabilidade: sem raiva, só números.",
            "Coleciona favores que fez e cobra no pior momento possível.",
            "Já escolheu o lado que vai perder e vai até o fim por teimosia, não por fé.",
            "Faz a coisa certa do jeito errado e dorme bem com isso.",
        ])
        pdm["esconde_de_si"] = _pick([
            "que quer ser perdoado por alguém que morreu na Maré",
            "que continua nisso porque não sabe fazer mais nada",
            "que tem medo do que vai encontrar se vencer",
            "que já foi exatamente igual a você — e perdeu",
            "que ainda espera o mar devolver alguém",
        ])
        pdm["ponta_de_trama"] = (
            f"{f['nome']}: {f['quer']} — e {f['segredo']}" if f["segredo"]
            else f"{f['nome']}: {f['quer']}"
        )

    if contexto:
        pdm["por_que_esta_aqui"] = contexto
    return pdm


def gerar_grupo(faccao, qtd, tier_lider=None, np_lider=None, contexto=None,
                forma="humano", np_min=0, np_max=20):
    """Grupo coerente: o líder carrega o tier alto; capangas são T0/T1 (obstáculo puro).
    Sem nome repetido e sem traço repetido dentro do mesmo grupo."""
    from mundo import FACCOES
    f = FACCOES.get(faccao) or FACCOES["civil"]
    base = np_lider or max(np_min, min(np_max, (f.get("np_lider") or 2) - _r(2) + 1))
    grupo, vistos, nomes = [], [], []

    if tier_lider is not None and tier_lider > 0:
        lid = gerar(faccao, tier_lider, np=base, papel="líder", contexto=contexto,
                    forma=forma, np_min=np_min, np_max=np_max)
        vistos += lid.get("tracos", [])
        if lid.get("nome"):
            nomes.append(lid["nome"])
        grupo.append(lid)

    for _ in range(max(0, qtd - (1 if grupo else 0))):
        np_cap = max(np_min, min(np_max, base - _r(3)))
        n = gerar(faccao, _r(2) - 1, np=np_cap, papel="capanga", contexto=contexto,
                  forma=forma, np_min=np_min, np_max=np_max, evitar_tracos=vistos)
        for _ in range(6):
            if not n.get("nome") or n["nome"] not in nomes:
                break
            n = gerar(faccao, n["tier"], np=np_cap, papel="capanga", contexto=contexto,
                      forma=forma, np_min=np_min, np_max=np_max, evitar_tracos=vistos)
        vistos += [t for t in n.get("tracos", []) if not n.get("tracos_esgotados")]
        if n.get("nome"):
            nomes.append(n["nome"])
        grupo.append(n)
    return grupo
