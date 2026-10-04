# -*- coding: utf-8 -*-
"""
XAN — Bestiário: bestas espirituais, demônios e feras ancestrais.
================================================================

Bestas prontas (as do cânone chinês) **e** um gerador procedural que cria uma
besta coerente com o nível, o elemento e o terreno do local — sempre com a
mesma entropia auditada do resto do sistema.

Cultivo de bestas
------------------
Bestas espirituais também cultivam: o nível delas segue a mesma escada 0–13 dos
humanos. Uma besta de nível 7 equivale a um Núcleo Dourado e já formou um
**núcleo de besta** (妖丹), o item mais valioso da alquimia.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .entropia import Aleatoriedade
from .regras import ELEMENTOS_CANONICOS, ELEMENTOS_NEUTROS

__all__ = [
    "CLASSES_DE_BESTA", "TAMANHOS", "Besta", "BESTAS", "besta_de",
    "gerar_besta", "bestas_por_nivel", "nucleo_de_besta",
    "AtaqueDeBesta", "HabilidadeDeBesta",
]

CLASSES_DE_BESTA: Tuple[str, ...] = (
    "fera", "besta_espiritual", "demonio", "fera_ancestral", "divindade_menor",
    "morto_vivo", "espirito_de_objeto",
)

TAMANHOS: Dict[str, Tuple[int, int]] = {
    # tamanho → (modificador de Defesa, multiplicador de Vitalidade em %)
    "minúsculo": (4, 40),
    "pequeno": (2, 70),
    "medio": (0, 100),
    "grande": (-2, 160),
    "enorme": (-4, 260),
    "colossal": (-6, 500),
}


@dataclass(frozen=True)
class AtaqueDeBesta:
    nome: str
    chines: str
    alcance: str
    dado: str
    pericia: str
    elemento: str
    efeitos: Tuple[str, ...] = ()


@dataclass(frozen=True)
class HabilidadeDeBesta:
    nome: str
    chines: str
    descricao: str
    mecanica: str


@dataclass
class Besta:
    nome: str
    chines: str
    classe: str
    nivel: int
    elemento: str
    tamanho: str
    habitat: str
    vitalidade: int
    qi: int
    defesa: int
    iniciativa: int
    atributos: Mapping[str, int]
    ataques: Tuple[AtaqueDeBesta, ...]
    habilidades: Tuple[HabilidadeDeBesta, ...]
    temperamento: str
    tesouro: str
    fraqueza: str
    descricao: str = ""
    domavel: bool = False
    inteligente: bool = False

    def __post_init__(self) -> None:
        if self.classe not in CLASSES_DE_BESTA:
            raise ValueError(f"classe de besta inválida {self.classe!r}")
        if self.tamanho not in TAMANHOS:
            raise ValueError(f"tamanho inválido {self.tamanho!r}")
        if self.elemento not in ELEMENTOS_CANONICOS + ELEMENTOS_NEUTROS:
            raise ValueError(f"elemento inválido {self.elemento!r}")
        if not (0 <= self.nivel <= 13):
            raise ValueError("nível de besta fora de 0..13")
        if not self.descricao.strip():
            artigo = "Um" if self.classe in ("demonio", "morto_vivo") else "Uma"
            classe_txt = {"demonio": "demônio", "morto_vivo": "morto-vivo",
                          "fera_ancestral": "fera ancestral",
                          "divindade_menor": "divindade menor",
                          "espirito_de_objeto": "espírito de objeto",
                          "besta_espiritual": "besta espiritual",
                          "fera": "fera"}[self.classe]
            object.__setattr__(
                self, "descricao",
                f"{artigo} {classe_txt} de tamanho {self.tamanho}, ligada ao "
                f"elemento {self.elemento}. Vive em {self.habitat}. "
                f"Temperamento: {self.temperamento}.")

    def ficha(self) -> str:
        a = self.atributos
        attrs = " ".join(f"{k.upper()}{a.get(k, 10)}"
                         for k in ("per", "con", "cha", "int", "luk", "pot"))
        linhas = [
            f"## {self.nome} ({self.chines})",
            f"*{self.classe.replace('_',' ')} · nível {self.nivel} · {self.elemento}"
            f" · {self.tamanho} · {self.habitat}*",
            "",
            f"- **Vitalidade:** {self.vitalidade} · **Qi:** {self.qi} · "
            f"**Defesa:** {self.defesa} · **Iniciativa:** {self.iniciativa:+d}",
            f"- **Atributos:** {attrs}",
            f"- **Temperamento:** {self.temperamento}",
            f"- **Fraqueza:** {self.fraqueza}",
            f"- **Tesouro:** {self.tesouro}",
            f"- **Domável:** {'sim' if self.domavel else 'não'} · "
            f"**Inteligente:** {'sim' if self.inteligente else 'não'}",
            "",
            self.descricao,
            "",
            "**Ataques:**",
        ]
        for at in self.ataques:
            eff = f" — {'; '.join(at.efeitos)}" if at.efeitos else ""
            linhas.append(f"- *{at.nome}* ({at.chines}) — {at.alcance}, "
                          f"{at.dado}, {at.elemento}{eff}")
        if self.habilidades:
            linhas += ["", "**Habilidades:**"]
            for h in self.habilidades:
                linhas.append(f"- *{h.nome}* ({h.chines}) — {h.descricao} "
                              f"**Mecânica:** {h.mecanica}")
        return "\n".join(linhas)


BESTAS: Dict[str, Besta] = {}


def _b(**kw) -> Besta:
    b = Besta(**kw)
    if b.nome in BESTAS:
        raise ValueError(f"besta {b.nome} duplicada")
    BESTAS[b.nome] = b
    return b


_A = AtaqueDeBesta
_H = HabilidadeDeBesta

_b(nome="Tigre Branco do Oeste", chines="白虎", classe="fera_ancestral", nivel=11,
   elemento="metal", tamanho="enorme", habitat="montanhas do oeste",
   vitalidade=420, qi=900, defesa=24, iniciativa=6,
   atributos={"per": 18, "con": 22, "cha": 10, "int": 16, "luk": 14, "pot": 18},
   ataques=(
       _A("Garra do Outono", "秋爪", "toque", "6d10", "punho", "metal",
          ("ignora 5 pontos de Defesa", "sangramento 2d6 por 3 rodadas")),
       _A("Rugido do Oeste", "西吼", "medio", "", "intimidacao", "metal",
          ("todos em 20 m testam Vontade de Ferro DD 24 ou fogem")),
   ),
   habilidades=(
       _H("Senhor dos Metais", "金主", "Todo metal a 100 m obedece a ela.",
          "armas de metal de oponentes têm −2 de dano; as dela, +2"),
       _H("Passo de Guerra", "戰步", "Move-se sem gastar ação.",
          "deslocamento dobrado e não provoca ataques de oportunidade"),
   ),
   temperamento="guardião severo; ataca quem desonra os mortos",
   tesouro="Pelo de Tigre Branco (ingrediente primordial de forja)",
   fraqueza="Fogo: sofre +4 de dano de qualquer fonte flamejante",
   descricao=("Um dos quatro símbolos celestiais. Não é uma besta comum: é uma "
              "função do mundo, e aparece quando o oeste está em desequilíbrio."),
   inteligente=True)

_b(nome="Dragão Azul do Leste", chines="青龍", classe="fera_ancestral", nivel=12,
   elemento="madeira", tamanho="colossal", habitat="céus e rios do leste",
   vitalidade=560, qi=1600, defesa=26, iniciativa=5,
   atributos={"per": 20, "con": 24, "cha": 18, "int": 20, "luk": 16, "pot": 20},
   ataques=(
       _A("Sopro de Primavera", "春息", "longo", "8d8", "folego_interno",
          "madeira", ("cura aliados no cone pelo mesmo valor")),
       _A("Garra de Nuvem", "雲爪", "toque", "7d12", "punho", "madeira",
          ("arremessa o alvo 30 m")),
   ),
   habilidades=(
       _H("Chamado da Chuva", "召雨", "Faz chover sobre uma província.",
          "muda o clima para chuva por 1d4 dias; plantas crescem 10×"),
       _H("Corpo de Névoa", "霧身", "Pode se tornar névoa.",
          "imune a dano físico por 1 rodada, uma vez por combate"),
   ),
   temperamento="benevolente com quem respeita, implacável com tiranos",
   tesouro="Chifre de Dragão Azul (elixir de longevidade)",
   fraqueza="Metal: uma lâmina de grau Céu ignora metade da Defesa",
   descricao=("O maior dos símbolos. Aparece uma vez por era, e quem o vê "
              "ganha um ano de sorte ou um ano de desgraça — nunca os dois."),
   inteligente=True)

_b(nome="Pássaro Vermelho do Sul", chines="朱雀", classe="fera_ancestral",
   nivel=11, elemento="fogo", tamanho="enorme", habitat="vulcões do sul",
   vitalidade=380, qi=1100, defesa=23, iniciativa=8,
   atributos={"per": 18, "con": 18, "cha": 22, "int": 16, "luk": 14, "pot": 16},
   ataques=(
       _A("Chuva de Brasas", "火雨", "longo", "6d8", "folego_interno", "fogo",
          ("área de 15 m", "fogo contínuo 1d8 por 3 rodadas")),
       _A("Asa Cortante", "翼斬", "curto", "5d10", "punho", "fogo", ()),
   ),
   habilidades=(
       _H("Renascimento", "涅槃", "Renasce das próprias cinzas.",
          "uma vez por década, volta com metade da Vitalidade após 1d4 dias"),
       _H("Presença Solar", "日威", "A luz dela queima mentiras.",
          "+4 em qualquer teste para detectar enganação na presença dela"),
   ),
   temperamento="orgulhosa, teatral, incapaz de ignorar um desafio",
   tesouro="Pena de Fênix (ressuscita uma vez)",
   fraqueza="Água: sofre −4 de dano causado quando molhada",
   descricao="A fênix do sul. Onde pousa, a terra fica fértil por cem anos.",
   inteligente=True)

_b(nome="Tartaruga Negra do Norte", chines="玄武", classe="fera_ancestral",
   nivel=11, elemento="agua", tamanho="colossal", habitat="mares e lagos do norte",
   vitalidade=640, qi=800, defesa=32, iniciativa=-2,
   atributos={"per": 16, "con": 26, "cha": 12, "int": 18, "luk": 14, "pot": 20},
   ataques=(
       _A("Cauda de Serpente", "蛇尾", "medio", "5d12", "punho", "agua",
          ("derruba; teste de Corpo de Ferro DD 22")),
       _A("Onda de Maré", "潮湧", "longo", "4d10", "folego_interno", "agua",
          ("inunda 50 m e apaga qualquer fogo")),
   ),
   habilidades=(
       _H("Casco do Mundo", "世甲", "Não pode ser movida nem ferida pelas costas.",
          "Defesa 32 contra ataques frontais; imune a derrubar"),
       _H("Memória das Águas", "水記", "Lembra de tudo o que já viu.",
          "responde uma pergunta verdadeira por encontro"),
   ),
   temperamento="lenta, antiga, indiferente a pressa",
   tesouro="Casco de Xuanwu (material primordial de armadura)",
   fraqueza="Terra: formações de terra reduzem sua Defesa em 6",
   descricao="A tartaruga-serpente do norte. Dizem que o mundo flutua sobre ela.",
   inteligente=True)

_b(nome="Qilin", chines="麒麟", classe="divindade_menor", nivel=10,
   elemento="terra", tamanho="grande", habitat="florestas intactas",
   vitalidade=300, qi=900, defesa=26, iniciativa=4,
   atributos={"per": 20, "con": 18, "cha": 20, "int": 20, "luk": 22, "pot": 18},
   ataques=(
       _A("Chifre da Verdade", "真角", "toque", "4d10", "punho", "terra",
          ("só ataca quem já matou um inocente")),
   ),
   habilidades=(
       _H("Não Pisa na Grama", "不踏生", "Não causa dano nem a uma folha.",
          "imune a qualquer ataque de quem não tenha matado um inocente"),
       _H("Aparição de Bom Governo", "瑞應", "Só aparece onde há justiça.",
          "ver um Qilin concede +10 permanente de Sorte a um personagem"),
   ),
   temperamento="manso; anda sem tocar o chão",
   tesouro="Nada — matar um Qilin amaldiçoa a linhagem inteira do assassino",
   fraqueza="Nenhuma conhecida; o que o afasta é a injustiça",
   descricao=("O presságio mais auspicioso do mundo. Um Qilin aparece quando um "
              "sábio nasce ou quando um governante é justo. Nunca os dois ao mesmo tempo."),
   inteligente=True)

_b(nome="Raposa de Nove Caudas", chines="九尾狐", classe="demonio", nivel=9,
   elemento="fogo", tamanho="medio", habitat="tumbas e florestas antigas",
   vitalidade=220, qi=700, defesa=24, iniciativa=7,
   atributos={"per": 18, "con": 12, "cha": 24, "int": 20, "luk": 16, "pot": 12},
   ataques=(
       _A("Fogo-Fátuo", "狐火", "medio", "4d6", "palma", "fogo",
          ("ilusão: o alvo não sabe se foi atingido até o fim da rodada")),
       _A("Garras Sedutoras", "媚爪", "toque", "3d8", "punho", "fogo", ()),
   ),
   habilidades=(
       _H("Metamorfose", "化形", "Toma forma humana perfeita.",
          "+6 em Enganação; só um teste de Sense de Qi DD 22 revela"),
       _H("Encanto", "魅惑", "Curva vontades com o olhar.",
          "teste de Vontade de Ferro DD 20 ou obedece por 1d4 horas"),
       _H("Devora Essência", "吸精", "Bebe o Qi de quem a ama.",
          "a cada noite com um parceiro, ele perde 1d4 de Vitalidade máxima"),
   ),
   temperamento="brincalhona, cruel, curiosamente leal a quem a diverte",
   tesouro="Pérola da Raposa (elixir de Carisma permanente)",
   fraqueza="Espelhos e água parada revelam a forma verdadeira",
   descricao=("Cada cauda é um século. A nona traz sabedoria suficiente para "
              "odiar o que ela se tornou."),
   inteligente=True, domavel=False)

_b(nome="Taotie", chines="饕餮", classe="demonio", nivel=10, elemento="terra",
   tamanho="grande", habitat="campos de batalha antigos",
   vitalidade=340, qi=400, defesa=20, iniciativa=2,
   atributos={"per": 12, "con": 24, "cha": 6, "int": 8, "luk": 8, "pot": 20},
   ataques=(
       _A("Fome Insaciável", "貪食", "toque", "5d12", "punho", "terra",
          ("engole o alvo; dano contínuo 3d8 por rodada até ser cortado de dentro")),
       _A("Mandíbula do Vazio", "虛口", "curto", "4d10", "punho", "vazio",
          ("consome Qi: o alvo perde 2d10×10 de Qi")),
   ),
   habilidades=(
       _H("Come Tudo", "無不食", "Inclui metal, Qi e magia.",
          "imune a veneno, fogo e dano de artefato de grau Terra ou inferior"),
       _H("Nunca Saciado", "不飽", "Cada presa o deixa mais faminto.",
          "+1 de dano cumulativo por criatura devorada neste encontro"),
   ),
   temperamento="fome pura; não negocia, não dorme, não para",
   tesouro="Nada: o estômago dele devolve apenas o que não conseguiu digerir",
   fraqueza="Não tem corpo completo — atacar a própria sombra o confunde",
   descricao=("Um dos quatro flagelos antigos. Tem cabeça e boca e nada mais: "
              "o resto foi comido por ele mesmo."),
   inteligente=False)

_b(nome="Qiongqi", chines="窮奇", classe="demonio", nivel=9, elemento="metal",
   tamanho="grande", habitat="estradas e fronteiras",
   vitalidade=260, qi=500, defesa=22, iniciativa=6,
   atributos={"per": 16, "con": 20, "cha": 10, "int": 16, "luk": 8, "pot": 16},
   ataques=(
       _A("Asas de Navalha", "刃翼", "curto", "4d10", "punho", "metal",
          ("corte à distância de 10 m")),
   ),
   habilidades=(
       _H("Premia o Mal", "賞惡", "Ajuda quem faz o errado.",
          "aliado de quem comete uma injustiça diante dela; ataca o justo"),
       _H("Ouve Línguas", "通言", "Entende qualquer idioma.",
          "nunca pode ser enganada por palavras, só por ações"),
   ),
   temperamento="tigre alado que torce pelo pior lado de todo mundo",
   tesouro="Asa de Qiongqi (artefato de voo de grau Céu)",
   fraqueza="Um ato genuinamente altruísta a deixa confusa por 1 rodada",
   descricao="O flagelo que recompensa a maldade. Aparece em julgamentos.",
   inteligente=True)

_b(nome="Jiao", chines="蛟", classe="besta_espiritual", nivel=7, elemento="agua",
   tamanho="enorme", habitat="rios profundos e lagos",
   vitalidade=240, qi=450, defesa=20, iniciativa=3,
   atributos={"per": 14, "con": 20, "cha": 8, "int": 12, "luk": 10, "pot": 16},
   ataques=(
       _A("Enrolar", "纏", "toque", "3d10", "punho", "agua",
          ("agarrado: o alvo não age até escapar com teste DD 20")),
       _A("Chamado da Enchente", "洪水", "longo", "3d8", "folego_interno",
          "agua", ("alaga a área; movimento reduzido à metade")),
   ),
   habilidades=(
       _H("Meio-Dragão", "半龍", "Um dia ainda vira dragão.",
          "ao atingir nível 10, passa por tribulação e vira Long 龍"),
       _H("Escamas de Rio", "河鱗", "Pelego duro e escorregadio.",
          "+4 de Defesa contra armas de metal dentro d'água"),
   ),
   temperamento="territorial; afoga pescadores que passam do limite marcado",
   tesouro="Núcleo de Jiao (ingrediente de elixir de grau Céu)",
   fraqueza="Trovão: sofre +6 de dano de técnicas de Trovão",
   descricao="A serpente-dragão dos rios. Ainda não é dragão, e sabe disso.",
   domavel=True)

_b(nome="Peng", chines="鵬", classe="besta_espiritual", nivel=10,
   elemento="madeira", tamanho="colossal", habitat="o mar do norte e o céu",
   vitalidade=400, qi=700, defesa=22, iniciativa=9,
   atributos={"per": 20, "con": 20, "cha": 10, "int": 16, "luk": 14, "pot": 18},
   ataques=(
       _A("Vento de Asa", "翼風", "longo", "5d10", "folego_interno", "madeira",
          ("cone de 60 m; arremessa tudo que pesar menos que um boi")),
       _A("Mergulho", "俯衝", "toque", "6d12", "punho", "madeira",
          ("+4 de dano se atacar de cima")),
   ),
   habilidades=(
       _H("Sombra de Três Mil Léguas", "三千裏影", "Cobre o sol ao voar.",
          "todos os alvos sob a sombra sofrem −2 em Percepção"),
       _H("Voo sem Cansaço", "不倦", "Voaria até o fim do mundo.",
          "nunca fica exausta; desloca 900 m por rodada"),
   ),
   temperamento="indiferente a tudo que não seja o horizonte",
   tesouro="Pena de Peng (permite voo permanente a quem a usar)",
   fraqueza="Não consegue pousar em terra firme: só em água ou picos",
   descricao=("Era um peixe chamado Kun antes de decidir que o mar era pequeno "
              "demais. Ainda não se conformou."),
   inteligente=True)

_b(nome="Baize", chines="白澤", classe="divindade_menor", nivel=9,
   elemento="nenhum", tamanho="grande", habitat="bibliotecas e sonhos",
   vitalidade=200, qi=1200, defesa=26, iniciativa=5,
   atributos={"per": 22, "con": 14, "cha": 18, "int": 26, "luk": 18, "pot": 14},
   ataques=(
       _A("Nome Verdadeiro", "真名", "medio", "3d6", "persuasao", "nenhum",
          ("dano direto à alma: ignora Qi e armadura")),
   ),
   habilidades=(
       _H("Conhece Todas as Criaturas", "知萬物", "Sabe o nome e a fraqueza de tudo.",
          "revela a fraqueza exata de qualquer criatura; +2 de dano do grupo contra ela"),
       _H("Fala em Sonhos", "夢語", "Aparece dormindo para quem vai morrer.",
          "concede uma profecia verdadeira e incompleta"),
   ),
   temperamento="educado, prolixo, impossível de interromper",
   tesouro="O próprio Baize: ditou o catálogo dos 11.520 demônios do mundo",
   fraqueza="Não pode mentir. Nunca. Nem por piedade.",
   descricao=("O leão-branco que sabe o nome de tudo. Ensinou ao Imperador "
              "Amarelo como matar cada monstro do mundo — e cobrou em histórias."),
   inteligente=True)

_b(nome="Cão-Cadáver", chines="殭屍", classe="morto_vivo", nivel=5,
   elemento="terra", tamanho="medio", habitat="tumbas mal seladas",
   vitalidade=150, qi=0, defesa=18, iniciativa=-1,
   atributos={"per": 8, "con": 20, "cha": 4, "int": 4, "luk": 6, "pot": 14},
   ataques=(
       _A("Garras Secas", "枯爪", "toque", "2d10", "punho", "terra",
          ("contato: teste de Resistência a Veneno DD 16 ou apodrece 1d4 por dia")),
       _A("Salto Rígido", "僵跳", "curto", "2d8", "passos_leves", "terra",
          ("salta 9 m com os joelhos travados")),
   ),
   habilidades=(
       _H("Não Respira", "無息", "Não precisa de ar, sangue ou comida.",
          "imune a veneno, sufocamento, sangramento e medo"),
       _H("Sino de Controle", "控屍鈴", "Obedece a quem tiver o sino.",
          "teste de Talismãs DD 18 para assumir o controle"),
   ),
   temperamento="obedece a ordens simples; odeia o próprio reflexo",
   tesouro="Talismã de selamento colado na testa (remove-o e ele enlouquece)",
   fraqueza="Fogo e arroz glutinoso; não cruza água corrente",
   descricao=("Um corpo que se recusa a descansar. Pula porque os joelhos "
              "endureceram há séculos e não dobram mais."),
   inteligente=False)

_b(nome="Lobo da Montanha Fria", chines="寒山狼", classe="fera", nivel=3,
   elemento="agua", tamanho="grande", habitat="tundra e picos nevados",
   vitalidade=70, qi=60, defesa=15, iniciativa=4,
   atributos={"per": 14, "con": 14, "cha": 6, "int": 8, "luk": 10, "pot": 12},
   ataques=(_A("Mordida Gelada", "冰咬", "toque", "2d6", "punho", "agua",
               ("−1 de deslocamento cumulativo por acerto")),),
   habilidades=(_H("Alcateia", "群", "Caça em grupo.",
                   "+2 de ataque por lobo adjacente ao mesmo alvo (máx. +6)"),),
   temperamento="caça em alcateia; nunca ataca sozinho",
   tesouro="Pele (30 pedras) e dente (ingrediente de elixir menor)",
   fraqueza="Fogo")

_b(nome="Macaco de Seis Braços", chines="六臂猿", classe="besta_espiritual",
   nivel=4, elemento="madeira", tamanho="medio", habitat="florestas densas",
   vitalidade=90, qi=120, defesa=17, iniciativa=6,
   atributos={"per": 14, "con": 12, "cha": 8, "int": 12, "luk": 14, "pot": 12},
   ataques=(_A("Seis Punhos", "六拳", "toque", "3d6", "punho", "madeira",
               ("três ataques na mesma rodada")),),
   habilidades=(_H("Imita Técnicas", "學技", "Aprende vendo.",
                   "depois de ver uma técnica 3 vezes, pode copiá-la com −2"),),
   temperamento="curioso e ladrão; rouba armas e devolve se for pago em fruta",
   tesouro="Nada, exceto o que roubou",
   fraqueza="Não resiste a uma aposta", domavel=True)

_b(nome="Serpente de Sete Cabeças", chines="七頭蛇", classe="demonio", nivel=8,
   elemento="agua", tamanho="enorme", habitat="pântanos e lagos envenenados",
   vitalidade=280, qi=300, defesa=19, iniciativa=3,
   atributos={"per": 14, "con": 22, "cha": 6, "int": 10, "luk": 8, "pot": 16},
   ataques=(_A("Sete Mordidas", "七咬", "toque", "4d8", "punho", "agua",
               ("veneno: 2d6 por rodada por 5 rodadas, cumulativo")),
           _A("Sopro de Miasma", "毒霧", "medio", "3d6", "folego_interno",
              "fogo", ("nuvem de 10 m; cega por 1d4 rodadas"))),
   habilidades=(_H("Cabeças Renascem", "再生", "Cortar uma faz nascer duas.",
                   "cada corte crítico gera uma cabeça nova (máx. 12); "
                   "só cauterizar com fogo impede"),),
   temperamento="dorme cem anos e acorda com fome",
   tesouro="Vesícula biliar (elixir de grau Céu contra venenos)",
   fraqueza="Fogo nas feridas impede a regeneração")

_b(nome="Gafanhoto de Praga", chines="蝗魔", classe="besta_espiritual", nivel=2,
   elemento="madeira", tamanho="pequeno", habitat="campos de cultivo",
   vitalidade=25, qi=10, defesa=14, iniciativa=5,
   atributos={"per": 10, "con": 8, "cha": 4, "int": 2, "luk": 6, "pot": 6},
   ataques=(_A("Enxame", "群噬", "toque", "1d6", "punho", "madeira",
               ("cada unidade é 1 HP; um enxame tem 1d100×10 unidades")),),
   habilidades=(_H("Devasta Colheitas", "食穀", "Acaba com uma província.",
                   "uma província afetada perde 50% da população em 1d4 anos"),),
   temperamento="não pensa; só come e se multiplica",
   tesouro="Nada", fraqueza="Fogo e pássaros espirituais")

_b(nome="Carpa que Salta o Portão do Dragão", chines="跳龍門鯉",
   classe="besta_espiritual", nivel=1, elemento="agua", tamanho="pequeno",
   habitat="cachoeiras altas",
   vitalidade=30, qi=40, defesa=13, iniciativa=2,
   atributos={"per": 10, "con": 10, "cha": 8, "int": 10, "luk": 16, "pot": 8},
   ataques=(_A("Bofetada de Cauda", "尾擊", "toque", "1d4", "punho", "agua", ()),),
   habilidades=(_H("Salto do Portão", "跳龍門", "Se subir a cachoeira, vira dragão.",
                   "teste de Sorte DD 30 uma vez na vida; sucesso = sobe para nível 7"),),
   temperamento="insistente; tenta a mesma cachoeira por décadas",
   tesouro="Escama dourada (amuleto de Sorte)",
   fraqueza="Qualquer rede comum", domavel=True)

_b(nome="Gato de Nove Vidas", chines="九命貓", classe="besta_espiritual", nivel=4,
   elemento="metal", tamanho="pequeno", habitat="telhados de cidades antigas",
   vitalidade=40, qi=90, defesa=20, iniciativa=8,
   atributos={"per": 18, "con": 8, "cha": 14, "int": 14, "luk": 18, "pot": 8},
   ataques=(_A("Salto Noturno", "夜躍", "toque", "2d6", "punho", "metal", ()),),
   habilidades=(_H("Nove Vidas", "九命", "Morre oito vezes.",
                   "cada morte custa uma vida; na nona, morre de verdade"),
                _H("Vê o Invisível", "見幽", "Enxerga fantasmas e selos.",
                   "+4 para detectar ilusões, mortos-vivos e formações"),),
   temperamento="faz o que quer; escolhe um dono e o ignora",
   tesouro="Nenhuma; ele já engoliu o que valia",
   fraqueza="Água", domavel=True, inteligente=True)

_b(nome="Urso de Ferro das Colinas", chines="鐵背熊", classe="fera", nivel=5,
   elemento="terra", tamanho="enorme", habitat="colinas e cavernas",
   vitalidade=190, qi=80, defesa=18, iniciativa=1,
   atributos={"per": 10, "con": 22, "cha": 4, "int": 6, "luk": 8, "pot": 18},
   ataques=(_A("Abraço de Ferro", "鐵抱", "toque", "4d10", "punho", "terra",
               ("agarrado: dano contínuo 2d10 por rodada")),),
   habilidades=(_H("Pele de Ferro", "鐵皮", "Pelagem mineralizada.",
                   "reduz em 4 todo dano de armas mortais e de grau Terra"),),
   temperamento="dorme o inverno inteiro; acorda faminto e mal-humorado",
   tesouro="Vesícula (elixir menor) e pele (armadura de grau Terra)",
   fraqueza="Barulho alto o desorienta")

_b(nome="Puppet de Sangue", chines="血傀", classe="morto_vivo", nivel=6,
   elemento="fogo", tamanho="medio", habitat="salões de cultos demoníacos",
   vitalidade=140, qi=200, defesa=19, iniciativa=4,
   atributos={"per": 12, "con": 18, "cha": 4, "int": 4, "luk": 6, "pot": 12},
   ataques=(_A("Chicote de Sangue", "血鞭", "medio", "3d8", "punho", "fogo",
               ("o sangue do alvo é puxado: perde 1d6 de Qi")),),
   habilidades=(_H("Feito de Alguém", "曾是誰", "Era uma pessoa.",
                   "quem o conheceu em vida sofre −2 em todos os testes contra ele"),
                _H("Reconstrói", "重聚", "O sangue volta.",
                   "recupera 2d10 de Vitalidade por rodada perto de sangue derramado"),),
   temperamento="obedece ao selo; odeia o próprio criador",
   tesouro="O selo de controle (dá comando sobre ele)",
   fraqueza="Fogo purificador e sutras de salvação")

_b(nome="Corvo de Três Pernas", chines="三足烏", classe="besta_espiritual",
   nivel=8, elemento="fogo", tamanho="medio", habitat="o próprio sol",
   vitalidade=180, qi=800, defesa=24, iniciativa=7,
   atributos={"per": 18, "con": 14, "cha": 12, "int": 16, "luk": 16, "pot": 12},
   ataques=(_A("Bico Solar", "日喙", "toque", "4d8", "punho", "fogo",
               ("queima: 2d6 por 3 rodadas; ignora armadura de gelo")),),
   habilidades=(_H("Carrega o Sol", "負日", "É ele que move o sol.",
                   "se morrer, o mundo fica sem dia até outro nascer"),
                _H("Luz Verdadeira", "真光", "Não há sombra onde ele está.",
                   "anula AMBIENTE:LUZ ruim num raio de 1 km"),),
   temperamento="obstinado; cumpre a mesma rota há dez mil anos",
   tesouro="Pena solar (ingrediente primordial)",
   fraqueza="Água do Mar do Norte", inteligente=True)

_b(nome="Tartaruga Espiritual Comum", chines="靈龜", classe="besta_espiritual",
   nivel=2, elemento="agua", tamanho="pequeno", habitat="lagos de templo",
   vitalidade=60, qi=50, defesa=17, iniciativa=-2,
   atributos={"per": 12, "con": 14, "cha": 6, "int": 12, "luk": 12, "pot": 10},
   ataques=(_A("Mordida Lenta", "慢咬", "toque", "1d6", "punho", "agua", ()),),
   habilidades=(_H("Casco Oracular", "卜甲", "As rachaduras do casco preveem.",
                   "uma vez por semana revela se uma ação trará azar"),),
   temperamento="paciente; já viu impérios acabarem",
   tesouro="Casco (material de adivinhação, 200 pedras)",
   fraqueza="Virada de costas não consegue se desvirar", domavel=True,
   inteligente=True)

_b(nome="Águia do Vento Cortante", chines="割風鷹", classe="fera", nivel=3,
   elemento="metal", tamanho="medio", habitat="penhascos altos",
   vitalidade=65, qi=70, defesa=16, iniciativa=6,
   atributos={"per": 16, "con": 12, "cha": 6, "int": 8, "luk": 10, "pot": 10},
   ataques=(_A("Mergulho de Navalha", "俯刃", "toque", "2d8", "punho", "metal",
               ("+3 de dano atacando de cima")),),
   habilidades=(_H("Visão de Léguas", "千里眼", "Enxerga a 5 km.",
                   "+4 em Rastreamento e Percepção à distância"),),
   temperamento="caça sozinha; aceita um dono se criada desde o ovo",
   tesouro="Penas (flechas de grau Terra)", fraqueza="Armadilhas de rede",
   domavel=True)

_b(nome="Aranha de Seda Espiritual", chines="靈蠶蛛", classe="besta_espiritual",
   nivel=4, elemento="madeira", tamanho="pequeno", habitat="florestas de bambu",
   vitalidade=80, qi=100, defesa=16, iniciativa=5,
   atributos={"per": 14, "con": 10, "cha": 4, "int": 12, "luk": 10, "pot": 8},
   ataques=(_A("Teia que Prende Qi", "縛氣絲", "medio", "1d6", "arma_oculta",
               "madeira", ("agarrado; o alvo não consegue circular Qi")),),
   habilidades=(_H("Seda de Formação", "陣絲", "A teia é uma formação natural.",
                   "cria uma barreira de Qi 40 em 1 minuto"),),
   temperamento="constrói, espera, conserta",
   tesouro="Fio de seda espiritual (material de grau Céu para vestes)",
   fraqueza="Fogo", domavel=True)

_b(nome="Cão Infernal de Duas Cabeças", chines="雙頭獄犬", classe="demonio",
   nivel=6, elemento="fogo", tamanho="grande", habitat="portões de reinos secretos",
   vitalidade=170, qi=180, defesa=19, iniciativa=5,
   atributos={"per": 16, "con": 18, "cha": 4, "int": 8, "luk": 8, "pot": 14},
   ataques=(_A("Duas Mordidas", "雙咬", "toque", "3d8", "punho", "fogo",
               ("dois ataques; cada um causa 1d6 de fogo contínuo")),),
   habilidades=(_H("Guarda de Portão", "守門", "Não sai do posto.",
                   "+4 de Defesa enquanto defender um portão ou entrada"),
                _H("Fareja Almas", "嗅魂", "Sabe quem já matou.",
                   "detecta culpa: +2 contra quem tem mortes registradas"),),
   temperamento="leal ao dono do portão, hostil a todos os outros",
   tesouro="Presas (arma de grau Terra) e núcleo de besta",
   fraqueza="Uma cabeça dorme enquanto a outra vigia: ataque surpresa na que dorme")


# ==========================================================================
# Gerador procedural de bestas
# ==========================================================================
_PARTES: Tuple[Tuple[str, str], ...] = (
    ("Jade", "玉"), ("Osso", "骨"), ("Cinza", "灰"), ("Trovão", "雷"),
    ("Geada", "霜"), ("Brasa", "燼"), ("Sombra", "影"), ("Cobre", "銅"),
    ("Névoa", "霧"), ("Espinho", "棘"), ("Cristal", "晶"), ("Sangue", "血"),
    ("Lua", "月"), ("Sol", "日"), ("Estrela", "星"), ("Abismo", "淵"),
    ("Vento", "風"), ("Pedra", "石"), ("Seda", "絲"), ("Veneno", "毒"),
)

_CORPOS: Tuple[Tuple[str, str], ...] = (
    ("Tigre", "虎"), ("Serpente", "蛇"), ("Grifo", "鷲"), ("Tartaruga", "龜"),
    ("Lobo", "狼"), ("Corvo", "烏"), ("Cervo", "鹿"), ("Macaco", "猿"),
    ("Touro", "牛"), ("Carpa", "鯉"), ("Escorpião", "蠍"), ("Centopeia", "蜈"),
    ("Morcego", "蝠"), ("Urso", "熊"), ("Grou", "鶴"), ("Leão", "獅"),
    ("Elefante", "象"), ("Rato", "鼠"), ("Gato", "貓"), ("Peixe", "魚"),
)

_HABITATS_POR_TERRENO: Dict[str, Tuple[str, ...]] = {
    "montanhas": ("desfiladeiros altos", "cavernas de picos nevados", "veios expostos"),
    "planicies": ("campos de cultivo", "estepes abertas", "rotas de caravana"),
    "florestas": ("copas densas", "clareiras de erva espiritual", "raízes antigas"),
    "deserto": ("dunas movediças", "oásis secos", "ruínas soterradas"),
    "tundra": ("geleiras", "lagos congelados", "tundra de vento"),
    "litoral": ("falésias", "baías rasas", "naufrágios"),
    "arquipelago": ("ilhas desabitadas", "recifes", "cavernas submarinas"),
    "pantano": ("lodo fundo", "mangues", "poços de miasma"),
    "vales": ("vales fluviais", "desfiladeiros férteis", "cânions"),
    "planalto": ("mesetas varridas pelo vento", "lagos salgados", "pastos altos"),
    "vulcanico": ("bocas de lava", "campos de cinza", "fontes ferventes"),
    "estepe": ("gramais sem fim", "manadas selvagens", "túmulos de pedra"),
}

_TEMPERAMENTOS: Tuple[str, ...] = (
    "territorial; ataca quem entra no raio de um quilômetro do ninho",
    "caçador de emboscada; nunca persegue além de cem passos",
    "curioso; segue viajantes por dias sem atacar",
    "agressivo apenas com quem usa fogo",
    "covarde contra inimigos maiores, feroz contra menores",
    "protetor de uma planta específica e de nada mais",
    "noturno; dorme em profundidade durante o dia",
    "atraído por metal e por pedras espirituais",
    "odeia o próprio reflexo e ataca espelhos",
    "social; vive em bandos de 1d6×10 indivíduos",
    "solitário absoluto; mata o próprio filhote se crescer demais",
    "obedece a sons de sino",
    "guarda uma entrada e não sai dela por nada",
    "migra uma vez por ano e destrói o que estiver no caminho",
)

_FRAQUEZAS: Tuple[str, ...] = (
    "fogo", "água corrente", "sinos e sons altos", "metal frio",
    "a própria sombra ao meio-dia", "ervas amargas", "sangue de tigre",
    "ser nomeada pelo nome verdadeiro", "espelhos", "frio extremo",
    "não consegue atravessar uma linha de sal", "arroz glutinoso",
    "um pedido sincero de desculpas", "luz solar direta",
)


def gerar_besta(
    aleat: Aleatoriedade,
    *,
    nivel: Optional[int] = None,
    elemento: Optional[str] = None,
    terreno: str = "florestas",
    classe: Optional[str] = None,
    tamanho: Optional[str] = None,
) -> Besta:
    """Gera uma besta coerente com o nível, o elemento e o terreno do local."""
    if terreno not in _HABITATS_POR_TERRENO:
        raise ValueError(f"terreno {terreno!r} não catalogado")
    if nivel is None:
        nivel = aleat.escolher_ponderado(
            list(range(0, 14)), [8, 14, 14, 13, 11, 9, 7, 6, 4, 3, 2, 2, 1, 1])
    if not (0 <= nivel <= 13):
        raise ValueError("nível de besta fora de 0..13")
    if elemento is None:
        elemento = aleat.escolher(list(ELEMENTOS_CANONICOS) + ["nenhum"])
    if elemento not in ELEMENTOS_CANONICOS + ELEMENTOS_NEUTROS:
        raise ValueError(f"elemento {elemento!r} inválido")
    if classe is None:
        classe = aleat.escolher_ponderado(
            list(CLASSES_DE_BESTA), [30, 30, 12, 3, 2, 8, 5])
    if tamanho is None:
        tamanho = aleat.escolher_ponderado(
            list(TAMANHOS), [4, 14, 34, 26, 16, 6])

    parte_rom, parte_char = aleat.escolher(list(_PARTES))
    corpo_rom, corpo_char = aleat.escolher(list(_CORPOS))
    nome = f"{parte_rom} {corpo_rom}"
    chines = parte_char + corpo_char
    if nivel >= 8:
        nome = f"{nome} Ancestral"
        chines = chines + "古"
    if classe == "morto_vivo":
        nome = f"{corpo_rom} Cadáver"
        chines = corpo_char + "屍"

    mod_defesa, mult_vit = TAMANHOS[tamanho]
    con = aleat.entre(8, 14) + nivel
    pot = aleat.entre(8, 14) + nivel // 2
    per = aleat.entre(8, 14) + nivel // 2
    vitalidade = max(10, (20 + con * 2 + nivel * 12) * mult_vit // 100)
    from .reinos import qi_maximo
    qi = qi_maximo(nivel, con, per, aleat.entre(6, 12))
    defesa = 10 + (per - 10) // 2 + nivel + mod_defesa
    iniciativa = (per - 10) // 2 + nivel // 3

    n_ataques = 1 + (1 if nivel >= 5 else 0) + (1 if nivel >= 9 else 0)
    ataques: List[AtaqueDeBesta] = []
    for i in range(n_ataques):
        dado_n = max(1, 1 + nivel // 2 + i)
        dado_f = aleat.escolher([4, 6, 8, 10, 12])
        alcance = aleat.escolher(["toque", "toque", "curto", "medio"])
        if alcance != "toque":
            alcance = aleat.escolher(["medio", "longo"])
        verbos = ["Mordida", "Garras", "Cauda", "Chifre", "Sopro", "Salto",
                  "Enrolar", "Espinhos", "Asa"]
        v = aleat.escolher(verbos)
        efeitos: List[str] = []
        if aleat.abaixo(100) < 30 + nivel * 3:
            efeitos.append(aleat.escolher([
                "veneno: 1d6 por rodada durante 3 rodadas",
                "sangramento: 1d8 por rodada até ser estancado",
                "derruba o alvo (teste de Corpo de Ferro DD 10+nível)",
                "agarrado: o alvo não age até escapar (DD 10+nível)",
                "consome Qi: o alvo perde 1d10×10 de Qi",
                "cega por 1d4 rodadas",
                "arremessa o alvo 3d6 metros",
                "reduz o deslocamento do alvo à metade",
            ]))
        ataques.append(_A(f"{v} de {parte_rom}", parte_char + corpo_char,
                          alcance, f"{dado_n}d{dado_f}",
                          aleat.escolher(["punho", "folego_interno", "arma_oculta"]),
                          elemento, tuple(efeitos)))

    habilidades: List[HabilidadeDeBesta] = []
    if nivel >= 4:
        # pares fixos (nome, descrição, mecânica) — sortear cada campo sozinho
        # produziria habilidades incoerentes.
        nome_h, desc_h, mec_h = aleat.escolher([
            ("Pele Endurecida", "o couro dela é mineral",
             "reduz em 2 todo dano de armas de grau mortal"),
            ("Sentido Aguçado", "percebe aproximações a mais de um quilômetro",
             "+4 em Percepção contra emboscadas"),
            ("Passo Silencioso", "move-se sem produzir som nem rastro",
             "+4 em Furtividade; nunca deixa pegada"),
            ("Fôlego Longo", "fica horas sem respirar",
             "imune a sufocamento e a veneno de grau Terra ou inferior"),
            ("Olho Noturno", "enxerga no escuro total",
             "ignora qualquer penalidade de AMBIENTE:LUZ"),
            ("Sangue Frio", "não sente dor",
             "luta até Vitalidade 0 sem penalidade de ESTADO:FERIMENTO"),
        ])
        habilidades.append(_H(nome_h, "異能", desc_h, mec_h))
    if nivel >= 7:
        habilidades.append(_H("Núcleo de Besta", "妖丹",
                              "Condensou um núcleo: é uma besta cultivadora.",
                              "pode usar Qi como escudo e aprender uma técnica"))
    if nivel >= 10:
        habilidades.append(_H("Fala Humana", "人言",
                              "Aprendeu a língua dos homens ouvindo.",
                              "pode negociar, mentir e fazer juramentos"))

    tesouros = [
        "pele e ossos (ingredientes de forja)",
        "um núcleo de besta do próprio nível",
        "nada — o que tinha já foi saqueado",
        "um artefato engolido há décadas",
        "ervas que crescem só no ninho dela",
        "um mapa tatuado no couro",
        "o corpo de um cultivador que ela matou, ainda com o anel",
    ]
    return Besta(
        nome=nome, chines=chines, classe=classe, nivel=nivel, elemento=elemento,
        tamanho=tamanho,
        habitat=aleat.escolher(_HABITATS_POR_TERRENO[terreno]),
        vitalidade=vitalidade, qi=qi, defesa=defesa, iniciativa=iniciativa,
        atributos={"per": per, "con": con, "cha": aleat.entre(3, 10),
                   "int": aleat.entre(2, 8) + nivel // 2,
                   "luk": aleat.entre(6, 14), "pot": pot},
        ataques=tuple(ataques), habilidades=tuple(habilidades),
        temperamento=aleat.escolher(_TEMPERAMENTOS),
        tesouro=aleat.escolher(tesouros),
        fraqueza=aleat.escolher(_FRAQUEZAS),
        descricao=(f"Uma {classe.replace('_',' ')} de {tamanho} associada a "
                   f"{elemento}, encontrada em {terreno}. Nível {nivel}."),
        domavel=aleat.abaixo(100) < (40 - nivel * 3),
        inteligente=nivel >= 8 or aleat.abaixo(100) < 8,
    )


def besta_de(nome: str) -> Besta:
    if nome not in BESTAS:
        raise ValueError(f"besta {nome!r} não catalogada ({len(BESTAS)} no bestiário)")
    return BESTAS[nome]


def bestas_por_nivel(nivel: int) -> Tuple[Besta, ...]:
    return tuple(b for b in BESTAS.values() if b.nivel == nivel)


def nucleo_de_besta(nivel: int) -> Optional[str]:
    """Grau do núcleo de besta (妖丹) conforme o nível — inteiro de tabela."""
    if nivel < 7:
        return None
    return {7: "terra", 8: "terra", 9: "terra", 10: "ceu", 11: "ceu",
            12: "primordial", 13: "primordial"}[nivel]
