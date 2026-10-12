"""
CÉU LACRADO — mundo murim/wuxia.
Lore + dados coerentes por facção/região. Nada aqui é aleatório solto:
cada lista existe para que um sorteio SEMPRE pertença a esta história.
"""

# ---------------------------------------------------------------- LORE NÚCLEO
LORE = """
CÉU LACRADO — há 900 anos o Último Ascendido partiu e selou o Portão de Jade.
Antes de sumir, deixou NOVE TÁBUAS DE JADE: não são livros, são LEIS. Cada
Tábua escreve no mundo uma regra física do Caminho Marcial (é por isso que o
sistema tem regras duras — elas são a física deste mundo).

  I    O Qi corre nos meridianos; canal vazio não carrega técnica.
  II   Corpo que não foi temperado estoura sob Qi demais.
  III  Toda técnica carrega um Nome; o Nome cobra do corpo.
  IV   Qi emprestado de sangue paga-se com vida (técnicas Proibidas).
  V    Dois Qi opostos se anulam; intenção vence força bruta.
  VI   Nenhum mortal vê o que está acima de três degraus dele.
  VII  A Terra lembra: lugares absorvem Qi e devolvem o que viram.
  VIII Nomes de verdade têm peso — juramentos se cumprem sozinhos.
  IX   Há um degrau acima do Último. Ninguém sabe o que guarda a porta.

A TÁBUA RACHADA (a Décima): fragmentos de uma lei que nunca foi promulgada.
Quem a lê entende uma regra a mais — e o mundo cobra. Semente de campanha.

O SEGREDO QUE AS NOVE CASAS SABEM: o Portão de Jade não foi selado por fora.
Foi trancado POR DENTRO. Alguma coisa ficou do outro lado e está empurrando.
Todo "Ascendido" dos últimos 900 anos, na verdade, desapareceu.
"""

# ---------------------------------------------------------------- DEGRAUS (rank)
# idx 1..9. "rank_efetivo" é o que entra nas fórmulas.
DEGRAUS = [
    {"idx": 1, "nome": "Forjamento Corporal",  "cn": "Duanti",  "qi": 10,  "pv": 10, "tec_max": 3,
     "marca": "O corpo deixa de ser humano comum: ossos densos, ferida fecha rápido."},
    {"idx": 2, "nome": "Abertura de Meridianos", "cn": "Kaimai", "qi": 22,  "pv": 16, "tec_max": 5,
     "marca": "Qi corre de verdade. Dá para sentir a intenção alheia a três passos."},
    {"idx": 3, "nome": "Condensação de Qi",     "cn": "Ningqi", "qi": 40,  "pv": 24, "tec_max": 8,
     "marca": "Qi sai do corpo: lâmina de vento, palma que empurra sem tocar."},
    {"idx": 4, "nome": "Núcleo Interno",        "cn": "Jiedan", "qi": 70,  "pv": 34, "tec_max": 12,
     "marca": "Um núcleo gira no dantian. Lutar três dias sem dormir vira possível."},
    {"idx": 5, "nome": "Alma Nascente",         "cn": "Yuanying", "qi": 110, "pv": 48, "tec_max": 16,
     "marca": "A alma pode sair do corpo por instantes. Um destes mata cem soldados."},
    {"idx": 6, "nome": "Transformação Divina",  "cn": "Huashen", "qi": 170, "pv": 66, "tec_max": 20,
     "marca": "O corpo obedece à vontade: ferida fechada com um pensamento."},
    {"idx": 7, "nome": "Retorno ao Vazio",      "cn": "Fanxu",  "qi": 250, "pv": 88, "tec_max": 24,
     "marca": "Presença esmaga: mortal comum desmaia a dez passos."},
    {"idx": 8, "nome": "Tribulação",            "cn": "Dujie",  "qi": 360, "pv": 116, "tec_max": 28,
     "marca": "O Céu ativamente tenta matá-lo. Pouquíssimos vivos."},
    {"idx": 9, "nome": "Ascensão",              "cn": "Daxian", "qi": 500, "pv": 150, "tec_max": 32,
     "marca": "Nenhum ser vivo confirmado no continente. Só lenda e ossos."},
]


def degrau(idx):
    return DEGRAUS[max(1, min(9, idx)) - 1]


# ---------------------------------------------------------------- FACÇÕES
FACCOES = {
    "alianca_garça": {
        "nome": "Aliança da Garça Branca", "tipo": "seita ortodoxa",
        "sede": "Pico da Garça (Chuvisco Cinzento)", "degrau_lider": 7,
        "lema": "A lâmina só desembainha depois da palavra.",
        "quer": "Manter a hegemonia ortodoxa sobre a Província da Chuva Verde.",
        "segredo": "O manual fundador é uma cópia — o original foi vendido ao Portão Carmesim há 60 anos para pagar uma derrota.",
        "desejos": {
            "trivial": ["cumprir a ordem e descer antes do escuro", "passar no exame de outono", "não sujar o manto", "impressionar o instrutor"],
            "profundo": ["descobrir quem tirou o Manual do Pico — e decidir se conta a alguém", "não virar o que os anciãos viraram", "pagar o preço de uma promessa feita a um discípulo morto"],
        },
        "artes": ["Garça Rompe a Névoa", "Palma do Rio Sereno", "Passo sobre Juncos", "Espada dos Nove Reflexos"],
        "nomes": ["Shen", "Lian", "Yue", "Qing", "Bai", "Xue", "Ming", "Ru"],
        "sobrenomes": ["Shen", "Luo", "Bai", "Yun", "Gu", "Mei"],
        "traços": ["fala baixo e nunca repete", "cumprimenta com a palma aberta", "não bebe na frente de estranhos",
                   "corrige a postura dos outros", "cheira a incenso de pinho", "anda com o peso todo no pé esquerdo", "nunca usa a palavra 'eu'", "carrega a espada na mão direita mesmo sem lâmina", "recusa abrigo sob telhado de palha", "guarda o cabelo preso com um pino de osso"],
    },
    "portao_carmesim": {
        "nome": "Portão Carmesim", "tipo": "seita heterodoxa (chamada demoníaca)",
        "sede": "Vale da Cinza Quente (fora da província)", "degrau_lider": 8,
        "lema": "Se o Céu não responde, nós respondemos.",
        "quer": "Recuperar as páginas da Tábua IV que a Aliança confiscou.",
        "segredo": "Suas artes de sangue não são heresia: são medicina de campo de um exército esquecido, distorcidas por quem as copiou.",
        "desejos": {
            "trivial": ["terminar a coleta e voltar para o Vale", "não deixar testemunha", "comer alguma coisa quente"],
            "profundo": ["provar que as artes de sangue eram medicina, não heresia", "recuperar as páginas da Tábua IV", "matar o homem da Aliança que assinou a ordem"],
        },
        "artes": ["Garra das Sete Cicatrizes", "Sutra do Sangue Quieto", "Palma da Cinza Quente", "Fio de Nove Agulhas"],
        "nomes": ["Chi", "Yan", "Hu", "Zhuo", "Wei", "Mo", "Lie"],
        "sobrenomes": ["Yan", "Chi", "Hu", "Zhuo", "Wei"],
        "traços": ["cicatrizes contadas como medalhas", "ri no momento errado", "nunca dá as costas a uma porta",
                   "carrega uma vasilha de barro selada", "fala de morte com carinho", "tatuagem de agulha no antebraço", "cozinha para os outros e não come", "conta as próprias cicatrizes em voz alta", "pede licença antes de entrar", "não mata quem está de joelhos"],
    },
    "faca_cega": {
        "nome": "Guilda Faca Cega", "tipo": "mercadores / contrabando / informação",
        "sede": "Cais de Sete Barcas", "degrau_lider": 5,
        "lema": "Ninguém vê a mão que pesa a prata.",
        "quer": "Monopolizar o sal e o registro de passaportes de Chuvisco Cinzento.",
        "segredo": "Vende para os dois lados e guarda um livro com o nome de todos que já compraram — inclusive dos mortos.",
        "desejos": {
            "trivial": ["fechar a conta do dia", "não perder a carga", "receber a comissão"],
            "profundo": ["comprar o próprio nome de volta do livro da Guilda", "descobrir em nome de quem o segundo tributo está sendo cobrado"],
        },
        "artes": ["Contagem Cega", "Punho do Peso Falso", "Passo de Cais"],
        "nomes": ["Jin", "Bao", "Fu", "Kuan", "Shu", "Luo"],
        "sobrenomes": ["Jin", "Bao", "Fu", "Kuan", "Huo"],
        "traços": ["conta moedas sem olhar", "sabe o preço de tudo na sala", "chama todo mundo de 'amigo'",
                   "mão esquerda sempre coberta", "nunca senta de costas para a janela", "sorriso que não chega aos olhos", "anota tudo num caderno de capa oleada", "oferece chá e cobra depois", "conhece o nome dos seus pais", "trabalha sempre com um capanga que nunca fala"],
    },
    "sino_silencioso": {
        "nome": "Ordem do Sino Silencioso", "tipo": "ordem monástica (só mulheres)",
        "sede": "Templo do Sino sem Badalo (Montanha Ossuda)", "degrau_lider": 6,
        "lema": "O sino não toca. Ele espera.",
        "quer": "Impedir que o badalo do sino seja encontrado.",
        "segredo": "A técnica suprema exige perder a voz para sempre — a abadessa atual é a terceira a fingir que nunca falou.",
        "desejos": {
            "trivial": ["terminar a vigília", "não quebrar o voto", "chegar ao templo antes da chuva"],
            "profundo": ["encontrar o badalo antes que alguém o faça tocar", "descobrir o que a abadessa disse naquela única vez"],
        },
        "artes": ["Sino sem Som", "Palma do Eco Atrasado", "Passo da Neve sem Pegada"],
        "nomes": ["Jing", "Ling", "Miao", "Xian", "Ning", "Yin"],
        "sobrenomes": ["Jing", "Ling", "Miao", "Xian"],
        "traços": ["fala por escrito em um caderninho", "ouve antes de olhar", "nunca pisa em sombra alheia",
                   "carrega um sino pequeno sem badalo", "reza por inimigos mortos", "costura o próprio manto com fio vermelho", "não mata inseto, só muda de lugar", "carrega um pote de sal", "escreve mais rápido do que fala", "não atravessa ponte de pedra"],
    },
    "corte_cinza": {
        "nome": "Corte Cinzenta", "tipo": "remanescente da dinastia caída",
        "sede": "Capital provincial (Vau de Pedra Verde), porões do antigo palácio", "degrau_lider": 6,
        "lema": "O trono é uma cadeira; nós lembramos quem sentou.",
        "quer": "Provar que as Nove Casas traíram o último imperador.",
        "segredo": "Guarda um herdeiro legítimo — que é um falso, criado há 30 anos para ser alvo no lugar do verdadeiro.",
        "desejos": {
            "trivial": ["conferir os passaportes e liberar a estrada", "não se molhar", "voltar para o turno"],
            "profundo": ["provar que as Nove Casas traíram o último imperador", "achar o herdeiro antes dos assassinos — ou antes da própria Corte"],
        },
        "artes": ["Selo Imperial Quebrado", "Lança do Portão Caído", "Passo de Corte"],
        "nomes": ["Zheng", "Kai", "Heng", "Yuan", "Tao", "Zong"],
        "sobrenomes": ["Zheng", "Kai", "Heng", "Yuan"],
        "traços": ["usa um selo de jade falso com orgulho", "fala de protocolo em ruínas", "não aceita presente",
                   "chama todos por títulos extintos", "escreve com a mão esquerda", "memoriza rostos de uma olhada", "cumprimenta primeiro quem tem menos poder", "guarda moeda da dinastia caída no punho", "não come com anfitrião", "corrige a pronúncia dos outros"],
    },
    "irmaos_ferrugem": {
        "nome": "Irmandade da Ferrugem", "tipo": "bandidos de estrada",
        "sede": "Passo da Garoa (acampamento móvel)", "degrau_lider": 3,
        "lema": "O que cai na lama é de quem pega.",
        "quer": "Sobreviver ao inverno e pagar o tributo à Faca Cega.",
        "segredo": "O chefe é um desertor da Aliança da Garça; ninguém da irmandade sabe o rosto verdadeiro dele.",
        "desejos": {
            "trivial": ["pegar a bolsa e sumir", "pagar o tributo à Faca Cega", "sobreviver ao inverno", "não ser o primeiro a atacar"],
            "profundo": ["sair da Irmandade vivo — o último que tentou virou aviso na estrada"],
        },
        "artes": ["Corte Sujo", "Punho de Corrente", "Passo de Barranco"],
        "nomes": ["Gou", "Shu", "La", "Tie", "Kuai", "Niu"],
        "sobrenomes": ["Tie", "Niu", "Gou"],
        "traços": ["falta um dente", "cheira a chuva velha", "ri alto demais", "tem uma orelha marcada a ferro",
                   "reza para uma pedra do caminho", "cospe antes de falar", "empresta a faca e depois cobra", "tem um dedo a menos", "guarda uma corda sempre à mão", "não bate em quem já caiu — por medo, não por pena"],
    },
    "semeadores": {
        "nome": "Semeadores de Chuva", "tipo": "rede de curandeiros e camponeses",
        "sede": "Vila Folha Caída", "degrau_lider": 4,
        "lema": "Quem cura não pergunta de que lado sangra.",
        "quer": "Manter a vila livre de tributo das seitas.",
        "segredo": "A matriarca trata, há onze anos, um homem do Portão Carmesim escondido no celeiro.",
        "desejos": {
            "trivial": ["voltar para casa antes da chuva", "encher o cesto", "não perder o moinho"],
            "profundo": ["manter a vila fora dos mapas das seitas", "continuar escondendo o homem do celeiro por mais um inverno"],
        },
        "artes": ["Agulha de Quatro Estações", "Palma que Fecha", "Chá dos Dez Passos"],
        "nomes": ["He", "Mu", "An", "Cao", "Shu", "Lan"],
        "sobrenomes": ["He", "Mu", "An", "Cao"],
        "traços": ["mãos manchadas de erva", "oferece chá antes de falar", "fala com plantas",
                   "não deixa ninguém entrar no celeiro", "conta doenças pelos olhos", "levanta antes do sol por hábito", "tem as unhas curtas e limpas", "chama todos de 'filho'", "guarda semente no bolso do manto", "não cobra de quem não pode pagar"],
    },
    "errante": {
        "nome": "Errante (sem bandeira)", "tipo": "livre",
        "sede": "nenhuma", "degrau_lider": 0,
        "lema": "",
        "quer": "Algo pequeno e humano: uma dívida, um túmulo, uma promessa.",
        "segredo": "",
        "desejos": {
            "trivial": ["uma refeição quente", "um teto sem goteira", "sumir antes de ser reconhecido"],
            "profundo": ["quitar uma dívida que ninguém mais lembra", "enterrar alguém direito", "descer da montanha de uma vez"],
        },
        "artes": ["Corte Sujo", "Punho de Corrente", "Passo de Barranco",
                  "Palma que Fecha", "Respiração de Quatro Contas", "Ouvido do Vale"],
        "nomes": ["An", "Yu", "Feng", "Lin", "Zhu", "Wei", "Ke", "San"],
        "sobrenomes": ["Mo", "Du", "Ye", "Qin", "Lou", "Tang", "Han"],
        "traços": ["capa remendada três vezes", "não revela o nome inteiro", "carrega um objeto que não usa",
                   "dorme de frente para a porta", "desenha no chão enquanto pensa", "fala sozinho quando pensa", "carrega uma pedra lisa no bolso", "não bebe nada que não tenha visto abrir", "olha o céu antes de responder", "conta histórias que terminam no meio"],
    },
}

# ---------------------------------------------------------------- REGIÃO
REGIAO = {
    "nome": "Província da Chuva Verde",
    "clima": "Chuva fina quase constante, névoa nos vales ao amanhecer. Estação das Águas Altas agora.",
    "chao": "Terra vermelha, arrozal em terraço, floresta de bambu, minério de ferro ruim.",
    "estradas": ["Estrada do Sal Velho", "Trilha da Garoa", "Caminho dos Juncos"],
    "lugares": [
        {"nome": "Vau de Pedra Verde", "tipo": "cidade", "pop": 12000,
         "desc": "Capital provincial sobre uma ponte de nove arcos. Sede da guarnição e do mercado de jade.",
         "faccao": "corte_cinza"},
        {"nome": "Chuvisco Cinzento", "tipo": "montanha",
         "desc": "Pico da Garça, sede da Aliança. Três mil degraus de pedra, ninguém sobe armado.",
         "faccao": "alianca_garça"},
        {"nome": "Passo da Garoa", "tipo": "estrada",
         "desc": "Desfiladeiro estreito na Estrada do Sal Velho. Único caminho de carroça entre o cais e a capital.",
         "faccao": "irmaos_ferrugem"},
        {"nome": "Cais de Sete Barcas", "tipo": "porto",
         "desc": "Porto fluvial de madeira podre, lanternas de óleo, cheiro de peixe e prata.",
         "faccao": "faca_cega"},
        {"nome": "Vila Folha Caída", "tipo": "vila", "pop": 340,
         "desc": "Trinta casas de barro e um moinho. Fica fora de qualquer mapa oficial.",
         "faccao": "semeadores"},
        {"nome": "Templo do Sino sem Badalo", "tipo": "templo",
         "desc": "Na Montanha Ossuda. Nunca se ouve som algum vindo de lá — nem de pássaros.",
         "faccao": "sino_silencioso"},
        {"nome": "Vale da Cinza Quente", "tipo": "ruina",
         "desc": "Fora da província, a quatro dias. Terra morna, cinza que nunca esfria, ossos empilhados.",
         "faccao": "portao_carmesim"},
        {"nome": "Ruínas de Qi Selado", "tipo": "ruina",
         "desc": "Nove pedras fincadas em círculo num arrozal morto. O arroz não cresce ali há 900 anos.",
         "faccao": None},
        {"nome": "Pântano da Lanterna", "tipo": "pantano",
         "desc": "Água até a cintura, gás que acende sozinho à noite. Dizem que as luzes são gente.",
         "faccao": None},
        {"nome": "Mercado de Jade", "tipo": "cidade",
         "desc": "Doze bancas dentro de um pátio murado em Vau de Pedra Verde. Só se negocia de dia.",
         "faccao": "faca_cega"},
        {"nome": "Estalagem do Terceiro Dedo", "tipo": "estalagem",
         "desc": "Beira da Estrada do Sal Velho. Um dedo de bronze pregado na porta como amuleto.",
         "faccao": None},
    ],
}

# ---------------------------------------------------------------- GANCHOS DE CAMPANHA
GANCHOS = [
    "O Manual da Garça foi roubado do Pico e substituído por uma cópia perfeita. Só três pessoas saberiam distinguir.",
    "Alguém está comprando todos os sinos de bronze da província. Ninguém sabe para quê.",
    "Um homem sem rosto aparece nos registros de três vilas diferentes no mesmo dia — há onze anos.",
    "O arroz não cresce nas Ruínas de Qi Selado, mas este ano uma única espiga nasceu. Está preta.",
    "A Faca Cega começou a exigir um segundo tributo. Não disse em nome de quem.",
    "O herdeiro da Corte Cinzenta fugiu — e a própria Corte o está caçando para protegê-lo de si mesmo.",
    "A abadessa do Sino Silencioso falou. Foi uma única palavra, e quem ouviu não consegue repeti-la.",
]

# ---------------------------------------------------------------- LISTAS DE ORÁCULO / EVENTO
# Cada evento PRECISA ser ancorado a um fato estabelecido. Se não der para
# ancorar, ele entra mudo (detalhe ambiental) e vira semente.
FOCO_EVENTO = [
    "um inimigo antigo", "um cobrador de dívida", "uma carta sem remetente", "um velho mestre",
    "um rival da mesma seita", "um animal ferido", "uma criança", "um funeral passando",
    "um selo de jade falso", "um homem que sabe o seu nome", "uma patrulha", "um incêndio distante",
    "uma mulher grávida", "um sino tocando fora de hora", "um cadáver recente", "um vendedor de chá",
]
ACAO_EVENTO = [
    "chega sem aviso", "está mentindo", "reconhece você", "pede ajuda", "oferece um negócio",
    "foge de algo", "traz uma notícia errada", "está morrendo", "está observando",
    "deixa algo cair", "bloqueia o caminho", "faz uma pergunta que ninguém deveria fazer",
]
ASSUNTO_EVENTO = [
    "uma Tábua de Jade", "o Portão de Jade", "uma dívida de sangue antiga", "um manual roubado",
    "um nome que não devia ser dito", "uma seita que não existe mais", "um tributo não pago",
    "uma promessa quebrada", "um túmulo vazio", "uma técnica proibida", "um herdeiro escondido",
    "a chuva que não para",
]

# ---------------------------------------------------------------- ENCONTROS POR TERRENO
# peso = chance relativa; rank = faixa de degrau; tier = profundidade narrativa (0-4)
ENCONTROS = {
    "estrada": [
        {"peso": 26, "que": "Bandidos da Irmandade da Ferrugem", "forma": "humano", "faccao": "irmaos_ferrugem",
         "rank": (1, 2), "tier": 1, "qtd": (2, 5), "ancora": "tributo da Faca Cega"},
        {"peso": 14, "que": "Caravana de sal da Faca Cega", "forma": "humano", "faccao": "faca_cega",
         "rank": (2, 3), "tier": 2, "qtd": (1, 3), "ancora": "monopólio do sal"},
        {"peso": 12, "que": "Patrulha da guarnição de Vau de Pedra Verde", "forma": "humano", "faccao": "corte_cinza",
         "rank": (1, 3), "tier": 2, "qtd": (3, 6), "ancora": "impostos e passaportes"},
        {"peso": 10, "que": "Peregrino a caminho do Pico da Garça", "forma": "humano", "faccao": "alianca_garça",
         "rank": (1, 2), "tier": 2, "qtd": (1, 2), "ancora": "manual roubado"},
        {"peso": 10, "que": "Um errante que já viu você antes", "forma": "humano", "faccao": "errante",
         "rank": (2, 4), "tier": 3, "qtd": (1, 1), "ancora": "passado do personagem"},
        {"peso": 8,  "que": "Carroça atolada, família de camponeses", "forma": "humano", "faccao": "semeadores",
         "rank": (0, 1), "tier": 1, "qtd": (2, 4), "ancora": "vila fora do mapa"},
        {"peso": 6,  "que": "Cobrador do Portão Carmesim", "forma": "humano", "faccao": "portao_carmesim",
         "rank": (3, 4), "tier": 3, "qtd": (1, 2), "ancora": "Tábua IV"},
        {"peso": 8,  "que": "Cães selvagens descendo da serra", "forma": "nao_humano", "faccao": None,
         "rank": (0, 1), "tier": 0, "qtd": (3, 6), "ancora": "inverno"},
        {"peso": 6,  "que": "Deslizamento bloqueando a estrada", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "chuva constante"},
    ],
    "floresta": [
        {"peso": 18, "que": "Caçadores da vila Folha Caída", "forma": "humano", "faccao": "semeadores",
         "rank": (1, 2), "tier": 1, "qtd": (1, 3), "ancora": "vila fora do mapa"},
        {"peso": 14, "que": "Um animal de Qi anormal (javali de chifre de ferro)", "forma": "nao_humano", "faccao": None,
         "rank": (2, 3), "tier": 0, "qtd": (1, 1), "ancora": "Tábua VII, terra que lembra"},
        {"peso": 12, "que": "Discípulos da Garça em treino proibido fora do pico", "forma": "humano", "faccao": "alianca_garça",
         "rank": (2, 3), "tier": 3, "qtd": (2, 3), "ancora": "manual roubado"},
        {"peso": 12, "que": "Ermitão que já foi alguém", "forma": "humano", "faccao": "errante",
         "rank": (4, 6), "tier": 4, "qtd": (1, 1), "ancora": "degrau acima"},
        {"peso": 10, "que": "Acampamento abandonado, ainda quente", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "Irmandade da Ferrugem"},
        {"peso": 10, "que": "Ladões de túmulos com um selo de jade", "forma": "humano", "faccao": "corte_cinza",
         "rank": (1, 2), "tier": 2, "qtd": (2, 4), "ancora": "herdeiro escondido"},
        {"peso": 8,  "que": "Uma monja do Sino, calada, seguindo alguém", "forma": "humano", "faccao": "sino_silencioso",
         "rank": (3, 4), "tier": 3, "qtd": (1, 1), "ancora": "badalo perdido"},
        {"peso": 8,  "que": "Névoa que não se move contra o vento", "forma": "sem_forma", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "Ruínas de Qi Selado"},
        {"peso": 8,  "que": "Fugitivo acorrentado que arrebentou as correntes", "forma": "humano", "faccao": "portao_carmesim",
         "rank": (2, 3), "tier": 3, "qtd": (1, 1), "ancora": "artes de sangue"},
    ],
    "cidade": [
        {"peso": 16, "que": "Guardas do portão exigindo taxa", "forma": "humano", "faccao": "corte_cinza",
         "rank": (1, 2), "tier": 1, "qtd": (2, 4), "ancora": "passaportes"},
        {"peso": 14, "que": "Agiota da Faca Cega com dois capangas", "forma": "humano", "faccao": "faca_cega",
         "rank": (2, 3), "tier": 2, "qtd": (1, 3), "ancora": "livro de nomes"},
        {"peso": 12, "que": "Discípulo da Garça em missão oficial", "forma": "humano", "faccao": "alianca_garça",
         "rank": (2, 4), "tier": 3, "qtd": (1, 2), "ancora": "manual roubado"},
        {"peso": 12, "que": "Duelo de honra marcado na praça", "forma": "humano", "faccao": None,
         "rank": (2, 3), "tier": 3, "qtd": (2, 2), "ancora": "Tábua VIII, juramentos"},
        {"peso": 10, "que": "Mendigo da rede de informação", "forma": "humano", "faccao": "errante",
         "rank": (1, 2), "tier": 2, "qtd": (1, 1), "ancora": "informação à venda"},
        {"peso": 10, "que": "Mercador de jade com uma peça que não devia existir", "forma": "humano", "faccao": "faca_cega",
         "rank": (1, 3), "tier": 3, "qtd": (1, 1), "ancora": "Tábuas de Jade"},
        {"peso": 8,  "que": "Emissário do Portão Carmesim, à luz do dia", "forma": "humano", "faccao": "portao_carmesim",
         "rank": (4, 5), "tier": 4, "qtd": (1, 1), "ancora": "guerra que vem"},
        {"peso": 8,  "que": "Procissão funerária de alguém importante", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 2, "qtd": (1, 1), "ancora": "quem morreu"},
        {"peso": 10, "que": "Bêbado que já foi mestre", "forma": "humano", "faccao": "errante",
         "rank": (3, 5), "tier": 3, "qtd": (1, 1), "ancora": "dívida antiga"},
    ],
    "montanha": [
        {"peso": 18, "que": "Discípulos da Garça em ronda", "forma": "humano", "faccao": "alianca_garça",
         "rank": (2, 3), "tier": 2, "qtd": (2, 4), "ancora": "manual roubado"},
        {"peso": 14, "que": "Fera de montanha (leopardo das brumas)", "forma": "nao_humano", "faccao": None,
         "rank": (2, 4), "tier": 0, "qtd": (1, 2), "ancora": "fauna local"},
        {"peso": 12, "que": "Um ancião sentado na pedra há anos", "forma": "humano", "faccao": "errante",
         "rank": (6, 7), "tier": 4, "qtd": (1, 1), "ancora": "Tábua VI"},
        {"peso": 12, "que": "Deslizamento / trilha destruída", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "chuva"},
        {"peso": 10, "que": "Monjas do Sino em silêncio absoluto", "forma": "humano", "faccao": "sino_silencioso",
         "rank": (3, 5), "tier": 3, "qtd": (2, 3), "ancora": "badalo perdido"},
        {"peso": 10, "que": "Contrabandistas com carga selada", "forma": "humano", "faccao": "faca_cega",
         "rank": (2, 3), "tier": 2, "qtd": (2, 4), "ancora": "contrabando"},
        {"peso": 8,  "que": "Um corpo pendurado, recente, com selo de jade", "forma": "humano", "faccao": "corte_cinza",
         "rank": (0, 0), "tier": 2, "qtd": (1, 1), "ancora": "herdeiro escondido"},
        {"peso": 8,  "que": "Ervas raras guardadas por algo que não é animal", "forma": "humano", "faccao": None,
         "rank": (3, 4), "tier": 1, "qtd": (1, 1), "ancora": "Tábua VII"},
        {"peso": 8,  "que": "Templo arruinado com inscrições da Tábua IX", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 2, "qtd": (1, 1), "ancora": "degrau acima do Último"},
    ],
    "ruina": [
        {"peso": 16, "que": "Guardião residual: Qi que tomou forma", "forma": "sem_forma", "faccao": None,
         "rank": (3, 5), "tier": 1, "qtd": (1, 1), "ancora": "Tábua VII"},
        {"peso": 14, "que": "Ladões de tumba, um deles já morreu lá dentro", "forma": "humano", "faccao": "corte_cinza",
         "rank": (1, 3), "tier": 2, "qtd": (2, 4), "ancora": "herdeiro escondido"},
        {"peso": 14, "que": "Praticante do Portão Carmesim colhendo cinza", "forma": "humano", "faccao": "portao_carmesim",
         "rank": (3, 4), "tier": 3, "qtd": (1, 2), "ancora": "Tábua IV"},
        {"peso": 12, "que": "Nada. Só o som da chuva parando de repente", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "Tábua IX"},
        {"peso": 12, "que": "Um sobrevivente de uma expedição anterior, louco", "forma": "humano", "faccao": "errante",
         "rank": (2, 3), "tier": 4, "qtd": (1, 1), "ancora": "o que ele viu"},
        {"peso": 10, "que": "Uma Tábua falsa sendo esculpida agora", "forma": "humano", "faccao": "faca_cega",
         "rank": (2, 4), "tier": 4, "qtd": (2, 3), "ancora": "Tábuas de Jade"},
        {"peso": 10, "que": "Cair de Qi: o ar pesa e feridas antigas abrem", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "Tábua II"},
        {"peso": 12, "que": "Um túmulo com o seu nome nele", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 4, "qtd": (1, 1), "ancora": "passado do personagem"},
    ],
    "porto": [
        {"peso": 18, "que": "Capangas da Faca Cega conferindo carga", "forma": "humano", "faccao": "faca_cega",
         "rank": (1, 3), "tier": 2, "qtd": (2, 5), "ancora": "monopólio do sal"},
        {"peso": 14, "que": "Marinheiros de fora da província", "forma": "humano", "faccao": "errante",
         "rank": (1, 2), "tier": 1, "qtd": (2, 4), "ancora": "o que existe além"},
        {"peso": 12, "que": "Contrabandista com passagem à venda", "forma": "humano", "faccao": "faca_cega",
         "rank": (2, 3), "tier": 2, "qtd": (1, 2), "ancora": "livro de nomes"},
        {"peso": 12, "que": "Uma barca que chegou vazia, com marcas de luta", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 2, "qtd": (1, 1), "ancora": "quem estava nela"},
        {"peso": 10, "que": "Cobrador do Portão Carmesim disfarçado de estivador", "forma": "humano", "faccao": "portao_carmesim",
         "rank": (3, 4), "tier": 3, "qtd": (1, 1), "ancora": "Tábua IV"},
        {"peso": 10, "que": "Prostituta/criado que ouve tudo", "forma": "humano", "faccao": None,
         "rank": (0, 1), "tier": 2, "qtd": (1, 1), "ancora": "informação à venda"},
        {"peso": 8,  "que": "Duelo por dívida de jogo", "forma": "humano", "faccao": None,
         "rank": (1, 2), "tier": 2, "qtd": (2, 2), "ancora": "Tábua VIII"},
        {"peso": 16, "que": "Chuva, cordame rangendo, ninguém olha para você", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "clima"},
    ],
    "templo": [
        {"peso": 22, "que": "Monja do Sino Silencioso", "forma": "humano", "faccao": "sino_silencioso",
         "rank": (2, 4), "tier": 3, "qtd": (1, 2), "ancora": "badalo perdido"},
        {"peso": 16, "que": "Peregrinos doentes pedindo cura", "forma": "humano", "faccao": "semeadores",
         "rank": (0, 1), "tier": 2, "qtd": (2, 5), "ancora": "epidemia"},
        {"peso": 14, "que": "A abadessa, em pessoa", "forma": "humano", "faccao": "sino_silencioso",
         "rank": (6, 6), "tier": 4, "qtd": (1, 1), "ancora": "ela falou uma vez"},
        {"peso": 12, "que": "Um sino pequeno sem badalo, esquecido num banco", "forma": "humano", "faccao": "sino_silencioso",
         "rank": (0, 0), "tier": 3, "qtd": (1, 1), "ancora": "badalo perdido"},
        {"peso": 12, "que": "Homem escondido no celeiro do templo", "forma": "humano", "faccao": "portao_carmesim",
         "rank": (3, 4), "tier": 4, "qtd": (1, 1), "ancora": "onze anos escondido"},
        {"peso": 12, "que": "Inscrições de uma Tábua que não combina com as outras", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 2, "qtd": (1, 1), "ancora": "Tábua Rachada"},
        {"peso": 12, "que": "Silêncio absoluto. Nenhum pássaro. Nenhuma chuva.", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "Tábua IX"},
    ],
    "pantano": [
        {"peso": 20, "que": "Gás de pântano acendendo sozinho", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "clima"},
        {"peso": 16, "que": "Corpos de uma batalha antiga, ainda de pé", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 2, "qtd": (1, 1), "ancora": "dinastia caída"},
        {"peso": 14, "que": "Sanguessugas de Qi (drenam Qi, não sangue)", "forma": "nao_humano", "faccao": None,
         "rank": (2, 3), "tier": 0, "qtd": (3, 8), "ancora": "Tábua I"},
        {"peso": 12, "que": "Um ermitão que mora numa casa sobre estacas", "forma": "humano", "faccao": "errante",
         "rank": (4, 6), "tier": 4, "qtd": (1, 1), "ancora": "dívida antiga"},
        {"peso": 12, "que": "Restos de uma barca da Faca Cega", "forma": "humano", "faccao": "faca_cega",
         "rank": (1, 2), "tier": 1, "qtd": (1, 3), "ancora": "carga perdida"},
        {"peso": 12, "que": "Alguém que você enterrou", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 4, "qtd": (1, 1), "ancora": "passado do personagem"},
        {"peso": 14, "que": "Névoa que devolve o som atrasado", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "Tábua VII"},
    ],
    "estalagem": [
        {"peso": 18, "que": "Mercadores jogando dados por sal", "forma": "humano", "faccao": "faca_cega",
         "rank": (0, 2), "tier": 1, "qtd": (2, 4), "ancora": "monopólio do sal"},
        {"peso": 16, "que": "Um forasteiro que não tira o chapéu", "forma": "humano", "faccao": "errante",
         "rank": (2, 4), "tier": 3, "qtd": (1, 1), "ancora": "passado do personagem"},
        {"peso": 14, "que": "Bandidos de folga, bêbados, do Passo da Garoa", "forma": "humano", "faccao": "irmaos_ferrugem",
         "rank": (1, 2), "tier": 1, "qtd": (2, 5), "ancora": "Irmandade da Ferrugem"},
        {"peso": 12, "que": "O estalajadeiro sabe de tudo e cobra caro", "forma": "humano", "faccao": None,
         "rank": (1, 2), "tier": 2, "qtd": (1, 1), "ancora": "informação à venda"},
        {"peso": 10, "que": "Discípulo expulso da Garça, procurando briga", "forma": "humano", "faccao": "alianca_garça",
         "rank": (2, 3), "tier": 3, "qtd": (1, 2), "ancora": "manual roubado"},
        {"peso": 10, "que": "Monge itinerante oferecendo chá", "forma": "humano", "faccao": "semeadores",
         "rank": (3, 5), "tier": 4, "qtd": (1, 1), "ancora": "dívida antiga"},
        {"peso": 10, "que": "Uma carta deixada na sua mesa por engano", "forma": "humano", "faccao": "corte_cinza",
         "rank": (0, 0), "tier": 3, "qtd": (1, 1), "ancora": "herdeiro escondido"},
        {"peso": 10, "que": "Chuva batendo na telha. Nada acontece.", "forma": "humano", "faccao": None,
         "rank": (0, 0), "tier": 0, "qtd": (1, 1), "ancora": "clima"},
    ],
}

ANIMAIS_LOCAL = [
    "javali de chifre de ferro", "leopardo das brumas", "garça de asa cinzenta",
    "serpente de bambu", "cão de arrozal", "peixe-lanterna do rio Verde",
    "macaco de mão prateada", "corvo de três gritos",
]

OBJETOS_LOCAL = [
    "selo de jade rachado", "moeda de bronze furada", "chuva de prata em fio",
    "tábua de jade falsa", "sino pequeno sem badalo", "vasilha de barro selada",
    "capa remendada", "dedo de bronze", "folha de chá prensada", "corda de bambu trançado",
]
