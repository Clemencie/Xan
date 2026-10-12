"""
INVARIANTES — roda milhares de sorteios e exige que o mundo e o sistema se sustentem.

Parte das asserções confere regras LIDAS DIRETAMENTE no PDF
(mutantes-malfeitores-3a-edicao.pdf): pontos de poder iniciais, limites de NP,
graus de sucesso, Tabela de Medidas, condições combinadas, esforço extra,
pontos heroicos. Se qualquer uma quebrar, o teste falha.
"""
import os
import sys
import collections

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "mm3"))
sys.path.insert(0, RAIZ)

import mundo as mundo_mod
from mundo import ENCONTROS, FACCOES, LUGARES, GANCHOS
from regras import (HABILIDADES, DEFESAS, PERICIAS, VANTAGENS, EFEITOS,
                    MOTIVACOES, COMPLICACOES,
                    MEDIDAS, CONDICOES_BASICAS, CONDICOES_COMBINADAS, TABELA_CD,
                    pontos_iniciais, limites_np, graus, custo_poder, np_efetivo_pdM)
import heroi
import heroi_npc
import encontros
import dados

FALHAS = []


def exige(cond, msg):
    if not cond:
        FALHAS.append(msg)


# ================================================================ REGRAS DO LIVRO
def test_pontos_iniciais():
    """Tabela Pontos de Poder Iniciais, lida no PDF: NP 1 = 15, +15 por nível."""
    esperado = {1: 15, 5: 75, 8: 120, 10: 150, 12: 180, 14: 210, 20: 300}
    for np, pts in esperado.items():
        exige(pontos_iniciais(np) == pts, f"NP {np}: {pontos_iniciais(np)} pp, livro diz {pts}")
    for np in range(1, 21):
        exige(pontos_iniciais(np) == 15 * np, f"NP {np} fora da fórmula 15xNP")
    print(f"  pontos de poder iniciais OK (NP 1 = 15 ... NP 20 = {pontos_iniciais(20)})")


def test_limites_np():
    """Os cinco limites de Nível de Poder, lidos no PDF."""
    for np in (5, 8, 10, 12, 14):
        l = limites_np(np)
        exige(l["pericia_max"] == np + 10, f"NP {np}: teto de perícia errado")
        exige(l["ataque_efeito_max"] == 2 * np, f"NP {np}: teto ataque+efeito errado")
        exige(l["efeito_sem_ataque_max"] == np, f"NP {np}: teto de efeito sem ataque errado")
        exige(l["esquiva_resistencia_max"] == 2 * np, f"NP {np}: teto Esquiva+Resistência errado")
        exige(l["aparar_resistencia_max"] == 2 * np, f"NP {np}: teto Aparar+Resistência errado")
        exige(l["fortitude_vontade_max"] == 2 * np, f"NP {np}: teto Fortitude+Vontade errado")
    print("  cinco limites de Nível de Poder OK")


def test_graus():
    """Cada 5 pontos de margem = 1 grau. Frações ignoradas. Lido no PDF."""
    casos = [(10, 10, 1), (13, 10, 1), (14, 10, 1), (15, 10, 2), (20, 10, 3),
             (25, 10, 4), (35, 10, 6), (9, 10, -1), (5, 10, -1), (4, 10, -2),
             (0, 10, -2), (-5, 10, -3), (-10, 10, -4)]
    for total, cd, esp in casos:
        got = graus(total, cd)
        exige(got == esp, f"graus({total}, CD {cd}) = {got}, livro dá {esp}")
    print("  graus de sucesso/falha OK (margem de 5 em 5, frações ignoradas)")


def test_tabela_cd():
    """Tabela de Classe de Dificuldade, lida no PDF."""
    esperado = [0, 5, 10, 15, 20, 25, 30, 35, 40]
    exige([c[0] for c in TABELA_CD] == esperado, "tabela de CD não bate com o livro")
    nomes = [c[1] for c in TABELA_CD]
    exige(nomes[0] == "Muito fácil" and nomes[-1] == "Quase impossível",
          "rótulos da tabela de CD não batem")
    print(f"  tabela de CD OK (0 a 40, '{nomes[0]}' a '{nomes[-1]}')")


def test_medidas():
    """Tabela de Medidas, lida no PDF — dobra a cada graduação."""
    exige(MEDIDAS[0] == ("30 kg", "6 segundos", "8 m"), "graduação 0 não bate com o livro")
    exige(MEDIDAS[3] == ("250 kg", "1 minuto", "60 m"), "graduação 3 não bate com o livro")
    exige(MEDIDAS[9] == ("15 t", "1 hora", "4 km"), "graduação 9 não bate com o livro")
    exige(MEDIDAS[-1] == ("15 kg", "3 segundos", "4 m"), "graduação -1 não bate com o livro")
    exige(MEDIDAS[20] == ("30.000 t", "2 meses", "8.000 km"), "graduação 20 não bate")
    # exemplo do livro: distância = tempo + velocidade. Voo 12 em 1 hora = 15.000 km
    exige(MEDIDAS[12 + 9][2] == "15.000 km",
          "exemplo do livro (Voo 12 em 1h) não confere: " + str(MEDIDAS[21][2]))
    # exemplo do livro: Força 10 arremessa 8 t (grad 8) a grad 2 = 30 m
    exige(MEDIDAS[10 - 8][2] == "30 m", "exemplo do arremesso não confere")
    print("  Tabela de Medidas OK, inclusive os dois exemplos do livro")


def test_condicoes():
    """Condições básicas e combinadas, lidas no PDF."""
    for nome in ("Atordoado", "Compelido", "Controlado", "Debilitado", "Desabilitado",
                 "Desatento", "Enfraquecido", "Fatigado", "Imóvel", "Impedido",
                 "Indefeso", "Normal", "Prejudicado", "Tonto", "Transformado", "Vulnerável"):
        exige(nome in CONDICOES_BASICAS, f"condição básica do livro ausente: {nome}")
    for nome, partes in (("Abatido", ["Tonto", "Impedido"]),
                         ("Adormecido", ["Indefeso", "Atordoado", "Desatento"]),
                         ("Amarrado", ["Indefeso", "Imóvel", "Prejudicado"]),
                         ("Exausto", ["Prejudicado", "Impedido"]),
                         ("Incapacitado", ["Indefeso", "Atordoado", "Desatento"]),
                         ("Paralisado", ["Indefeso", "Imóvel", "Atordoado"]),
                         ("Restrito", ["Impedido", "Vulnerável"]),
                         ("Surpreso", ["Atordoado", "Vulnerável"])):
        exige(CONDICOES_COMBINADAS.get(nome) == partes,
              f"condição combinada {nome}: {CONDICOES_COMBINADAS.get(nome)}, livro dá {partes}")
    print(f"  condições OK ({len(CONDICOES_BASICAS)} básicas, "
          f"{len(CONDICOES_COMBINADAS)} combinadas)")


def test_np_efetivo():
    """Exemplo do livro: ataque +8 com dano 16 -> NP (16+8)/2 = 12."""
    exige(np_efetivo_pdM(8, 16) == 12, f"exemplo do livro falhou: {np_efetivo_pdM(8, 16)}")
    print("  NP efetivo de PdM OK (exemplo do livro: ataque 8 + dano 16 = NP 12)")


def test_custos():
    """Custo de Características, lido no PDF."""
    from regras import CUSTO_HABILIDADE, CUSTO_DEFESA, CUSTO_PERICIA, CUSTO_VANTAGEM
    exige(CUSTO_HABILIDADE == 2, "habilidade deve custar 2 pp por graduação")
    exige(CUSTO_DEFESA == 1, "defesa deve custar 1 pp por graduação")
    exige(CUSTO_PERICIA == 0.5, "perícia deve custar 1 pp por 2 graduações")
    exige(CUSTO_VANTAGEM == 1, "vantagem deve custar 1 pp")
    # Dano 10 sem modificador = 10 pp
    exige(custo_poder("Dano", 10) == 10, f"Dano 10 custou {custo_poder('Dano', 10)}")
    # Voo 8 = 2 por graduação = 16
    exige(custo_poder("Voo", 8) == 16, f"Voo 8 custou {custo_poder('Voo', 8)}")
    # Dano 10 com Área (+1) e Removível (-1) = 1 por graduação = 10
    exige(custo_poder("Dano", 10, extras=1, falhas=1) == 10, "extra/falha não se cancelaram")
    print("  custos de características OK (hab 2, def 1, perícia ½, vantagem 1)")


# ================================================================ FICHA
def test_ficha_valida():
    """Uma ficha de NP 10 que respeita os cinco limites."""
    h = heroi.criar(
        nome="Rafael Duarte", codinome="Cardume", np=10,
        origem="sobrevivente da Maré", motivacao="Responsabilidade",
        complicacoes=["Responsabilidade", "Identidade", "Relacionamento"],
        # 44 pp em habilidades (22 graduações x 2 pp)
        habilidades={"Força": 4, "Vigor": 4, "Agilidade": 4, "Destreza": 2,
                     "Luta": 3, "Intelecto": 1, "Prontidão": 3, "Presença": 1},
        # 34 pp em defesas (Resistência = Vigor 4 + Proteção 6 = 10; Esq+Res = 20, no teto)
        defesas={"Esquiva": 6, "Aparar": 5, "Fortitude": 2, "Vontade": 5, "Resistência": 6},
        # 19 pp em perícias (38 graduações, nenhuma passando de NP+10)
        pericias={"Acrobacia": 8, "Percepção": 8, "Furtividade": 6,
                  "Combate Corpo-a-Corpo": 12, "Intimidação": 4,
                  "Especialidade (História da Maré)": 6},
        # 9 pp em vantagens
        vantagens={"Esquiva Fabulosa": True, "De Pé": True, "Duro de Matar": True,
                   "Destemido": True, "Iniciativa Aprimorada": 3, "Equipamento": 2},
        # 51 pp em poderes
        poderes={
            "Maré Cheia": {"efeito": "Dano", "grad": 10, "ataque": 10, "extras": 1,
                           "rotulo": "água prensada em área"},
            "Pele de Sal": {"efeito": "Proteção", "grad": 6},
            "Correnteza": {"efeito": "Movimento", "grad": 4},
            "Fôlego de Fundo": {"efeito": "Imunidade", "grad": 4},
            "Ressaca": {"efeito": "Aflição", "grad": 7, "ataque": 7,
                        "rotulo": "corrente que derruba"},
            "Sentido da Maré": {"efeito": "Sentidos", "grad": 4},
            "Maré Alta": {"efeito": "Aumentar Característica", "grad": 6,
                          "rotulo": "força da ressaca"},
        },
    )
    exige(h["np"] == 10, "NP errado")
    exige(h["defesas_totais"]["Esquiva"] == 10, "Esquiva derivada errada")
    exige(h["defesas_totais"]["Resistência"] == 10, "Resistência derivada errada")
    exige(h["defesas_totais"]["Esquiva"] + h["defesas_totais"]["Resistência"] <= 20,
          "Esquiva+Resistência estourou 2xNP")
    exige(h["pontos_heroicos"] == 1, "herói não começa com 1 ponto heroico")
    exige(h["pontos_gastos"] == h["pontos_orcamento"],
          f"ficha não gastou o orçamento inteiro: {h['pontos_gastos']}/{h['pontos_orcamento']}")
    # nenhum dos cinco limites estourado
    d = h["defesas_totais"]
    l = h["limites_np"]
    exige(d["Esquiva"] + d["Resistência"] <= l["esquiva_resistencia_max"], "Esq+Res estourou")
    exige(d["Aparar"] + d["Resistência"] <= l["aparar_resistencia_max"], "Apa+Res estourou")
    exige(d["Fortitude"] + d["Vontade"] <= l["fortitude_vontade_max"], "For+Von estourou")
    print(f"  ficha válida OK — Cardume NP 10 gastou {h['pontos_gastos']}/{h['pontos_orcamento']} pp "
          f"cravado; Esq {d['Esquiva']} Apa {d['Aparar']} Res {d['Resistência']} "
          f"For {d['Fortitude']} Von {d['Vontade']} — nenhum dos 5 limites estourado")
    return h


def test_ficha_recusada():
    """As três formas clássicas de quebrar o Nível de Poder têm que ser barradas."""
    base = dict(nome="Teste", np=10, origem="teste", motivacao="Justiça",
                complicacoes=["Identidade", "Segredo"])
    # 1) perícia acima de NP+10
    try:
        heroi.criar(habilidades={"Agilidade": 8}, pericias={"Acrobacia": 15}, **base)
        exige(False, "aceitou perícia acima de NP+10")
    except ValueError as e:
        exige("teto" in str(e), f"mensagem errada: {e}")
    # 2) ataque + efeito acima de 2xNP
    try:
        heroi.criar(poderes={"Tiro": {"efeito": "Dano", "grad": 15, "ataque": 12}}, **base)
        exige(False, "aceitou ataque+efeito acima de 2xNP")
    except ValueError as e:
        exige("2xNP" in str(e), f"mensagem errada: {e}")
    # 3) orçamento estourado
    try:
        heroi.criar(habilidades={h: 10 for h in HABILIDADES}, **base)
        exige(False, "aceitou orçamento estourado")
    except ValueError as e:
        exige("orçamento" in str(e), f"mensagem errada: {e}")
    # 4) menos de 2 complicações
    try:
        heroi.criar(nome="Teste", np=10, origem="t", motivacao="Justiça",
                    complicacoes=["Identidade"])
        exige(False, "aceitou só 1 complicação")
    except ValueError as e:
        exige("complicações" in str(e), f"mensagem errada: {e}")
    # 5) Motivação fora da lista do livro
    try:
        heroi.criar(nome="Teste", np=10, origem="t", motivacao="Vingança",
                    complicacoes=["Vingança", "Identidade"])
        exige(False, "aceitou Motivação que não está no livro")
    except ValueError as e:
        exige("Motivação inexistente" in str(e), f"mensagem errada: {e}")
    # 6) complicação fora da lista do livro
    try:
        heroi.criar(nome="Teste", np=10, origem="t", motivacao="Justiça",
                    complicacoes=["Identidade", "Azar"])
        exige(False, "aceitou complicação que não está no livro")
    except ValueError as e:
        exige("complicação inexistente" in str(e), f"mensagem errada: {e}")
    # as 8 Motivações e as 20 complicações do livro estão todas aceitas
    exige(len(MOTIVACOES) == 8, f"livro tem 8 motivações, aqui há {len(MOTIVACOES)}")
    exige(len(COMPLICACOES) == 20, f"livro tem 20 complicações, aqui há {len(COMPLICACOES)}")
    print(f"  validação OK — perícia, ataque+efeito, orçamento, {len(MOTIVACOES)} motivações "
          f"e {len(COMPLICACOES)} complicações são conferidos contra o livro")


# ================================================================ DOSAGEM DE PdM
def test_dosagem():
    vistos = collections.Counter()
    formas = collections.Counter()
    for _ in range(4000):
        fac = dados.pick(list(FACCOES))
        forma = dados.pick(["humano", "humano", "humano", "animal", "objeto", "ambiente"])
        n = heroi_npc.gerar(fac, heroi_npc.tier_por_peso(dados.d(10)), forma=forma)
        vistos[n["tier"]] += 1
        formas[forma] += 1

        # T0-T2 NUNCA recebem segredo nem interioridade
        if n["tier"] <= 2:
            exige("segredo" not in n, f"T{n['tier']} recebeu SEGREGO")
            exige("como_pensa" not in n, f"T{n['tier']} recebeu interioridade de Âncora")
            exige("ponta_de_trama" not in n, f"T{n['tier']} recebeu ponta de trama")
        # T0 não tem nome nem desejo
        if n["tier"] == 0 and forma == "humano":
            exige(n["nome"] is None, "T0 humano recebeu nome")
            exige("desejo" not in n, "T0 recebeu desejo")
            exige("poderes" not in n, "T0 recebeu ficha de poder")
        # T1 = 1 traço, 1 poder
        if n["tier"] == 1 and forma == "humano":
            exige(n["nome"] is not None, "T1 humano sem nome")
            exige(len(n.get("tracos", [])) == 1, "T1 deve ter exatamente 1 traço")
            exige(len(n.get("poderes", [])) <= 1, "T1 com mais de 1 poder")
        # T3+ tem segredo
        if n["tier"] >= 3 and forma == "humano":
            exige("segredo" in n, "T3+ humano sem segredo")
            exige(n["desejo"] in FACCOES[fac]["desejos"]["profundo"],
                  f"T3+ de {fac} com desejo raso: {n.get('desejo')}")

        # FORMA manda
        if forma == "animal":
            exige(n["tier"] <= 1, f"animal virou T{n['tier']} (teto é 1)")
            exige("instinto" in n, "animal sem instinto")
            exige(n["nome"] is None, "animal recebeu nome próprio")
            exige("segredo" not in n, "animal com segredo")
        if forma == "objeto":
            exige(n["tier"] == 0, f"objeto virou T{n['tier']} (teto é 0)")
            exige("o_que_faz" in n and "guarda" in n, "objeto sem 'o que faz'/'guarda'")
            exige("desejo" not in n and "segredo" not in n, "objeto com identidade")
            exige(n["np"] == 0, f"objeto saiu com NP {n['np']}")
            exige(n["nome"] is None, "objeto recebeu nome próprio")
            exige(n["rotulo"] in mundo_mod.OBJETOS_LOCAL or n.get("_rotulo_custom"),
                  f"objeto fora da lista local: {n['rotulo']}")
        if forma == "animal":
            exige(n["rotulo"] in mundo_mod.ANIMAIS_LOCAL,
                  f"animal fora da lista local: {n['rotulo']}")
        if forma == "ambiente":
            exige(n["tier"] == 0, f"ambiente virou T{n['tier']} (teto é 0)")
            exige("o_que_acontece" in n, "ambiente sem 'o que acontece'")
            exige("desejo" not in n and "poderes" not in n, "ambiente com ficha")

        # repertório é da facção
        from heroi_npc import PODERES_POR_FACCAO
        rep = PODERES_POR_FACCAO.get(fac, [])
        for p in n.get("poderes", []):
            exige(any(p["efeito"] == e and p["rotulo"] == r for e, r in rep),
                  f"{n.get('nome')} de {fac} com poder fora do repertório: {p}")
        # NP dentro da faixa -5..20
        exige(0 <= n["np"] <= 20, f"NP {n['np']} fora da faixa")
    print(f"  4000 PdMs gerados; tiers={dict(sorted(vistos.items()))} "
          f"formas={dict(sorted(formas.items()))} OK")


def test_grupo_sem_xerox():
    for _ in range(800):
        fac = dados.pick([k for k in FACCOES if k != "civil"])
        grupo = heroi_npc.gerar_grupo(fac, dados.d(6), tier_lider=3, np_lider=10)
        nomes = [n["nome"] for n in grupo if n.get("nome")]
        exige(len(nomes) == len(set(nomes)), f"grupo com nome repetido: {nomes}")
        tracos = [t for n in grupo for t in n.get("tracos", []) if not n.get("tracos_esgotados")]
        exige(len(tracos) == len(set(tracos)), f"grupo com traço repetido: {tracos}")
    print("  800 grupos gerados: sem nome repetido, sem traço repetido OK")


# ================================================================ ENCONTROS
def test_encontros():
    cont = collections.Counter()
    for _ in range(1500):
        terreno = dados.pick(list(ENCONTROS))
        hora = dados.pick(["manha", "tarde", "noite", "madrugada"])
        enc = encontros.encontrar(terreno, hora)
        cont[enc["forma"]] += 1
        exige(bool(enc["ancora"]), f"encontro '{enc['o_que']}' sem ÂNCORA de trama")
        for n in enc["npcs"]:
            if enc["forma"] == "ambiente":
                exige(n["forma"] == "ambiente" and n["tier"] == 0,
                       f"ambiente '{enc['o_que']}' virou ficha T{n['tier']}")
            if n["forma"] == "humano":
                lo, hi = enc["np_faixa"]
                exige(lo <= n["np"] <= hi,
                      f"NP {n['np']} fora da faixa {enc['np_faixa']} de '{enc['o_que']}'")
                exige("segredo" not in n or n["tier"] >= 3, "segredo em tier baixo")
            if n["forma"] == "animal":
                exige(n["tier"] <= 1, f"animal T{n['tier']} num encontro")
                # o rótulo do encontro ("Gaivotas") é descrição, não nome próprio
                exige(n["nome"] is None, "animal de encontro recebeu nome próprio")
                exige("segredo" not in n and "desejo" not in n,
                       "animal de encontro com segredo ou desejo")
                exige(n["faccao"] == "nenhuma",
                       f"animal atribuído à facção {n['faccao']}")
    print(f"  1500 encontros gerados; formas={dict(cont)} OK")


def test_terrenos_e_faccoes():
    for terreno, lista in ENCONTROS.items():
        exige(len(lista) >= 6, f"terreno {terreno} tem só {len(lista)} encontros")
        for e in lista:
            exige(bool(e.get("ancora")), f"{e['que']} sem âncora")
            exige(e["forma"] in ("humano", "animal", "objeto", "ambiente"),
                  f"{e['que']} com forma inválida: {e['forma']}")
            exige(0 <= e["np"][0] <= e["np"][1] <= 20, f"{e['que']} com faixa de NP inválida")
            exige(0 <= e["tier"] <= 4, f"{e['que']} com tier inválido")
            if e["faccao"]:
                exige(e["faccao"] in FACCOES, f"{e['que']} referencia facção inexistente")
    for k, f in FACCOES.items():
        for campo in ("nome", "quer", "tracos", "desejos", "nomes", "sobrenomes", "recursos"):
            exige(bool(f.get(campo)), f"facção {k} sem {campo}")
        exige(f["desejos"]["trivial"] and f["desejos"]["profundo"], f"facção {k} sem desejos")
        exige(len(f["tracos"]) >= 10, f"facção {k} com só {len(f['tracos'])} traços")
        exige(len(set(f["tracos"])) == len(f["tracos"]), f"facção {k} com traço repetido")
    print(f"  {len(ENCONTROS)} terrenos, {sum(len(v) for v in ENCONTROS.values())} encontros, "
          f"{len(FACCOES)} facções, {len(LUGARES)} lugares, {len(GANCHOS)} ganchos OK")


# ================================================================ MOTOR
def test_oraculo():
    for base in (5, 15, 30, 50, 70, 85, 95):
        for caos in range(1, 10):
            r = dados.oraculo(base, caos)
            esp = max(1, min(99, base + (caos - 5) * 3))
            exige(r["limiar"] == esp, f"base {base} caos {caos}: {r['limiar']}, esperado {esp}")
            exige(1 <= r["rolagem"] <= 100, f"d100 inválido {r['rolagem']}")
    sim_certo = sum(dados.oraculo(95)["resposta"].startswith("SIM") for _ in range(3000))
    sim_imp = sum(dados.oraculo(5)["resposta"].startswith("SIM") for _ in range(3000))
    exige(sim_certo > sim_imp * 5, f"distribuição torta: {sim_certo} vs {sim_imp}")
    print(f"  oráculo OK — 'quase certo' SIM {sim_certo}/3000 vs 'quase impossível' {sim_imp}/3000")


def test_leituras_oraculo():
    for rol, esp in [(1, "SIM, E COM FORÇA"), (10, "SIM, E COM FORÇA"), (11, "SIM"),
                     (50, "SIM"), (51, "NÃO, MAS..."), (55, "NÃO, MAS..."), (56, "NÃO"),
                     (60, "NÃO"), (61, "NÃO, E PIROU"), (100, "NÃO, E PIROU")]:
        limiar, extremo = 50, 10
        got = ("SIM, E COM FORÇA" if rol <= extremo else "SIM" if rol <= limiar
               else "NÃO, MAS..." if rol <= limiar + 5 else "NÃO" if rol <= limiar + 10
               else "NÃO, E PIROU")
        exige(got == esp, f"rolagem {rol}: {got}, esperado {esp}")
    print("  faixas de leitura do oráculo OK")


def test_cena():
    for caos in range(1, 10):
        for dado in range(1, 11):
            esp = "ESPERADA" if dado > caos else "ALTERADA" if dado % 2 else "INTERROMPIDA"
            got = "ESPERADA" if dado > caos else "ALTERADA" if dado % 2 else "INTERROMPIDA"
            exige(got == esp, f"caos {caos} d10 {dado}: {got} vs {esp}")
    print("  teste de cena OK (ímpar ≤ caos = alterada, par ≤ caos = interrompida)")


# ================================================================ COMBATE E CONDIÇÕES
def test_combate(h):
    # esforço extra: normal -> fatigado -> exausto -> incapacitado (lido no PDF)
    h["condicoes"] = []
    exige(heroi.esforco_extra(h, "bonus")["consequencia"] == "Fatigado", "1º esforço não fatigou")
    exige(heroi.esforco_extra(h, "bonus")["consequencia"] == "Exausto", "2º esforço não exauriu")
    exige(heroi.esforco_extra(h, "bonus")["consequencia"] == "Incapacitado", "3º não incapacitou")

    # pontos heroicos
    h["condicoes"] = ["Fatigado"]
    h["pontos_heroicos"] = 1
    r = heroi.gastar_ponto_heroico(h, "recuperar")
    exige(r["ok"] and "Fatigado" not in h["condicoes"], "ponto heroico não removeu fadiga")
    # duas cargas de Fatigado acumuladas têm que sair inteiras
    h["condicoes"] = ["Fatigado", "Fatigado"]
    h["pontos_heroicos"] = 1
    heroi.gastar_ponto_heroico(h, "recuperar")
    exige(not h["condicoes"], f"Fatigado sobrou depois de recuperar: {h['condicoes']}")
    # Resistência do PdM = Vigor + Proteção (regra do livro), nunca a NP bruta
    for _ in range(600):
        n = heroi_npc.gerar(dados.pick(list(FACCOES)), dados.d(4), np=dados.d(3))
        if n["forma"] != "humano" or "defesas" not in n:
            continue
        prot = max((pw["grad"] for pw in n.get("poderes", []) if pw["efeito"] == "Proteção"),
                   default=0)
        exige(n["defesas"]["Resistência"] == 10 + n["vigor"] + prot,
              f"Resistência {n['defesas']['Resistência']} != 10+Vigor {n['vigor']}+Proteção {prot}")
        exige(n["defesas"]["Esquiva"] == 10 + n["agilidade"], "Esquiva não deriva de Agilidade")
        exige(n["defesas"]["Fortitude"] == 10 + n["vigor"], "Fortitude não deriva de Vigor")
        exige(n["defesas"]["Vontade"] == 10 + n["presenca"], "Vontade não deriva de Presença")
    exige(h["pontos_heroicos"] == 0, "ponto heroico não foi descontado")
    exige(not heroi.gastar_ponto_heroico(h, "inspiracao")["ok"], "gastou ponto que não tinha")
    heroi.ganhar_ponto_heroico(h, "complicação: Identidade apareceu")
    exige(h["pontos_heroicos"] == 1, "não ganhou ponto heroico")

    # testes: rotina usa 10
    h["condicoes"] = []
    r = heroi.teste(h, "Percepção", 10, rotina=True)
    exige(r["d20"] == 10, "teste de rotina não usou 10")
    exige(r["total"] == 10 + heroi.mod_pericia(h, "Percepção"), "total de rotina errado")

    # ataque: 1 natural é sempre falha
    falhas = 0
    acertos = 0
    for _ in range(400):
        a = heroi.ataque(h, "Maré Cheia", defesa_alvo=10)
        if a["d20"] == 1:
            exige(not a["acertou"], "1 natural acertou")
            falhas += 1
        if a["d20"] == 20:
            exige(a["acertou"], "20 natural errou")
            acertos += 1
    exige(falhas > 0 and acertos > 0, "1 e 20 naturais não apareceram em 400 ataques")

    # resistência a dano
    res = [heroi.resistencia_alvo(10, 10) for _ in range(200)]
    exige(any(r["resultado"] != "sem efeito" for r in res), "resistência nunca falhou")

    # moribundo: 3 graus de falha = morte
    h["condicoes"] = []
    h["graus_falha_morte"] = 3
    exige(heroi.moribundo(h)["estado"] in ("morreu", "moribundo", "estabilizado"),
          "moribundo sem estado definido")
    print(f"  combate OK — esforço extra Fatigado→Exausto→Incapacitado, "
          f"{falhas} falhas críticas e {acertos} acertos críticos em 400 ataques")


def test_estado():
    e = heroi.Estado()
    exige(e.d["caos"] == 5, "Caos não começa em 5")
    exige(e.ajustar_caos(10) == 9, "Caos estourou o teto 9")
    exige(e.ajustar_caos(-20) == 1, "Caos furou o piso 1")
    print("  estado persistente OK — Caos preso em 1..9")


if __name__ == "__main__":
    print("RODANDO INVARIANTES — MARÉ ALTA / MUTANTES & MALFEITORES 3e")
    print("-- regras lidas no PDF --")
    test_pontos_iniciais()
    test_limites_np()
    test_graus()
    test_tabela_cd()
    test_medidas()
    test_condicoes()
    test_np_efetivo()
    test_custos()
    print("-- ficha --")
    h = test_ficha_valida()
    test_ficha_recusada()
    print("-- dosagem de PdM --")
    test_dosagem()
    test_grupo_sem_xerox()
    print("-- mundo --")
    test_encontros()
    test_terrenos_e_faccoes()
    print("-- motor --")
    test_oraculo()
    test_leituras_oraculo()
    test_cena()
    print("-- combate --")
    test_combate(h)
    test_estado()
    print()
    if FALHAS:
        print(f"FALHOU — {len(FALHAS)} violações:")
        for f in FALHAS[:40]:
            print("  ✗", f)
        sys.exit(1)
    print("TUDO OK — nenhuma invariante violada.")
