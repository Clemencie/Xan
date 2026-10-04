# -*- coding: utf-8 -*-
"""
XAN — Reinos de Cultivo, Leis, Rupturas e Tribulações.
======================================================

Fusão fiel de duas tradições:

* **Amazing Cultivation Simulator**: níveis 0–12 com as quatro etapas
  (Moldagem de Qi, Moldagem de Núcleo, Núcleo Dourado, Espírito Primordial),
  os três caminhos (Xiandao 仙道, Shendao 神道, Corpo 體修), o Núcleo Dourado
  com **grau 9 a 1 decidido por fatores objetivos**, e a Tribulação Celestial.
* **Murim/Wuxia coreano-chinês**: a escada marcial Terceira Classe → Segunda →
  Primeira → Pico → Transcendente → Irrestrito → Absoluto → Natureza, com Qi de
  espada (劍氣), Força de espada (劍罡) e Espada da Mente (心劍).

Regra de ouro desta camada
--------------------------
Nenhum avanço é decidido "pela história". Toda ruptura é uma **Declaração**
comprometida por hash e resolvida pelo motor imparcial. Todo número desta
tabela é inteiro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .auditoria import DiarioDeAuditoria
from .entropia import Aleatoriedade
from .resolucao import Declaracao, Resultado, resolver, teste_oposto

__all__ = [
    "XIANDAO", "SHENDAO", "CORPO", "MARCIAL", "MONSTRO",
    "NivelDeCultivo", "REINOS", "reino_de", "Lei", "LEIS", "lei_de",
    "compatibilidade_de_lei", "qi_maximo", "vitalidade_maxima",
    "defesa_de", "pontos_de_ruptura", "dd_de_ruptura",
    "formar_nucleo_dourado", "GrauDoNucleo",
    "tentar_ruptura", "tribulacao_celestial", "raios_de_tribulacao",
    "tabela_de_desvio_de_qi", "longevidade_base",
]

XIANDAO = "xiandao"
SHENDAO = "shendao"
CORPO = "corpo"
MARCIAL = "marcial"
MONSTRO = "monstro"

CAMINHOS: Tuple[str, ...] = (XIANDAO, SHENDAO, CORPO, MARCIAL, MONSTRO)


@dataclass(frozen=True)
class NivelDeCultivo:
    """Uma linha da escada universal de níveis 0–13."""

    nivel: int
    trilha: str                    # nome da Trilha Não-Ortodoxa (universal)
    xiandao: str
    shendao: str
    corpo: str
    marcial: str
    longevidade: int               # anos de vida típicos neste nível
    qi_base: int
    vitalidade_base: int
    metodo: str                    # como se SAI deste nível
    dd_ruptura: int                # DD da rolagem (só vale se metodo="rolagem")
    xp_necessario: int             # pontos de cultivo exigidos para tentar sair
    poder_marzial: str             # manifestação típica de Qi

    METODOS = ("rolagem", "pontuacao", "tribulacao", "nenhum")

    def __post_init__(self) -> None:
        if self.metodo not in self.METODOS:
            raise ValueError(f"método de ruptura inválido {self.metodo!r}")
        if self.metodo == "rolagem" and not (5 <= self.dd_ruptura <= 45):
            raise ValueError(
                f"nível {self.nivel}: metodo rolagem exige dd_ruptura em 5..45")
        if self.metodo != "rolagem" and self.dd_ruptura != 0:
            raise ValueError(
                f"nível {self.nivel}: metodo {self.metodo} não usa DD")

    def nome_para(self, caminho: str) -> str:
        return {
            XIANDAO: self.xiandao, SHENDAO: self.shendao, CORPO: self.corpo,
            MARCIAL: self.marcial, MONSTRO: self.xiandao,
        }[caminho]


REINOS: Tuple[NivelDeCultivo, ...] = (
    NivelDeCultivo(0, "Mortal", "Mortal", "Mortal", "Mortal",
                   "Guerreiro de Terceira Classe", 70, 0, 20, "rolagem", 12, 100,
                   "Nenhum Qi interno; só músculo e treino."),
    NivelDeCultivo(1, "Temperado", "Moldagem de Qi I", "Estado Ascético",
                   "Fase de Remoldagem", "Terceira Classe", 90, 20, 25,
                   "rolagem", 13, 250,
                   "Sente o Qi; tempera pele e músculo."),
    NivelDeCultivo(2, "Concentrado", "Moldagem de Qi II", "Estado Ascético",
                   "Fase de Remoldagem", "Segunda Classe", 100, 35, 30,
                   "rolagem", 14, 600,
                   "Qi circula nos 12 meridianos; quebra pedra com a palma."),
    NivelDeCultivo(3, "Moldador", "Moldagem de Qi III", "Estado Ascético",
                   "Fase de Remoldagem", "Primeira Classe", 120, 55, 36,
                   "rolagem", 16, 1400,
                   "Imbui a arma com Qi; salta telhados."),
    NivelDeCultivo(4, "Portão da Mente", "Moldagem de Núcleo I",
                   "Estado de Peregrino", "Limpeza de Medula", "Reino do Pico",
                   150, 80, 45, "rolagem", 18, 3000,
                   "Abre o Portão da Mente; Qi externo visível como névoa."),
    NivelDeCultivo(5, "Caldeirão", "Moldagem de Núcleo II",
                   "Estado de Peregrino", "Limpeza de Medula", "Pico Supremo",
                   180, 110, 55, "rolagem", 20, 6500,
                   "Emissão de Qi de Espada (劍氣) a curta distância."),
    NivelDeCultivo(6, "Moldador de Essência", "Moldagem de Núcleo III",
                   "Estado de Peregrino", "Limpeza de Medula", "Transcendente",
                   220, 150, 70, "pontuacao", 0, 14000,
                   "Condensa o Núcleo Dourado: o grau decide o resto da vida."),
    NivelDeCultivo(7, "Núcleo Dourado", "Núcleo Dourado I", "Estado Divino",
                   "Fase de Incubação", "Irrestrito", 300, 200, 90,
                   "rolagem", 24, 28000,
                   "Força de Espada (劍罡) visível; voo sustentado."),
    NivelDeCultivo(8, "Alquimia", "Núcleo Dourado II", "Estado Divino",
                   "Fase de Incubação", "Absoluto — Alma Marcial", 400, 260,
                   115, "rolagem", 26, 55000,
                   "Domínio do próprio elemento; golpes que fendem colinas."),
    NivelDeCultivo(9, "Embrionário", "Núcleo Dourado III", "Estado Divino",
                   "Fase de Incubação", "Absoluto — Sem Limite", 500, 340,
                   150, "tribulacao", 0, 110000,
                   "Converte a alma: três raios decidem se ela nasce."),
    NivelDeCultivo(10, "Incubação da Origem", "Espírito Primordial I",
                   "Estado de Realização", "Fase do Caos",
                   "Reino da Natureza — Despertar", 800, 440, 200,
                   "rolagem", 30, 220000,
                   "Alma Nascente projetável; sobrevive à destruição do corpo."),
    NivelDeCultivo(11, "Espírito Ascendente", "Espírito Primordial II",
                   "Estado de Realização", "Fase do Caos",
                   "Reino da Natureza — Eterno", 1200, 560, 260,
                   "tribulacao", 0, 440000,
                   "Espada da Mente (心劍); quatro raios sobre o cultivador."),
    NivelDeCultivo(12, "Espírito Primordial", "Espírito Primordial III",
                   "Estado de Realização", "Fase do Caos",
                   "Reino da Natureza — Divino", 2000, 700, 340,
                   "tribulacao", 0, 0,
                   "Nove raios: a Ascensão. Poucos na história ouviram o segundo."),
    NivelDeCultivo(13, "Ascensão", "Imortal 仙", "Divindade 神",
                   "Caos Unificado", "Trono Constelar 星座", 99999, 900, 600,
                   "nenhum", 0, 0,
                   "Deixa o plano mortal. Não volta — mas deixa estátua e altar."),
)


def reino_de(nivel: int) -> NivelDeCultivo:
    if not isinstance(nivel, int) or isinstance(nivel, bool):
        raise TypeError("nível deve ser int")
    if not (0 <= nivel <= 13):
        raise ValueError(f"nível {nivel} fora de 0..13")
    return REINOS[nivel]


def longevidade_base(nivel: int) -> int:
    return reino_de(nivel).longevidade


# ==========================================================================
# LEIS (功法) — as "classes" do XAN
# ==========================================================================
@dataclass(frozen=True)
class Lei:
    codigo: str
    nome: str
    chines: str
    caminho: str
    elemento: str
    familia: str              # taiyi | avancada | shendao | corpo | marcial | demoniaca
    requisitos: Mapping[str, int]
    dd_extra: int             # ajuste na dificuldade das rupturas desta Lei
    descricao: str
    tags: Tuple[str, ...] = ()
    tecnicas_iniciais: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.caminho not in CAMINHOS:
            raise ValueError(f"caminho inválido {self.caminho!r}")
        from .regras import ELEMENTOS_CANONICOS, ELEMENTOS_NEUTROS
        if self.elemento not in ELEMENTOS_CANONICOS + ELEMENTOS_NEUTROS:
            raise ValueError(f"elemento inválido {self.elemento!r}")
        for k, v in self.requisitos.items():
            if k not in ("per", "con", "cha", "int", "luk", "pot"):
                raise ValueError(f"atributo de requisito inválido {k!r}")
            if not isinstance(v, int) or not (1 <= v <= 20):
                raise ValueError(f"requisito {k}={v} fora de 1..20")


def _lei(codigo, nome, chines, caminho, elemento, familia, req, dd_extra,
         descricao, tags=(), tecnicas=()) -> Lei:
    lei = Lei(codigo, nome, chines, caminho, elemento, familia, req, dd_extra,
              descricao, tuple(tags), tuple(tecnicas))
    if codigo in LEIS:
        raise ValueError(f"lei {codigo} duplicada")
    LEIS[codigo] = lei
    return lei


LEIS: Dict[str, Lei] = {}

# --- Leis Supremas Taiyi (as cinco elementais básicas do ACS) --------------
_lei("TAIYI_METAL", "Lei da Sabedoria do Grande Carro", "北斗洞心劫法",
     XIANDAO, "metal", "taiyi", {"per": 7, "con": 4, "int": 5}, 0,
     "Cultiva observando as sete estrelas do Carro do Norte. Concede leitura de "
     "destinos, artefatos de legado e uma percepção que beira a adivinhação.",
     tags=("adivinhacao", "artefatos", "estrelas"),
     tecnicas=("Bússola do Carro", "Lâmina Estelar", "Olho do Observador"))
_lei("TAIYI_MADEIRA", "Lei das Seis Rotas de Reincarnação", "長生六道輪迴經",
     XIANDAO, "madeira", "taiyi", {"con": 6, "int": 6, "luk": 3, "per": 4}, 0,
     "Percorre as seis rotas do samsara. Renasce o corpo, sela bestas em "
     "contratos espirituais e transforma morte em progresso.",
     tags=("reencarnacao", "contratos", "cura"),
     tecnicas=("Selo das Seis Rotas", "Contrato Espiritual", "Corpo que Renasce"))
_lei("TAIYI_AGUA", "Lei dos Dezesseis Passos Supremos", "太和十六洞天",
     XIANDAO, "agua", "taiyi", {"con": 7, "cha": 5, "int": 6}, 0,
     "Abre dezesseis grutas-celestes internas. Cada ruptura concede um passo e "
     "um domínio; é a Lei das rupturas detalhadas e da defesa absoluta.",
     tags=("defesa", "grutas", "passos"),
     tecnicas=("Passo da Caverna", "Manto de Água Parada", "Dezesseis Selos"))
_lei("TAIYI_FOGO", "Lei do Refino do Sol Verdadeiro", "三陽三昧丙丁煉火訣",
     XIANDAO, "fogo", "taiyi", {"per": 5, "con": 5, "cha": 5, "int": 5, "luk": 5}, 0,
     "A Lei do equilíbrio: exige cinco atributos parelhos e devolve o fogo "
     "sâmadi capaz de forjar qualquer coisa. A favorita dos generalistas.",
     tags=("fogo_samadi", "forja", "equilibrio"),
     tecnicas=("Chama Sâmadi", "Corpo de Três Sóis", "Forja Solar"))
_lei("TAIYI_TERRA", "Lei do Refino do Girassol", "葵花煉神大法",
     XIANDAO, "terra", "taiyi", {"per": 6, "cha": 6, "int": 6}, 0,
     "Refina o espírito como o girassol segue o sol. Cultivo veloz, alma "
     "resiliente e uma presença que curva multidões.",
     tags=("espirito", "presenca", "velocidade"),
     tecnicas=("Palma do Girassol", "Refino do Espírito", "Aura Solar"))

# --- Leis avançadas não-Taiyi ---------------------------------------------
_lei("CORTE_EMOCOES", "Lei do Corte das Emoções", "太上忘情道",
     XIANDAO, "fogo", "avancada", {"per": 5, "cha": 9, "int": 5}, 1,
     "Esquecer o sentimento para conter o Dao. Carisma absurdo, coração de "
     "gelo: quem a segue perde laços e ganha poder. Imune a Demônios Interiores "
     "comuns, mas vulnerável ao Vazio.",
     tags=("apatia", "carisma", "risco"),
     tecnicas=("Olhar Esquecido", "Coração Sereno", "Golpe sem Apego"))
_lei("ALQUIMIA_PRIMORDIAL", "Lei da Alquimia Primordial", "九轉金丹直指",
     XIANDAO, "fogo", "avancada", {"per": 6, "con": 5, "int": 6}, 0,
     "Nove viragens do elixir dourado. Rupturas dependentes de pílulas "
     "específicas, mas quem domina a fornalha domina o próprio destino.",
     tags=("alquimia", "elixires", "fornalha"),
     tecnicas=("Fornalha Interna", "Nove Viragens", "Dedo de Ouro"))
_lei("ROUBO_CELESTIAL", "Lei do Roubo Celestial", "偷天決",
     XIANDAO, "terra", "avancada", {"con": 9, "luk": 3}, 2,
     "Rouba o Qi do céu e dos outros. A mais rápida e a mais odiada: cada "
     "ruptura exige sacrificar algo — longevidade, um laço ou uma vítima.",
     tags=("roubo", "sacrificio", "rapidez"),
     tecnicas=("Mão que Rouba o Céu", "Drenar Essência", "Trocar o Sol"))
_lei("SETE_MASSACRES", "Espada dos Sete Massacres", "七殺劍訣",
     XIANDAO, "metal", "avancada", {"per": 7, "con": 7, "luk": 4}, 1,
     "Sete estrelas de matança. Poder ofensivo sem igual e um preço: cada "
     "estágio exige uma morte à altura. Alma de Espada no nível 11.",
     tags=("ofensiva", "espada", "sangue"),
     tecnicas=("Aura de Espada", "Sete Cortes", "Alma de Espada"))
_lei("MIL_ARTEFATOS", "Lei dos Mil Artefatos", "己寅九衝多寶真解",
     XIANDAO, "madeira", "avancada", {"per": 8, "int": 5, "luk": 3}, 0,
     "Dez mil tesouros voam ao comando. O cultivador é fraco sozinho e "
     "imparável cercado das próprias obras.",
     tags=("artefatos", "voo", "colecionador"),
     tecnicas=("Tesouro Voador", "Chuva de Lâminas", "Vínculo de Artefato"))
_lei("PUREZA_JADE", "Lei Imortal da Pureza de Jade", "玉清仙法",
     XIANDAO, "nenhum", "avancada", {"per": 4, "int": 7, "luk": 6}, 0,
     "O caminho ortodoxo mais puro: sem elemento, sem atalhos, sem dívidas. "
     "Lento, estável e com o maior teto de Ascensão.",
     tags=("ortodoxa", "estavel", "ascensao"),
     tecnicas=("Sopro de Jade", "Manto Puro", "Escada de Nuvens"))
_lei("SIMBOLOS_PRIMORDIAIS", "Lei dos Símbolos Primordiais", "太元五符元籙",
     XIANDAO, "nenhum", "avancada", {"per": 8, "cha": 4, "int": 8}, 0,
     "Cinco talismãs natais condensados na ruptura. Domina selos, barreiras e "
     "a arte de prender o que não pode ser morto.",
     tags=("talismas", "selos", "barreiras"),
     tecnicas=("Talismã Natal", "Selo de Partida", "Barreira de Nuvem"))
_lei("CONQUISTA_NIMBO", "Lei da Conquista do Nimbo", "雲霄征伐律",
     XIANDAO, "nenhum", "avancada", {"per": 6, "cha": 6, "luk": 6}, 1,
     "Núcleo Yin ou Yang conforme a polaridade da ruptura. Conquista céus "
     "alheios: rouba formação, clima e favores divinos.",
     tags=("nimbos", "conquista", "duplo_nucleo"),
     tecnicas=("Nimbo Subjugado", "Marcha das Nuvens", "Decreto de Conquista"))

# --- Leis Shendao (divindade pela fé) ------------------------------------
_lei("TROVAO_CELESTIAL", "Sutra da Salvação pelo Trovão Celestial", "九天雷救經",
     SHENDAO, "nenhum", "shendao", {"cha": 7, "int": 5, "con": 4}, 0,
     "Divindade punitiva: milagres de raio, julgamento e proteção de cidades. "
     "Exige Fé acima de Humanidade.",
     tags=("juizo", "raio", "milagres"),
     tecnicas=("Milagre do Trovão", "Julgamento", "Égide do Crente"))
_lei("OITO_CEUS", "Sadhana dos Oito Céus", "八天修行法",
     SHENDAO, "nenhum", "shendao", {"cha": 6, "per": 6, "int": 6}, 0,
     "Constrói um Reino Divino de até 48 estados. Lenta, caríssima e capaz de "
     "erguer exércitos de fé.",
     tags=("reino_divino", "fe", "dominio"),
     tecnicas=("Trono Menor", "Chamado dos Fiéis", "Procissão"))
_lei("SALVACAO_SUBMUNDO", "Sutra da Salvação do Submundo", "幽冥救苦經",
     SHENDAO, "nenhum", "shendao", {"cha": 8, "int": 4}, 1,
     "Guia os mortos. Remove obsessões e Demônios Interiores de terceiros, "
     "mas atrai o ressentimento dos vivos.",
     tags=("mortos", "exorcismo", "obsessao"),
     tecnicas=("Barco dos Mortos", "Lanterna do Submundo", "Absolvição"))

# --- Leis Corporais (體修) ------------------------------------------------
_lei("VAJRA_DOURADO", "Corpo do Vajra Dourado", "金剛不壞體",
     CORPO, "metal", "corpo", {"con": 8, "pot": 5}, 0,
     "Templo Shaolin: a carne vira metal. Defesa imbatível, zero sutileza.",
     tags=("defesa", "shaolin", "indestrutivel"),
     tecnicas=("Pele de Bronze", "Osso de Ferro", "Sino Dourado"))
_lei("DRAGAO_AZUL", "Corpo Imortal do Dragão Azul", "青龍不死身",
     CORPO, "madeira", "corpo", {"con": 6, "pot": 7}, 0,
     "Regeneração monstruosa. Membros crescem de volta; venenos viram comida.",
     tags=("regeneracao", "dragao", "veneno"),
     tecnicas=("Sangue que Refloresce", "Garra do Dragão", "Fôlego Verde"))
_lei("TARTARUGA_NEGRA", "Arte da Carapaça da Tartaruga Negra", "玄武甲功",
     CORPO, "agua", "corpo", {"con": 7, "per": 4}, 0,
     "Escudo de Qi condensado e longevidade extrema. Lento como geleira, "
     "imparável como maré.",
     tags=("escudo", "longevidade", "lento"),
     tecnicas=("Carapaça Negra", "Passo de Maré", "Sono Profundo"))
_lei("FENIX_CARMESIM", "Corpo da Fênix Carmesim", "朱雀焚身訣",
     CORPO, "fogo", "corpo", {"con": 7, "pot": 6}, 1,
     "Queima o próprio sangue por poder. Renasce uma vez por década — e cada "
     "renascimento cobra um laço.",
     tags=("renascimento", "sangue", "fenix"),
     tecnicas=("Asa de Brasa", "Renascimento", "Chuva de Cinzas"))
_lei("MONTANHA_INABALAVEL", "Moldagem da Montanha Inabalável", "不動山嶽體",
     CORPO, "terra", "corpo", {"con": 9, "pot": 4}, 0,
     "Não pode ser movido. Literalmente: formações inteiras quebram nele.",
     tags=("imovel", "forca", "ancora"),
     tecnicas=("Raiz de Montanha", "Punho de Pedra", "Peso do Mundo"))

# --- Trilha Marcial (murim puro, sem imortalidade) ------------------------
_lei("AMEIXEIRA", "Arte da Espada da Flor de Ameixeira", "梅花劍法",
     MARCIAL, "madeira", "marcial", {"per": 5, "con": 4}, 0,
     "Monte Hua: vinte e quatro formas que florescem como ameixeiras. Beleza "
     "letal e a pior defesa do Murim.",
     tags=("espada", "monte_hua", "elegancia"),
     tecnicas=("Pétala que Cai", "Vinte e Quatro Formas", "Chuvisco de Aço"))
_lei("PALMA_TAIJI", "Palma Taiji de Wudang", "太極掌",
     MARCIAL, "agua", "marcial", {"per": 5, "int": 5}, 0,
     "Wudang: ceder para vencer. Redireciona força, devolve golpes e vence "
     "adversários maiores sem nunca atacar primeiro.",
     tags=("contra_ataque", "wudang", "suave"),
     tecnicas=("Círculo que Devolve", "Passo das Nuvens", "Palma Sem Força"))
_lei("PUNHO_VAJRA", "Punho Arhat de Shaolin", "羅漢拳",
     MARCIAL, "metal", "marcial", {"con": 6}, 0,
     "Shaolin: dezoito mãos de Arhat. Simples, honesto, devastador.",
     tags=("punho", "shaolin", "externa"),
     tecnicas=("Dezoito Mãos", "Grito do Leão", "Corpo de Ferro Menor"))
_lei("AGULHAS_TANG", "Arte das Agulhas Ocultas do Clã Tang", "唐門暗器術",
     MARCIAL, "metal", "marcial", {"per": 6, "int": 4}, 0,
     "Sichuan Tang: venenos e armas ocultas. Nunca vence de frente, quase "
     "sempre vence.",
     tags=("veneno", "armas_ocultas", "tang"),
     tecnicas=("Chuva de Agulhas", "Sopro Envenenado", "Manga de Seda"))
_lei("FORMACOES_ZHUGE", "Arte das Formações do Clã Zhuge", "諸葛奇門陣",
     MARCIAL, "terra", "marcial", {"int": 7, "per": 4}, 0,
     "Estratégia e portas estranhas. Um Zhuge sozinho vale dez espadas "
     "posicionadas no lugar errado.",
     tags=("formacoes", "estrategia", "zhuge"),
     tecnicas=("Porta Estranha", "Oito Trigramas", "Mapa Vivo"))
_lei("CAJADO_MENDIGO", "Caminho do Mendigo Errante", "打狗棒法",
     MARCIAL, "madeira", "marcial", {"cha": 5, "con": 4}, 0,
     "Seita dos Mendigos: a maior rede de informações do Murim e um cajado que "
     "quebra joelhos.",
     tags=("informacao", "mendigos", "cajado"),
     tecnicas=("Cajado que Bate no Cão", "Rede de Sussurros", "Palma do Pedinte"))
_lei("PALMA_DRAGAO_PENG", "Palma do Dragão do Norte (Peng)", "彭家龍掌",
     MARCIAL, "fogo", "marcial", {"con": 7}, 0,
     "Hebei Peng: arte externa pura. O corpo é a arma e a arma é o corpo.",
     tags=("externa", "peng", "bruta"),
     tecnicas=("Palma do Dragão", "Costas de Ferro", "Avanço de Touro"))
_lei("DEMONIO_CELESTIAL", "Caminho do Demônio Celestial", "天魔功",
     MARCIAL, "fogo", "demoniaca", {"con": 6, "luk": 5}, 2,
     "Culto do Demônio Celestial: chama sagrada, sangue e poder imediato. Cada "
     "estágio é mais forte e mais caro que o anterior.",
     tags=("demoniaca", "chama", "sangue"),
     tecnicas=("Chama do Demônio", "Garra de Sangue", "Riso do Abismo"))
_lei("SANGUE_SETE_ESTRELAS", "Arte do Sangue das Sete Estrelas", "七殺血功",
     MARCIAL, "agua", "demoniaca", {"con": 5, "luk": 6}, 2,
     "Seita não-ortodoxa: cultiva matando. Progresso acelerado e Desvio de Qi "
     "quase garantido sem disciplina.",
     tags=("demoniaca", "sangue", "assassinato"),
     tecnicas=("Sede das Sete Estrelas", "Passo de Sombra", "Dívida de Sangue"))


def lei_de(codigo: str) -> Lei:
    if codigo not in LEIS:
        raise ValueError(
            f"lei {codigo!r} não existe. Leis publicadas: {len(LEIS)}")
    return LEIS[codigo]


def leis_por_caminho(caminho: str) -> Tuple[Lei, ...]:
    return tuple(l for l in LEIS.values() if l.caminho == caminho)


# --------------------------------------------------------------------------
# Compatibilidade com a Lei (Law Match) — inteiro, 0..150
# --------------------------------------------------------------------------
def compatibilidade_de_lei(
    atributos: Mapping[str, int],
    lei: Lei,
) -> Tuple[int, List[str]]:
    """Aderência entre atributos e requisitos da Lei — inteiro de 0 a 150.

    Cada atributo exigido rende ``min(valor, 2×requisito) × 100 ÷ requisito``:
    cumprir exatamente dá 100%, o dobro dá 200% (e a média final é truncada em
    150%). Abaixo do requisito, cai proporcionalmente. Tudo em aritmética
    inteira — nenhuma casa decimal, nenhum arredondamento de plataforma.
    """
    if not lei.requisitos:
        raise ValueError("lei sem requisitos — impossível calcular compatibilidade")
    razoes: List[str] = []
    soma = 0
    for atr, req in sorted(lei.requisitos.items()):
        valor = int(atributos.get(atr, 0))
        if valor < 0:
            raise ValueError(f"atributo {atr} negativo")
        razao = min(valor, 2 * req) * 100 // req
        soma += razao
        status = ("supera" if valor > req else
                  ("cumpre" if valor == req else "abaixo"))
        razoes.append(f"{atr} {valor}/{req} → {razao}% ({status})")
    match = max(0, min(150, soma // len(lei.requisitos)))
    return match, razoes


# --------------------------------------------------------------------------
# Estatísticas derivadas
# --------------------------------------------------------------------------
def qi_maximo(nivel: int, con: int, per: int, int_: int,
              grau_do_nucleo: Optional[int] = None) -> int:
    """Reserva máxima de Qi.

    ``Qi = base do reino + Constituição + Percepção÷2 + Inteligência÷2
            + bônus do Núcleo Dourado``

    O Qi é ao mesmo tempo **mana e escudo** (como no ACS): enquanto houver Qi,
    o dano é absorvido por ele antes de tocar a Vitalidade. Por isso a reserva é
    deliberadamente modesta — uma luta precisa acabar, e não pode acabar por
    cansaço de quem anota.
    """
    base = reino_de(nivel).qi_base
    bonus_nucleo = 0
    if grau_do_nucleo is not None:
        if not (1 <= grau_do_nucleo <= 9):
            raise ValueError("grau do núcleo vai de 1 (supremo) a 9 (inferior)")
        if nivel < 7:
            raise ValueError("só existe bônus de Núcleo a partir do nível 7")
        bonus_nucleo = (10 - grau_do_nucleo) * 25 + nivel * 5
    return base + int(con) + int(per) // 2 + int(int_) // 2 + bonus_nucleo


def vitalidade_maxima(nivel: int, con: int, pot: int) -> int:
    return reino_de(nivel).vitalidade_base + 2 * int(con) + int(pot) + 3 * nivel


def defesa_de(
    modo: str,
    nivel: int,
    atributo_relevante: int,
    graduacao: int,
    manto_de_qi: bool = False,
) -> int:
    """Defesa passiva, conforme o modo declarado ANTES do encontro.

    * ``esquiva``      → Percepção + Passos Leves (não ser tocado)
    * ``resistencia``  → Constituição + Corpo de Ferro (aguentar o golpe)
    * ``aparar``       → Constituição + graduação na própria arma (devolver)

    Conta: ``base + bônus de atributo + graduação + manto``.

    Dois cuidados de projeto, deliberados:

    1. O **nível NÃO entra aqui**. A diferença de reinos já é tratada pela regra
       ``REINO:SUPRESSAO`` (±2 por nível de lacuna). Contar as duas coisas seria
       contar o mesmo fato duas vezes — e tornaria mestres intocáveis.
    2. O **Qi NÃO infla a Defesa**. O Qi é escudo no sentido do ACS: ele absorve
       *dano*, não acerto. Deixá-lo subir a DD transformaria cultivador rico em
       alvo impossível. Quem quer Defesa maior gasta Qi sustentando um
       **Manto de Qi** (+2, custa 10 de Qi por rodada).
    """
    modos = ("esquiva", "resistencia", "aparar")
    if modo not in modos:
        raise ValueError(f"modo de defesa deve ser um de {modos}")
    if not isinstance(manto_de_qi, bool):
        raise TypeError("manto_de_qi deve ser bool")
    bonus = (int(atributo_relevante) - 10) // 2
    base = {"esquiva": 10, "resistencia": 11, "aparar": 10}[modo]
    return base + bonus + int(graduacao) + (2 if manto_de_qi else 0)


def pontos_de_ruptura(nivel: int) -> int:
    """Pontos de cultivo exigidos para sair deste nível."""
    return reino_de(nivel).xp_necessario


def dd_de_ruptura(nivel: int, compatibilidade: int, lei: Lei) -> int:
    """DD da rolagem para SAIR do nível, ajustado pela compatibilidade com a Lei.

    Cada 25 pontos de compatibilidade acima de 100 reduz a DD em 1; abaixo de 60
    aumenta 1 a cada 15 pontos faltantes. Tetos fixos em 5 e 45.
    """
    if reino_de(nivel).metodo != "rolagem":
        raise ValueError(
            f"o nível {nivel} sai por '{reino_de(nivel).metodo}', não por rolagem"
        )
    dd = reino_de(nivel).dd_ruptura
    if compatibilidade > 100:
        dd -= (compatibilidade - 100) // 25
    elif compatibilidade < 60:
        dd += (60 - compatibilidade + 14) // 15
    return max(5, min(45, dd + lei.dd_extra))


# --------------------------------------------------------------------------
# Núcleo Dourado (金丹) — grau decidido por fatores objetivos, uma única vez
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class GrauDoNucleo:
    grau: int
    pontuacao: int
    parcelas: Tuple[Tuple[str, int], ...]
    razoes: Tuple[str, ...]
    titulo: str

    def markdown(self) -> str:
        linhas = [
            f"### Núcleo Dourado — grau {self.grau} ({self.titulo})",
            f"**Pontuação final: {self.pontuacao}**",
            "",
            "| Fator | Pontos |", "|---|---:|",
        ]
        for nome, pts in self.parcelas:
            linhas.append(f"| {nome} | {pts:+d} |")
        linhas += ["", "**Justificativas:**"]
        linhas += [f"- {r}" for r in self.razoes]
        return "\n".join(linhas)


_TITULOS_DO_GRAU = {
    1: "Núcleo de Taiyi — uma vez por era",
    2: "Núcleo Imaculado",
    3: "Núcleo Radiante",
    4: "Núcleo Sólido",
    5: "Núcleo Comum",
    6: "Núcleo Turvo",
    7: "Núcleo Rachado",
    8: "Núcleo Impuro",
    9: "Núcleo de Escória",
}
_TABELA_GRAU: Tuple[Tuple[int, int], ...] = (
    (95, 1), (85, 2), (72, 3), (60, 4), (48, 5), (36, 6), (25, 7), (15, 8),
    (-10 ** 9, 9),
)

TABELA_FENGSHUI_PONTOS = {
    "muito_auspicioso": 8, "auspicioso": 4, "neutro": 0,
    "sinistro": -4, "muito_sinistro": -8,
}
TABELA_DENSIDADE_PONTOS = {
    "esteril": -8, "pobre": -4, "comum": 0, "rica": 4,
    "veia_espiritual": 8, "terra_imortal": 12,
}
TABELA_ELIXIR_PONTOS = {
    "nenhum": 0, "menor": 2, "medio": 5, "maior": 9, "celestial": 14,
}


def formar_nucleo_dourado(
    *,
    qi_maximo_atual: int,
    fengshui: str,
    densidade_qi: str,
    harmonia: int,
    estado_mental: int,
    elixir: str,
    compatibilidade: int,
    compreensao: int,
    mestre_presente: bool,
    artefato: str = "nenhum",
) -> GrauDoNucleo:
    """Calcula o grau do Núcleo Dourado. **Determinístico: não rola dado.**

    Como no ACS, formar o Núcleo não pode "falhar": sempre se forma um núcleo.
    O que varia é a qualidade, e ela é uma conta fechada sobre fatos declarados.
    A única tentativa é a definitiva.
    """
    if qi_maximo_atual < 0:
        raise ValueError("Qi máximo negativo não existe")
    if not (0 <= estado_mental <= 200):
        raise ValueError("estado mental vai de 0 a 200")
    if not (0 <= compreensao <= 100000):
        raise ValueError("compreensão fora de faixa")
    if not (0 <= compatibilidade <= 150):
        raise ValueError("compatibilidade vai de 0 a 150")
    if fengshui not in TABELA_FENGSHUI_PONTOS:
        raise ValueError(f"feng shui inválido {fengshui!r}")
    if densidade_qi not in TABELA_DENSIDADE_PONTOS:
        raise ValueError(f"densidade de Qi inválida {densidade_qi!r}")
    if elixir not in TABELA_ELIXIR_PONTOS:
        raise ValueError(f"elixir inválido {elixir!r}")
    if not (0 <= harmonia <= 12):
        raise ValueError("harmonia elemental vai de 0 a 12")
    if artefato not in ("nenhum", "mortal", "terra", "ceu", "primordial"):
        raise ValueError(f"artefato inválido {artefato!r}")
    if not isinstance(mestre_presente, bool):
        raise TypeError("mestre_presente deve ser bool")

    parcelas: List[Tuple[str, int]] = []
    razoes: List[str] = []

    p = qi_maximo_atual // 100
    parcelas.append(("Qi máximo acumulado", p))
    razoes.append(f"Qi máximo {qi_maximo_atual} ÷ 100 = {p:+d}")

    p = TABELA_FENGSHUI_PONTOS[fengshui]
    parcelas.append(("Feng Shui do local", p))
    razoes.append(f"sala {fengshui.replace('_',' ')} = {p:+d}")

    p = TABELA_DENSIDADE_PONTOS[densidade_qi]
    parcelas.append(("Densidade de Qi do local", p))
    razoes.append(f"densidade {densidade_qi.replace('_',' ')} = {p:+d}")

    parcelas.append(("Harmonia de estação/hora/clima", harmonia))
    razoes.append(f"harmonia elemental calculada = {harmonia:+d}")

    p = estado_mental // 10
    parcelas.append(("Estado mental (Coração do Dao)", p))
    razoes.append(f"estado mental {estado_mental} ÷ 10 = {p:+d}")

    p = TABELA_ELIXIR_PONTOS[elixir]
    parcelas.append(("Elixir de ruptura", p))
    razoes.append(f"elixir {elixir} = {p:+d}")

    p = compatibilidade // 10
    parcelas.append(("Compatibilidade com a Lei", p))
    razoes.append(f"aderência {compatibilidade}% ÷ 10 = {p:+d}")

    p = compreensao // 200
    parcelas.append(("Compreensão acumulada", p))
    razoes.append(f"compreensão {compreensao} ÷ 200 = {p:+d}")

    p = {"nenhum": 0, "mortal": 0, "terra": 2, "ceu": 5, "primordial": 9}[artefato]
    parcelas.append(("Artefato de cultivo", p))
    razoes.append(f"artefato {artefato} = {p:+d}")

    p = 4 if mestre_presente else 0
    parcelas.append(("Mestre guiando a ruptura", p))
    razoes.append(f"mestre presente: {mestre_presente} = {p:+d}")

    total = sum(v for _, v in parcelas)
    grau = 9
    for limiar, g in _TABELA_GRAU:
        if total >= limiar:
            grau = g
            break
    return GrauDoNucleo(
        grau=grau, pontuacao=total, parcelas=tuple(parcelas),
        razoes=tuple(razoes), titulo=_TITULOS_DO_GRAU[grau],
    )


# --------------------------------------------------------------------------
# Rupturas, Tribulação e Desvio de Qi
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultadoDeRuptura:
    resultado: Resultado
    nivel_anterior: int
    nivel_novo: int
    avancou: bool
    consequencia: str
    desvio_de_qi: Optional[Tuple[int, str]]

    def resumo(self) -> str:
        cab = "AVANÇOU" if self.avancou else "FALHOU"
        return (f"{cab}: nível {self.nivel_anterior} → {self.nivel_novo} | "
                f"{self.consequencia}\n{self.resultado.resumo()}")


_TABELA_DESVIO: Tuple[Tuple[int, str], ...] = (
    (1, "O dantian racha: perde 25% dos pontos de cultivo acumulados e 1d6 de Vitalidade."),
    (2, "Um meridiano se rompe: −1 permanente em Constituição até ser curado por um Ancião."),
    (3, "Um Demônio Interior se instala: ganha um 心魔 com desejo próprio (gere em npcs)."),
    (4, "Regressão: cai 1 nível de cultivo e perde a técnica mais recente."),
    (5, "Coma de 1d4 meses; ao despertar, −2 em Percepção por um ano inteiro."),
    (6, "O Qi inverte e o corpo explode. Morte definitiva — sem ressurreição."),
)


def tabela_de_desvio_de_qi(
    aleat: Aleatoriedade,
    gravidade: str = "comum",
) -> Tuple[int, str]:
    """Sorteia a consequência do Desvio de Qi (走火入魔).

    ``gravidade`` desloca a tabela: ``comum`` usa 1d6 direto, ``grave`` soma +1
    ao índice, ``catastrofica`` soma +2. A gravidade é um fato declarado antes.
    """
    if gravidade not in ("comum", "grave", "catastrofica"):
        raise ValueError("gravidade deve ser comum, grave ou catastrofica")
    desloc = {"comum": 0, "grave": 1, "catastrofica": 2}[gravidade]
    face = aleat.entre(1, 6)
    indice = min(6, face + desloc)
    return _TABELA_DESVIO[indice - 1]


def tentar_ruptura(
    *,
    ator: str,
    nivel_atual: int,
    compatibilidade: int,
    lei: Lei,
    valor_de_int: int,
    graduacao_de_compreensao: int,
    fatos: Optional[Mapping[str, Any]] = None,
    regras: Sequence[str] = ("AMBIENTE:FENGSHUI", "AMBIENTE:DENSIDADE_QI",
                             "RECURSO:ELIXIR", "PREPARO:MEDITACAO"),
    aleat: Optional[Aleatoriedade] = None,
    diario: Optional[DiarioDeAuditoria] = None,
) -> ResultadoDeRuptura:
    """Rola a ruptura de nível. Se o nível 7 (Núcleo Dourado) for o alvo, use
    ``formar_nucleo_dourado`` em vez disto — lá não há dado."""
    if nivel_atual < 0 or nivel_atual >= 13:
        raise ValueError("ruptura só se aplica entre os níveis 0 e 12")
    metodo = reino_de(nivel_atual).metodo
    if metodo != "rolagem":
        raise ValueError(
            f"o nível {nivel_atual} sai por '{metodo}': use "
            + ("formar_nucleo_dourado()" if metodo == "pontuacao" else
               "tribulacao_celestial()" if metodo == "tribulacao" else "nada")
        )
    aleat = aleat or Aleatoriedade()
    dd = dd_de_ruptura(nivel_atual, compatibilidade, lei)
    base = {
        "fengshui": "neutro", "densidade_qi": "comum", "elixir": "nenhum",
        "meditou": False,
    }
    base.update(dict(fatos or {}))
    decl = Declaracao(
        acao=f"romper para {reino_de(nivel_atual + 1).trilha}",
        ator=ator,
        atributo="int",
        valor_atributo=valor_de_int,
        bonus_atributo=(valor_de_int - 10) // 2,
        pericia="compreensao",
        graduacao=max(0, min(5, graduacao_de_compreensao)),
        dificuldade=dd,
        regras=tuple(regras),
        fatos=base,
        contexto={"reino": nivel_atual, "lei": lei.codigo,
                  "compatibilidade": compatibilidade},
    )
    res = resolver(decl, aleat, diario)
    if res.sucesso:
        return ResultadoDeRuptura(
            res, nivel_atual, nivel_atual + 1, True,
            f"ruptura bem-sucedida para {reino_de(nivel_atual + 1).trilha}",
            None,
        )
    # Falha: risco de Desvio de Qi proporcional à margem negativa.
    gravidade = "comum"
    if res.margem <= -10 or res.critico == "desvio":
        gravidade = "catastrofica"
    elif res.margem <= -5:
        gravidade = "grave"
    desvio = tabela_de_desvio_de_qi(aleat, gravidade)
    return ResultadoDeRuptura(
        res, nivel_atual, nivel_atual, False,
        f"ruptura falhou (gravidade {gravidade})", desvio,
    )


_RAIOS_POR_NIVEL: Dict[int, int] = {6: 0, 9: 3, 11: 4, 12: 9}


def raios_de_tribulacao(nivel: int, demoniaca: bool = False) -> int:
    """Quantos raios caem ao SAIR do nível informado.

    6 → Núcleo Dourado: só Leis demoníacas enfrentam o céu aqui (1 raio).
    9 → Alma Nascente: 3 raios.   11 → Espírito: 4 raios.
    12 → Ascensão: 9 raios, os Nove Trovões do Julgamento Celestial.
    Leis demoníacas sempre somam +1 raio: o céu cobra mais caro o atalho.
    """
    if nivel not in _RAIOS_POR_NIVEL:
        raise ValueError(
            f"o nível {nivel} não enfrenta tribulação (método "
            f"'{reino_de(nivel).metodo}')"
        )
    n = _RAIOS_POR_NIVEL[nivel] + (1 if demoniaca else 0)
    if n == 0:
        raise ValueError(
            "o nível 6 só convoca tribulação para Leis demoníacas"
        )
    return n


@dataclass(frozen=True)
class Raio:
    indice: int
    dificuldade: int
    resultado: Resultado
    absorvido_pelo_qi: int
    dano_na_vitalidade: int


@dataclass(frozen=True)
class Tribulacao:
    nivel: int
    raios: Tuple[Raio, ...]
    sobreviveu: bool
    ascendeu: bool
    vitalidade_restante: int
    qi_restante: int
    resumo_texto: str


def tribulacao_celestial(
    *,
    ator: str,
    nivel: int,
    demoniaca: bool,
    valor_de_con: int,
    graduacao_de_defesa: int,
    vitalidade: int,
    qi_atual: int,
    escudo_extra: int = 0,
    fatos: Optional[Mapping[str, Any]] = None,
    regras: Sequence[str] = ("RECURSO:ARTEFATO", "AMBIENTE:FORMACAO",
                             "RECURSO:ELIXIR", "REINO:SUPRESSAO",
                             "PREPARO:QUEIMA_LONGEVIDADE"),
    aleat: Optional[Aleatoriedade] = None,
    diario: Optional[DiarioDeAuditoria] = None,
) -> Tribulacao:
    """A Tribulação Celestial (天劫): o céu ataca quem desafia a ordem natural.

    Cada raio é uma Declaração comprometida e rolada pelo motor imparcial. O Qi
    funciona como escudo e é consumido antes da Vitalidade, exatamente como no
    ACS. Nenhum raio pode ser "perdoado" pela narrativa.
    """
    if reino_de(nivel).metodo != "tribulacao" and not (nivel == 6 and demoniaca):
        raise ValueError(
            f"o nível {nivel} não enfrenta tribulação celestial"
        )
    aleat = aleat or Aleatoriedade()
    n_raios = raios_de_tribulacao(nivel, demoniaca)
    if n_raios == 0:
        raise ValueError("nenhum raio previsto para este nível")

    # REINO:SUPRESSAO é sempre do ponto de vista de QUEM ROLA: aqui quem rola é
    # o cultivador, e o "oponente" é o próprio céu (um nível acima).
    base_fatos = {
        "artefato": "nenhum", "formacao": "nenhuma", "elixir": "nenhum",
        "anos_queimados": 0,
        "reino_atacante": nivel, "reino_alvo": nivel + 1,
    }
    base_fatos.update(dict(fatos or {}))

    raios: List[Raio] = []
    vit, qi = int(vitalidade), int(qi_atual)
    for k in range(1, n_raios + 1):
        dd = 14 + nivel + 2 * (k - 1)
        # Poder do raio: cresce com o reino e com a posição na sequência.
        # Calibrado para que UM raio falho seja sobrevivível e DOIS sejam fatais
        # — ou seja, a tribulação se vence com preparo, não com sorte.
        poder = 30 + 43 * nivel + 20 * (k - 1)
        decl = Declaracao(
            acao=f"resistir ao {k}º raio da tribulação (DD {dd})",
            ator=ator,
            atributo="con",
            valor_atributo=valor_de_con,
            bonus_atributo=(valor_de_con - 10) // 2,
            pericia="corpo_de_ferro",
            graduacao=max(0, min(5, graduacao_de_defesa)),
            dificuldade=dd,
            regras=tuple(regras),
            fatos=base_fatos,
            contexto={"reino": nivel, "raio": k, "poder": poder,
                      "escudo_extra": escudo_extra},
        )
        res = resolver(decl, aleat, diario)
        dano = 0 if res.sucesso else max(1, poder - res.total)
        absorvido = min(qi, dano)
        qi -= absorvido
        vit -= (dano - absorvido)
        raios.append(Raio(k, dd, res, absorvido, max(0, dano - absorvido)))
        if vit <= 0:
            break

    sobreviveu = vit > 0
    ascendeu = sobreviveu and nivel >= 12
    linhas = [
        f"Tribulação Celestial de {ator} — nível {nivel}, {n_raios} raios"
        + (" (Lei demoníaca)" if demoniaca else ""),
    ]
    for r in raios:
        linhas.append(
            f"  raio {r.indice}: DD {r.dificuldade} → {r.resultado.total} "
            f"({r.resultado.grau}) | Qi absorveu {r.absorvido_pelo_qi}, "
            f"Vitalidade perdeu {r.dano_na_vitalidade}"
        )
    linhas.append(
        f"  resultado: {'SOBREVIVEU' if sobreviveu else 'CORPO DESTRUÍDO'} — "
        f"Vitalidade {vit}, Qi {qi}"
        + (" | ASCENSÃO" if ascendeu else "")
    )
    return Tribulacao(nivel, tuple(raios), sobreviveu, ascendeu, vit, qi,
                      "\n".join(linhas))
