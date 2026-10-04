# -*- coding: utf-8 -*-
"""
XAN — Espinha dorsal de aleatoriedade (camada 2: dados).
========================================================

Notação suportada (tudo em minúsculas, espaços ignorados):

    NdS            N dados de S faces           1d20, 3d6, 2d10
    NdS!           dados explosivos no valor máximo      2d6!
    NdS!T          dados explosivos a partir de T        1d10!8
    NdS kh M       mantém as M MAIORES faces             4d6kh1
    NdS kl M       mantém as M MENORES faces             2d20kl1
    NdS!T kh M     combináveis                           3d8!7kh2
    d%            _percentil (1d100)
    NdF            dados Fudge/Fate (-1, 0, +1)
    expressões     1d20 + 5 - 1d4 + 2

Garantias de imparcialidade:
    * cada face vem de ``Aleatoriedade.abaixo(S)`` → uniforme exato, sem viés
      de módulo, para qualquer número de faces (inclusive d7, d13, d100);
    * ``kh``/``kl`` são **regras declaradas antes da rolagem** e valem igual
      para todos os atores. Não existe "kh secreto" nem seleção pós-hoc:
      todas as faces sorteadas ficam registradas em ``faces``;
    * o valor esperado é calculado com ``fractions.Fraction`` (exato), o que
      permite ao módulo ``justica`` conferir empiricamente a teoria;
    * dados explosivos têm teto de encadeamento para não travar a mesa.
"""

from __future__ import annotations

import itertools
import math
import re
from functools import lru_cache
from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Optional, Sequence, Tuple

from .entropia import Aleatoriedade

__all__ = [
    "ErroDeNotacao",
    "TermoDado",
    "Rolagem",
    "rolar",
    "valor_esperado",
    "minimo_maximo",
    "D20",
    "D6",
]

_LIMITE_FACES = 1_000_000
_LIMITE_QUANTIDADE = 1_000
_LIMITE_EXPLOSAO = 256  # teto de encadeamento por dado original

_TERMO_RE = re.compile(
    r"(?:"
    r"(?P<count>\d*)d(?P<sides>\d+|%|f)(?P<suffix>(?:!\d*|kh\d+|kl\d+|k\d+)*)"
    r"|"
    r"(?P<const>\d+)"
    r")"
)
_KEEP_RE = re.compile(r"(kh|kl|k)(\d+)")
_EXPLODE_RE = re.compile(r"!(\d*)")


class ErroDeNotacao(ValueError):
    """Expressão de dados inválida."""


@dataclass(frozen=True)
class TermoDado:
    """Um grupo de dados dentro da expressão. Imutável."""

    quantidade: int
    lados: int
    faces: Tuple[int, ...]           # TODAS as faces sorteadas, na ordem
    mantidas: Tuple[int, ...]        # faces que entram na soma
    descartadas: Tuple[int, ...]     # faces excluídas por kh/kl (transparência)
    modo_manter: str                 # "", "kh", "kl"
    quantidade_manter: int           # 0 = mantém todas
    explosao: int                    # 0 = desligada; senão limiar
    explosivos: int                  # quantas faces extras foram geradas
    fudge: bool = False
    sinal: int = 1                   # +1 ou -1 (termo subtraído da expressão)

    def __post_init__(self) -> None:
        if self.sinal not in (1, -1):
            raise ErroDeNotacao(f"sinal de termo deve ser +1 ou -1, veio {self.sinal}")

    @property
    def soma(self) -> int:
        return self.sinal * sum(self.mantidas)

    def expressao(self) -> str:
        s = f"{self.quantidade}d"
        if self.fudge:
            s += "F"
        elif self.lados == 100:
            s += "%"
        else:
            s += str(self.lados)
        if self.explosao:
            s += "!" + (str(self.explosao) if self.explosao != self.lados else "")
        if self.modo_manter:
            s += f"{self.modo_manter}{self.quantidade_manter}"
        return s


@dataclass(frozen=True)
class Rolagem:
    """Resultado completo e imutável de uma expressão de dados.

    Guarda tudo que é necessário para auditar: faces sorteadas, faces
    mantidas, faces descartadas, constante e total. Não existe método que
    altere o total depois de criado.
    """

    expressao: str
    termos: Tuple[TermoDado, ...]
    constante: int
    total: int
    minimo: int
    maximo: int
    valor_esperado: Fraction
    limite_aberto: bool = False  # True se há dado explosivo
    identificador: str = ""      # vínculo com o registro de auditoria

    def faces(self) -> Tuple[int, ...]:
        saida: List[int] = []
        for t in self.termos:
            saida.extend(t.faces)
        return tuple(saida)

    def descricao(self) -> str:
        partes = []
        for t in self.termos:
            corpo = "[" + ", ".join(str(f) for f in t.faces) + "]"
            if t.descartadas:
                corpo += " (descartadas: " + ", ".join(str(f) for f in t.descartadas) + ")"
            partes.append(f"{t.expressao()}→{corpo}={t.soma}")
        if self.constante:
            partes.append(f"constante={self.constante:+d}")
        return "  ".join(partes) + f"  ⇒  TOTAL {self.total}"

    def __post_init__(self) -> None:
        # Invariante: o total TEM que ser a soma aritmética das partes.
        esperado = sum(t.soma for t in self.termos) + self.constante
        if esperado != self.total:
            raise AssertionError(
                f"Rolagem inconsistente: total={self.total} mas partes somam {esperado}"
            )
        if self.minimo > self.maximo:
            raise AssertionError("intervalo [minimo, maximo] invertido")
        if not (self.minimo <= self.total <= self.maximo) and not self.limite_aberto:
            raise AssertionError("total fora do intervalo possível")


@lru_cache(maxsize=512)
def _parsear(expressao: str) -> Tuple[Tuple[TermoDado, ...], int]:
    """Devolve (modelos de termo, constante). Modelos ainda sem faces.

    O resultado é imutável e cacheado: expressões repetidas (o caso normal numa
    sessão) não repagaram o custo do parser.
    """
    if not isinstance(expressao, str):
        raise ErroDeNotacao("expressão deve ser texto")
    # Espaço só é permitido junto de operadores/sufixos. "1d20 5" é ambíguo
    # (seria 1d205) e por isso é rejeitado: nada de interpretação silenciosa.
    if re.search(r"\d\s+\d", expressao):
        raise ErroDeNotacao(
            f"número separado por espaço sem operador: {expressao!r} — use '+' ou '-'"
        )
    s = re.sub(r"\s+", "", expressao).lower()
    if not s:
        raise ErroDeNotacao("expressão vazia")
    if len(s) > 400:
        raise ErroDeNotacao("expressão longa demais (máx. 400 caracteres)")

    modelos: List[TermoDado] = []
    constante = 0
    i = 0
    sinal = 1
    while i < len(s):
        # sinal opcional antes de cada termo
        if s[i] in "+-":
            sinal = -1 if s[i] == "-" else 1
            i += 1
            if i >= len(s):
                raise ErroDeNotacao(f"sinal sem termo no final: {expressao!r}")
        m = _TERMO_RE.match(s, i)
        if not m:
            raise ErroDeNotacao(f"trecho incompreensível em {s[i:]!r} (de {expressao!r})")
        if m.group("const") is not None:
            constante += sinal * int(m.group("const"))
        else:
            count = m.group("count")
            quantidade = 1 if count == "" else int(count)
            if quantidade < 1:
                raise ErroDeNotacao("quantidade de dados deve ser >= 1")
            if quantidade > _LIMITE_QUANTIDADE:
                raise ErroDeNotacao(f"máximo de {_LIMITE_QUANTIDADE} dados por termo")
            sides = m.group("sides")
            fudge = sides == "f"
            if sides == "%":
                lados = 100
            elif fudge:
                lados = 3
            else:
                lados = int(sides)
                if lados < 2:
                    raise ErroDeNotacao("dado precisa de pelo menos 2 faces")
                if lados > _LIMITE_FACES:
                    raise ErroDeNotacao(f"máximo de {_LIMITE_FACES} faces")

            suffix = m.group("suffix") or ""
            modo_manter, qtd_manter = "", 0
            km = _KEEP_RE.search(suffix)
            if km:
                modo_manter = "kh" if km.group(1) in ("kh", "k") else "kl"
                qtd_manter = int(km.group(2))
                if qtd_manter < 1:
                    raise ErroDeNotacao(
                        "manter zero dados não significa nada; use pelo menos "
                        f"{modo_manter}1"
                    )
                if qtd_manter > quantidade:
                    raise ErroDeNotacao(
                        f"{modo_manter}{qtd_manter} impossível com {quantidade} dados"
                    )
            explosao = 0
            em = _EXPLODE_RE.search(suffix)
            if em:
                txt = em.group(1)
                explosao = lados if txt == "" else int(txt)
                if not (1 <= explosao <= lados):
                    raise ErroDeNotacao(
                        f"limiar de explosão {explosao} fora de [1,{lados}]"
                    )
            if sinal not in (1, -1):
                raise ErroDeNotacao(f"sinal inválido {sinal}")
            modelos.append(
                TermoDado(
                    quantidade=quantidade,
                    lados=lados,
                    faces=(),
                    mantidas=(),
                    descartadas=(),
                    modo_manter=modo_manter,
                    quantidade_manter=qtd_manter,
                    explosao=explosao,
                    explosivos=0,
                    fudge=fudge,
                    sinal=sinal,
                )
            )
        i = m.end()
        sinal = 1
        if i < len(s) and s[i] not in "+-":
            raise ErroDeNotacao(f"esperava '+' ou '-' em {s[i:]!r} (de {expressao!r})")

    if not modelos and constante == 0:
        raise ErroDeNotacao("expressão sem dados e sem valor")
    return tuple(modelos), constante


def _sortear_termo(modelo: TermoDado, aleat: Aleatoriedade) -> TermoDado:
    faces: List[int] = []
    extras = 0
    for _ in range(modelo.quantidade):
        if modelo.fudge:
            v = aleat.abaixo(3) - 1
            faces.append(v)
            continue
        v = aleat.abaixo(modelo.lados) + 1
        faces.append(v)
        if modelo.explosao:
            cadeia = 0
            while v >= modelo.explosao and cadeia < _LIMITE_EXPLOSAO:
                cadeia += 1
                extras += 1
                v = aleat.abaixo(modelo.lados) + 1
                faces.append(v)

    if modelo.modo_manter and modelo.quantidade_manter < len(faces):
        # Ordenação determinística: valor e, no empate, posição original.
        ordem = sorted(
            range(len(faces)),
            key=lambda idx: (faces[idx], idx),
            reverse=(modelo.modo_manter == "kh"),
        )
        manter_idx = set(ordem[: modelo.quantidade_manter])
        mantidas = tuple(f for idx, f in enumerate(faces) if idx in manter_idx)
        descartadas = tuple(f for idx, f in enumerate(faces) if idx not in manter_idx)
    else:
        mantidas = tuple(faces)
        descartadas = ()

    return TermoDado(
        quantidade=modelo.quantidade,
        lados=modelo.lados,
        faces=tuple(faces),
        mantidas=mantidas,
        descartadas=descartadas,
        modo_manter=modelo.modo_manter,
        quantidade_manter=modelo.quantidade_manter,
        explosao=modelo.explosao,
        explosivos=extras,
        fudge=modelo.fudge,
        sinal=modelo.sinal,
    )


def rolar(
    expressao: str,
    aleat: Aleatoriedade,
    constante_extra: int = 0,
    identificador: str = "",
) -> Rolagem:
    """Rola uma expressão de dados. ``constante_extra`` é aritmética declarada."""
    modelos, constante = _parsear(expressao)
    constante += int(constante_extra)
    termos = tuple(_sortear_termo(m, aleat) for m in modelos)
    total = sum(t.soma for t in termos) + constante
    lo, hi = minimo_maximo(termos, constante)
    ve = valor_esperado(termos, constante)
    return Rolagem(
        expressao=expressao,
        termos=termos,
        constante=constante,
        total=total,
        minimo=lo,
        maximo=hi,
        valor_esperado=ve,
        limite_aberto=any(t.explosao for t in termos),
        identificador=identificador,
    )


# --------------------------------------------------------------------------
# Matemática exata (usada por testes de justiça e pela documentação)
#
# Tudo em ``fractions.Fraction``: nada de ponto flutuante no caminho crítico.
# Para ``kh``/``kl`` o valor esperado é calculado por **estatística de ordem**
# (fórmula fechada e exata), e não por enumeração nem por aproximação.
# --------------------------------------------------------------------------
def _media_dado_simples(lados: int, fudge: bool, explosao: int) -> Fraction:
    """Média de UM dado. Com explosão, soma da série geométrica convergente."""
    if fudge:
        return Fraction(0)
    base = Fraction(lados + 1, 2)
    if not explosao:
        return base
    p_explodir = Fraction(lados - explosao + 1, lados)
    if p_explodir >= 1:
        raise ErroDeNotacao("explosão com probabilidade 1 não converge")
    return base / (1 - p_explodir)


def _esperado_da_k_esima_maior(n: int, lados: int, k: int) -> Fraction:
    """E[X_(k)] — a k-ésima MAIOR face de n dados de ``lados`` faces.

    E[X_(k)] = Σ_v P(X_(k) >= v), e a k-ésima MAIOR face é >= v exatamente
    quando pelo menos k dados mostram valor >= v. Binomial exata em Fraction.
    """
    if not (1 <= k <= n):
        raise ErroDeNotacao("ordem fora de faixa")
    preciso = k          # k-ésima MAIOR >= v  sse  pelo menos k dados >= v
    total = Fraction(0)
    for v in range(1, lados + 1):
        p = Fraction(lados - v + 1, lados)
        q = 1 - p
        prob = Fraction(0)
        for i in range(preciso, n + 1):
            prob += Fraction(math.comb(n, i)) * (p ** i) * (q ** (n - i))
        total += prob
    return total


def _esperado_mantidas(t: "TermoDado") -> Fraction:
    """Valor esperado exato das faces MANTIDAS de um termo."""
    if t.fudge:
        # dF: faces -1/0/+1. kh mantém as maiores, kl as menores.
        media_unica = Fraction(0)
        if not t.modo_manter or t.quantidade_manter >= t.quantidade:
            return t.quantidade * media_unica
        # enumeração exata: 3^n é pequeno para n razoável
        espaco = 3 ** t.quantidade
        if espaco > 200_000:
            raise ErroDeNotacao("kh/kl em dF com dados demais para cálculo exato")
        soma = Fraction(0)
        for combo in itertools.product((-1, 0, 1), repeat=t.quantidade):
            ordenado = sorted(combo, reverse=(t.modo_manter == "kh"))
            k = t.quantidade_manter or t.quantidade
            soma += sum(ordenado[:k])
        return soma / espaco
    if not t.modo_manter or t.quantidade_manter >= t.quantidade:
        return t.quantidade * _media_dado_simples(t.lados, t.fudge, t.explosao)
    if t.explosao:
        raise ErroDeNotacao(
            "valor esperado exato de kh/kl combinado com dado explosivo não tem "
            "forma fechada implementada; a rolagem continua válida"
        )
    m = t.quantidade_manter
    if t.modo_manter == "kh":
        return sum((_esperado_da_k_esima_maior(t.quantidade, t.lados, k)
                    for k in range(1, m + 1)), Fraction(0))
    # kl: soma das m menores = soma total − soma das (n−m) maiores
    total = t.quantidade * Fraction(t.lados + 1, 2)
    maiores = sum(
        (_esperado_da_k_esima_maior(t.quantidade, t.lados, k)
         for k in range(1, t.quantidade - m + 1)),
        Fraction(0),
    )
    return total - maiores


def valor_esperado(termos: Sequence[TermoDado], constante: int = 0) -> Fraction:
    """Valor esperado **exato** da expressão, em ``Fraction``."""
    total = Fraction(constante)
    for t in termos:
        total += t.sinal * _esperado_mantidas(t)
    return total


def minimo_maximo(termos: Sequence[TermoDado], constante: int = 0) -> Tuple[int, int]:
    """Menor e maior total possíveis ignorando explosões encadeadas."""
    lo = hi = constante
    for t in termos:
        k = t.quantidade_manter if (t.modo_manter and t.quantidade_manter) else t.quantidade
        menor, maior = (-1, 1) if t.fudge else (1, t.lados)
        if t.sinal == 1:
            lo += k * menor
            hi += k * maior
        else:
            lo -= k * maior
            hi -= k * menor
    return lo, hi


# --------------------------------------------------------------------------
# Atalhos de mesa
# --------------------------------------------------------------------------
def D20(aleat: Aleatoriedade, modificador: int = 0) -> Rolagem:
    """O dado central do XAN."""
    return rolar("1d20", aleat, constante_extra=modificador)


def D6(aleat: Aleatoriedade, quantidade: int = 1) -> Rolagem:
    return rolar(f"{quantidade}d6", aleat)
