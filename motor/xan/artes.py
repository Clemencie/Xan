# -*- coding: utf-8 -*-
"""
XAN — Artes, Tesouros e Ofícios.
================================

Técnicas (武功), Artefatos (法器), Talismãs (符), Formações (陣法), Elixires (丹)
e Ervas Espirituais (靈草). Tudo com **custos e efeitos numéricos**, para que a
mesa resolva por regra e não por discussão.

Convenção de dano
-----------------
    Dano = dados da técnica
         + bônus do atributo de ataque
         + metade da margem de sucesso do golpe (arredondada para baixo)
         + escala de reino (nível × 4)

O Qi funciona como escudo e é consumido antes da Vitalidade.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .entropia import Aleatoriedade
from .dados import rolar

__all__ = [
    "Tecnica", "TECNICAS", "tecnica_de", "tecnicas_de_lei", "tecnicas_livres",
    "dano_de", "Artefato", "Talisma", "Formacao", "Elixir", "Erva",
    "ARTEFATOS", "TALISMAS", "FORMACOES", "ELIXIRES", "ERVAS",
    "GRAUS_DE_ARTEFATO", "sortear_tesouro", "ALCANCES",
]

TIPOS_DE_TECNICA = ("ataque", "defesa", "movimento", "cura", "util", "passiva",
                    "cultivo", "social")
ALCANCES = ("toque", "curto", "medio", "longo", "extremo", "pessoal")


@dataclass(frozen=True)
class Tecnica:
    codigo: str
    nome: str
    chines: str
    tipo: str
    lei: str                    # "livre" se qualquer um pode aprender
    nivel_minimo: int
    elemento: str
    custo_qi: int
    alcance: str
    dado_base: str              # ex.: "2d6"; vazio para técnicas sem dano
    pericia: str
    escalada: int               # dados extras a cada N níveis acima do mínimo
    cooldown: int
    efeitos: Tuple[str, ...]
    descricao: str
    ignora_supressao: bool = False

    def __post_init__(self) -> None:
        if self.tipo not in TIPOS_DE_TECNICA:
            raise ValueError(f"tipo de técnica inválido {self.tipo!r}")
        if self.alcance not in ALCANCES:
            raise ValueError(f"alcance inválido {self.alcance!r}")
        from .regras import ELEMENTOS_CANONICOS, ELEMENTOS_NEUTROS
        if self.elemento not in ELEMENTOS_CANONICOS + ELEMENTOS_NEUTROS:
            raise ValueError(f"elemento inválido {self.elemento!r}")
        if not (0 <= self.nivel_minimo <= 13):
            raise ValueError("nível mínimo fora de 0..13")
        if self.custo_qi < 0:
            raise ValueError("custo de Qi negativo")
        if self.cooldown < 0:
            raise ValueError("cooldown negativo")


TECNICAS: Dict[str, Tecnica] = {}


def _t(codigo, nome, chines, tipo, lei, nivel, elemento, custo, alcance,
       dado_base, pericia, escalada, cooldown, efeitos, descricao,
       ignora_supressao=False):
    if codigo in TECNICAS:
        raise ValueError(f"técnica {codigo} duplicada")
    t = Tecnica(codigo, nome, chines, tipo, lei, nivel, elemento, custo, alcance,
                dado_base, pericia, escalada, cooldown, tuple(efeitos), descricao,
                bool(ignora_supressao))
    TECNICAS[codigo] = t
    return t


# ==========================================================================
# Técnicas livres (qualquer cultivador pode aprendê-las)
# ==========================================================================
_t("LIVRE_CORTE_QI", "Corte de Qi", "氣斬", "ataque", "livre", 1, "nenhum", 5,
   "medio", "1d8", "espada", 1, 0, (),
   "O básico do básico: lança uma lâmina de Qi. Todo discípulo interno aprende.")
_t("LIVRE_PALMA_VENTANIA", "Palma da Ventania", "風掌", "ataque", "livre", 0,
   "nenhum", 0, "toque", "1d6", "punho", 1, 0, (),
   "Golpe de palma comum entre guerreiros de terceira classe.")
_t("LIVRE_PASSO_NUVEM", "Passo de Nuvem", "雲步", "movimento", "livre", 2,
   "nenhum", 8, "pessoal", "", "passos_leves", 0, 1,
   ("ativa ALVO:PASSOS_LEVES contra ataques por 1 rodada",
    "+3 m de salto por nível de cultivo"),
   "Qinggong básico: deslizar sobre telhados e água.")
_t("LIVRE_ESCUDO_QI", "Escudo de Qi", "氣護罩", "defesa", "livre", 2, "nenhum",
   15, "pessoal", "", "folego_interno", 0, 1,
   ("+2 de Defesa por rodada sustentada", "consome 5 Qi por rodada mantida"),
   "Condensa Qi em uma barreira fina. Frágil, mas salva vidas.")
_t("LIVRE_CIRCULACAO", "Circulação Menor", "小周天", "cultivo", "livre", 1,
   "nenhum", 0, "pessoal", "", "meditacao", 0, 0,
   ("recupera 1d6+CON Qi por hora de meditação",
    "+1 de estado mental por dia de prática contínua"),
   "O ciclo básico de Qi pelos meridianos. Base de tudo.")
_t("LIVRE_CIRCULACAO_MAIOR", "Circulação Maior", "大周天", "cultivo", "livre", 4,
   "nenhum", 0, "pessoal", "", "meditacao", 0, 0,
   ("recupera 2d6+CON Qi por hora", "concede +1 em tentativas de ruptura"),
   "O ciclo completo; exige os 12 meridianos abertos.")
_t("LIVRE_SENTIDO_QI", "Sentido de Qi", "氣感術", "util", "livre", 1, "nenhum",
   3, "pessoal", "", "percepcao_de_qi", 0, 0,
   ("revela o nível de cultivo de um alvo a até 30 m",
    "detecta veias espirituais e formações ocultas"),
   "Ver o Qi do mundo. Indispensável em qualquer negociação.")
_t("LIVRE_TRANSMISSAO_VOZ", "Transmissão de Voz", "傳音入密", "util", "livre", 4,
   "nenhum", 6, "longo", "", "percepcao_de_qi", 0, 0,
   ("fala com uma pessoa a distância sem que terceiros ouçam"),
   "Qi conduz o som direto ao ouvido alheio.")
_t("LIVRE_VOO", "Voo sobre Objeto", "御物飛行", "movimento", "livre", 6,
   "nenhum", 40, "pessoal", "", "meditacao", 0, 0,
   ("voo sustentado; consome 10 Qi por minuto",
    "velocidade = 100 m/rodada + 20 por nível acima de 6"),
   "Montar uma espada ou tesouro e voar. O marco do Transcendente.")
_t("LIVRE_CURA_INTERNA", "Cura Interna", "內療", "cura", "livre", 3, "madeira",
   25, "pessoal", "", "medicina", 0, 2,
   ("recupera 2d6+INT de Vitalidade", "remove 1 sangramento"),
   "Dirigir Qi para fechar as próprias feridas.")

# ==========================================================================
# Espada dos Sete Massacres (Metal)
# ==========================================================================
_t("SM_AURA_ESPADA", "Aura de Espada", "劍氣", "ataque", "SETE_MASSACRES", 5,
   "metal", 20, "longo", "3d8", "espada", 2, 1,
   ("corte à distância ignorando cobertura parcial"),
   "Qi de espada visível. O primeiro sinal de um mestre de verdade.")
_t("SM_FORCA_ESPADA", "Força de Espada", "劍罡", "ataque", "SETE_MASSACRES", 8,
   "metal", 60, "medio", "5d8", "espada", 3, 2,
   ("ignora 5 pontos de defesa", "corta formação de grau Terra"),
   "A lâmina ganha cor e substância. Fende colinas.")
_t("SM_SETE_CORTES", "Sete Cortes Encadeados", "七連斬", "ataque",
   "SETE_MASSACRES", 6, "metal", 45, "curto", "2d8", "espada", 1, 2,
   ("sete ataques na mesma rodada, cada um com −2 cumulativo",
    "cada acerto restaura 3 Qi"),
   "A técnica assinatura: sete golpes no tempo de um.")
_t("SM_ALMA_ESPADA", "Alma de Espada", "劍魂", "passiva", "SETE_MASSACRES", 11,
   "metal", 0, "pessoal", "", "espada", 0, 0,
   ("a espada ataca sozinha (Espada da Mente)",
    "+4 em todos os testes de espada", "imune a desarmar"),
   "A espada deixa de ser ferramenta e vira extensão da alma.",
   ignora_supressao=True)

# ==========================================================================
# Lei do Corte das Emoções (Fogo)
# ==========================================================================
_t("CE_OLHAR_ESQUECIDO", "Olhar Esquecido", "忘情眼", "social", "CORTE_EMOCOES",
   4, "fogo", 12, "medio", "", "intimidacao", 0, 2,
   ("o alvo faz teste de Vontade de Ferro ou perde a ação por 1 rodada",
    "não afeta quem ama o usuário"),
   "Um olhar sem nada dentro. Aterroriza porque não há o que apelar.")
_t("CE_GOLPE_SEM_APEGO", "Golpe sem Apego", "無情斬", "ataque",
   "CORTE_EMOCOES", 7, "fogo", 55, "curto", "4d10", "palma", 2, 2,
   ("+4 de dano contra alvos com disposição devoto ou amigavel"),
   "Mata sem hesitar. Quanto mais próximo o alvo, mais limpo o corte.",
   ignora_supressao=True)
_t("CE_CORACAO_SERENO", "Coração Sereno", "太上忘情", "passiva",
   "CORTE_EMOCOES", 9, "fogo", 0, "pessoal", "", "vontade_de_ferro", 0, 0,
   ("imune a Demônio Interior comum", "não pode ganhar laços novos",
    "estado mental nunca cai abaixo de 40"),
   "A paz absoluta — e o seu preço.")

# ==========================================================================
# Lei do Roubo Celestial (Terra)
# ==========================================================================
_t("RC_DRENAR_ESSENCIA", "Drenar Essência", "吸元", "ataque", "ROUBO_CELESTIAL",
   5, "terra", 0, "toque", "2d6", "palma", 1, 1,
   ("todo o dano causado vira Qi para o usuário",
    "alvos de nível maior que o usuário sofrem Desvio de Qi no 20 natural"),
   "Roubar o cultivo alheio. Odiada em todas as seitas ortodoxas.")
_t("RC_MAO_ROUBA_CEU", "Mão que Rouba o Céu", "偷天手", "util",
   "ROUBO_CELESTIAL", 8, "terra", 80, "medio", "", "prestidigitacao", 0, 3,
   ("troca a posição de dois objetos ou pessoas de tamanho similar",
    "pode trocar um golpe fatal por um objeto"),
   "Furta a própria causalidade por um instante.",
   ignora_supressao=True)
_t("RC_TROCAR_O_SOL", "Trocar o Sol", "換日", "util", "ROUBO_CELESTIAL", 11,
   "terra", 200, "longo", "", "estrategia", 0, 6,
   ("altera o clima da região por 1d4 horas",
    "custo: 10 anos de longevidade"),
   "Roubar o céu inteiro. O preço é a própria vida.")

# ==========================================================================
# Taiyi — as cinco elementais
# ==========================================================================
_t("GC_BUSSOLA", "Bússola do Grande Carro", "北斗盤", "util", "TAIYI_METAL", 4,
   "metal", 18, "pessoal", "", "astrologia", 0, 1,
   ("revela um fato verdadeiro sobre o destino de um alvo",
    "+2 em testes de Percepção contra ilusões"),
   "As sete estrelas apontam o que será.")
_t("GC_LAMINA_ESTELAR", "Lâmina Estelar", "星刃", "ataque", "TAIYI_METAL", 6,
   "metal", 35, "longo", "3d10", "espada", 2, 1,
   ("ignora cobertura total à noite"),
   "Sete lâminas de luz estelar orbitam o usuário.")
_t("SR_SELO_SEIS_ROTAS", "Selo das Seis Rotas", "六道印", "util",
   "TAIYI_MADEIRA", 7, "madeira", 70, "toque", "", "percepcao_de_qi", 0, 4,
   ("sela uma besta espiritual inconsciente em contrato",
    "a besta mantém o próprio nível de cultivo"),
   "Prende uma criatura numa das seis rotas do samsara.",
   ignora_supressao=True)
_t("SR_CORPO_QUE_RENASCE", "Corpo que Renasce", "輪迴身", "passiva",
   "TAIYI_MADEIRA", 10, "madeira", 0, "pessoal", "", "meditacao", 0, 0,
   ("uma vez por ano, sobrevive a dano que mataria",
    "custo: perde 1 nível de cultivo e todas as memórias do último mês"),
   "A morte como mais uma das seis rotas.")
_t("SP_PASSO_CIERNA", "Passo da Caverna", "洞天步", "movimento", "TAIYI_AGUA", 5,
   "agua", 25, "pessoal", "", "passos_leves", 0, 1,
   ("teletransporte de até 15 m para uma gruta já visitada",
    "+3 de Defesa até o próximo turno"),
   "As dezesseis grutas celestes são todas o mesmo lugar.")
_t("SP_MANTO_AGUA_PARADA", "Manto de Água Parada", "止水袍", "defesa",
   "TAIYI_AGUA", 6, "agua", 40, "pessoal", "", "folego_interno", 0, 2,
   ("absorve os próximos 30 pontos de dano", "reflete 1d6 de dano de fogo"),
   "Nada atravessa água completamente parada.")
_t("SV_CHAMA_SAMADI", "Chama Sâmadi", "三昧真火", "ataque", "TAIYI_FOGO", 7,
   "fogo", 65, "medio", "4d8", "palma", 2, 2,
   ("dano contínuo de 1d8 por 3 rodadas", "queima madeira e derrete metal"),
   "O fogo verdadeiro que forja artefatos e destrói demônios.")
_t("SV_CORPO_TRES_SOIS", "Corpo de Três Sóis", "三陽體", "passiva",
   "TAIYI_FOGO", 9, "fogo", 0, "pessoal", "", "corpo_de_ferro", 0, 0,
   ("+20% de Qi máximo", "imune a frio extremo", "+2 em forja e alquimia"),
   "Três sóis internos: um no dantian, um no coração, um na testa.")
_t("GR_PALMA_GIRASSOL", "Palma do Girassol", "葵花掌", "ataque",
   "TAIYI_TERRA", 5, "terra", 30, "curto", "3d6", "palma", 2, 1,
   ("+2 de acerto durante o dia"),
   "Doce e implacável, como tudo que cresce para a luz.")
_t("GR_REFINO_ESPIRITO", "Refino do Espírito", "煉神", "cultivo", "TAIYI_TERRA",
   6, "terra", 0, "pessoal", "", "meditacao", 0, 0,
   ("ganho de cultivo dobrado enquanto o estado mental estiver acima de 80"),
   "O espírito refinado puxa o Qi sozinho.")

# ==========================================================================
# Corpo (體修)
# ==========================================================================
_t("VD_PELE_BRONZE", "Pele de Bronze", "銅皮", "passiva", "VAJRA_DOURADO", 3,
   "metal", 0, "pessoal", "", "corpo_de_ferro", 0, 0,
   ("+3 de Defesa natural", "reduz em 2 todo dano de arma mortal"),
   "Primeira remodelagem: a carne endurece.")
_t("VD_SINO_DOURADO", "Sino Dourado", "金鐘罩", "defesa", "VAJRA_DOURADO", 6,
   "metal", 50, "pessoal", "", "corpo_de_ferro", 0, 3,
   ("imune a dano por 2 rodadas", "ao terminar, sofre metade do dano absorvido"),
   "O sino toca e nada entra.")
_t("DA_SANGUE_REFLORESCE", "Sangue que Refloresce", "回血", "passiva",
   "DRAGAO_AZUL", 5, "madeira", 0, "pessoal", "", "corpo_de_ferro", 0, 0,
   ("regenera 1d6 de Vitalidade por rodada", "regenera membros em 1d4 meses",
    "imune a venenos de grau Terra ou inferior"),
   "O corpo do dragão não aceita morrer.")
_t("TN_CARAPACA_NEGRA", "Carapaça Negra", "玄武甲", "defesa", "TARTARUGA_NEGRA",
   6, "agua", 45, "pessoal", "", "corpo_de_ferro", 0, 2,
   ("+8 de Defesa", "velocidade reduzida à metade"),
   "A tartaruga negra não vence: simplesmente não perde.")
_t("FC_ASA_BRASA", "Asa de Brasa", "朱雀翼", "movimento", "FENIX_CARMESIM", 7,
   "fogo", 60, "pessoal", "", "passos_leves", 0, 3,
   ("voo curto e +4 em iniciativa", "deixa um rastro que causa 1d6 de dano de fogo"),
   "Asas de fogo que queimam o próprio usuário.")
_t("MI_RAIZ_MONTANHA", "Raiz de Montanha", "山根", "defesa",
   "MONTANHA_INABALAVEL", 4, "terra", 25, "pessoal", "", "corpo_de_ferro", 0, 2,
   ("não pode ser movido, derrubado ou empurrado",
    "+6 de Defesa contra ataques corpo a corpo"),
   "Quem enraíza não cai.")

# ==========================================================================
# Marcial (murim)
# ==========================================================================
_t("AM_PETALA_CAI", "Pétala que Cai", "落梅", "ataque", "AMEIXEIRA", 2,
   "madeira", 8, "curto", "2d6", "espada", 1, 0,
   ("+2 de dano se o alvo estiver em movimento"),
   "Primeira forma do Monte Hua: leve, enganosa, certeira.")
_t("AM_VINTE_QUATRO", "Vinte e Quatro Formas", "二十四式", "ataque", "AMEIXEIRA",
   5, "madeira", 30, "curto", "3d6", "espada", 2, 1,
   ("três ataques na mesma rodada com −1 cumulativo"),
   "A sequência completa: uma tempestade de pétalas de aço.")
_t("PT_CIRCULO_DEVOLVE", "Círculo que Devolve", "太極圈", "defesa", "PALMA_TAIJI",
   3, "agua", 12, "toque", "", "palma", 0, 1,
   ("redireciona um ataque corpo a corpo contra outro alvo adjacente",
    "o novo alvo é escolhido pelo dado de posição, não pelo jogador"),
   "Wudang: a força do inimigo é o seu próprio castigo.")
_t("PT_PASSO_NUVENS_WD", "Passo das Nuvens", "雲縱", "movimento", "PALMA_TAIJI",
   4, "agua", 15, "pessoal", "", "passos_leves", 0, 1,
   ("+4 de Defesa por 1 rodada", "movimento sem som"),
   "Andar como quem pisa nuvem.")
_t("PV_DEZOITO_MAOS", "Dezoito Mãos de Arhat", "羅漢十八手", "ataque",
   "PUNHO_VAJRA", 2, "metal", 6, "toque", "2d8", "punho", 1, 0,
   ("+1 de dano cumulativo a cada rodada do mesmo combate (máx. +5)"),
   "Shaolin: simples, honesto, devastador.")
_t("PV_GRITO_LEAO", "Grito do Leão", "獅吼功", "util", "PUNHO_VAJRA", 6, "metal",
   35, "medio", "", "intimidacao", 0, 3,
   ("todos em 10 m fazem teste de Vontade de Ferro ou ficam atordoados 1 rodada",
    "quebra ilusões e possessões"),
   "O rugido que limpa a mente e rompe feitiços.")
_t("AT_CHUVA_AGULHAS", "Chuva de Agulhas", "暴雨梨花針", "ataque",
   "AGULHAS_TANG", 3, "metal", 10, "medio", "2d6", "arma_oculta", 1, 1,
   ("alvo sofre 1d4 de dano de veneno por rodada por 3 rodadas",
    "ignora 4 pontos de Defesa de armadura"),
   "Clã Tang: mil agulhas de uma vez. Ninguém sobrevive de frente.")
_t("AT_SOPRO_ENVENENADO", "Sopro Envenenado", "毒霧", "ataque", "AGULHAS_TANG",
   5, "metal", 25, "curto", "1d6", "arma_oculta", 1, 3,
   ("nuvem de 6 m: teste de Resistência a Veneno ou −2 em tudo por 1 hora"),
   "O ar vira arma.")
_t("FZ_PORTA_ESTRANHA", "Porta Estranha", "奇門遁甲", "util", "FORMACOES_ZHUGE",
   4, "terra", 30, "medio", "", "formacoes", 0, 2,
   ("monta uma formação menor em 1 rodada em vez de 10 minutos",
    "+2 em todos os testes de formação"),
   "Os oito portões se abrem onde o estrategista quiser.")
_t("CM_CAJADO_CAES", "Cajado que Bate no Cão", "打狗棒", "ataque",
   "CAJADO_MENDIGO", 1, "madeira", 4, "curto", "1d10", "cajado", 1, 0,
   ("+2 contra alvos de nível superior"),
   "A técnica secreta do chefe dos mendigos: humilha mestres.")
_t("PD_PALMA_DRAGAO", "Palma do Dragão", "龍掌", "ataque", "PALMA_DRAGAO_PENG",
   3, "fogo", 15, "toque", "2d10", "punho", 1, 0,
   ("derruba o alvo em 1 rodada se falhar em Corpo de Ferro"),
   "Hebei Peng: força externa pura.")
_t("DC_CHAMA_DEMONIO", "Chama do Demônio Celestial", "天魔火", "ataque",
   "DEMONIO_CELESTIAL", 4, "fogo", 20, "medio", "3d6", "palma", 2, 1,
   ("dano contínuo 1d6 por 2 rodadas",
    "cada uso reduz o estado mental em 3"),
   "A chama sagrada do culto. Queima o inimigo e o usuário.")
_t("DC_GARRA_SANGUE", "Garra de Sangue", "血爪", "ataque", "DEMONIO_CELESTIAL",
   6, "fogo", 35, "curto", "3d8", "punho", 2, 1,
   ("cura o usuário em metade do dano causado",
    "reduz o estado mental em 5"),
   "Bebe a vida alheia. O Culto ensina que isto é misericórdia.")
_t("SS_SEDE_SETE_ESTRELAS", "Sede das Sete Estrelas", "七殺渴", "ataque",
   "SANGUE_SETE_ESTRELAS", 5, "agua", 30, "toque", "2d10", "arma_oculta", 1, 1,
   ("+1 cumulativo de dano para cada pessoa morta pelo usuário hoje (máx. +10)",
    "risco de Desvio de Qi em caso de 1 natural"),
   "A seita não-ortodoxa que cultiva matando.")
_t("SS_PASSO_SOMBRA", "Passo de Sombra", "影步", "movimento",
   "SANGUE_SETE_ESTRELAS", 3, "agua", 12, "pessoal", "", "furtividade", 0, 1,
   ("invisível enquanto não atacar", "+4 no primeiro ataque após se ocultar"),
   "Sumir no canto do olho.")

# ==========================================================================
# Shendao — milagres
# ==========================================================================
_t("SD_MILAGRE_TROVAO", "Milagre do Trovão", "雷神跡", "ataque",
   "TROVAO_CELESTIAL", 6, "metal", 0, "longo", "4d6", "lideranca", 2, 3,
   ("custa 30 de Fé em vez de Qi", "alvos com disposição hostil sofrem +4"),
   "O deus julga através da mão do fiel.")
_t("SD_JULGAMENTO", "Julgamento", "審判", "social", "TROVAO_CELESTIAL", 8,
   "metal", 0, "medio", "", "intimidacao", 0, 4,
   ("revela publicamente uma culpa real do alvo",
    "custa 60 de Fé; se o alvo for inocente, o usuário perde 20 de Fé"),
   "Nenhum segredo sobrevive ao tribunal do céu.",
   ignora_supressao=True)
_t("SD_TRONO_MENOR", "Trono Menor", "小神座", "util", "OITO_CEUS", 9, "nenhum", 0,
   "pessoal", "", "lideranca", 0, 6,
   ("cria um estado do Reino Divino", "cada estado concede um milagre menor",
    "custa 100 de Fé e um assentamento de fiéis"),
   "O primeiro degrau da divindade.")
_t("SD_BARCO_MORTOS", "Barco dos Mortos", "幽冥船", "cura",
   "SALVACAO_SUBMUNDO", 7, "nenhum", 0, "toque", "", "medicina", 0, 4,
   ("remove obsessões e Demônios Interiores de terceiros",
    "custa 50 de Fé; o alvo pode morrer se o demônio resistir"),
   "Levar a alma embora antes que ela apodreça.")


# ==========================================================================
# Alquimia Primordial (九轉金丹直指, Fogo)
# ==========================================================================
_t("AP_FORNALHA_INTERNA", "Fornalha Interna", "內爐", "cultivo",
   "ALQUIMIA_PRIMORDIAL", 4, "fogo", 20, "pessoal", "", "alquimia", 0, 0,
   ("+4 em testes de Alquimia", "refina elixires sem caldeirão físico",
    "consome 20 Qi por virada"),
   "O dantian vira fornalha. Onde estiver, há um forno.")
_t("AP_CHAMA_DA_FORNALHA", "Chama da Fornalha", "爐火", "ataque",
   "ALQUIMIA_PRIMORDIAL", 5, "fogo", 30, "medio", "3d8", "palma", 2, 1,
   ("derrete armaduras de grau mortal ou terra",
    "dano contínuo 1d6 por 2 rodadas"),
   "O mesmo fogo que refina ouro também refina carne.")
_t("AP_NOVE_VIRADAS", "Nove Viragens do Elixir", "九轉", "util",
   "ALQUIMIA_PRIMORDIAL", 7, "fogo", 90, "pessoal", "", "alquimia", 0, 4,
   ("eleva em um subgrau qualquer elixir refinado nesta sessão",
    "cada virada exige uma erva do grau correspondente"),
   "Nove vezes o mesmo elixir: na nona, ele muda de natureza.")
_t("AP_DEDO_DE_OURO", "Dedo de Ouro", "金指", "ataque",
   "ALQUIMIA_PRIMORDIAL", 8, "fogo", 70, "toque", "4d10", "palma", 2, 3,
   ("ou refina o alvo (dano) ou refina o aliado (cura o mesmo valor)",
    "a escolha é declarada ANTES do ataque e registrada"),
   "O dedo que decide o que uma coisa vai virar.")

# ==========================================================================
# Mil Artefatos (己寅九衝多寶真解, Madeira)
# ==========================================================================
_t("MA_TESOURO_VOADOR", "Tesouro Voador", "御寶", "ataque", "MIL_ARTEFATOS", 5,
   "madeira", 25, "longo", "3d8", "forja_de_artefatos", 2, 1,
   ("usa o poder do artefato como bônus de dano",
    "pode atacar dois alvos distintos na mesma rodada"),
   "O artefato luta sozinho, obedecendo à vontade do dono.")
_t("MA_VINCULO_DE_ARTEFATO", "Vínculo de Artefato", "煉寶", "util",
   "MIL_ARTEFATOS", 4, "madeira", 40, "toque", "", "forja_de_artefatos", 0, 4,
   ("liga permanentemente um artefato à Alma",
    "+1 de poder enquanto o vínculo durar; o artefato volta à mão se perdido"),
   "Sangue, Qi e intenção: o tesouro passa a conhecer o dono.")
_t("MA_CHUVA_DE_LAMINAS", "Chuva de Lâminas", "萬刃雨", "ataque",
   "MIL_ARTEFATOS", 8, "madeira", 90, "longo", "6d6", "forja_de_artefatos", 3, 3,
   ("área de 20 m; todos os alvos são atingidos",
    "exige pelo menos 12 lâminas vinculadas"),
   "Mil lâminas no céu, mil mortes no chão.")
_t("MA_MURALHA_DE_TESOUROS", "Muralha de Tesouros", "寶牆", "defesa",
   "MIL_ARTEFATOS", 6, "madeira", 60, "pessoal", "", "forja_de_artefatos", 0, 2,
   ("+8 de Defesa por 2 rodadas", "absorve 40 de dano antes de quebrar"),
   "Cem artefatos girando em volta como uma armadura viva.")

# ==========================================================================
# Pureza de Jade (玉清仙法, sem elemento)
# ==========================================================================
_t("PJ_SOPRO_DE_JADE", "Sopro de Jade", "玉清氣", "cura", "PUREZA_JADE", 3,
   "nenhum", 25, "toque", "", "medicina", 0, 1,
   ("cura 3d6 de Vitalidade", "remove um veneno ou doença de grau Terra"),
   "O sopro ortodoxo: limpa o que entrou errado no corpo.")
_t("PJ_MANTO_PURO", "Manto Puro", "淨衣", "defesa", "PUREZA_JADE", 5, "nenhum",
   35, "pessoal", "", "vontade_de_ferro", 0, 1,
   ("+6 de Defesa", "imune a corrupção, posse e maldições de grau inferior"),
   "Nada impuro toca quem se veste de vazio.")
_t("PJ_ESCADA_DE_NUVENS", "Escada de Nuvens", "雲梯", "movimento", "PUREZA_JADE",
   6, "nenhum", 30, "pessoal", "", "passos_leves", 0, 1,
   ("voo sereno sem gasto adicional por rodada",
    "+2 em testes de Equilíbrio e Passos Leves"),
   "Subir como quem sobe uma escada que só ele vê.")
_t("PJ_LUZ_DE_YUQING", "Luz de Yuqing", "玉清光", "ataque", "PUREZA_JADE", 9,
   "nenhum", 100, "longo", "5d8", "palma", 3, 3,
   ("+6 de dano contra demônios, mortos-vivos e corrompidos",
    "ilumina 1 km e desfaz ilusões"),
   "A luz do palácio mais alto do céu. Não julga: apenas existe.",
   ignora_supressao=True)

# ==========================================================================
# Símbolos Primordiais (太元五符元籙, sem elemento)
# ==========================================================================
_t("SMP_TALISMA_NATAL", "Cinco Talismãs Natais", "五本命符", "passiva",
   "SIMBOLOS_PRIMORDIAIS", 7, "nenhum", 0, "pessoal", "", "talismas", 0, 0,
   ("condensa cinco talismãs natais na ruptura",
    "cada talismã natal concede um efeito permanente de grau Céu"),
   "A ruptura vira oficina: o corpo sai tatuado de poder.")
_t("SMP_SELO_DE_PARTIDA", "Selo de Partida", "遁符", "movimento",
   "SIMBOLOS_PRIMORDIAIS", 4, "nenhum", 20, "pessoal", "", "talismas", 0, 2,
   ("teletransporte para qualquer selo marcado anteriormente",
    "sem limite de distância, mas o selo é consumido"),
   "Ir embora antes de chegar a estar em perigo.")
_t("SMP_BARREIRA_DE_NUVEM", "Barreira de Nuvem", "雲障", "defesa",
   "SIMBOLOS_PRIMORDIAIS", 5, "nenhum", 45, "medio", "", "talismas", 0, 2,
   ("barreira de Qi 60 cobrindo 6 m", "dura até ser rompida"),
   "Um desenho no ar que o mundo respeita.")
_t("SMP_SELO_DIVINO", "Selo da Residência Divina", "神居籙", "util",
   "SIMBOLOS_PRIMORDIAIS", 10, "nenhum", 150, "longo", "", "talismas", 0, 6,
   ("prende um alvo de nível até 12 por 1d4 dias",
    "o alvo pode romper com teste de Vontade de Ferro DD 30"),
   "O selo que os imortais usavam para guardar monstros.",
   ignora_supressao=True)

# ==========================================================================
# Conquista do Nimbo (雲霄征伐律, sem elemento)
# ==========================================================================
_t("CN_NIMBO_SUBJUGADO", "Nimbo Subjugado", "伏雲", "ataque", "CONQUISTA_NIMBO",
   5, "nenhum", 30, "medio", "3d8", "palma", 2, 1,
   ("nuvem sólida esmaga o alvo; derruba se falhar em Corpo de Ferro",
    "+2 de dano durante tempestades"),
   "As nuvens obedecem a quem já conquistou uma.")
_t("CN_MARCHA_DAS_NUVENS", "Marcha das Nuvens", "雲行", "movimento",
   "CONQUISTA_NIMBO", 4, "nenhum", 20, "pessoal", "", "passos_leves", 0, 1,
   ("deslocamento dobrado", "pode caminhar sobre ar e água"),
   "Marchar como quem tem o céu por estrada.")
_t("CN_DECRETO_DE_CONQUISTA", "Decreto de Conquista", "征伐令", "social",
   "CONQUISTA_NIMBO", 8, "nenhum", 80, "longo", "", "lideranca", 0, 6,
   ("assume o comando de uma formação inimiga por 1d4 rodadas",
    "exige que o usuário supere o nível do mestre da formação"),
   "Um decreto que os céus alheios obedecem.")
_t("CN_NUCLEO_YIN_YANG", "Núcleo Yin-Yang", "陰陽核", "passiva",
   "CONQUISTA_NIMBO", 9, "nenhum", 0, "pessoal", "", "meditacao", 0, 0,
   ("dois núcleos: um Yin e um Yang",
    "troca de polaridade uma vez por combate, invertendo vantagens elementais"),
   "A polaridade da ruptura decide qual núcleo nasce primeiro.")


def tecnica_de(codigo: str) -> Tecnica:
    if codigo not in TECNICAS:
        raise ValueError(f"técnica {codigo!r} não existe ({len(TECNICAS)} publicadas)")
    return TECNICAS[codigo]


def tecnicas_de_lei(lei: str) -> Tuple[Tecnica, ...]:
    return tuple(t for t in TECNICAS.values() if t.lei == lei)


def tecnicas_livres(nivel_maximo: int = 13) -> Tuple[Tecnica, ...]:
    return tuple(t for t in TECNICAS.values()
                 if t.lei == "livre" and t.nivel_minimo <= nivel_maximo)


def dano_de(
    tecnica: Tecnica,
    nivel: int,
    bonus_atributo: int,
    margem: int,
    aleat: Aleatoriedade,
) -> Tuple[int, str]:
    """Dano final. Retorna (valor, descrição da conta)."""
    if not tecnica.dado_base:
        return 0, "técnica sem dano direto"
    passos = max(0, (nivel - tecnica.nivel_minimo) // 3)
    extras = passos * tecnica.escalada
    expressao = tecnica.dado_base
    if extras:
        expressao += f"+{extras}d{int(tecnica.dado_base.split('d')[1])}"
    r = rolar(expressao, aleat)
    escala = nivel * 4
    margem_bonus = max(0, margem) // 2
    total = r.total + int(bonus_atributo) + margem_bonus + escala
    conta = (f"{expressao}={r.total} + attr{bonus_atributo:+d} "
             f"+ margem/2 {margem_bonus:+d} + escala de reino {escala:+d} = {total}")
    return max(0, total), conta


# ==========================================================================
# Tesouros
# ==========================================================================
GRAUS_DE_ARTEFATO: Tuple[str, ...] = ("mortal", "terra", "ceu", "primordial")
SUBGRAUS: Tuple[str, ...] = ("baixo", "medio", "alto")


@dataclass(frozen=True)
class Artefato:
    codigo: str
    nome: str
    chines: str
    grau: str
    subgrau: str
    tipo: str                  # arma | armadura | tesouro_voador | selo | adorno
    elemento: str
    poder: int                 # bônus inteiro aplicável
    vinculo: bool              # exige ligação de sangue/Alma Nascente
    descricao: str

    def __post_init__(self) -> None:
        if self.grau not in GRAUS_DE_ARTEFATO:
            raise ValueError(f"grau de artefato inválido {self.grau!r}")
        if self.subgrau not in SUBGRAUS:
            raise ValueError(f"subgrau inválido {self.subgrau!r}")
        if not isinstance(self.poder, int):
            raise TypeError("poder deve ser int")


ARTEFATOS: Tuple[Artefato, ...] = (
    Artefato("ESPADA_COMUM", "Espada de Aço Comum", "凡鐵劍", "mortal", "medio",
             "arma", "metal", 0, False, "Bem feita, sem Qi. Quebra contra um mestre."),
    Artefato("SABRE_TIGRE", "Sabre do Tigre Faminto", "餓虎刀", "mortal", "alto",
             "arma", "metal", 1, False, "Aço dobrado mil vezes pelo Clã Peng."),
    Artefato("VESTES_SEDA_FERRO", "Vestes de Seda de Ferro", "鐵布衫", "mortal",
             "alto", "armadura", "metal", 1, False, "Tecidas com fio de casulo espiritual."),
    Artefato("ANEL_ESPIRITO_BAIXO", "Anel de Espírito Inferior", "儲物戒", "terra",
             "baixo", "adorno", "nenhum", 1, False,
             "Espaço dimensional de 10 m³. Todo cultivador quer um."),
    Artefato("ESPADA_GELO_ETERN", "Espada do Gelo Eterno", "寒冰劍", "terra",
             "medio", "arma", "agua", 2, False,
             "Lâmina que nunca esquenta; congela feridas e impede sangramento."),
    Artefato("TALISMA_NATAL", "Talismã Natal Condensado", "本命符", "terra",
             "alto", "selo", "nenhum", 2, True,
             "Condensado na ruptura; quebra se o dono morrer."),
    Artefato("LANCA_DRAGAO_NEGRO", "Lança do Dragão Negro", "黑龍槍", "terra",
             "alto", "arma", "agua", 3, False, "Pesada como maré. Exige CON 16."),
    Artefato("SINO_MOSTEIRO", "Sino do Mosteiro Silencioso", "寂鐘", "terra",
             "medio", "tesouro_voador", "metal", 2, False,
             "Voa e ataca sozinho; o som quebra ilusões."),
    Artefato("ESPADA_SETE_ESTRELAS", "Espada das Sete Estrelas", "七星劍", "ceu",
             "baixo", "arma", "metal", 4, True,
             "Lâmina do Carro do Norte. Corta formação de grau Céu."),
    Artefato("CALDEIRAO_NOVE_VIRADAS", "Caldeirão das Nove Viradas", "九轉鼎",
             "ceu", "medio", "adorno", "fogo", 4, True,
             "Fornalha portátil; +4 em Alquimia e dobra o rendimento."),
    Artefato("CARROÇA_NIMBO", "Carruagem de Nimbo", "雲車", "ceu", "baixo",
             "tesouro_voador", "agua", 3, False,
             "Voo a 500 m/rodada e abrigo contra intempéries."),
    Artefato("SELO_CEU_TERRA", "Selo que Prende Céu e Terra", "天地印", "ceu",
             "alto", "selo", "terra", 5, True,
             "Imobiliza um alvo de nível até 2 acima do usuário."),
    Artefato("ESPELHO_KARMA", "Espelho do Karma", "業鏡", "ceu", "alto", "adorno",
             "nenhum", 5, True,
             "Mostra a verdadeira forma e as culpas de quem olha."),
    Artefato("PEROLA_MAR_EAST", "Pérola do Mar Leste", "東海珠", "primordial",
             "baixo", "adorno", "agua", 7, True,
             "Contém um mar. Dizem que foi o olho de um dragão ancestral."),
    Artefato("LAMPADA_ALMA", "Lâmpada da Alma Eterna", "魂燈", "primordial",
             "medio", "selo", "fogo", 8, True,
             "Enquanto arder, o dono não morre definitivamente."),
    Artefato("ESPADA_TAIYI", "Espada de Taiyi", "太一劍", "primordial", "alto",
             "arma", "nenhum", 10, True,
             "A lâmina que cortou o caos. Só aceita quem tem Núcleo grau 1."),
)


@dataclass(frozen=True)
class Talisma:
    codigo: str
    nome: str
    chines: str
    grau: str
    efeito: str
    duracao: str
    uso_unico: bool
    dd_de_criacao: int


TALISMAS: Tuple[Talisma, ...] = (
    Talisma("TAL_SOMBRA_PARTIDA", "Talismã da Sombra que Parte", "遁影符",
            "terra", "Teletransporte de até 30 m", "instantâneo", True, 16),
    Talisma("TAL_CORACAO_TRANQUILO", "Talismã do Coração Tranquilo", "静心符",
            "terra", "+20 de estado mental; suprime Demônio Interior por 1 dia",
            "1 dia", True, 14),
    Talisma("TAL_ARMADURA_ESCURA", "Talismã de Armadura Escura", "暗甲符",
            "terra", "+4 de Defesa", "1 hora", True, 18),
    Talisma("TAL_ESPADA_AFIADA", "Talismã da Espada Afiada", "利劍符",
            "terra", "+2 de dano em arma", "1 combate", True, 18),
    Talisma("TAL_MALDICAO_VIL", "Talismã da Maldição Vil", "邪咒符",
            "terra", "−2 em todos os testes do alvo", "1 dia", True, 20),
    Talisma("TAL_CORACAO_CELESTE", "Talismã do Coração Celeste", "天心符",
            "ceu", "Anula um ataque fatal", "instantâneo", True, 28),
    Talisma("TAL_RESIDENCIA_DIVINA", "Talismã da Residência Divina", "神居符",
            "ceu", "Cria um refúgio extradimensional por 12 horas", "12 horas",
            True, 30),
    Talisma("TAL_PERCEPCAO_DIVINA", "Talismã da Percepção Divina", "神感符",
            "ceu", "Enxerga através de qualquer ilusão de grau Céu", "1 hora",
            True, 30),
    Talisma("TAL_VEU_CELESTE", "Talismã Véu-do-Céu", "遮天符", "primordial",
            "Oculta o usuário até de adivinhação divina", "1 dia", True, 38),
    Talisma("TAL_LATENTE", "Talismã Latente", "潛符", "primordial",
            "Esconde uma pessoa ou objeto do destino por um ano", "1 ano", True,
            40),
)


@dataclass(frozen=True)
class Formacao:
    codigo: str
    nome: str
    chines: str
    grau: str
    nucleos: int               # quantos cultivadores/objetos sustentam
    nivel_minimo_do_nucleo: int
    efeito: str
    dd_de_montagem: int
    dd_de_rompimento: int


FORMACOES: Tuple[Formacao, ...] = (
    Formacao("FOR_CERCO_MENOR", "Cerco Menor dos Cinco Elementos", "小五行陣",
             "terra", 5, 2, "Impede saída e −2 em testes de quem está dentro",
             16, 18),
    Formacao("FOR_BARREIRA_SEITA", "Barreira da Seita", "護山大陣", "ceu", 9, 7,
             "Escudo de Qi 500 sobre toda a montanha; alerta invasores", 28, 34),
    Formacao("FOR_OITO_TRIGRAMAS", "Matriz dos Oito Trigramas", "八卦陣", "terra",
             8, 3, "Desorienta: quem entra perde a noção de direção", 20, 22),
    Formacao("FOR_ESPADA_SETENTAS", "Matriz das Setenta e Duas Espadas",
             "七十二劍陣", "ceu", 12, 6,
             "72 lâminas atacam em conjunto: dano 8d10 por rodada", 30, 32),
    Formacao("FOR_REUNIAO_QI", "Reunião de Qi", "聚靈陣", "terra", 4, 1,
             "Duplica a densidade de Qi do local para cultivo", 14, 12),
    Formacao("FOR_SELAMENTO_ETERN", "Selamento Eterno", "永封陣", "primordial",
             18, 10, "Prende um ser de nível até 13 indefinidamente", 40, 42),
    Formacao("FOR_ILUSAO_NEVOA", "Ilusão da Névoa Sonhadora", "迷霧幻陣",
             "terra", 6, 4, "Cria ilusões sensoriais completas", 18, 20),
)


@dataclass(frozen=True)
class Elixir:
    codigo: str
    nome: str
    chines: str
    grau: str
    efeito: str
    permanente: bool
    dd_de_refino: int
    nivel_minimo_do_alquimista: int
    erva_principal: str


ERVAS_NOMES: Tuple[str, ...] = (
    "Erva-do-Ouro Líquido", "Flor de Lótus de Nove Pétalas",
    "Ginseng de Mil Anos", "Raiz de Dragão Adormecido",
    "Cogumelo da Nuvem Roxa", "Fruto da Árvore do Samsara",
    "Musgo do Poço Gelado", "Cipó que Chora Sangue",
    "Semente de Fogo Solar", "Folha de Prata Lunar",
)


@dataclass(frozen=True)
class Erva:
    nome: str
    elemento: str
    grau: str
    idade_minima: int
    habitat: str


ERVAS: Tuple[Erva, ...] = (
    Erva("Erva-do-Ouro Líquido", "metal", "terra", 50, "veias de minério"),
    Erva("Flor de Lótus de Nove Pétalas", "agua", "ceu", 300, "lagos espirituais"),
    Erva("Ginseng de Mil Anos", "madeira", "ceu", 1000, "florestas antigas"),
    Erva("Raiz de Dragão Adormecido", "terra", "terra", 200, "encostas de veia"),
    Erva("Cogumelo da Nuvem Roxa", "fogo", "terra", 80, "altitudes nebulosas"),
    Erva("Fruto da Árvore do Samsara", "nenhum", "primordial", 3000,
         "árvores espirituais"),
    Erva("Musgo do Poço Gelado", "agua", "mortal", 20, "cavernas úmidas"),
    Erva("Cipó que Chora Sangue", "madeira", "terra", 150, "campos de batalha"),
    Erva("Semente de Fogo Solar", "fogo", "ceu", 500, "vulcões e terras de fogo"),
    Erva("Folha de Prata Lunar", "metal", "terra", 120, "picos acima das nuvens"),
)


ELIXIRES: Tuple[Elixir, ...] = (
    Elixir("ELI_CULTIVO_MENOR", "Pílula de Cultivo Menor", "小丹", "mortal",
           "+200 pontos de cultivo", False, 12, 1, "Musgo do Poço Gelado"),
    Elixir("ELI_BASE_ETERN", "Pílula de Fundação Eterna", "永基丹", "terra",
           "+2 na próxima rolagem de ruptura", False, 18, 4,
           "Cogumelo da Nuvem Roxa"),
    Elixir("ELI_NUCLEO_DOURADO", "Pílula do Núcleo Dourado", "金丹", "ceu",
           "+9 pontos na formação do Núcleo Dourado", False, 26, 6,
           "Flor de Lótus de Nove Pétalas"),
    Elixir("ELI_ALMA_NASCENTE", "Pílula da Alma Nascente", "元嬰丹", "ceu",
           "+1 nível de cultivo imediato (sem tribulação até o nível 9)", False,
           30, 9, "Ginseng de Mil Anos"),
    Elixir("ELI_LONGEVIDADE", "Pílula da Longevidade", "延壽丹", "primordial",
           "+300 anos de vida", True, 36, 10, "Semente de Fogo Solar"),
    Elixir("ELI_ETERNIDADE", "Pílula da Eternidade", "永恆丹", "primordial",
           "+10% permanente em todos os atributos e +500 de Vitalidade máxima",
           True, 42, 12, "Fruto da Árvore do Samsara"),
    Elixir("ELI_FLAGELO", "Pílula do Flagelo", "劫丹", "ceu",
           "+10% permanente em todos os atributos, −60 de Vitalidade máxima",
           True, 34, 9, "Cipó que Chora Sangue"),
    Elixir("ELI_CURA_NOVE_VIRADAS", "Pílula das Nove Viragens", "九轉還丹", "ceu",
           "Restaura toda a Vitalidade e remove um veneno", False, 28, 7,
           "Raiz de Dragão Adormecido"),
    Elixir("ELI_MENTE_QUIETA", "Pílula da Mente Quieta", "定心丹", "terra",
           "+40 de estado mental e remove um Demônio Interior menor", False, 16,
           3, "Erva-do-Ouro Líquido"),
)


# --------------------------------------------------------------------------
# Tesouros: sorteio ponderado por nível (todas as probabilidades são inteiras)
# --------------------------------------------------------------------------
def _peso_de_grau_pelo_nivel(grau: str, nivel: int) -> int:
    """Peso inteiro de cada grau de tesouro conforme o nível do local."""
    tabela = {
        "mortal":     (60, 45, 30, 18, 10, 5, 2, 1, 0, 0, 0, 0, 0, 0),
        "terra":      (35, 45, 55, 55, 45, 32, 20, 12, 6, 3, 1, 0, 0, 0),
        "ceu":        ( 4,  9, 14, 24, 38, 50, 60, 65, 55, 40, 25, 12, 5, 2),
        "primordial": ( 0,  0,  0,  1,  2,  4,  8, 14, 25, 40, 55, 70, 80, 90),
    }[grau]
    return tabela[max(0, min(13, nivel))]


def sortear_tesouro(
    aleat: Aleatoriedade,
    nivel_do_local: int,
    *,
    sorte: int = 10,
    tipo: Optional[str] = None,
) -> Tuple[str, Artefato | Talisma | Elixir | None, int]:
    """Sorteia um tesouro. Retorna (categoria, objeto, quantidade de pedras).

    ``sorte`` desloca o peso dos graus superiores — é um atributo de ficha,
    declarado antes, igual para todos.
    """
    if not (0 <= nivel_do_local <= 13):
        raise ValueError("nível do local fora de 0..13")
    fator = max(10, 100 + (int(sorte) - 10) * 4)
    pesos = {g: _peso_de_grau_pelo_nivel(g, nivel_do_local)
             for g in GRAUS_DE_ARTEFATO}
    pesos["ceu"] = pesos["ceu"] * fator // 100
    pesos["primordial"] = pesos["primordial"] * fator // 100
    pesos = {k: v for k, v in pesos.items() if v > 0}
    grau = aleat.escolher_ponderado(sorted(pesos), [pesos[k] for k in sorted(pesos)])

    subgrau = aleat.escolher(SUBGRAUS)
    pedras = _pedras_espirituais(aleat, nivel_do_local, sorte)

    # Subgrau afeta apenas o VALOR em pedras espirituais, nunca o objeto.
    pedras = max(1, pedras * {"baixo": 1, "medio": 3, "alto": 8}[subgrau] // 3)

    if aleat.abaixo(100) < 35:
        tal = [t for t in TALISMAS if t.grau == grau]
        if tal:
            return "talisma", aleat.escolher(tal), pedras
    if aleat.abaixo(100) < 25:
        eli = [e for e in ELIXIRES if e.grau == grau]
        if eli:
            return "elixir", aleat.escolher(eli), pedras
    candidatos: List[Any] = [a for a in ARTEFATOS if a.grau == grau
                             and (tipo is None or a.tipo == tipo)]
    if not candidatos:
        candidatos = [a for a in ARTEFATOS if a.grau == grau]
    if not candidatos:
        return "pedras", None, pedras
    return "artefato", aleat.escolher(candidatos), pedras


_PEDRAS_POR_NIVEL: Tuple[int, ...] = (
    5, 15, 40, 100, 250, 600, 1500, 4000, 10000, 25000, 60000, 150000, 400000,
    1000000,
)


def _pedras_espirituais(aleat: Aleatoriedade, nivel: int, sorte: int) -> int:
    base = _PEDRAS_POR_NIVEL[max(0, min(13, nivel))]
    # 3d6-3 dá uma cauda longa e justa, sem float
    fator = rolar("3d6", aleat).total - 3      # 0..15
    bonus = max(0, (int(sorte) - 10) // 2)
    return max(1, base * (1 + fator // 5) + bonus * base // 10)
