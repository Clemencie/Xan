# -*- coding: utf-8 -*-
"""
XAN — NPCs: personalidade, desejos, relações e conduta.
=======================================================

Requisito do sistema: *NPCs têm personalidades e desejos*. Aqui isso é um
**modelo computável**, não uma ficha de sugestões.

Três camadas
------------
1. **Personalidade** — as Cinco Virtudes confucianas (五常) mapeadas ao Wuxing,
   como na tradição:
       仁 Rén  Benevolência → Madeira     義 Yì  Retidão      → Metal
       禮 Lǐ   Propriedade  → Fogo        智 Zhì Sabedoria    → Água
       信 Xìn  Integridade  → Terra
   Mais um **Temperamento dos Oito Trigramas** (Bagua) e 2–4 **Traços** com
   efeito mecânico declarado.

2. **Desejos** — oito camadas independentes e frequentemente contraditórias:
   desejo imediato, ambição, obsessão, medo, dever, segredo, linha vermelha e
   preço. Cada camada é sorteada com peso derivado das virtudes, então a
   personalidade *causa* o desejo — não é decoração.

3. **Relações** — um livro-razão de eventos objetivos com peso inteiro.
   A **Disposição** é a *soma derivada*, nunca uma impressão do mestre.

Conduta resolvida por dado
--------------------------
Quando o que o NPC faria não é óbvio, quem decide é o motor imparcial: uma
``Declaracao`` comprometida por hash, rolada contra a Tabela de Conduta. O
mestre não escolhe. E quando dois desejos do próprio NPC entram em conflito, o
conflito também vai para o dado.

Tudo isto é gerado pela mesma ``Aleatoriedade`` auditada do resto do sistema:
semente reproduz o mesmo NPC, e a fonte viva impede manipulação na mesa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .auditoria import DiarioDeAuditoria
from .entropia import Aleatoriedade
from .personagens import Pericia, PERICIAS, RACAS, RaizEspiritual, sortear_raiz
from .regras import PRIORIDADE_DE_CAMADA_DE_DESEJO
from .reinos import CAMINHOS, LEIS, lei_de
from .resolucao import (
    Declaracao, Resultado, ResultadoOposto, resolver, teste_oposto,
)

__all__ = [
    "Virtudes", "VIRTUDE_ELEMENTO", "Temperamento", "TEMPERAMENTOS",
    "Traco", "TRACOS", "Desejos", "Npc", "gerar_npc",
    "VIRTUDE_PARA_ATRIBUTO", "EventoDeRelacao", "EVENTOS_DE_RELACAO",
    "LivroDeRelacoes", "PEDIDOS_TIPICOS",
    "DISPOSICOES", "disposicao_para", "TABELA_DE_CONDUTA",
    "resolver_conduta", "resolver_conflito_de_desejos", "Agenda", "camada_ativa",
    "VIRTUDE_DA_CAMADA",
    "gerar_nome", "SOBRENOMES",
]


# ==========================================================================
# 1. Personalidade
# ==========================================================================
VIRTUDE_ELEMENTO: Dict[str, str] = {
    "ren": "madeira", "yi": "metal", "li": "fogo", "zhi": "agua", "xin": "terra",
}

# Cada virtude governa o atributo do MESMO elemento:
#   ren 仁 Madeira → Inteligência    yi 義 Metal → Constituição
#   li 禮 Fogo    → Carisma         zhi 智 Água → Percepção
#   xin 信 Terra  → Potencial
VIRTUDE_PARA_ATRIBUTO: Dict[str, str] = {
    "ren": "int", "yi": "con", "li": "cha", "zhi": "per", "xin": "pot",
}


@dataclass(frozen=True)
class Virtudes:
    """As Cinco Virtudes (五常), cada uma de 1 a 10. Média mortal = 5."""

    ren: int
    yi: int
    li: int
    zhi: int
    xin: int

    def __post_init__(self) -> None:
        for nome in ("ren", "yi", "li", "zhi", "xin"):
            v = getattr(self, nome)
            if not isinstance(v, int) or isinstance(v, bool):
                raise TypeError(f"virtude {nome} deve ser int")
            if not (1 <= v <= 10):
                raise ValueError(f"virtude {nome}={v} fora de 1..10")

    @property
    def dominante(self) -> str:
        ordem = sorted((("ren", self.ren), ("yi", self.yi), ("li", self.li),
                        ("zhi", self.zhi), ("xin", self.xin)),
                       key=lambda kv: (-kv[1], kv[0]))
        return ordem[0][0]

    @property
    def falha(self) -> str:
        ordem = sorted((("ren", self.ren), ("yi", self.yi), ("li", self.li),
                        ("zhi", self.zhi), ("xin", self.xin)),
                       key=lambda kv: (kv[1], kv[0]))
        return ordem[0][0]

    def bonus(self, nome: str) -> int:
        """Bônus inteiro derivado: (virtude − 5) ÷ 2, arredondado para baixo."""
        if nome not in VIRTUDE_ELEMENTO:
            raise ValueError(f"virtude desconhecida {nome!r}")
        return (getattr(self, nome) - 5) // 2

    Nomes = {"ren": "Benevolência 仁", "yi": "Retidão 義", "li": "Propriedade 禮",
             "zhi": "Sabedoria 智", "xin": "Integridade 信"}

    def texto(self) -> str:
        partes = [f"{self.Nomes[k]} {getattr(self, k)}"
                  for k in ("ren", "yi", "li", "zhi", "xin")]
        return " · ".join(partes) + f"\n    dominante: {self.Nomes[self.dominante]} · falha: {self.Nomes[self.falha]}"


@dataclass(frozen=True)
class Temperamento:
    codigo: str
    nome: str
    trigram: str
    caractere: str
    natureza: str
    bonus_social: int
    bonus_iniciativa: int
    gatilho: str
    descricao: str


TEMPERAMENTOS: Dict[str, Temperamento] = {t.codigo: t for t in (
    Temperamento("qian", "O Céu", "乾", "☰", "imperativo", 2, 1,
                 "ser desobedecido por um inferior",
                 "Comanda como quem não concebe recusa. Fala pouco e decide tudo."),
    Temperamento("kun", "A Terra", "坤", "☷", "receptivo", 1, -1,
                 "ser forçado a escolher sozinho",
                 "Sustenta os outros. Enorme paciência; quando se move, é definitivo."),
    Temperamento("zhen", "O Trovão", "震", "☳", "impulsivo", -1, 3,
                 "ser interrompido ou humilhado",
                 "Age antes de pensar e pensa enquanto bate. Odiar devagar não existe."),
    Temperamento("xun", "O Vento", "巽", "☴", "instável", 2, 2,
                 "ficar preso a um compromisso",
                 "Penetra por qualquer fresta, muda de ideia sem aviso, nunca some de vez."),
    Temperamento("kan", "A Água", "坎", "☵", "astuto", 0, 1,
                 "ser exposto ou lido por outra pessoa",
                 "Guarda o que sabe. Perigo escondido dentro de beleza tranquila."),
    Temperamento("li", "O Fogo", "離", "☲", "apaixonado", 3, 0,
                 "ser ignorado ou deixado de fora",
                 "Brilha e se agarra ao que ama. Esplendor que precisa de combustível."),
    Temperamento("gen", "A Montanha", "艮", "☶", "obstinado", -2, 0,
                 "ser apressado",
                 "Para quando decide parar. Impossível empurrar, impossível apressar."),
    Temperamento("dui", "O Lago", "兌", "☱", "comunicativo", 3, -1,
                 "silêncio prolongado ou solidão",
                 "Fala, agrada e abre portas. Também abre a boca na hora errada."),
)}


@dataclass(frozen=True)
class Traco:
    codigo: str
    nome: str
    descricao: str
    efeito: str                     # texto de regra, sempre um modificador declarado
    dominio: str                    # social | combate | cultivo | mente | mundo
    peso_por_virtude: Tuple[str, ...]   # virtudes que tornam o traço mais provável
    incompativel: Tuple[str, ...] = ()


TRACOS: Dict[str, Traco] = {}


def _tr(codigo, nome, descricao, efeito, dominio, virtudes=(), incompativel=()):
    if codigo in TRACOS:
        raise ValueError(f"traço {codigo} duplicado")
    t = Traco(codigo, nome, descricao, efeito, dominio, tuple(virtudes),
              tuple(incompativel))
    TRACOS[codigo] = t
    return t


# --- sociais ---
_tr("GUARDA_RANCOR", "Guarda rancor por gerações",
    "Uma ofensa nunca é esquecida, nem perdoada, nem prescrita.",
    "SOCIAL:DISPOSICAO cai uma categoria e nunca sobe de volta com quem o ofendeu",
    "social", ("yi",), ("PERDOA_FACIL",))
_tr("PERDOA_FACIL", "Perdoa fácil demais",
    "Aceita qualquer desculpa, inclusive as falsas.",
    "+1 em SOCIAL:DISPOSICAO após pedido de desculpas; vulnerável a mentiras (−2 contra ENGANACAO)",
    "social", ("ren",), ("GUARDA_RANCOR",))
_tr("JURAMENTO_DE_SANGUE", "Leva juramentos a sangue",
    "Um juramento feito é um juramento cumprido, custe o que custar.",
    "+3 para resistir a qualquer proposta que exija quebrar um juramento",
    "social", ("yi", "xin"))
_tr("COBRADOR_DE_DIVIDAS", "Cobra toda dívida",
    "Registra cada favor recebido e cada favor concedido.",
    "+2 em NEGOCIACAO contra quem lhe deve; SOCIAL:DIVIDA_DE_HONRA sempre contado",
    "social", ("zhi", "xin"))
_tr("FACE_ACIMA_DE_TUDO", "A face acima de tudo",
    "Perder reputação dói mais que perder um braço.",
    "−4 em qualquer teste que envolva humilhação pública; +2 quando há plateia",
    "social", ("li",))
_tr("ANFITRIAO_PERFEITO", "Anfitrião perfeito",
    "Ninguém passa fome ou frio perto dele.",
    "+2 em ETIQUETA e NEGOCIACAO em território próprio", "social", ("li", "ren"))
_tr("BOCA_SOLTA", "Boca solta",
    "Conta o que não devia, especialmente depois de beber.",
    "−3 em MENTIRA; 25% de chance por cena de revelar um segredo que conhece",
    "social", (), ("SEGREDO_GUARDADO",))
_tr("SEGREDO_GUARDADO", "Guarda segredo até a morte",
    "Leva para o túmulo o que lhe foi confiado.",
    "+4 em MENTIRA e em resistir a interrogatório", "social", ("zhi", "xin"),
    ("BOCA_SOLTA",))
_tr("MENTOR_PACIENTE", "Mentor paciente",
    "Ensina sem cobrar e sem pressa.",
    "Discípulos aprendem manuais pela metade do custo de Compreensão",
    "social", ("ren", "xin"))
_tr("DESPREZA_FRACOS", "Despreza os fracos",
    "Não fala com quem considera inferior.",
    "−3 em SOCIAL contra personagens de nível 3+ abaixo do dele",
    "social", ("yi",), ("PROTEGE_FRACOS",))
_tr("PROTEGE_FRACOS", "Protege os fracos",
    "Não consegue assistir a uma injustiça calado.",
    "+2 em COMBATE quando defende alguém mais fraco; recusa recompensa por isso",
    "social", ("ren", "yi"), ("DESPREZA_FRACOS",))

# --- combate ---
_tr("SANGUE_QUENTE", "Sangue quente",
    "Aceita qualquer desafio, de qualquer um, em qualquer hora.",
    "+2 em COMBATE:SURPRESA a favor quando ele ataca primeiro; nunca recusa duelo",
    "combate", (), ("PRUDENCIA_EXTREMA",))
_tr("PRUDENCIA_EXTREMA", "Prudência extrema",
    "Só entra em luta que já venceu na cabeça.",
    "+2 em COMBATE:DEFESA_DECLARADA; −2 em iniciativa por excesso de cautela",
    "combate", ("zhi",), ("SANGUE_QUENTE",))
_tr("MATADOR_FRIO", "Matador frio",
    "Não sente nada ao matar. Nem prazer, nem culpa.",
    "imune a ESTADO:DEMONIO_INTERIOR por mortes cometidas; +1 em dano contra alvo ferido",
    "combate", ("xin",), ())
_tr("NAO_MATA_MULHERES", "Código: não mata quem se rende",
    "Existe uma linha que ele não cruza nem em guerra.",
    "recusa atacar alvo rendido; −2 em dano se forçado a fazê-lo",
    "combate", ("yi", "ren"))
_tr("COLECIONADOR_DE_ARMAS", "Coleciona armas",
    "Cada lâmina famosa do mundo tem dono na cabeça dele.",
    "+1 em RECURSO:ARTEFATO com armas; paga 50% acima do preço por armas de grau Céu",
    "combate", ())
_tr("DUELISTA_VANIDOSO", "Duelista vaidoso",
    "Anuncia a técnica antes de usar. Sempre.",
    "+2 de dano no golpe anunciado, mas o alvo sabe o que vem e ganha +1 de Defesa",
    "combate", ("li",))
_tr("LUTADOR_SUJO", "Luta sujo",
    "Areia nos olhos, faca na manga, veneno no chá.",
    "+2 em ARMA_OCULTA e PRESTIDIGITACAO; −2 em SOCIAL:FACE com ortodoxos",
    "combate", ("zhi",))
_tr("CORPO_DE_ACO", "Corpo de aço",
    "Já levou golpes que matariam três homens.",
    "+2 em ESTADO:FERIMENTO (sofre a penalidade uma categoria mais leve)",
    "combate", ("yi",))

# --- cultivo e mente ---
_tr("OBSESSO_POR_CULTIVO", "Obcecado pelo cultivo",
    "Dorme meditando. Conversa meditando.",
    "+2 em ganho de pontos de cultivo; −2 em SOCIAL quando o assunto não é cultivo",
    "cultivo", ("xin",))
_tr("CACADOR_DE_MANUAIS", "Caçador de manuais",
    "Trocaria a própria espada por uma página inédita.",
    "+2 em COMPREENSAO para aprender manuais; paga qualquer preço por escrituras",
    "cultivo", ("zhi",))
_tr("CORACAO_FRAGIL", "Coração do Dao frágil",
    "Duvita de si mesmo no pior momento possível.",
    "−10 de estado mental após qualquer fracasso crítico; risco de Desvio de Qi dobrado",
    "mente", (), ("CORACAO_DE_PEDRA",))
_tr("CORACAO_DE_PEDRA", "Coração de pedra",
    "Nada o abala. Nem tragédia, nem alegria.",
    "estado mental nunca cai abaixo de 60; −2 em SOCIAL:DISPOSICAO por parecer insensível",
    "mente", ("xin", "zhi"), ("CORACAO_FRAGIL",))
_tr("VISIONARIO", "Visionário",
    "Vê o padrão antes de o padrão existir.",
    "+2 em ASTROLOGIA e LEITURA_DE_FENGSHUI; previsões dele tendem a se cumprir",
    "mente", ("zhi",))
_tr("PARANOICO", "Paranoico",
    "Toda gentileza esconde uma faca.",
    "+3 em LEITURA_DE_PESSOAS; nunca aceita comida ou bebida de estranhos",
    "mente", ("zhi",), ("CONFIANCA_CEGA",))
_tr("CONFIANCA_CEGA", "Confiança cega",
    "Acredita em quem quer que fale com convicção.",
    "−3 em LEITURA_DE_PESSOAS; +2 em SOCIAL:HIERARQUIA ao obedecer superiores",
    "mente", ("ren",), ("PARANOICO",))
_tr("DEMÔNIO_ANTIGO", "Demônio Interior antigo",
    "Algo mora nele há anos e espera o pior dia para sair.",
    "−2 em VONTADE_DE_FERRO; em estado mental abaixo de 30, o demônio age por ele",
    "mente", ())
_tr("ILUMINADO", "Beira da iluminação",
    "Teve um vislumbre do Dao e nunca mais foi o mesmo.",
    "+2 em COMPREENSAO; fala em enigmas que só fazem sentido depois",
    "mente", ("zhi", "ren"))

# --- mundo e hábitos ---
_tr("VICIADO_EM_ELIXIRES", "Viciado em elixires",
    "Precisa de mais uma pílula. Só mais uma.",
    "+1 em RECURSO:ELIXIR; a cada mês sem elixir perde 5 de estado mental",
    "mundo", ())
_tr("JOVEM_MESTRE_ARROGANTE", "Jovem mestre arrogante",
    "Filho de alguém importante e consciente disso a cada frase.",
    "+3 em SOCIAL:HIERARQUIA contra inferiores; −3 contra superiores; provoca duelos",
    "social", ("li",))
_tr("SERVO_HUMILDE", "Servo humilde",
    "Nasceu para obedecer e aprendeu a gostar.",
    "+2 em obedecer ordens; −3 em liderar; some em multidões",
    "social", (), ("JOVEM_MESTRE_ARROGANTE",))
_tr("EREMITA", "Eremita",
    "Vive longe e não quer visita.",
    "+2 em SOBREVIVENCIA e MEDITACAO em local isolado; −2 em ETIQUETA",
    "mundo", ("xin",))
_tr("ANDARILHO", "Andarilho sem raiz",
    "Nunca ficou mais de um mês no mesmo lugar.",
    "+2 em SOBREVIVENCIA e NAVEGACAO; nenhum aliado tem DISPOSICAO acima de cordial",
    "mundo", (), ())
_tr("COMERCIANTE_NATO", "Comerciante nato",
    "Vende gelo a um cultivador de Gelo.",
    "+3 em COMERCIO e NEGOCIACAO; nunca paga preço cheio",
    "mundo", ("zhi",))
_tr("MEDICO_COMPASSIVO", "Médico compassivo",
    "Trata qualquer um, de qualquer seita, sem perguntar.",
    "+3 em MEDICINA; recusa cobrar de pobres; ganha Dívida de Honra de quem salva",
    "mundo", ("ren",))
_tr("VENENOLOGO", "Venenólogo",
    "Conhece trezentas formas de alguém morrer dormindo.",
    "+3 em RESISTENCIA_A_VENENO e ERVAS; temido por todas as seitas ortodoxas",
    "mundo", ("zhi",))
_tr("CAÇADOR_DE_DEMONIOS", "Caçador de demônios",
    "Jurou exterminar uma linhagem inteira.",
    "+2 de dano contra bestas espirituais e corrompidos; nunca recusa essa caçada",
    "mundo", ("yi",))
_tr("BEBERRAO", "Beberrão impenitente",
    "Genial sóbrio, insuportável bêbado — e está sempre bêbado.",
    "−1 em testes com graduação alta enquanto bebe; +2 em MENTIRA para se safar",
    "mundo", ())
_tr("SONHADOR", "Sonhador incurável",
    "Fala de um futuro que ninguém mais enxerga.",
    "+2 em INSPIRAR aliados; −2 em PERCEBER ameaças imediatas",
    "mundo", ("ren",))
_tr("CUMPRIDOR_DE_CONTRATOS", "Cumpridor de contratos",
    "O papel vale mais que a pessoa.",
    "nunca quebra um contrato escrito; +2 em COMERCIO com contrato firmado",
    "mundo", ("xin",))
_tr("PROFETA_AUTOPROCLAMADO", "Profeta autoproclamado",
    "Acredita que o céu fala com ele. Talvez fale.",
    "+2 em ASTROLOGIA e LIDERANCA sobre crentes; perde Face a cada profecia errada",
    "mundo", ("li",))
_tr("GUARDIAO_DE_PORTA", "Guardião de porta",
    "Passou a vida impedindo que algo saísse — ou entrasse.",
    "+3 em resistir a travessias; conhece um segredo do que guarda",
    "mundo", ("xin", "yi"))
_tr("HERDEIRO_DECEPCIONADO", "Herdeiro decepcionado",
    "A família esperava um gênio e ganhou ele.",
    "+2 em provar valor diante da própria facção; −2 de estado mental em reuniões de clã",
    "social", ())
_tr("RETORNADO", "Retornado do abismo",
    "Morreu, viu algo, voltou. Não é mais bem o mesmo.",
    "+2 em VONTADE_DE_FERRO contra medo; −2 em SOCIAL com quem não sabe",
    "mente", ())


# ==========================================================================
# 2. Desejos
# ==========================================================================
# Cada camada é uma lista de (texto, pesos por virtude dominante).
# O peso é inteiro: ren/yi/li/zhi/xin.
_DESEJO_IMEDIATO: Tuple[Tuple[str, Tuple[int, int, int, int, int]], ...] = (
    ("Chegar a tempo de impedir uma execução pública", (3, 4, 1, 1, 1)),
    ("Vender uma informação antes que ela estrague", (0, 1, 2, 4, 1)),
    ("Comprar uma erva específica, custe o que custar", (1, 0, 1, 3, 2)),
    ("Provar a alguém que não é mais um inútil", (2, 2, 3, 1, 2)),
    ("Encontrar um lugar seguro para dormir esta noite", (1, 0, 1, 3, 2)),
    ("Humilhar publicamente um rival", (0, 1, 3, 2, 0)),
    ("Entregar uma carta sem saber o que ela contém", (0, 1, 1, 1, 5)),
    ("Recrutar os personagens para uma escolta", (2, 2, 3, 2, 1)),
    ("Matar alguém antes do fim do dia", (0, 3, 0, 2, 1)),
    ("Descobrir quem o está seguindo", (0, 1, 0, 5, 1)),
    ("Recuperar um objeto que lhe foi roubado", (1, 4, 1, 2, 2)),
    ("Pedir perdão a alguém que não merece", (5, 2, 2, 0, 3)),
    ("Aprender uma única linha de um manual proibido", (0, 1, 0, 4, 1)),
    ("Sair desta cidade antes que a seita chegue", (1, 0, 1, 3, 2)),
    ("Conseguir um discípulo antes de morrer", (3, 2, 2, 1, 4)),
    ("Beber até esquecer o que viu", (2, 0, 1, 0, 0)),
    ("Comprar a liberdade de alguém", (5, 3, 2, 1, 2)),
    ("Ganhar um torneio local de apostas", (0, 0, 2, 2, 1)),
)
_AMBICAO: Tuple[Tuple[str, Tuple[int, int, int, int, int]], ...] = (
    ("Tornar-se Mestre da própria seita", (1, 3, 3, 2, 2)),
    ("Fundar uma seita que dure mil anos", (2, 2, 3, 3, 3)),
    ("Formar um Núcleo Dourado de grau 1", (1, 2, 1, 3, 4)),
    ("Ascender e deixar um altar para os descendentes", (1, 2, 1, 3, 3)),
    ("Vingar o extermínio do próprio clã", (1, 5, 0, 2, 2)),
    ("Reunir as sete partes de um manual partido", (0, 1, 0, 5, 3)),
    ("Ser lembrado como o maior espadachim da era", (1, 3, 4, 1, 1)),
    ("Curar uma doença que ninguém mais cura", (5, 2, 1, 3, 3)),
    ("Acabar com uma facção demoníaca inteira", (3, 5, 1, 2, 2)),
    ("Ficar rico o bastante para comprar uma montanha", (0, 1, 1, 4, 2)),
    ("Encontrar o imortal que salvou sua vida na infância", (3, 2, 2, 2, 4)),
    ("Devolver ao mundo o que a família dele tirou", (5, 4, 1, 1, 3)),
    ("Descobrir o que existe depois da Ascensão", (0, 0, 0, 5, 1)),
    ("Criar os filhos longe do Murim", (5, 2, 2, 2, 4)),
    ("Matar o próprio mestre", (0, 2, 0, 3, 0)),
    ("Unificar o Murim sob uma única aliança", (2, 4, 4, 3, 3)),
    ("Escrever um manual que supere todos os outros", (1, 1, 1, 5, 3)),
    ("Quebrar o ciclo de reencarnação de uma pessoa amada", (4, 2, 1, 3, 3)),
)
_OBSESSAO: Tuple[Tuple[str, Tuple[int, int, int, int, int]], ...] = (
    ("Não pode ver um superior sendo injusto sem intervir", (4, 4, 1, 0, 1)),
    ("Precisa vencer cada duelo, mesmo os que não importam", (0, 3, 4, 1, 0)),
    ("Não consegue mentir. Fisicamente.", (1, 3, 2, 0, 5)),
    ("Coleciona promessas alheias e as cobra no pior momento", (0, 1, 1, 4, 2)),
    ("Não abandona ninguém para trás, nem inimigos feridos", (5, 3, 1, 0, 3)),
    ("Só dorme com a arma na mão", (0, 2, 0, 3, 2)),
    ("Precisa ser o último a sair de qualquer sala", (0, 0, 4, 1, 0)),
    ("Não aceita dinheiro de quem considera inferior", (1, 4, 3, 0, 2)),
    ("Faz uma oferenda antes de cada refeição", (2, 1, 4, 0, 4)),
    ("Não suporta ver sangue derramado em terreno sagrado", (4, 3, 2, 0, 2)),
    ("Testa todo mundo, o tempo todo, sem avisar", (0, 1, 1, 5, 0)),
    ("Nunca repete um caminho duas vezes", (0, 0, 0, 4, 1)),
    ("Registra cada morte que causa, em pedra ou papel", (1, 3, 0, 2, 4)),
    ("Não consegue recusar um pedido de criança", (5, 2, 1, 0, 3)),
    ("Precisa saber o nome verdadeiro de todos à volta", (0, 0, 0, 5, 2)),
    ("Cuida de uma planta que não existe mais", (3, 0, 0, 0, 2)),
)
_MEDO: Tuple[Tuple[str, Tuple[int, int, int, int, int]], ...] = (
    ("Fogo — viu a aldeia queimar quando criança", (1, 1, 1, 1, 1)),
    ("Ser esquecido por quem ama", (3, 1, 2, 1, 2)),
    ("Alturas, apesar de saber voar", (0, 0, 1, 1, 0)),
    ("O próprio reflexo desde a última ruptura", (0, 0, 0, 3, 1)),
    ("Perder o cultivo e voltar a ser mortal", (1, 2, 2, 2, 3)),
    ("Trair sem querer — sonha que já traiu", (1, 4, 1, 1, 3)),
    ("Um homem específico que ele já viu uma vez", (0, 2, 0, 3, 1)),
    ("Silêncio absoluto", (1, 0, 2, 1, 1)),
    ("Ser responsável pela morte de um inocente", (5, 3, 1, 1, 3)),
    ("Água parada", (1, 0, 0, 1, 1)),
    ("A própria raiva", (2, 2, 1, 2, 1)),
    ("Não ser suficiente", (2, 2, 3, 1, 2)),
    ("Multidões olhando", (0, 0, 3, 0, 1)),
    ("Ficar sozinho para sempre", (3, 0, 2, 0, 1)),
)
_DEVER: Tuple[Tuple[str, Tuple[int, int, int, int, int]], ...] = (
    ("Para com o mestre que o tirou da sarjeta", (2, 3, 2, 1, 5)),
    ("Para com a seita, acima da própria vida", (1, 4, 3, 1, 4)),
    ("Para com um irmão de juramento", (3, 4, 1, 1, 4)),
    ("Para com a família, que não sabe o que ele faz", (4, 2, 3, 1, 3)),
    ("Para com uma promessa feita a um moribundo", (2, 4, 1, 1, 5)),
    ("Para com os discípulos que dependem dele", (5, 2, 2, 1, 4)),
    ("Para com o Império, que odeia o Murim", (0, 3, 3, 2, 3)),
    ("Para com um deus que exige fé diária", (2, 2, 4, 0, 4)),
    ("Para com ninguém — e isso o assombra", (0, 0, 0, 2, 0)),
    ("Para com uma dívida de sangue ainda não paga", (1, 5, 0, 2, 3)),
    ("Para com a cidade onde nasceu", (4, 3, 2, 1, 3)),
    ("Para com o próprio nome, que carrega o de outro", (1, 2, 3, 2, 3)),
)
_SEGREDO: Tuple[Tuple[str, Tuple[int, int, int, int, int]], ...] = (
    ("Matou o próprio irmão de seita por acidente e culpou outro", (0, 1, 0, 3, 1)),
    ("Sua Raiz Espiritual é uma mutação que ele esconde", (0, 0, 1, 4, 1)),
    ("Está morrendo: faltam menos de dois anos", (1, 1, 1, 2, 3)),
    ("Aprende uma arte demoníaca em segredo", (0, 1, 0, 3, 0)),
    ("Nunca formou o Núcleo — finge com truques e talismãs", (0, 1, 1, 4, 0)),
    ("É filho ilegítimo de um Ancião de outra seita", (1, 1, 2, 1, 2)),
    ("Traiu uma vez e ninguém nunca soube", (0, 2, 0, 2, 1)),
    ("Guarda o mapa de uma ruína que já saqueou sozinho", (0, 1, 0, 3, 1)),
    ("Tem um Demônio Interior antigo adormecido", (0, 1, 0, 2, 2)),
    ("Salvou um demônio e o deixou fugir", (3, 1, 0, 1, 2)),
    ("Vende informações para uma facção inimiga", (0, 0, 1, 3, 0)),
    ("Queimou longevidade para vencer um duelo — e perdeu dez anos", (1, 2, 1, 2, 2)),
    ("Não é quem diz ser; o verdadeiro morreu em seus braços", (1, 1, 1, 2, 2)),
    ("Ama alguém de uma facção inimiga", (3, 1, 1, 0, 2)),
)
_LINHA_VERMELHA: Tuple[Tuple[str, Tuple[int, int, int, int, int]], ...] = (
    ("Nunca mata crianças — nem demônios crianças", (5, 4, 2, 1, 3)),
    ("Nunca quebra um juramento, nem sob tortura", (1, 5, 2, 1, 5)),
    ("Nunca ataca pelas costas", (1, 4, 3, 0, 3)),
    ("Nunca recusa abrigo a um perseguido", (5, 3, 2, 0, 3)),
    ("Nunca revela o que um paciente lhe conta", (2, 2, 2, 2, 5)),
    ("Nunca luta contra o próprio mestre", (2, 3, 3, 0, 4)),
    ("Nunca usa veneno", (1, 4, 2, 0, 3)),
    ("Nunca abandona um cadáver sem ritos", (3, 2, 4, 0, 4)),
    ("Nunca mente sobre o próprio nome", (1, 3, 1, 0, 5)),
    ("Nenhuma — e é exatamente isso que o torna perigoso", (0, 0, 0, 2, 0)),
    ("Nunca rouba de pobres", (4, 3, 1, 1, 3)),
    ("Nunca desobedece uma ordem direta do superior", (0, 2, 4, 0, 5)),
)
_PRECO: Tuple[Tuple[str, Tuple[int, int, int, int, int]], ...] = (
    ("Pedras espirituais — qualquer quantia resolve quase tudo", (0, 1, 1, 3, 0)),
    ("Um manual de grau Céu", (0, 1, 0, 4, 1)),
    ("A liberdade de alguém que ele ama", (4, 2, 1, 1, 3)),
    ("O nome de quem o humilhou", (1, 3, 1, 2, 1)),
    ("Uma erva que só cresce onde ninguém vai", (0, 1, 0, 4, 2)),
    ("Um dia de vida a mais", (1, 1, 1, 2, 4)),
    ("Que alguém o chame de mestre, com sinceridade", (3, 1, 3, 0, 3)),
    ("Nada: não pode ser comprado, só convencido", (2, 4, 2, 2, 5)),
    ("A cabeça de um inimigo específico", (0, 4, 0, 2, 1)),
    ("Um lugar para pertencer", (4, 1, 2, 0, 3)),
    ("Uma mentira dita a alguém importante", (0, 1, 1, 3, 0)),
    ("O perdão de uma pessoa que ele feriu", (5, 3, 1, 0, 4)),
)


@dataclass(frozen=True)
class Desejos:
    imediato: str
    ambicao: str
    obsessao: str
    medo: str
    dever: str
    segredo: str
    linha_vermelha: str
    preco: str

    def texto(self) -> str:
        return "\n".join(
            f"    {rotulo}: {valor}" for rotulo, valor in (
                ("Desejo imediato", self.imediato),
                ("Ambição", self.ambicao),
                ("Obsessão", self.obsessao),
                ("Medo", self.medo),
                ("Dever", self.dever),
                ("Segredo", self.segredo),
                ("Linha vermelha", self.linha_vermelha),
                ("Preço", self.preco),
            )
        )

    def prioridades(self) -> Tuple[str, ...]:
        """Ordem em que estes desejos mandam quando conflitam.

        Derivada aritmeticamente da personalidade — não é escolha do mestre:
        1. Medo (sobrevivência imediata)
        2. Linha vermelha (o que jamais fará: sempre vence qualquer oferta)
        3. Dever (compromisso com terceiros)
        4. Obsessão (compulsão)
        5. Ambição (objetivo de vida)
        6. Desejo imediato (a cena atual)
        7. Preço (o que o faz mudar de lado)
        """
        return ("medo", "linha_vermelha", "dever", "obsessao", "ambicao",
                "imediato", "preco")


def _sortear_desejos(aleat: Aleatoriedade, v: Virtudes) -> Desejos:
    pesos_v = (v.ren, v.yi, v.li, v.zhi, v.xin)

    def escolha(tabela):
        itens = [t[0] for t in tabela]
        pesos = []
        for _, pv in tabela:
            # peso base 1 + alinhamento com as virtudes do NPC
            w = 1 + sum(a * b for a, b in zip(pv, pesos_v))
            pesos.append(max(1, w))
        return aleat.escolher_ponderado(itens, pesos)

    return Desejos(
        imediato=escolha(_DESEJO_IMEDIATO),
        ambicao=escolha(_AMBICAO),
        obsessao=escolha(_OBSESSAO),
        medo=escolha(_MEDO),
        dever=escolha(_DEVER),
        segredo=escolha(_SEGREDO),
        linha_vermelha=escolha(_LINHA_VERMELHA),
        preco=escolha(_PRECO),
    )


def _sortear_tracos(aleat: Aleatoriedade, v: Virtudes, quantidade: int) -> Tuple[str, ...]:
    escolhidos: List[str] = []
    bloqueados: set = set()
    for _ in range(quantidade):
        candidatas = []
        pesos = []
        for codigo, t in TRACOS.items():
            if codigo in escolhidos or codigo in bloqueados:
                continue
            w = 1
            for virt in t.peso_por_virtude:
                w += max(0, getattr(v, virt) - 4) * 2
            if not t.peso_por_virtude:
                w = 2
            candidatas.append(codigo)
            pesos.append(max(1, w))
        if not candidatas:
            break
        codigo = aleat.escolher_ponderado(candidatas, pesos)
        escolhidos.append(codigo)
        bloqueados.update(TRACOS[codigo].incompativel)
    return tuple(escolhidos)


# ==========================================================================
# 3. Relações — livro-razão com pesos inteiros
# ==========================================================================
EVENTOS_DE_RELACAO: Dict[str, int] = {
    "salvou_a_vida": 6,
    "salvou_um_ente_querido": 8,
    "curou_uma_ferida": 3,
    "ensinou_uma_tecnica": 4,
    "deu_um_presente_de_grau_superior": 3,
    "cumpriu_uma_promessa": 3,
    "defendeu_em_publico": 4,
    "venceu_um_duelo_honrado": 2,
    "perdeu_um_duelo_honrado": -1,
    "mentiu_para_ele": -3,
    "roubou_dele": -5,
    "humilhou_em_publico": -6,
    "matou_um_aliado": -10,
    "matou_um_familiar": -20,
    "quebrou_um_juramento": -7,
    "revelou_o_segredo_dele": -12,
    "recusou_ajuda_em_crise": -4,
    "trocou_favores": 2,
    "compartilhou_uma_refeicao": 1,
    "serviu_juntos_na_mesma_seita": 2,
    "faccoes_em_guerra": -4,
    "faccoes_aliadas": 3,
    "hierarquia_superior_dele": 2,
    "hierarquia_inferior_dele": -1,
    "dever_de_honra": 5,
}

# Faixas simétricas — as mesmas publicadas no LIVRO cap. 12.7 e 21.14.
DISPOSICOES: Tuple[Tuple[int, str], ...] = (
    (10, "devoto"),          # ≥ 10
    (6, "amigavel"),         # 6 a 9
    (3, "cordial"),          # 3 a 5
    (-2, "neutro"),          # −2 a 2
    (-5, "desconfiado"),     # −5 a −3
    (-9, "hostil"),          # −9 a −6
    (-10 ** 9, "inimigo_jurado"),   # ≤ −10
)


def disposicao_para(valor: int) -> str:
    """Categoria derivada da soma do livro-razão. Nunca é opinião."""
    for limiar, nome in DISPOSICOES:
        if valor >= limiar:
            return nome
    return "inimigo_jurado"


@dataclass(frozen=True)
class EventoDeRelacao:
    codigo: str
    peso: int
    quando: str
    detalhe: str
    alvo: str

    def __post_init__(self) -> None:
        if self.codigo not in EVENTOS_DE_RELACAO:
            raise ValueError(
                f"evento de relação {self.codigo!r} não catalogado. "
                f"Catálogo: {len(EVENTOS_DE_RELACAO)} eventos.")
        if self.peso != EVENTOS_DE_RELACAO[self.codigo]:
            raise ValueError(
                f"peso declarado {self.peso} ≠ peso do catálogo "
                f"{EVENTOS_DE_RELACAO[self.codigo]} para {self.codigo}"
            )


@dataclass
class LivroDeRelacoes:
    """Ledger append-only de fatos relacionais entre um NPC e vários alvos."""

    eventos: Tuple[EventoDeRelacao, ...] = ()

    def registrar(self, codigo: str, alvo: str, quando: str = "",
                  detalhe: str = "",
                  diario: Optional[DiarioDeAuditoria] = None,
                  ator: str = "") -> "LivroDeRelacoes":
        if codigo not in EVENTOS_DE_RELACAO:
            raise ValueError(f"evento {codigo!r} não catalogado")
        ev = EventoDeRelacao(codigo, EVENTOS_DE_RELACAO[codigo], quando,
                             detalhe, alvo)
        self.eventos = self.eventos + (ev,)
        if diario is not None:
            diario.registrar(
                "relacao",
                {"codigo": codigo, "alvo": alvo, "peso": ev.peso,
                 "quando": quando, "detalhe": detalhe},
                ator=ator,
            )
        return self

    def disposicao(self, alvo: str) -> int:
        return sum(e.peso for e in self.eventos if e.alvo == alvo)

    def categoria(self, alvo: str) -> str:
        return disposicao_para(self.disposicao(alvo))

    def historico(self, alvo: str) -> Tuple[EventoDeRelacao, ...]:
        return tuple(e for e in self.eventos if e.alvo == alvo)


# ==========================================================================
# Agenda (relógio de 6 segmentos) e Npc
# ==========================================================================
@dataclass
class Agenda:
    """Relógio de progresso de um plano fora de cena.

    Avança por **rolagem**, não por vontade do mestre: cada avanço consome um
    dado e fica registrado. Quando enche, a agenda acontece — queira o grupo ou
    não.
    """

    objetivo: str
    segmentos: int = 6
    preenchidos: int = 0
    dificuldade: int = 15
    historico: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not (2 <= self.segmentos <= 12):
            raise ValueError("relógios têm de 2 a 12 segmentos")
        if self.preenchidos > self.segmentos:
            raise ValueError("relógio não pode estar mais cheio que o tamanho")

    def completa(self) -> bool:
        return self.preenchidos >= self.segmentos

    def avancar(self, quanto: int, motivo: str) -> int:
        if quanto <= 0:
            raise ValueError("avanço deve ser positivo")
        antes = self.preenchidos
        self.preenchidos = min(self.segmentos, self.preenchidos + quanto)
        self.historico = self.historico + (f"+{self.preenchidos - antes} {motivo}",)
        return self.preenchidos


def _milhar(n: int) -> str:
    """Formata inteiro com separador de milhar em pt-BR, sem float."""
    negativo = n < 0
    s = str(abs(int(n)))
    grupos = []
    while s:
        grupos.append(s[-3:])
        s = s[:-3]
    out = ".".join(reversed(grupos)) or "0"
    return ("-" if negativo else "") + out


@dataclass
class Npc:
    """Um ser humano completo, gerado por regras e auditável."""

    nome: str
    sexo: str
    idade: int
    raca: str
    virtudes: Virtudes
    temperamento: Temperamento
    tracos: Tuple[str, ...]
    desejos: Desejos
    atributos: Mapping[str, int]
    pericias: Mapping[str, int]
    nivel: int
    caminho: str
    lei: Optional[str]
    raiz: RaizEspiritual
    faccao: str
    posto: str
    ocupacao: str
    localizacao: str
    face: int
    estado_mental: int
    pedras_espirituais: int
    tecnicas: Tuple[str, ...]
    livros: Dict[str, LivroDeRelacoes] = field(default_factory=dict)
    agendas: Tuple[Agenda, ...] = ()
    segredo_conhecido_por: Tuple[str, ...] = ()
    identificador: str = ""

    # -- derivados ---------------------------------------------------------
    def bonus(self, atributo: str) -> int:
        return (int(self.atributos[atributo]) - 10) // 2

    def disposicao_para(self, alvo: str) -> Tuple[int, str]:
        livro = self.livros.get(alvo)
        if livro is None:
            return 0, "neutro"
        return livro.disposicao(alvo), livro.categoria(alvo)

    def fato_de_disposicao(self, alvo: str) -> Dict[str, str]:
        """Fato pronto para alimentar SOCIAL:DISPOSICAO no Registro de Regras."""
        return {"disposicao": self.disposicao_para(alvo)[1]}

    def registrar_relacao(self, alvo: str, codigo: str, quando: str = "",
                          detalhe: str = "",
                          diario: Optional[DiarioDeAuditoria] = None) -> None:
        livro = self.livros.setdefault(alvo, LivroDeRelacoes())
        livro.registrar(codigo, alvo, quando, detalhe, diario, ator=self.nome)

    def qi_max(self) -> int:
        from .reinos import qi_maximo
        return qi_maximo(self.nivel, self.atributos["con"], self.atributos["per"],
                         self.atributos["int"])

    def vitalidade_max(self) -> int:
        from .reinos import vitalidade_maxima
        return vitalidade_maxima(self.nivel, self.atributos["con"],
                                 self.atributos["pot"])

    def ficha(self) -> str:
        a = self.atributos
        attrs = " ".join(f"{k.upper()}{a[k]}" for k in ("per", "con", "cha", "int", "luk", "pot"))
        tracos_txt = "; ".join(TRACOS[t].nome for t in self.tracos) or "—"
        from .reinos import reino_de
        lei_txt = lei_de(self.lei).nome if self.lei else "sem Lei (marcial comum)"
        linhas = [
            f"## {self.nome}",
            f"*{self.ocupacao} · {self.faccao or 'sem facção'}"
            f"{(' — ' + self.posto) if self.posto else ''} · {self.localizacao}*",
            "",
            f"- **Corpo:** {self.raca}, {self.sexo}, {self.idade} anos",
            f"- **Cultivo:** nível {self.nivel} — {reino_de(self.nivel).nome_para(self.caminho)}"
            f" · caminho {self.caminho} · {lei_txt}",
            f"- **Atributos:** {attrs}",
            f"- **Qi máx:** {self.qi_max()} · **Vitalidade máx:** {self.vitalidade_max()}",
            f"- **Raiz:** {self.raiz.texto()}",
            f"- **Temperamento:** {self.temperamento.nome} {self.temperamento.caractere}"
            f" ({self.temperamento.trigram}) — {self.temperamento.natureza}. "
            f"*Gatilho:* {self.temperamento.gatilho}",
            f"- **Cinco Virtudes:** {self.virtudes.texto()}",
            f"- **Traços:** {tracos_txt}",
            f"- **Face:** {self.face} · **Estado mental:** {self.estado_mental}/200 · "
            f"**Pedras espirituais:** {_milhar(self.pedras_espirituais)}",
            f"- **Técnicas:** {', '.join(self.tecnicas) or '—'}",
            "",
            "### Desejos",
            self.desejos.texto(),
        ]
        if self.agendas:
            linhas += ["", "### Agendas em curso"]
            for ag in self.agendas:
                linhas.append(
                    f"- {ag.objetivo}: {ag.preenchidos}/{ag.segmentos}"
                    + (" — **COMPLETA**" if ag.completa() else ""))
        if self.livros:
            linhas += ["", "### Livro de relações"]
            for alvo in sorted(self.livros):
                livro = self.livros[alvo]
                linhas.append(
                    f"- **{alvo}**: disposição {livro.disposicao(alvo):+d} "
                    f"→ {livro.categoria(alvo)}")
                for e in livro.eventos:
                    linhas.append(f"    - {e.codigo} ({e.peso:+d}) {e.quando} — {e.detalhe}")
        return "\n".join(linhas)


# ==========================================================================
# Nomes
# ==========================================================================
SOBRENOMES: Tuple[Tuple[str, str], ...] = (
    ("Li", "李"), ("Wang", "王"), ("Zhang", "張"), ("Liu", "劉"), ("Chen", "陳"),
    ("Yang", "楊"), ("Zhao", "趙"), ("Huang", "黃"), ("Zhou", "周"), ("Wu", "吳"),
    ("Xu", "徐"), ("Sun", "孫"), ("Ma", "馬"), ("Zhu", "朱"), ("Hu", "胡"),
    ("Guo", "郭"), ("He", "何"), ("Lin", "林"), ("Gao", "高"), ("Luo", "羅"),
    ("Zheng", "鄭"), ("Liang", "梁"), ("Xie", "謝"), ("Song", "宋"), ("Tang", "唐"),
    ("Han", "韓"), ("Feng", "馮"), ("Cao", "曹"), ("Peng", "彭"), ("Zeng", "曾"),
    ("Xiao", "蕭"), ("Tian", "田"), ("Dong", "董"), ("Pan", "潘"), ("Yuan", "袁"),
    ("Cai", "蔡"), ("Jiang", "蔣"), ("Yu", "余"), ("Du", "杜"), ("Ye", "葉"),
    ("Cheng", "程"), ("Su", "蘇"), ("Wei", "魏"), ("Lü", "呂"), ("Ding", "丁"),
    ("Shen", "沈"), ("Ren", "任"), ("Yao", "姚"), ("Lu", "盧"), ("Fu", "傅"),
    ("Zhong", "鍾"), ("Cui", "崔"), ("Tan", "譚"), ("Liao", "廖"), ("Fan", "範"),
    ("Jin", "金"), ("Shi", "石"), ("Dai", "戴"), ("Jia", "賈"), ("Xia", "夏"),
    ("Qiu", "邱"), ("Fang", "方"), ("Hou", "侯"), ("Zou", "鄒"), ("Xiong", "熊"),
    ("Meng", "孟"), ("Qin", "秦"), ("Bai", "白"), ("Yan", "閻"), ("Xue", "薛"),
    ("Duan", "段"), ("Lei", "雷"), ("Tao", "陶"), ("Mao", "毛"), ("Chang", "常"),
    ("Gu", "顧"), ("Lai", "賴"), ("Kang", "康"), ("Hua", "華"), ("Hong", "洪"),
    ("Gong", "龔"), ("Nangong", "南宮"), ("Murong", "慕容"), ("Zhuge", "諸葛"),
    ("Sima", "司馬"), ("Shangguan", "上官"), ("Dongfang", "東方"), ("Dugu", "獨孤"),
    ("Huangfu", "皇甫"), ("Linghu", "令狐"), ("Zhangsun", "長孫"),
    ("Yuchi", "尉遲"), ("Gongsun", "公孫"), ("Tang", "唐門"),
)

_NOMES_MASCULINOS: Tuple[Tuple[str, str], ...] = (
    ("Tian", "天"), ("Yun", "雲"), ("Feng", "風"), ("Long", "龍"), ("Hu", "虎"),
    ("Shan", "山"), ("Yue", "岳"), ("Hai", "海"), ("Chuan", "川"), ("Shi", "石"),
    ("Tie", "鐵"), ("Jian", "劍"), ("Ying", "影"), ("Guang", "光"), ("Ming", "明"),
    ("Qing", "清"), ("Xuan", "玄"), ("Wu", "無"), ("Ji", "極"), ("Tai", "太"),
    ("Yang", "陽"), ("Gang", "剛"), ("Yong", "勇"), ("Zhi", "志"), ("Cheng", "承"),
    ("Chang", "長"), ("Qian", "千"), ("Wan", "萬"), ("Han", "寒"), ("Shuang", "霜"),
    ("Lei", "雷"), ("Dian", "電"), ("Xing", "星"), ("Chen", "辰"), ("Hao", "昊"),
    ("Xuan", "軒"), ("Yu", "宇"), ("Bo", "博"), ("Wen", "文"), ("Wu", "武"),
    ("Ren", "仁"), ("Yi", "義"), ("De", "德"), ("Dao", "道"), ("Zhen", "真"),
    ("Shan", "善"), ("Xiao", "孝"), ("Zhong", "忠"), ("Bai", "白"), ("Fei", "飛"),
    ("Sheng", "聖"), ("Kuang", "狂"), ("Ye", "野"), ("Mo", "墨"), ("Bing", "兵"),
    ("Hong", "鴻"), ("Rui", "銳"), ("Kai", "凱"), ("Zhuo", "卓"), ("Heng", "恆"),
    ("Yuan", "遠"), ("An", "安"), ("Ping", "平"), ("Sheng", "生"), ("Hui", "慧"),
    ("Wuji", "無忌"), ("Bubai", "不敗"), ("Changsheng", "長生"), ("Xiaoyao", "逍遙"),
    ("Potian", "破天"), ("Lingxiao", "凌霄"), ("Zhixing", "知行"), ("Wuque", "無缺"),
)
_NOMES_FEMININOS: Tuple[Tuple[str, str], ...] = (
    ("Yue", "月"), ("Xue", "雪"), ("Bing", "冰"), ("Shuang", "霜"), ("Hua", "花"),
    ("Mei", "梅"), ("Lan", "蘭"), ("Zhu", "竹"), ("Ju", "菊"), ("Lian", "蓮"),
    ("Yu", "玉"), ("Zhu", "珠"), ("Zhen", "珍"), ("Bao", "寶"), ("Xiang", "香"),
    ("Fang", "芳"), ("Li", "麗"), ("Mei", "美"), ("Yan", "豔"), ("Juan", "娟"),
    ("Xiu", "秀"), ("Jing", "靜"), ("Wan", "婉"), ("Rou", "柔"), ("Qin", "琴"),
    ("Xiao", "簫"), ("Ge", "歌"), ("Wu", "舞"), ("Shi", "詩"), ("Shu", "書"),
    ("Qing", "青"), ("Bi", "碧"), ("Cui", "翠"), ("Hong", "紅"), ("Zi", "紫"),
    ("Su", "素"), ("Jie", "潔"), ("Hui", "慧"), ("Ling", "靈"), ("Xian", "仙"),
    ("Yao", "瑤"), ("Lin", "琳"), ("Shan", "珊"), ("Ling", "玲"), ("Die", "蝶"),
    ("Yan", "燕"), ("Ying", "鶯"), ("Feng", "鳳"), ("Luan", "鸞"), ("Yun", "雲"),
    ("Xia", "霞"), ("Yan", "煙"), ("Yu", "雨"), ("Lu", "露"), ("Xin", "心"),
    ("Meng", "夢"), ("Yi", "憶"), ("Si", "思"), ("Nian", "念"), ("Chou", "愁"),
    ("Lian", "憐"), ("Ruo", "若"), ("Qian", "淺"), ("Wushuang", "無雙"),
    ("Chang'e", "嫦娥"), ("Jinghong", "驚鴻"), ("Liushui", "流水"),
    ("Bingxin", "冰心"), ("Yixiao", "一笑"), ("Qingxuan", "青萱"),
)
_NEUTROS: Tuple[Tuple[str, str], ...] = (
    ("Yi", "一"), ("Er", "二"), ("San", "三"), ("Si", "四"), ("Wu", "五"),
    ("Liu", "六"), ("Qi", "七"), ("Ba", "八"), ("Jiu", "九"), ("Shi", "十"),
    ("Mo", "默"), ("Kong", "空"), ("Xu", "虛"), ("Jing", "淨"), ("Hui", "晦"),
)


def gerar_nome(aleat: Aleatoriedade, sexo: str = "",
               composto: bool = False) -> Tuple[str, str]:
    """Gera um nome no padrão chinês: sobrenome + 1–2 caracteres de nome.

    Retorna (nome romanizado, nome em caracteres).
    """
    if sexo == "":
        sexo = aleat.escolher(["masculino", "feminino", "neutro"])
    if composto:
        sob_pool = [s for s in SOBRENOMES if len(s[0]) > 3]
        if not sob_pool:
            sob_pool = list(SOBRENOMES)
    else:
        sob_pool = list(SOBRENOMES)
    sob_rom, sob_char = aleat.escolher(sob_pool)
    pool = {"masculino": _NOMES_MASCULINOS, "feminino": _NOMES_FEMININOS}.get(
        sexo, _NEUTROS)
    n = aleat.escolher([1, 1, 2, 2, 2])
    escolhidos = aleat.amostrar(list(pool), n) if n <= len(pool) else list(pool)[:n]
    rom = " ".join([sob_rom] + [e[0] for e in escolhidos])
    char = sob_char + "".join(e[1] for e in escolhidos)
    return rom, char


# ==========================================================================
# Geração completa de NPC
# ==========================================================================
OCUPACOES: Tuple[Tuple[str, Tuple[int, int, int, int, int]], ...] = (
    ("Ancião de seita", (1, 3, 2, 5, 4)),
    ("Mestre de seita", (2, 4, 4, 4, 3)),
    ("Discípulo interno", (2, 3, 2, 2, 3)),
    ("Discípulo externo", (3, 2, 2, 1, 2)),
    ("Cultivador errante", (1, 2, 2, 3, 2)),
    ("Assassino de aluguel", (0, 2, 1, 5, 2)),
    ("Comerciante de tesouros", (1, 1, 4, 4, 3)),
    ("Alquimista", (2, 1, 1, 5, 4)),
    ("Ferreiro de artefatos", (1, 3, 1, 4, 4)),
    ("Médico andarilho", (5, 2, 2, 4, 3)),
    ("Mestre de formações", (0, 1, 1, 5, 4)),
    ("Talismã-mestre", (0, 1, 2, 5, 4)),
    ("Eremita da montanha", (1, 2, 1, 4, 5)),
    ("Chefe de clã nobre", (2, 3, 5, 3, 4)),
    ("Jovem mestre", (1, 2, 4, 1, 1)),
    ("Mendigo da Seita dos Mendigos", (3, 3, 3, 3, 2)),
    ("Espião de facção", (1, 1, 3, 5, 1)),
    ("Guarda de caravana", (2, 4, 1, 2, 3)),
    ("Caçador de bestas espirituais", (2, 4, 1, 3, 2)),
    ("Taberneiro", (3, 2, 4, 2, 3)),
    ("Funcionário imperial", (0, 2, 5, 4, 3)),
    ("Camponês", (4, 2, 3, 1, 5)),
    ("Culto demoníaco — acólito", (0, 1, 1, 3, 0)),
    ("Culto demoníaco — sacerdote", (0, 2, 3, 4, 1)),
    ("Monge de Shaolin", (4, 3, 4, 2, 5)),
    ("Daoísta de Wudang", (2, 2, 3, 5, 4)),
    ("Cortêsã informante", (2, 1, 4, 4, 1)),
    ("Escrivão de manuais", (1, 1, 2, 5, 4)),
    ("Domador de bestas", (3, 2, 1, 3, 3)),
    ("Bandido de estrada", (0, 1, 1, 2, 0)),
    ("General do Império", (1, 4, 4, 4, 3)),
    ("Fantasma de um morto recente", (2, 2, 1, 2, 2)),
    ("Espírito de objeto despertado", (1, 1, 2, 4, 5)),
    ("Besta espiritual em forma humana", (2, 3, 1, 2, 2)),
)

POSTOS: Tuple[str, ...] = (
    "Ancião Supremo", "Ancião", "Grande Ancião", "Mestre de Pavilhão",
    "Chefe de Ramo", "Discípulo Núcleo", "Discípulo Interno",
    "Discípulo Externo", "Servo", "Convidado", "Nenhum",
)


def gerar_npc(
    aleat: Aleatoriedade,
    *,
    nome: Optional[str] = None,
    nivel: Optional[int] = None,
    ocupacao: Optional[str] = None,
    faccao: str = "",
    localizacao: str = "",
    caminho: Optional[str] = None,
    lei: Optional[str] = None,
    raca: str = "humano",
    sexo: str = "",
    tabela_de_raiz: str = "realista",
    numero_de_traços: Optional[int] = None,
    agendas: int = 0,
) -> Npc:
    """Gera um NPC completo. Determinístico para uma dada semente."""
    if raca not in RACAS:
        raise ValueError(f"raça inválida {raca!r}")

    itens = [o[0] for o in OCUPACOES]
    pesos = [1 for _ in OCUPACOES]
    if ocupacao:
        if ocupacao not in itens:
            raise ValueError(f"ocupação {ocupacao!r} não catalogada")
        ocup = ocupacao
    else:
        ocup = aleat.escolher_ponderado(itens, pesos)
    peso_ocup = dict(OCUPACOES)[ocup]

    # virtudes: 1d6+2 por virtude, deslocadas pela ocupação (coerência, não acaso cego)
    from .dados import rolar
    vals = {}
    for i, chave in enumerate(("ren", "yi", "li", "zhi", "xin")):
        base = rolar("1d6", aleat).total + 1 + peso_ocup[i] // 2
        vals[chave] = max(1, min(10, base))
    virtudes = Virtudes(**vals)

    temperamento = aleat.escolher(sorted(TEMPERAMENTOS))
    temperamento = TEMPERAMENTOS[temperamento]

    if numero_de_traços is None:
        numero_de_traços = aleat.entre(2, 4)
    tracos = _sortear_tracos(aleat, virtudes, numero_de_traços)

    desejos = _sortear_desejos(aleat, virtudes)

    if sexo == "":
        sexo = aleat.escolher(["masculino", "feminino", "neutro"])
    if nome is None:
        nome, _ = gerar_nome(aleat, sexo if sexo != "neutro" else "")

    # nível: distribuição por ocupação (mestres são raros)
    if nivel is None:
        faixas = [(0, 30), (1, 18), (2, 14), (3, 11), (4, 7), (5, 5),
                  (6, 4), (7, 3), (8, 2), (9, 2), (10, 1), (11, 1), (12, 1)]
        nivel = aleat.escolher_ponderado([f[0] for f in faixas], [f[1] for f in faixas])

    if caminho is None:
        if nivel <= 3 and aleat.abaixo(100) < 60:
            caminho = "marcial"
        else:
            caminho = aleat.escolher_ponderado(
                ["xiandao", "shendao", "corpo", "marcial"],
                [60, 8, 15, 17],
            )
    if caminho not in CAMINHOS:
        raise ValueError(f"caminho inválido {caminho!r}")

    # lei compatível com o caminho e com o nível
    if lei is not None:
        if lei not in LEIS:
            raise ValueError(f"lei {lei!r} não existe")
        if LEIS[lei].caminho != caminho and caminho != "monstro":
            raise ValueError(
                f"a Lei {lei} pertence ao caminho {LEIS[lei].caminho}, não a {caminho}")
    else:
        candidatas = sorted(c for c, l in LEIS.items() if l.caminho == caminho)
        lei = aleat.escolher(candidatas) if (candidatas and nivel >= 1) else None

    attrs = {k: max(3, min(20, rolar("4d6kh3", aleat).total + nivel // 2))
             for k in ("per", "con", "cha", "int", "luk", "pot")}
    raiz = sortear_raiz(aleat, sorte=attrs["luk"], tabela=tabela_de_raiz)

    per: Dict[str, int] = {}
    n_per = aleat.entre(3, 6) + nivel // 3
    for _ in range(min(n_per, 6)):
        c = aleat.escolher(sorted(PERICIAS))
        per[c] = min(5, per.get(c, 0) + aleat.entre(1, 2))

    tecnicas: List[str] = []
    from .artes import TECNICAS, tecnicas_de_lei, tecnicas_livres
    for t in tecnicas_livres(nivel):
        if aleat.abaixo(100) < 30:
            tecnicas.append(t.codigo)
    if lei:
        for t in tecnicas_de_lei(lei):
            if t.nivel_minimo <= nivel and aleat.abaixo(100) < 65:
                tecnicas.append(t.codigo)
    if not tecnicas:
        tecnicas = ["LIVRE_PALMA_VENTANIA"] if nivel >= 1 else []

    face = aleat.entre(-2, 4) + virtudes.li // 3 + nivel // 4
    estado_mental = aleat.entre(35, 95)
    pedras = aleat.entre(0, 40) * (nivel + 1) * (nivel + 1)
    if ocup in ("Comerciante de tesouros", "Chefe de clã nobre", "Funcionário imperial"):
        pedras *= aleat.entre(5, 30)

    agendas_lista: List[Agenda] = []
    for i in range(max(0, agendas)):
        objetivos = [
            f"Executar: {desejos.ambicao.lower()}",
            f"Resolver antes que descubram: {desejos.segredo.lower()}",
            f"Alcançar: {desejos.imediato.lower()}",
            f"Destruir um rival e tomar o posto dele",
            f"Reunir recursos para a próxima ruptura",
            f"Encontrar e recrutar um gênio",
        ]
        agendas_lista.append(Agenda(
            objetivo=aleat.escolher(objetivos),
            segmentos=aleat.escolher([4, 6, 6, 8]),
            preenchidos=aleat.entre(0, 3),
            dificuldade=12 + nivel,
        ))

    return Npc(
        nome=nome, sexo=sexo, idade=aleat.entre(16, 90) if raca == "humano"
        else aleat.entre(30, 900), raca=raca, virtudes=virtudes,
        temperamento=temperamento, tracos=tracos, desejos=desejos,
        atributos=attrs, pericias=per, nivel=nivel, caminho=caminho, lei=lei,
        raiz=raiz, faccao=faccao,
        posto=aleat.escolher(POSTOS) if faccao else "Nenhum",
        ocupacao=ocup, localizacao=localizacao, face=face,
        estado_mental=estado_mental, pedras_espirituais=pedras,
        tecnicas=tuple(tecnicas), agendas=tuple(agendas_lista),
        identificador=aleat.unico(),
    )


# ==========================================================================
# Conduta resolvida por dado (o mestre NÃO decide)
# ==========================================================================
TABELA_DE_CONDUTA: Tuple[Tuple[str, int, int, str], ...] = (
    # (codigo, margem mínima, margem máxima, conduta)
    ("ataca", -10 ** 6, -16,
     "Considera o pedido uma ameaça e ataca sem aviso."),
    ("hostil", -15, -11,
     "Recusa com hostilidade aberta; a disposição cai e ele avisa quem manda."),
    ("expulsa", -10, -6, "Expulsa o alvo e manda recado de que não quer vê-lo de novo."),
    ("recusa", -5, -1, "Recusa o pedido de forma seca e encerra o assunto."),
    ("negocia", 0, 4, "Aceita negociar: exige um preço condizente com o seu Preço."),
    ("ajuda_condicional", 5, 9,
     "Ajuda, mas cobra um favor registrado no livro de relações (trocou_favores)."),
    ("ajuda_generosa", 10, 14,
     "Ajuda de boa vontade e ainda oferece informação sobre o próprio Desejo imediato."),
    ("revela_segredo", 15, 19,
     "Confia o suficiente para deixar escapar parte do Segredo."),
    ("jura_lealdade", 20, 10 ** 6,
     "Oferece um juramento: registra dever_de_honra no livro de relações."),
)


@dataclass(frozen=True)
class Conduta:
    codigo: str
    texto: str
    resultado: Resultado
    desejo_ativo: str

    def resumo(self) -> str:
        return f"{self.codigo.upper()}: {self.texto}\n  {self.resultado.resumo()}"


def _escolher_por_margem(margem: int) -> Tuple[str, str]:
    for codigo, lo, hi, texto in TABELA_DE_CONDUTA:
        if lo <= margem <= hi:
            return codigo, texto
    raise AssertionError("tabela de conduta não cobre a margem — erro de projeto")


def resolver_conduta(
    npc: Npc,
    alvo: str,
    pedido: str,
    aleat: Aleatoriedade,
    *,
    magnitude: str = "favor_sem_risco",
    dificuldade: Optional[int] = None,
    fatos_extras: Optional[Mapping[str, Any]] = None,
    diario: Optional[DiarioDeAuditoria] = None,
) -> Conduta:
    """Decide no dado como o NPC responde a um pedido.

    Modificadores usados — todos do Registro de Regras, todos derivados de fatos:
      * SOCIAL:DISPOSICAO — do livro-razão de relações
      * SOCIAL:FACE       — reputação do NPC
      * SOCIAL:HIERARQUIA — posto relativo declarado
      * FACCAO:RELACAO    — relação entre as facções
    O **Desejo** relevante não é bônus: é o filtro que decide qual das condutas
    vencedoras se manifesta, usando a prioridade aritmética de ``Desejos``.
    """
    disposicao = npc.disposicao_para(alvo)[1]
    face_categoria = ("desonrada" if npc.face <= -2 else
                      "arranhada" if npc.face < 0 else
                      "neutra" if npc.face < 3 else
                      "respeitada" if npc.face < 6 else "gloriosa")
    fatos: Dict[str, Any] = {"disposicao": disposicao, "face": face_categoria}
    regras = ["SOCIAL:DISPOSICAO", "SOCIAL:FACE"]
    extras = dict(fatos_extras or {})
    for chave, codigo in (("hierarquia", "SOCIAL:HIERARQUIA"),
                          ("relacao_de_faccoes", "FACCAO:RELACAO"),
                          ("divida_de_honra", "SOCIAL:DIVIDA_DE_HONRA"),
                          ("segredo_exposto", "SOCIAL:SEGREDO_EXPOSTO")):
        if chave in extras:
            fatos[chave] = extras[chave]
            regras.append(codigo)
    for chave in ("elixir", "talisma"):
        if chave in extras:
            fatos[chave] = extras[chave]
            regras.append({"elixir": "RECURSO:ELIXIR", "talisma": "RECURSO:TALISMA"}[chave])

    if dificuldade is None:
        if magnitude not in PEDIDOS_TIPICOS:
            raise ValueError(
                f"magnitude {magnitude!r} fora da tabela; opções "
                f"{sorted(PEDIDOS_TIPICOS)}")
        dificuldade = PEDIDOS_TIPICOS[magnitude]
    dd = max(5, min(45, dificuldade + npc.virtudes.bonus("xin") * 2
                    - npc.temperamento.bonus_social))

    decl = Declaracao(
        acao=f"responder ao pedido ({magnitude}): {pedido}",
        ator=npc.nome,
        alvo=alvo,
        atributo="cha",
        valor_atributo=npc.atributos["cha"],
        bonus_atributo=npc.bonus("cha"),
        pericia="persuasao",
        graduacao=max(0, min(5, npc.pericias.get("persuasao", 0)
                             + npc.virtudes.bonus("li"))),
        dificuldade=dd,
        regras=tuple(regras),
        fatos=fatos,
        contexto={"npc": npc.identificador, "nivel": npc.nivel,
                  "temperamento": npc.temperamento.codigo,
                  "magnitude": magnitude},
    )
    res = resolver(decl, aleat, diario)
    codigo, texto = _escolher_por_margem(res.margem)

    # A camada de desejo que se manifesta é DERIVADA da personalidade do NPC:
    # entre as camadas capazes de produzir esta conduta, vence a de maior
    # (prioridade × 10 + bônus da virtude governante). Conta fechada, sem dado
    # extra e sem preferência do mestre.
    desejo_ativo = camada_ativa(codigo, npc)

    if _viola_linha_vermelha(npc, codigo):
        codigo, texto = ("recusa", "Recusa de forma absoluta: o pedido cruza a "
                                   "linha vermelha dele.")
        desejo_ativo = "linha_vermelha"

    return Conduta(codigo, texto, res, desejo_ativo)


_LINHAS_QUE_BLOQUEIAM = {
    "Nunca mata crianças — nem demônios crianças": ("ataca",),
    "Nunca quebra um juramento, nem sob tortura": (),
    "Nunca ataca pelas costas": (),
    "Nunca recusa abrigo a um perseguido": ("expulsa", "hostil"),
    "Nunca revela o que um paciente lhe conta": ("revela_segredo",),
    "Nunca luta contra o próprio mestre": ("ataca",),
    "Nunca usa veneno": (),
    "Nunca abandona um cadáver sem ritos": (),
    "Nunca mente sobre o próprio nome": (),
    "Nunca rouba de pobres": (),
    "Nunca desobedece uma ordem direta do superior": ("recusa", "expulsa", "hostil"),
}


def camada_ativa(codigo: str, npc: Npc) -> str:
    """Qual camada de desejo está produzindo esta conduta neste NPC."""
    if codigo not in _CAMADAS_POR_CONDUTA:
        raise ValueError(f"conduta {codigo!r} fora da tabela")
    melhor: Optional[str] = None
    melhor_peso = None
    for camada in _CAMADAS_POR_CONDUTA[codigo]:
        virt = VIRTUDE_DA_CAMADA[camada]
        peso = _PRIORIDADE_DE_CAMADA[camada] * 10 + npc.virtudes.bonus(virt)
        if melhor_peso is None or peso > melhor_peso:
            melhor, melhor_peso = camada, peso
    assert melhor is not None
    return melhor


def _viola_linha_vermelha(npc: Npc, codigo: str) -> bool:
    bloqueados = _LINHAS_QUE_BLOQUEIAM.get(npc.desejos.linha_vermelha, ())
    return codigo in bloqueados


@dataclass(frozen=True)
class ConflitoDeDesejos:
    vencedor: str
    perdedor: str
    resultado: Optional[ResultadoOposto]
    conduta: str
    criterio: str = ""

    def resumo(self) -> str:
        base = (f"CONFLITO DE DESEJOS: {self.vencedor} supera {self.perdedor}\n"
                f"  → {self.conduta}\n  critério: {self.criterio}")
        if self.resultado is not None:
            base += "\n" + self.resultado.resumo()
        return base


_PRIORIDADE_DE_CAMADA: Dict[str, int] = PRIORIDADE_DE_CAMADA_DE_DESEJO

# Virtude que governa cada camada de desejo (usada para escolher o atributo).
VIRTUDE_DA_CAMADA: Dict[str, str] = {
    "medo": "zhi",             # Sabedoria percebe o perigo
    "linha_vermelha": "yi",    # Retidão é o que não se cruza
    "dever": "xin",            # Integridade sustenta o compromisso
    "obsessao": "ren",         # Benevolência/afeto vira compulsão
    "ambicao": "li",           # Propriedade/posição social
    "imediato": "ren",
    "preco": "zhi",
    "segredo": "zhi",
}

# Dificuldade declarada por magnitude do pedido. É um fato sobre o PEDIDO, não
# uma concessão narrativa: vale igual para todo NPC e para toda mesa.
PEDIDOS_TIPICOS: Dict[str, int] = {
    "informacao_comum": 10,
    "direcao_ou_abrigo": 12,
    "favor_sem_risco": 14,
    "emprestimo_de_bem": 17,
    "informacao_sensivel": 18,
    "escolta_ou_viagem": 20,
    "risco_de_vida_menor": 23,
    "traicao_de_faccao": 28,
    "segredo_mortal": 32,
    "sacrificio_de_vida": 40,
}

# Quais camadas de desejo podem produzir cada conduta.
_CAMADAS_POR_CONDUTA: Dict[str, Tuple[str, ...]] = {
    "ataca": ("medo", "obsessao", "ambicao"),
    "hostil": ("medo", "obsessao", "dever", "ambicao"),
    "expulsa": ("medo", "linha_vermelha", "dever", "obsessao"),
    "recusa": ("linha_vermelha", "medo", "dever", "obsessao", "ambicao",
               "imediato"),
    "negocia": ("preco", "ambicao", "imediato"),
    "ajuda_condicional": ("dever", "imediato", "preco", "ambicao"),
    "ajuda_generosa": ("imediato", "dever", "ambicao", "obsessao"),
    "revela_segredo": ("imediato", "preco", "dever"),
    "jura_lealdade": ("dever", "ambicao", "imediato"),
}


def resolver_conflito_de_desejos(
    npc: Npc,
    camada_a: str,
    camada_b: str,
    aleat: Aleatoriedade,
    *,
    contexto: Optional[Mapping[str, Any]] = None,
    diario: Optional[DiarioDeAuditoria] = None,
) -> ConflitoDeDesejos:
    """Quando dois desejos do NPC mandam coisas incompatíveis, o dado decide.

    Cada lado rola ``1d20 + prioridade da camada + bônus da virtude ligada``
    contra DD 10. Não existe "o mestre decide que ele prioriza o dever".
    """
    for c in (camada_a, camada_b):
        if c not in _PRIORIDADE_DE_CAMADA:
            raise ValueError(
                f"camada de desejo {c!r} inexistente; opções "
                f"{sorted(_PRIORIDADE_DE_CAMADA)}")
    if camada_a == camada_b:
        raise ValueError("as duas camadas precisam ser diferentes")

    # A linha vermelha NÃO compete no dado: é veto absoluto declarado no Cap. 12.
    # Rolar aqui seria dar ao acaso a chance de fazer o NPC cruzar a única linha
    # que ele jurou não cruzar.
    if "linha_vermelha" in (camada_a, camada_b):
        outra = camada_b if camada_a == "linha_vermelha" else camada_a
        if diario is not None:
            diario.registrar("veto", {"npc": npc.identificador,
                                      "vencedor": "linha_vermelha",
                                      "perdedor": outra}, ator=npc.nome)
        return ConflitoDeDesejos(
            "linha_vermelha", outra, None,
            _conduta_por_camada("linha_vermelha", npc),
            "veto absoluto: a linha vermelha não vai ao dado")

    def decl(camada: str) -> Declaracao:
        virt = VIRTUDE_DA_CAMADA[camada]
        atr = VIRTUDE_PARA_ATRIBUTO[virt]
        return Declaracao(
            acao=f"impor o desejo '{camada}'",
            ator=npc.nome,
            atributo=atr,
            valor_atributo=int(npc.atributos[atr]),
            bonus_atributo=npc.bonus(atr),
            pericia="vontade_de_ferro",
            graduacao=max(0, min(5, npc.pericias.get("vontade_de_ferro", 0)
                                 + npc.virtudes.bonus(virt))),
            dificuldade=10,
            regras=("DESEJO:PRIORIDADE",),
            fatos={"camada": camada},
            contexto={"npc": npc.identificador, **dict(contexto or {})},
        )

    res_op = teste_oposto(decl(camada_a), decl(camada_b), aleat, diario)
    vencedor = camada_a if res_op.vencedor == "atacante" else camada_b
    perdedor = camada_b if vencedor == camada_a else camada_a
    return ConflitoDeDesejos(
        vencedor, perdedor, res_op, _conduta_por_camada(vencedor, npc),
        res_op.criterio)


def _conduta_por_camada(camada: str, npc: Npc) -> str:
    textos = {
        "medo": "Foge, se esconde ou se submete — o medo venceu e ele some da cena.",
        "linha_vermelha": "Recusa absolutamente. Nada o faz cruzar essa linha.",
        "dever": "Age pelo dever: cumpre o compromisso mesmo contra o próprio interesse.",
        "obsessao": "Age pela compulsão — e faz algo que ninguém esperava dele.",
        "ambicao": "Age mirando o objetivo de vida; ignora o imediato.",
        "imediato": "Age pelo que quer agora, nesta cena, sem pensar em amanhã.",
        "preco": "Negocia: só se move se o preço certo aparecer na mesa.",
        "segredo": "Age para proteger o segredo, mesmo que isso custe o resto.",
    }
    return textos[camada]
