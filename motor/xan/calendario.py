# -*- coding: utf-8 -*-
"""
XAN — Calendário, estações, horas e clima.
==========================================

O tempo no XAN é **mecânica**, não decoração: estação, hora Yin/Yang e clima
entram como fatos objetivos no Registro de Regras e na harmonia elemental de
uma ruptura de cultivo (como em *Amazing Cultivation Simulator*, onde janelas
de clima e estação decidem a qualidade do Núcleo Dourado).

Estrutura
---------
* Ano de 12 meses lunares, 4 estações de 3 meses, mês de 30 dias.
* Dia dividido em 12 **shichen** (時辰) de 2 horas, cada um com Yin/Yang e um
  ramo terrestre.
* Clima sorteado por região/estação com pesos inteiros exatos.

Tudo determinístico a partir da semente do mundo: duas mesas com a mesma
semente têm o mesmo clima no mesmo dia.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .entropia import Aleatoriedade

__all__ = [
    "ESTACOES", "MESES", "SHICHEN", "CLIMAS",
    "Data", "Hora", "avancar_dias", "estacao_do_mes", "yin_yang_da_hora",
    "sortear_clima", "clima_por_elemento", "JANELAS_AUSPICIOSAS",
]

ESTACOES: Tuple[str, ...] = ("primavera", "verao", "outono", "inverno")

MESES: Tuple[Tuple[int, str, str], ...] = (
    (1, "Yín", "寅"), (2, "Mǎo", "卯"), (3, "Chén", "辰"),
    (4, "Sì", "巳"), (5, "Wǔ", "午"), (6, "Wèi", "未"),
    (7, "Shēn", "申"), (8, "Yǒu", "酉"), (9, "Xū", "戌"),
    (10, "Hài", "亥"), (11, "Zǐ", "子"), (12, "Chǒu", "丑"),
)

SHICHEN: Tuple[Tuple[str, str, int, int, str], ...] = (
    # (nome, caractere, hora inicial, hora final, polaridade)
    ("Zǐ", "子", 23, 1, "yang"),    # meia-noite: o yang nasce no yin pleno
    ("Chǒu", "丑", 1, 3, "yin"),
    ("Yín", "寅", 3, 5, "yang"),
    ("Mǎo", "卯", 5, 7, "yin"),
    ("Chén", "辰", 7, 9, "yang"),
    ("Sì", "巳", 9, 11, "yin"),
    ("Wǔ", "午", 11, 13, "yang"),   # meio-dia
    ("Wèi", "未", 13, 15, "yin"),
    ("Shēn", "申", 15, 17, "yang"),
    ("Yǒu", "酉", 17, 19, "yin"),
    ("Xū", "戌", 19, 21, "yang"),
    ("Hài", "亥", 21, 23, "yin"),
)

CLIMAS: Tuple[str, ...] = (
    "limpo", "nublado", "chuva", "nevoeiro", "nevasca",
    "tempestade", "miasma", "calor_extremo", "frio_extremo",
)

# Elemento que cada clima manifesta — usado na harmonia de ruptura.
CLIMA_ELEMENTO: Dict[str, str] = {
    "limpo": "nenhum",
    "nublado": "nenhum",
    "chuva": "agua",
    "nevoeiro": "agua",
    "nevasca": "agua",
    "tempestade": "metal",       # trovão/raio associado ao Metal no ACS
    "miasma": "fogo",            # miasma tóxico = Fogo no ACS
    "calor_extremo": "fogo",
    "frio_extremo": "agua",
}

# Peso inteiro por (estação, clima). Nada de float: probabilidades exatas.
_PESOS_CLIMA: Dict[Tuple[str, str], int] = {
    ("primavera", "limpo"): 30, ("primavera", "nublado"): 20,
    ("primavera", "chuva"): 25, ("primavera", "nevoeiro"): 12,
    ("primavera", "tempestade"): 6, ("primavera", "miasma"): 4,
    ("primavera", "nevasca"): 1, ("primavera", "calor_extremo"): 1,
    ("primavera", "frio_extremo"): 1,
    ("verao", "limpo"): 34, ("verao", "nublado"): 14,
    ("verao", "chuva"): 16, ("verao", "tempestade"): 14,
    ("verao", "calor_extremo"): 12, ("verao", "nevoeiro"): 4,
    ("verao", "miasma"): 4, ("verao", "nevasca"): 1,
    ("verao", "frio_extremo"): 1,
    ("outono", "limpo"): 32, ("outono", "nublado"): 18,
    ("outono", "chuva"): 14, ("outono", "nevoeiro"): 14,
    ("outono", "tempestade"): 10, ("outono", "miasma"): 5,
    ("outono", "frio_extremo"): 4, ("outono", "nevasca"): 2,
    ("outono", "calor_extremo"): 1,
    ("inverno", "limpo"): 24, ("inverno", "nublado"): 18,
    ("inverno", "nevasca"): 22, ("inverno", "frio_extremo"): 16,
    ("inverno", "nevoeiro"): 8, ("inverno", "chuva"): 6,
    ("inverno", "tempestade"): 3, ("inverno", "miasma"): 2,
    ("inverno", "calor_extremo"): 1,
}

# Janelas auspiciosas por elemento da Lei (inspirado no ACS): melhor estação e
# melhor dia do mês para romper.
JANELAS_AUSPICIOSAS: Dict[str, Dict[str, Tuple[int, ...]]] = {
    "fogo":  {"estacao": ("primavera", "verao"), "dias": tuple(range(1, 15))},
    "madeira": {"estacao": ("inverno", "primavera"), "dias": tuple(range(1, 15))},
    "metal": {"estacao": ("outono", "inverno"), "dias": tuple(range(16, 31))},
    "agua":  {"estacao": ("outono", "inverno"), "dias": tuple(range(16, 31))},
    "terra": {"estacao": ("verao", "outono"), "dias": tuple(range(1, 31))},
    "nenhum": {"estacao": ESTACOES, "dias": tuple(range(1, 31))},
    "vazio": {"estacao": ESTACOES, "dias": tuple(range(1, 31))},
}


@dataclass(frozen=True)
class Data:
    ano: int
    mes: int          # 1..12
    dia: int          # 1..30

    def __post_init__(self) -> None:
        if not (1 <= self.mes <= 12):
            raise ValueError(f"mês {self.mes} fora de 1..12")
        if not (1 <= self.dia <= 30):
            raise ValueError(f"dia {self.dia} fora de 1..30")
        if self.ano < 1:
            raise ValueError("ano deve ser >= 1")

    @property
    def estacao(self) -> str:
        return estacao_do_mes(self.mes)

    @property
    def mes_nome(self) -> str:
        return MESES[self.mes - 1][1]

    @property
    def dia_absoluto(self) -> int:
        return (self.ano - 1) * 360 + (self.mes - 1) * 30 + self.dia

    def texto(self) -> str:
        return f"{self.dia:02d} de {self.mes_nome} ({self.mes}º mês), ano {self.ano} — {self.estacao}"


@dataclass(frozen=True)
class Hora:
    shichen: int      # 0..11

    def __post_init__(self) -> None:
        if not (0 <= self.shichen <= 11):
            raise ValueError(f"shichen {self.shichen} fora de 0..11")

    @classmethod
    def da_hora_solar(cls, hora: int) -> "Hora":
        if not (0 <= hora <= 23):
            raise ValueError("hora solar fora de 0..23")
        return cls(((hora + 1) // 2) % 12)

    @property
    def nome(self) -> str:
        return SHICHEN[self.shichen][0]

    @property
    def caractere(self) -> str:
        return SHICHEN[self.shichen][1]

    @property
    def polaridade(self) -> str:
        return SHICHEN[self.shichen][4]

    @property
    def intervalo(self) -> str:
        return f"{SHICHEN[self.shichen][2]:02d}h–{SHICHEN[self.shichen][3]:02d}h"

    def texto(self) -> str:
        return f"{self.nome} {self.caractere} ({self.intervalo}, {self.polaridade})"


def estacao_do_mes(mes: int) -> str:
    if not (1 <= mes <= 12):
        raise ValueError("mês fora de 1..12")
    return ESTACOES[(mes - 1) // 3]


def avancar_dias(data: Data, dias: int) -> Data:
    """Aritmética de calendário exata (sem float, sem fuso horário)."""
    total = data.dia_absoluto + dias
    if total < 1:
        raise ValueError("data resultante anterior ao ano 1")
    total -= 1
    ano, resto = divmod(total, 360)
    mes, dia = divmod(resto, 30)
    return Data(ano + 1, mes + 1, dia + 1)


def yin_yang_da_hora(hora: Hora) -> str:
    return hora.polaridade


def sortear_clima(
    aleat: Aleatoriedade,
    estacao: str,
    regiao_elemento: str = "nenhum",
    altitude: int = 0,
) -> str:
    """Clima com pesos inteiros exatos, ajustado pelo elemento da região."""
    if estacao not in ESTACOES:
        raise ValueError(f"estação inválida {estacao!r}")
    itens: List[str] = []
    pesos: List[int] = []
    for clima in CLIMAS:
        p = _PESOS_CLIMA.get((estacao, clima), 0)
        if p <= 0:
            continue
        # região de elemento forte puxa o clima correspondente
        if CLIMA_ELEMENTO.get(clima) == regiao_elemento:
            p *= 3
        # altitude elevada favorece neve/frio e reduz chuva
        if altitude >= 2:
            if clima in ("nevasca", "frio_extremo"):
                p *= 2
            elif clima == "chuva":
                p = max(1, p // 2)
        itens.append(clima)
        pesos.append(p)
    return aleat.escolher_ponderado(itens, pesos)


def clima_por_elemento(clima: str) -> str:
    if clima not in CLIMA_ELEMENTO:
        raise ValueError(f"clima desconhecido {clima!r}")
    return CLIMA_ELEMENTO[clima]


def harmonia_elemental(
    elemento_da_lei: str,
    estacao: str,
    dia: int,
    polaridade: str,
    clima: str,
) -> Tuple[int, List[str]]:
    """Pontos de harmonia (0..12) entre o momento e o elemento da Lei.

    Retorna (pontos, razões) — cada ponto tem motivo escrito, para a mesa
    conferir a conta em vez de confiar numa opinião.
    """
    from .regras import ELEMENTOS_CANONICOS, ELEMENTOS_NEUTROS
    elem = elemento_da_lei.lower()
    if elem not in ELEMENTOS_CANONICOS + ELEMENTOS_NEUTROS:
        raise ValueError(f"elemento de lei inválido {elemento_da_lei!r}")
    if estacao not in ESTACOES:
        raise ValueError(f"estação inválida {estacao!r}; opções {list(ESTACOES)}")
    if polaridade not in ("yin", "yang"):
        raise ValueError(f"polaridade inválida {polaridade!r}; use yin ou yang")
    if not isinstance(dia, int) or isinstance(dia, bool) or not (1 <= dia <= 30):
        raise ValueError(f"dia {dia!r} fora de 1..30")
    pontos = 0
    razoes: List[str] = []
    if elem in ELEMENTOS_NEUTROS:
        return 4, ["leis sem elemento recebem harmonia neutra fixa (+4)"]

    janela = JANELAS_AUSPICIOSAS[elem]
    if estacao in janela["estacao"]:
        pontos += 4
        razoes.append(f"estação {estacao} dentro da janela auspiciosa (+4)")
    if dia in janela["dias"]:
        pontos += 2
        razoes.append(f"dia {dia} dentro da quinzena auspiciosa (+2)")
    # Yin/Yang: elementos fogo/madeira são yang; metal/agua são yin; terra é neutro
    polaridade_ideal = {"fogo": "yang", "madeira": "yang",
                        "metal": "yin", "agua": "yin", "terra": None}[elem]
    if polaridade_ideal is None:
        pontos += 1
        razoes.append("Terra é neutra e recebe +1 em qualquer polaridade")
    elif polaridade == polaridade_ideal:
        pontos += 2
        razoes.append(f"hora {polaridade} coincide com a polaridade do elemento (+2)")
    else:
        pontos -= 2
        razoes.append(f"hora {polaridade} contraria o elemento {elem} (-2)")

    if clima_por_elemento(clima) == elem:
        pontos += 4
        razoes.append(f"clima {clima} manifesta {elem} (+4)")
    elif clima_por_elemento(clima) in ("nenhum",):
        pontos += 1
        razoes.append("clima neutro não interfere (+1)")
    else:
        outro = clima_por_elemento(clima)
        from .regras import ELEMENTOS_SUPERADORES
        if ELEMENTOS_SUPERADORES[outro] == elem:
            pontos -= 3
            razoes.append(f"clima {clima} ({outro}) supera {elem} (-3)")
        else:
            pontos -= 1
            razoes.append(f"clima {clima} ({outro}) não favorece {elem} (-1)")

    return max(0, min(12, pontos)), razoes
