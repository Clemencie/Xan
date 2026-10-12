"""
REGRAS RÍGIDAS — técnicas, custos, degraus, dano, Qi.
Tudo aqui é matemática fechada: sem improviso.

Cada técnica tem uma CASA de origem ("casa"). Quem não é da casa não a conhece —
o gerador de NPC usa isso para impedir que um guarda da Corte Cinzenta apareça
usando Passo sobre Juncos, que é da Garça Branca.
"""
from mundo import DEGRAUS, degrau

COMUNS = "comum"          # qualquer um pode saber (não pertence a casa nenhuma)

# ---------------------------------------------------------------- TÉCNICAS
# casa     : facção dona da arte, ou None = genérica (o mundo inteiro conhece)
# rank     : degrau mínimo (1-9)
# custo    : Qi por uso
# dano     : "d10", "2d8"... ou None (utilitária)
# fadiga   : +estresse de meridianos por uso
# tipo     : ataque | defesa | movimento | interno | percepcao | especial
# raridade : comum | raro | proibida
TECNICAS = {
    # ================= BÁSICO UNIVERSAL (qualquer um aprende) =================
    "Respiração de Quatro Contas": {"casa": None, "rank": 1, "custo": 1, "dano": None, "fadiga": -2,
                              "tipo": "interno", "raridade": "comum",
                              "desc": "Quatro respirações contadas: devolve 1d4 Qi no meio da luta."},
    "Ouvido do Vale":          {"casa": None, "rank": 2, "custo": 3, "dano": None, "fadiga": 0,
                              "tipo": "percepcao", "raridade": "comum",
                              "desc": "Qi no tímpano: ouve passos através de parede, e conta quantos são."},
    "Corte das Sete Folhas":   {"casa": None, "rank": 2, "custo": 5, "dano": "d12", "fadiga": 2,
                              "tipo": "ataque", "raridade": "comum",
                              "desc": "Sete cortes curtos num único movimento de pulso. Difícil de bloquear, fácil de errar."},
    "Contagem Cega":           {"casa": "faca_cega", "rank": 3, "custo": 4, "dano": None, "fadiga": 0,
                              "tipo": "percepcao", "raridade": "comum",
                              "desc": "Pesa o Qi alheio como se pesa prata: diz o degrau de quem está na sala."},

    # ================= IRMANDADE DA FERRUGEM (bandidos) =================
    "Corte Sujo":              {"casa": "irmaos_ferrugem", "rank": 1, "custo": 2, "dano": "d8+1",
                              "fadiga": 1, "tipo": "ataque", "raridade": "comum",
                              "desc": "Golpe sem forma que mira tendão, joelho ou olho. Feito para terminar rápido."},
    "Punho de Corrente":       {"casa": "irmaos_ferrugem", "rank": 1, "custo": 3, "dano": "d10",
                              "fadiga": 1, "tipo": "ataque", "raridade": "comum",
                              "desc": "Sequência de três socos encadeados; o terceiro carrega o Qi dos dois primeiros."},
    "Passo de Barranco":       {"casa": "irmaos_ferrugem", "rank": 1, "custo": 2, "dano": None,
                              "fadiga": 0, "tipo": "movimento", "raridade": "comum",
                              "desc": "Qi nos pés: desce pedra molhada como se fosse degrau seco."},

    # ================= SEMEADORES DE CHUVA (curandeiros) =================
    "Palma que Fecha":         {"casa": "semeadores", "rank": 1, "custo": 4, "dano": None, "fadiga": 1,
                              "tipo": "defesa", "raridade": "comum",
                              "desc": "Pressiona a ferida com Qi e fecha carne. Cura 1d6 PV, deixa cicatriz."},
    "Agulha de Quatro Estações": {"casa": "semeadores", "rank": 2, "custo": 5, "dano": None, "fadiga": 1,
                              "tipo": "especial", "raridade": "raro",
                              "desc": "Três agulhas em pontos de meridiano. Paralisa um braço por 1d4 turnos (Vontade nega)."},
    "Chá dos Dez Passos":      {"casa": "semeadores", "rank": 3, "custo": 6, "dano": None, "fadiga": 0,
                              "tipo": "interno", "raridade": "raro",
                              "desc": "Uma xícara. Remove veneno conhecido e devolve 2d6 Qi. Uma vez por dia."},

    # ================= ALIANÇA DA GARÇA BRANCA (ortodoxa) =================
    "Passo de Cais":           {"casa": "faca_cega", "rank": 1, "custo": 2, "dano": None, "fadiga": 0,
                              "tipo": "movimento", "raridade": "comum",
                              "desc": "Andar de quem aprendeu a não escorregar em madeira molhada. Não cai, não faz barulho."},
    "Garça Rompe a Névoa":     {"casa": "alianca_garça", "rank": 2, "custo": 4, "dano": "d10+2",
                              "fadiga": 1, "tipo": "ataque", "raridade": "comum",
                              "desc": "Estocada única da Garça Branca: o braço estica além do que o ombro permite."},
    "Passo sobre Juncos":      {"casa": "alianca_garça", "rank": 2, "custo": 3, "dano": None,
                              "fadiga": 0, "tipo": "movimento", "raridade": "comum",
                              "desc": "Corre sobre água rasa e junco sem afundar. +2 em Defesa de Esquiva por 1 turno."},
    "Punho do Peso Falso":     {"casa": "faca_cega", "rank": 2, "custo": 4, "dano": "d8+1", "fadiga": 1,
                              "tipo": "ataque", "raridade": "comum",
                              "desc": "Soco curto de agiota: mira o fígado. Tira o ar do alvo por um turno."},
    "Palma do Rio Sereno":     {"casa": "alianca_garça", "rank": 3, "custo": 7, "dano": "d10+3",
                              "fadiga": 2, "tipo": "ataque", "raridade": "comum",
                              "desc": "Palmada lenta que empurra sem tocar. Derruba e afasta 2d4 passos."},
    "Espada dos Nove Reflexos": {"casa": "alianca_garça", "rank": 3, "custo": 8, "dano": "2d6",
                              "fadiga": 2, "tipo": "ataque", "raridade": "raro",
                              "desc": "Uma lâmina, nove imagens. O inimigo bloqueia oito; a nona é a de verdade."},

    # ================= ORDEM DO SINO SILENCIOSO =================
    "Sino sem Som":            {"casa": "sino_silencioso", "rank": 3, "custo": 9, "dano": None,
                              "fadiga": 3, "tipo": "defesa", "raridade": "raro",
                              "desc": "Um toque que não faz barulho anula todo som num raio de 5 passos — inclusive o seu grito."},
    "Passo da Neve sem Pegada": {"casa": "sino_silencioso", "rank": 3, "custo": 6, "dano": None,
                              "fadiga": 1, "tipo": "movimento", "raridade": "raro",
                              "desc": "Não deixa marca, não quebra galho, não desloca ar. Furtividade quase automática."},
    "Palma do Eco Atrasado":   {"casa": "sino_silencioso", "rank": 5, "custo": 13, "dano": "2d10",
                              "fadiga": 4, "tipo": "ataque", "raridade": "raro",
                              "desc": "O golpe acerta agora; a dor chega três respirações depois, dobrada."},

    # ================= PORTÃO CARMESIM =================
    "Palma da Cinza Quente":   {"casa": "portao_carmesim", "rank": 3, "custo": 8, "dano": "d12+2",
                              "fadiga": 3, "tipo": "ataque", "raridade": "comum",
                              "desc": "A mão esquenta até fumegar. Queimadura não fecha por cura comum."},
    "Garra das Sete Cicatrizes": {"casa": "portao_carmesim", "rank": 4, "custo": 10, "dano": "2d8",
                              "fadiga": 3, "tipo": "ataque", "raridade": "raro",
                              "desc": "Sete rasgos que não fecham. A ferida reabre em cada combate seguinte até tratada."},
    "Fio de Nove Agulhas":     {"casa": "portao_carmesim", "rank": 4, "custo": 11, "dano": "d10+4",
                              "fadiga": 3, "tipo": "ataque", "raridade": "raro",
                              "desc": "Agulhas lançadas em leque, guiadas por Qi. Ignora metade da armadura."},
    "Sutra do Sangue Quieto":  {"casa": "portao_carmesim", "rank": 5, "custo": 0, "dano": "2d10",
                              "fadiga": 0, "tipo": "ataque", "raridade": "proibida",
                              "desc": "Não gasta Qi: gasta PV (2d6). Rompe a Tábua I. Cada uso = +1 Dívida do Céu."},

    # ================= CORTE CINZENTA =================
    "Passo de Corte":          {"casa": "corte_cinza", "rank": 2, "custo": 3, "dano": None, "fadiga": 0,
                              "tipo": "movimento", "raridade": "comum",
                              "desc": "Passo cerimonioso de palácio: entra na sala sem que ninguém perceba que entrou."},
    "Selo Imperial Quebrado":  {"casa": "corte_cinza", "rank": 4, "custo": 9, "dano": None,
                              "fadiga": 2, "tipo": "especial", "raridade": "raro",
                              "desc": "Um selo no ar que trava uma técnica inimiga por um turno (oposição de Qi)."},
    "Lança do Portão Caído":   {"casa": "corte_cinza", "rank": 5, "custo": 14, "dano": "3d8",
                              "fadiga": 4, "tipo": "ataque", "raridade": "raro",
                              "desc": "Empurra a lança com o corpo inteiro: atravessa portão de madeira e o que estiver atrás."},

    # ================= SEM CASA (lendárias / perdidas) =================
    "Núcleo em Chamas":        {"casa": None, "rank": 5, "custo": 20, "dano": None, "fadiga": 6,
                              "tipo": "interno", "raridade": "raro",
                              "desc": "Queima o próprio núcleo: +1 degrau efetivo por 1d4+1 turnos. Depois, -1 degrau por um dia."},
    "Olho do Céu Rachado":     {"casa": None, "rank": 6, "custo": 18, "dano": None, "fadiga": 5,
                              "tipo": "percepcao", "raridade": "raro",
                              "desc": "Por um turno, você vê a técnica inimiga antes dela acontecer. Ignora uma Defesa."},
    "Nove Sóis no Vale":       {"casa": None, "rank": 7, "custo": 40, "dano": "6d10", "fadiga": 10,
                              "tipo": "ataque", "raridade": "raro",
                              "desc": "Nove lâminas de Qi caem do ar sobre um vale. A terra fica estéril por uma estação."},
    "Passo que Atravessa a Chuva": {"casa": None, "rank": 7, "custo": 25, "dano": None, "fadiga": 6,
                              "tipo": "movimento", "raridade": "raro",
                              "desc": "Uma passada cobre cem passos. A chuva não o molha porque ele não estava lá."},
    "Palma da Tábua Rachada":  {"casa": None, "rank": 8, "custo": 0, "dano": "8d10", "fadiga": 0,
                              "tipo": "ataque", "raridade": "proibida",
                              "desc": "Usa uma lei que não devia existir. Custo: um ano de vida por uso, e +3 Dívida do Céu."},
}

# técnicas que qualquer um pode aprender, independente de casa
def genericas(rank_max=9):
    return [n for n, t in TECNICAS.items()
            if t["casa"] is None and t["rank"] <= rank_max and t["raridade"] != "proibida"]


PROFICIENCIAS = ["Entrada", "Pequena Realização", "Grande Realização", "Perfeição"]
PROF_FX = {
    "Entrada":            {"dano": 1.0, "acerto": 0, "custo": 1.0, "nota": "funciona, mas você pensa antes"},
    "Pequena Realização": {"dano": 1.0, "acerto": 1, "custo": 1.0, "nota": "sai sem pensar"},
    "Grande Realização":  {"dano": 1.5, "acerto": 2, "custo": 0.75, "nota": "o corpo faz sozinho"},
    "Perfeição":          {"dano": 2.0, "acerto": 4, "custo": 0.5, "nota": "a técnica escolhe por você"},
}

# ---------------------------------------------------------------- ATRIBUTOS
ATRIBUTOS = ["Corpo", "Passo", "Mente", "Vontade"]
CUSTO_MOD = {-1: -1, 0: 0, 1: 2, 2: 4, 3: 7, 4: 12}   # orçamento: 6 pontos


def validar_criacao(distribuicao):
    """distribuicao: {'Corpo': mod, ...}. Retorna (ok, pontos_gastos, erros)."""
    erros = []
    if set(distribuicao) != set(ATRIBUTOS):
        erros.append("precisa distribuir exatamente Corpo, Passo, Mente, Vontade")
        return False, 0, erros
    total = 0
    for a, m in distribuicao.items():
        if m not in CUSTO_MOD:
            erros.append(f"{a}: modificador {m} fora da faixa (-1 a +4)")
            continue
        total += CUSTO_MOD[m]
    if total > 6:
        erros.append(f"orçamento estourado: {total}/6 pontos")
    return (len(erros) == 0 and total <= 6), total, erros


# ---------------------------------------------------------------- ESTILOS
ESTILOS = {
    "Espada":  {"arma": "espada", "dado": 8, "alcance": 1,
                "bonus": "Vantagem em bloqueio com lâmina.",
                "passiva": "+1 Defesa de Aparar quando empunha espada."},
    "Sabre":   {"arma": "sabre", "dado": 10, "alcance": 1,
                "bonus": "Ataque em área contra 2 alvos adjacentes.",
                "passiva": "Dano +2 quando ataca mais de um alvo no mesmo turno."},
    "Punho":   {"arma": "punhos", "dado": 6, "alcance": 0,
                "bonus": "Combo: acerto consecutivo dá +1 dano acumulado (máx +4).",
                "passiva": "Gasta 1 Qi a menos na primeira técnica de cada combate."},
    "Palma":   {"arma": "palma", "dado": 6, "alcance": 1,
                "bonus": "Impacto interno: ignora metade da armadura.",
                "passiva": "Técnicas internas custam 2 Qi a menos."},
    "Lança":   {"arma": "lança", "dado": 8, "alcance": 2,
                "bonus": "Ataca de 2 passos; inimigo adjacente te dá Desvantagem.",
                "passiva": "+2 em Defesa de Aparar contra armas de alcance 1."},
    "Chicote": {"arma": "corda/chicote", "dado": 6, "alcance": 2,
                "bonus": "Pode desarmar (oposição Corpo vs Corpo).",
                "passiva": "Alvo atingido fica -1 em Defesa por 1 turno."},
    "Arco":    {"arma": "arco", "dado": 8, "alcance": 12,
                "bonus": "Desvantagem em combate corpo a corpo.",
                "passiva": "Recarregar é ação livre uma vez por turno."},
}

# ---------------------------------------------------------------- ORIGENS
ORIGENS = {
    "Bastardo de casa nobre": {"bonus": {"Mente": 1}, "qi": 2, "pv": 4,
        "gancho": "Você tem um sobrenome que não pode dizer em voz alta."},
    "Discípulo expulso":      {"bonus": {"Corpo": 1}, "qi": 4, "pv": 6,
        "gancho": "Sua seita registrou sua morte. Você discorda."},
    "Soldado de guarnição":   {"bonus": {"Corpo": 1}, "qi": 0, "pv": 10,
        "gancho": "Você obedeceu a uma ordem que matou uma vila. O nome da vila era Folha Caída."},
    "Guarda de caravana":     {"bonus": {"Passo": 1}, "qi": 2, "pv": 6,
        "gancho": "A Faca Cega tem seu nome no livro. Você não sabe por quê."},
    "Herborista":             {"bonus": {"Mente": 1}, "qi": 4, "pv": 2,
        "gancho": "Você trata gente dos dois lados da guerra e já escondeu o homem errado."},
    "Mendigo de rede":        {"bonus": {"Passo": 1}, "qi": 2, "pv": 4,
        "gancho": "Você sabe o preço de três segredos. Ainda não vendeu nenhum."},
    "Caçador de serra":       {"bonus": {"Corpo": 1}, "qi": 2, "pv": 6,
        "gancho": "Você viu, uma vez, algo descer da montanha andando como gente."},
    "Ferreiro de lâminas":    {"bonus": {"Corpo": 1}, "qi": 0, "pv": 8,
        "gancho": "Você forjou uma lâmina que não aceita bainha comum. Ela está com outra pessoa."},
    "Médico itinerante":      {"bonus": {"Mente": 1}, "qi": 6, "pv": 2,
        "gancho": "Você já viu uma ferida que não foi feita por arma nenhuma."},
    "Ator de trupes":         {"bonus": {"Mente": 1}, "qi": 2, "pv": 4,
        "gancho": "Você decorou um manual inteiro para uma peça. Ninguém sabia que era verdadeiro."},
    "Condenado fugido":       {"bonus": {"Passo": 1}, "qi": 2, "pv": 8,
        "gancho": "Sua sentença era de cem anos. Faltavam noventa e três."},
    "Órfão de clã caído":     {"bonus": {"Vontade": 1}, "qi": 6, "pv": 4,
        "gancho": "Sobrou uma tábua de jade da sua família. Ela está rachada."},
}

# ---------------------------------------------------------------- TÁBUAS (física do mundo)
TABUAS = {
    "I":  "Qi corre nos meridianos. Canal vazio não carrega técnica: gastar Qi abaixo de 0 causa 1d6 de Contragolpe e não produz efeito.",
    "II": "Corpo não temperado estoura. Usar técnica de rank maior que o seu = +2 estresse de meridianos e Desvantagem no acerto.",
    "III": "Toda técnica tem Nome e o Nome cobra. Cada uso soma Fadiga; a 10 de Fadiga você perde a técnica até dormir.",
    "IV": "Qi de sangue paga com vida. Técnica Proibida: zero Qi, dano em PV próprio, e +1 Dívida do Céu por uso.",
    "V":  "Intenção vence força. Num duelo declarado (ambos conscientes e sem pressa), Mente substitui Corpo na Defesa.",
    "VI": "Ninguém vê acima de três degraus. Contra oponente 4+ degraus acima, você não pode mirar pontos fracos: Dano -6.",
    "VII": "A terra lembra. Em Ruínas e Templos, rolagens de Percepção recebem +2 e o Qi regenera pela metade.",
    "VIII": "Juramento pesa. Promessa feita com testemunha e palavra empenhada vira obrigação mecânica: quebrá-la = -1 em tudo por uma cena.",
    "IX": "Há um degrau acima do Último. Ninguém que chegou perto voltou para contar qual é o custo.",
}
