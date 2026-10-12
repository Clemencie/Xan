"""
MUTANTES & MALFEITORES 3ª EDIÇÃO — núcleo de regras.

Fontes: o PDF "mutantes-malfeitores-3a-edicao.pdf" (Steve Kenson, trad. Jambô)
forneceu — verificado por leitura direta — a Tabela de Medidas, a tabela de CD,
graus de sucesso, testes de rotina/opostos/comparativos/graduados, modificadores
de circunstância, condições, esforço extra, pontos heroicos, pontos de poder
iniciais, custo de características e os cinco limites de Nível de Poder.

Os capítulos de detalhe que o extrator não devolveu (Perícias, Vantagens, Poderes,
Ação & Aventura, Mestrando) estão implementados a partir do sistema publicado;
cada bloco diz qual é a fonte. Nada aqui é invenção de casa: se não está no livro,
está marcado como ADENDO.
"""

# ============================================================ HABILIDADES (Cap. 3)
# 2 pontos de poder por graduação. Faixa -5 a 20. 0 = mediano, 7 = ápice humano.
HABILIDADES = {
    "Força":      {"abrev": "FOR", "mede": "Força física, levantar, arremessar, dano corpo-a-corpo"},
    "Vigor":      {"abrev": "VIG", "mede": "Saúde, resistência, Fortitude, veneno, fadiga"},
    "Agilidade":  {"abrev": "AGI", "mede": "Coordenação, equilíbrio, Esquiva, acrobacia"},
    "Destreza":   {"abrev": "DES", "mede": "Mira, mão firme, ataques à distância"},
    "Luta":       {"abrev": "LUT", "mede": "Combate corpo-a-corpo, Aparar"},
    "Intelecto":  {"abrev": "INT", "mede": "Raciocínio, conhecimento, tecnologia"},
    "Prontidão":  {"abrev": "PRO", "mede": "Sentidos, percepção, iniciativa"},
    "Presença":   {"abrev": "PRE", "mede": "Força de personalidade, interação, Vontade"},
}
CUSTO_HABILIDADE = 2

# ============================================================ DEFESAS (Cap. 3)
# 1 ponto de poder por +1 além da graduação básica dada pela habilidade.
DEFESAS = {
    "Esquiva":    {"base": "Agilidade", "tipo": "ativa",  "contra": "ataques à distância"},
    "Aparar":     {"base": "Luta",      "tipo": "ativa",  "contra": "ataques corpo-a-corpo"},
    "Fortitude":  {"base": "Vigor",     "tipo": "salvamento", "contra": "veneno, doença, físico"},
    "Vontade":    {"base": "Presença",  "tipo": "salvamento", "contra": "efeitos mentais"},
    "Resistência": {"base": "Vigor",    "tipo": "salvamento", "contra": "dano"},
}
CUSTO_DEFESA = 1

# ============================================================ PERÍCIAS (Cap. 4)
# 1 ponto de poder por 2 graduações. Total (habilidade + perícia + vantagem) <= NP + 10.
PERICIAS = {
    "Acrobacia":           {"hab": "Agilidade",  "tipo": "movimento", "treinada": False},
    "Atletismo":           {"hab": "Força",      "tipo": "movimento", "treinada": False},
    "Combate à Distância": {"hab": "Destreza",   "tipo": "combate",   "treinada": False},
    "Combate Corpo-a-Corpo": {"hab": "Luta",     "tipo": "combate",   "treinada": False},
    "Enganação":           {"hab": "Presença",   "tipo": "interação", "treinada": False},
    "Especialidade":       {"hab": "Intelecto",  "tipo": "conhecimento", "treinada": True},
    "Furtividade":         {"hab": "Agilidade",  "tipo": "manipulação", "treinada": False},
    "Intimidação":         {"hab": "Presença",   "tipo": "interação", "treinada": False},
    "Intuição":            {"hab": "Prontidão",  "tipo": "interação", "treinada": False},
    "Investigação":        {"hab": "Intelecto",  "tipo": "conhecimento", "treinada": False},
    "Percepção":           {"hab": "Prontidão",  "tipo": "manipulação", "treinada": False},
    "Persuasão":           {"hab": "Presença",   "tipo": "interação", "treinada": False},
    "Prestidigitação":     {"hab": "Destreza",   "tipo": "manipulação", "treinada": True},
    "Tecnologia":          {"hab": "Intelecto",  "tipo": "conhecimento", "treinada": True},
    "Tratamento":          {"hab": "Intelecto",  "tipo": "conhecimento", "treinada": True},
    "Veículos":            {"hab": "Destreza",   "tipo": "movimento", "treinada": False},
}
CUSTO_PERICIA = 0.5   # 1 pp por 2 graduações

# ============================================================ VANTAGENS (Cap. 5)
# 1 ponto de poder por vantagem ou graduação de vantagem.
VANTAGENS = {
    "Ação em Movimento":   {"grad": False, "efeito": "Move-se sem penalidade antes/depois da ação padrão"},
    "Ataque Acurado":      {"grad": True,  "efeito": "Troca -2 de ataque por +2 de efeito (por graduação)"},
    "Ataque Defensivo":    {"grad": False, "efeito": "-2 de ataque, +2 em Esquiva e Aparar até o próximo turno"},
    "Ataque Dominó":       {"grad": False, "efeito": "Acerto crítico também em 19 (e 18 na segunda graduação)"},
    "Ataque Imprudente":   {"grad": False, "efeito": "+2 de ataque, -2 em Esquiva e Aparar"},
    "Ataque Poderoso":     {"grad": True,  "efeito": "Troca -1 de ataque por +1 de dano (por graduação)"},
    "Ataque Preciso":      {"grad": True,  "efeito": "Ignora penalidade de circunstância no ataque (por graduação)"},
    "Atraente":            {"grad": False, "efeito": "+2 em testes de interação com quem se atrai por você"},
    "Bem Informado":       {"grad": False, "efeito": "Teste de Especialidade para saber algo que deveria saber"},
    "Bem Relacionado":     {"grad": False, "efeito": "Teste de Persuasão para obter favor de um contato"},
    "Benefício":           {"grad": True,  "efeito": "Riqueza, autorização, status — definido com o mestre"},
    "Capanga":             {"grad": False, "efeito": "Um capanga pode absorver um ataque dirigido a você"},
    "Contatos":            {"grad": True,  "efeito": "Rede de informantes; teste de Especialidade por ajuda"},
    "Crítico Aprimorado":  {"grad": True,  "efeito": "Amplia a faixa de crítico do ataque escolhido"},
    "De Pé":               {"grad": False, "efeito": "Levanta-se como ação livre"},
    "Defesa Aprimorada":   {"grad": True,  "efeito": "+1 em Esquiva ou Aparar (por graduação)"},
    "Derrubar Aprimorado": {"grad": False, "efeito": "Não fica vulnerável ao derrubar"},
    "Desarmar Aprimorado": {"grad": False, "efeito": "Não fica vulnerável ao desarmar"},
    "Destemido":           {"grad": False, "efeito": "Imune a efeitos de medo"},
    "Duro de Matar":       {"grad": False, "efeito": "Ignora a condição abatido; aguenta moribundo por mais tempo"},
    "Empatia com Animais": {"grad": False, "efeito": "Acalma e se comunica com animais"},
    "Equipamento":         {"grad": True,  "efeito": "1 pp = 5 pontos de equipamento"},
    "Esforço Extraordinário": {"grad": False, "efeito": "Usa esforço extra ficando apenas fatigado (1x por cena)"},
    "Esforço Supremo":     {"grad": False, "efeito": "Usa esforço extra sem fadiga (1x por cena)"},
    "Esquiva Fabulosa":    {"grad": False, "efeito": "Não fica vulnerável nem indefeso contra ataques que não vê"},
    "Estrangular":         {"grad": False, "efeito": "Agarrar também causa dano por asfixia"},
    "Evasão":              {"grad": True,  "efeito": "Metade do dano de efeitos de área (total na 2ª graduação)"},
    "Fascinar":            {"grad": False, "efeito": "Prende a atenção de um alvo com teste de Presença"},
    "Faz-Tudo":            {"grad": False, "efeito": "Escolhe 3 perícias; usa Intelecto no lugar da habilidade base"},
    "Iniciativa Aprimorada": {"grad": True, "efeito": "+4 de iniciativa por graduação"},
    "Inimigo Favorito":    {"grad": False, "efeito": "+2 contra um tipo definido de oponente"},
    "Interpor-se":         {"grad": False, "efeito": "Recebe no lugar de um aliado adjacente o ataque"},
    "Memória Eidética":     {"grad": False, "efeito": "Lembra de tudo que viu ou ouviu"},
    "Mira Aprimorada":     {"grad": False, "efeito": "Ignora penalidade por cobertura e distância"},
    "Prender Arma":        {"grad": False, "efeito": "Acerto crítico trava a arma do oponente"},
    "Quebrar Aprimorado":  {"grad": False, "efeito": "Quebra objetos com menos graus de sucesso"},
    "Rastrear":            {"grad": False, "efeito": "Segue trilha com Percepção"},
    "Redirecionar":        {"grad": False, "efeito": "Desvia um ataque corpo-a-corpo para outro alvo adjacente"},
    "Rolamento Defensivo": {"grad": True,  "efeito": "-1 de dano de área por graduação"},
    "Saque Rápido":        {"grad": False, "efeito": "Sacar arma é ação livre"},
    "Segunda Chance":      {"grad": True,  "efeito": "Re-rola uma falha específica (definida por graduação)"},
    "Sorte":               {"grad": True,  "efeito": "+1 em salvamentos de Fortitude ou Vontade por graduação"},
    "Tomar a Iniciativa":  {"grad": False, "efeito": "Age primeiro na primeira rodada contra inimigos de NP menor"},
    "Tolerância Maior":    {"grad": False, "efeito": "Aguenta esforço extra e ambientes extremos por mais tempo"},
    "Trabalho em Equipe":  {"grad": False, "efeito": "Seus ajudantes dão bônus maior em testes de equipe"},
    "Zombar":              {"grad": False, "efeito": "Teste de Enganação para deixar o alvo abatido"},
}
CUSTO_VANTAGEM = 1

# ============================================================ EFEITOS DE PODER (Cap. 6)
# Custo por graduação, antes de extras (+1 pp) e falhas (-1 pp).
# Fonte: Cap. 6 do livro. ADENDO = valor consagrado do sistema, não lido no PDF.
EFEITOS = {
    # --- ofensivos
    "Dano":            {"custo": 1, "salvamento": "Resistência", "tipo": "ataque",
                        "fonte": "ADENDO (pág. 104 não extraída)",
                        "desc": "Dano direto. CD do salvamento = 10 + graduações de Dano."},
    "Aflição":         {"custo": 1, "salvamento": "Fortitude ou Vontade", "tipo": "ataque",
                        "fonte": "ADENDO (pág. 94)",
                        "desc": "Impõe condições em degraus: 1 grau = 1ª condição, 2 = 2ª, 3+ = 3ª."},
    "Enfraquecer":     {"custo": 1, "salvamento": "Fortitude", "tipo": "ataque",
                        "fonte": "ADENDO (pág. 106)", "desc": "Reduz graduações de habilidade ou poder."},
    "Nulificar":       {"custo": 1, "salvamento": "Vontade", "tipo": "utilidade",
                        "fonte": "ADENDO (pág. 118)", "desc": "Cancela poderes de um descritor."},
    # --- defensivos
    "Proteção":        {"custo": 1, "salvamento": None, "tipo": "defesa",
                        "fonte": "ADENDO (pág. 149)", "desc": "Soma à Resistência. Extra Impenetrável: conta dobrado contra Dano."},
    "Imunidade":       {"custo": 1, "salvamento": None, "tipo": "defesa",
                        "fonte": "ADENDO (pág. 109)", "desc": "1 pp por ponto de imunidade (frio, fogo, medo, doença...)."},
    "Regeneração":     {"custo": 1, "salvamento": None, "tipo": "defesa",
                        "fonte": "ADENDO (pág. 119)", "desc": "Recupera condições e dano mais rápido."},
    "Deflexão":        {"custo": 1, "salvamento": None, "tipo": "defesa",
                        "fonte": "ADENDO (pág. 105)", "desc": "Desvia ataques à distância."},
    # --- físicos / de movimento
    "Aumentar Característica": {"custo": 1, "salvamento": None, "tipo": "aumento",
                        "fonte": "ADENDO (pág. 97)", "desc": "Soma graduações a qualquer característica. Inclui Força Aumentada."},
    "Crescimento":     {"custo": 2, "salvamento": None, "tipo": "aumento",
                        "fonte": "ADENDO (pág. 100)", "desc": "+1 Tamanho por graduação: +Força, +Resistência, -Esquiva."},
    "Encolhimento":    {"custo": 2, "salvamento": None, "tipo": "aumento",
                        "fonte": "ADENDO (pág. 105)", "desc": "-1 Tamanho por graduação: +Esquiva, +Furtividade, -Força."},
    "Voo":             {"custo": 2, "salvamento": None, "tipo": "movimento",
                        "fonte": "ADENDO (pág. 127)", "desc": "Velocidade aérea = graduação na Tabela de Medidas."},
    "Velocidade":      {"custo": 1, "salvamento": None, "tipo": "movimento",
                        "fonte": "ADENDO (pág. 127)", "desc": "Velocidade em terra acima do normal."},
    "Salto":           {"custo": 1, "salvamento": None, "tipo": "movimento",
                        "fonte": "ADENDO (pág. 120)", "desc": "Salta distâncias da Tabela de Medidas."},
    "Natação":         {"custo": 1, "salvamento": None, "tipo": "movimento",
                        "fonte": "ADENDO (pág. 118)", "desc": "Nada em velocidade de graduação."},
    "Escavação":       {"custo": 1, "salvamento": None, "tipo": "movimento",
                        "fonte": "ADENDO (pág. 106)", "desc": "Atravessa terra e rocha."},
    "Teleporte":       {"custo": 2, "salvamento": None, "tipo": "movimento",
                        "fonte": "ADENDO (pág. 124)", "desc": "Distância instantânea pela Tabela de Medidas."},
    "Movimento":       {"custo": 1, "salvamento": None, "tipo": "movimento",
                        "fonte": "ADENDO (pág. 116)", "desc": "1 pp por tipo: escalar paredes, andar na água, balançar-se, correr na vertical..."},
    "Alongamento":     {"custo": 1, "salvamento": None, "tipo": "movimento",
                        "fonte": "ADENDO (pág. 94)", "desc": "Estica o corpo; +alcance de agarrar."},
    "Intangibilidade": {"custo": 5, "salvamento": None, "tipo": "defesa",
                        "fonte": "ADENDO (pág. 109)", "desc": "Atravessa matéria sólida."},
    "Invisibilidade / Camuflagem": {"custo": 2, "salvamento": None, "tipo": "sensorial",
                        "fonte": "ADENDO (pág. 96)", "desc": "Some de um sentido por graduação de sentido."},
    # --- sensoriais e mentais
    "Sentidos":        {"custo": 1, "salvamento": None, "tipo": "sensorial",
                        "fonte": "ADENDO (pág. 120)", "desc": "1 pp por sentido: visão no escuro, infravisão, radar, detecção..."},
    "Sentido Remoto":  {"custo": 1, "salvamento": None, "tipo": "sensorial",
                        "fonte": "ADENDO (pág. 124)", "desc": "Percebe à distância."},
    "Compreender":     {"custo": 1, "salvamento": None, "tipo": "mental",
                        "fonte": "ADENDO (pág. 98)", "desc": "Entende linguagens: animais, máquinas, mortos."},
    "Comunicação":     {"custo": 1, "salvamento": None, "tipo": "mental",
                        "fonte": "ADENDO (pág. 98)", "desc": "Fala à distância ou por outro meio."},
    "Leitura Mental":  {"custo": 2, "salvamento": "Vontade", "tipo": "mental",
                        "fonte": "ADENDO (pág. 112)", "desc": "Lê pensamentos. Falha: exige toque, concentração, etc."},
    "Ilusão":          {"custo": 1, "salvamento": "Vontade", "tipo": "mental",
                        "fonte": "ADENDO (pág. 107)", "desc": "Cria imagens falsas em um ou mais sentidos."},
    "Invocar":         {"custo": 2, "salvamento": None, "tipo": "utilidade",
                        "fonte": "ADENDO (pág. 111)", "desc": "Chama criaturas ou constructos."},
    # --- utilidade
    "Cura":            {"custo": 1, "salvamento": None, "tipo": "utilidade",
                        "fonte": "ADENDO (pág. 103)", "desc": "Remove condições e dano de outro."},
    "Criar":           {"custo": 1, "salvamento": None, "tipo": "utilidade",
                        "fonte": "ADENDO (pág. 100)", "desc": "Constrói objetos sólidos de energia ou matéria."},
    "Mover Objeto":    {"custo": 1, "salvamento": None, "tipo": "utilidade",
                        "fonte": "ADENDO (pág. 116)", "desc": "Telecinese: move massa pela Tabela de Medidas."},
    "Ambiente":        {"custo": 2, "salvamento": None, "tipo": "utilidade",
                        "fonte": "ADENDO (pág. 95)", "desc": "Muda luz, temperatura, clima, gravidade numa área."},
    "Morfar":          {"custo": 5, "salvamento": None, "tipo": "aumento",
                        "fonte": "ADENDO (pág. 114)", "desc": "Vira outra coisa, com as características dela."},
    "Variável":        {"custo": 5, "salvamento": None, "tipo": "aumento",
                        "fonte": "ADENDO (pág. 126)", "desc": "5 pp por graduação trocável em qualquer outra característica."},
    "Rapidez":         {"custo": 1, "salvamento": None, "tipo": "aumento",
                        "fonte": "ADENDO (pág. 119)", "desc": "Faz tarefas mentais e manuais em velocidade sobre-humana."},
    "Imortalidade":    {"custo": 1, "salvamento": None, "tipo": "aumento",
                        "fonte": "ADENDO (pág. 108)", "desc": "Não envelhece e/ou volta da morte."},
    "Controle da Sorte": {"custo": 1, "salvamento": None, "tipo": "utilidade",
                        "fonte": "ADENDO (pág. 100)", "desc": "Manipula pontos heroicos e rolagens alheias."},
    "Característica":  {"custo": 1, "salvamento": None, "tipo": "utilidade",
                        "fonte": "ADENDO (pág. 97)", "desc": "Um fato do personagem que não é número: patentes, contatos, reputação."},
}

EXTRAS = ["Acurado", "Afeta Corpóreo", "Afeta Intangível", "Afeta Objetos", "Alcance", "Área",
          "Ataque", "Contagioso", "Dimensional", "Duração Aumentada", "Efeito Alternativo",
          "Engatilhado", "Impenetrável", "Indireto", "Ligado", "Multiataque", "Penetrante",
          "Preciso", "Reação", "Resistência Alternativa", "Seletivo", "Sustentado", "Sutil",
          "Teleguiado", "Traiçoeiro"]
FALHAS = ["Ação Aumentada", "Alcance Reduzido", "Ativação", "Baseado em Agarrar", "Cansativo",
          "Concentração", "Dissipação", "Distração", "Efeito Colateral", "Exige Teste",
          "Inconstante", "Incontrolável", "Impreciso", "Limitado", "Perceptível", "Permanente",
          "Removível", "Resistível", "Retroalimentação"]

# ============================================================ CONDIÇÕES (Cap. 1, lido no PDF)
# ====================================================================== MOTIVAÇÕES
# Lidas no PDF (cap. 1). A Motivação é uma complicação obrigatória: quando o mestre
# a usa contra você, você ganha 1 ponto heroico.
MOTIVACOES = [
    "Aceitação", "Adrenalina", "Cobiça", "Fazer o Bem",
    "Justiça", "Patriotismo", "Reconhecimento", "Responsabilidade",
]

# ====================================================================== COMPLICAÇÕES
# Lista do livro. Não dão pontos: dão ponto heroico quando o mestre cobra.
COMPLICACOES = [
    "Acidente", "Deficiência", "Fama", "Fobia", "Fraqueza", "Honra", "Identidade",
    "Inimigo", "Irritação", "Obsessão", "Ódio", "Peculiaridade", "Perda de Poder",
    "Preconceito", "Relacionamento", "Reputação", "Responsabilidade", "Rivalidade",
    "Segredo", "Vício",
]


CONDICOES_BASICAS = {
    "Atordoado":  "não pode executar ações, nem livres",
    "Compelido":  "dirigido por força externa, luta contra; só ações livres + 1 padrão, escolhidas por quem controla",
    "Controlado": "sem vontade própria; quem controla dita as ações",
    "Debilitado": "uma ou mais habilidades abaixo de -5",
    "Desabilitado": "-5 de circunstância em todos os testes",
    "Desatento":  "inconsciente dos arredores; cobertura total contra seus sentidos",
    "Enfraquecido": "perdeu pontos de poder temporariamente",
    "Fatigado":   "fica Impedido; recupera com 1 hora de descanso",
    "Imóvel":     "sem velocidade, não sai do lugar, mas ainda age",
    "Impedido":   "move-se à metade (-1 graduação de velocidade)",
    "Indefeso":   "defesas ativas = 0; atacante pode usar teste de rotina e todo acerto é crítico",
    "Normal":     "nenhuma condição",
    "Prejudicado": "-2 de circunstância em todos os testes",
    "Tonto":      "limitado a ações livres + 1 ação padrão",
    "Transformado": "características alteradas; o total de pontos de poder não pode subir",
    "Vulnerável": "defesas ativas divididas pela metade (arredonda para cima)",
}
CONDICOES_COMBINADAS = {
    "Abatido":       ["Tonto", "Impedido"],
    "Adormecido":    ["Indefeso", "Atordoado", "Desatento"],
    "Amarrado":      ["Indefeso", "Imóvel", "Prejudicado"],
    "Caído":         ["Impedido"],
    "Cego":          ["Impedido", "Desatento", "Vulnerável"],
    "Exausto":       ["Prejudicado", "Impedido"],
    "Incapacitado":  ["Indefeso", "Atordoado", "Desatento"],
    "Moribundo":     ["Indefeso", "Atordoado", "Desatento"],
    "Paralisado":    ["Indefeso", "Imóvel", "Atordoado"],
    "Restrito":      ["Impedido", "Vulnerável"],
    "Surdo":         [],
    "Surpreso":      ["Atordoado", "Vulnerável"],
    "Transe":        ["Atordoado"],
}
# condições que se sobrepõem a outras
SOBREPOSICAO = {
    "Controlado": ["Compelido"], "Atordoado": ["Tonto"], "Debilitado": ["Desabilitado", "Enfraquecido"],
    "Desabilitado": ["Prejudicado"], "Imóvel": ["Impedido"], "Indefeso": ["Vulnerável"],
}

# ============================================================ TABELA DE MEDIDAS (lida no PDF)
MEDIDAS = {
    -5: ("1 kg", "1/8 segundo", "25 cm"), -4: ("2 kg", "1/4 segundo", "50 cm"),
    -3: ("4 kg", "1/2 segundo", "1 m"),   -2: ("8 kg", "1 segundo", "2 m"),
    -1: ("15 kg", "3 segundos", "4 m"),    0: ("30 kg", "6 segundos", "8 m"),
    1: ("60 kg", "12 segundos", "15 m"),   2: ("120 kg", "30 segundos", "30 m"),
    3: ("250 kg", "1 minuto", "60 m"),     4: ("500 kg", "2 minutos", "120 m"),
    5: ("1 t", "4 minutos", "250 m"),      6: ("2 t", "8 minutos", "500 m"),
    7: ("4 t", "15 minutos", "1 km"),      8: ("8 t", "30 minutos", "2 km"),
    9: ("15 t", "1 hora", "4 km"),        10: ("30 t", "2 horas", "8 km"),
    11: ("60 t", "4 horas", "15 km"),     12: ("120 t", "8 horas", "30 km"),
    13: ("250 t", "16 horas", "60 km"),   14: ("500 t", "1 dia", "120 km"),
    15: ("1.000 t", "2 dias", "250 km"),  16: ("2.000 t", "4 dias", "500 km"),
    17: ("4.000 t", "1 semana", "1.000 km"), 18: ("8.000 t", "2 semanas", "2.000 km"),
    19: ("15.000 t", "1 mês", "4.000 km"), 20: ("30.000 t", "2 meses", "8.000 km"),
    21: ("60.000 t", "4 meses", "15.000 km"), 22: ("120.000 t", "8 meses", "30.000 km"),
    23: ("250.000 t", "1,5 anos", "60.000 km"), 24: ("500.000 t", "3 anos", "120.000 km"),
    25: ("1 milhão t", "6 anos", "250.000 km"), 26: ("2 milhões t", "12 anos", "500.000 km"),
    27: ("4 milhões t", "25 anos", "1 milhão km"), 28: ("8 milhões t", "50 anos", "2 milhões km"),
    29: ("15 milhões t", "1 século", "4 milhões km"), 30: ("30 milhões t", "2 séculos", "8 milhões km"),
}


def medida(grad, coluna="massa"):
    """coluna: massa | tempo | distância."""
    i = {"massa": 0, "tempo": 1, "distancia": 2}[coluna]
    if grad in MEDIDAS:
        return MEDIDAS[grad][i]
    if grad < -5:
        return "menos que 1 kg / 1/8 s / 25 cm"
    return "acima de 30.000 t / 2 meses / 8.000 km"


# ============================================================ CD E GRAUS (lidos no PDF)
TABELA_CD = [
    (0,  "Muito fácil",      "perceber algo à vista"),
    (5,  "Fácil",            "escalar uma corda com nós"),
    (10, "Médio",            "ouvir um segurança se aproximando"),
    (15, "Difícil",          "desarmar um explosivo"),
    (20, "Desafiador",       "nadar contra uma correnteza forte"),
    (25, "Formidável",       "escalar uma montanha molhada e escorregadia"),
    (30, "Heroico",          "sobrepujar um sistema de segurança sofisticado"),
    (35, "Super-heroico",    "convencer guardas a deixar você entrar sem credencial"),
    (40, "Quase impossível", "rastrear um comando na selva sem lua após 12 dias de chuva"),
]


def graus(total, cd):
    """Grau de sucesso/falha. Cada 5 pontos de margem = 1 grau. Frações ignoradas.
    20 natural soma um passo (sucesso crítico) — aplicado por quem chama."""
    margem = total - cd
    if margem >= 0:
        return 1 + margem // 5
    return -((-margem - 1) // 5 + 1)


# ============================================================ NÍVEL DE PODER (lido no PDF)
def pontos_iniciais(np):
    """Tabela Pontos de Poder Iniciais: NP 1 = 15, +15 por nível."""
    return 15 * max(1, min(20, np))


def limites_np(np):
    """Os cinco limites que o Nível de Poder impõe."""
    return {
        "pericia_max": np + 10,      # habilidade + perícia + vantagem
        "ataque_efeito_max": 2 * np,  # bônus de ataque + graduações do efeito ligado
        "efeito_sem_ataque_max": np,  # efeito com salvamento mas sem teste de ataque
        "esquiva_resistencia_max": 2 * np,
        "aparar_resistencia_max": 2 * np,
        "fortitude_vontade_max": 2 * np,
    }


def custo_poder(efeito, grad, extras=0, falhas=0):
    """([custo básico + extras - falhas] x graduações) + modificadores planos."""
    base = EFEITOS[efeito]["custo"]
    return max(1, base + extras - falhas) * grad


def np_efetivo_pdM(ataque, efeito):
    """Nível de Poder efetivo de um PdM = (ataque + efeito) / 2. Exemplo do livro."""
    return (ataque + efeito) / 2
