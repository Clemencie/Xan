# -*- coding: utf-8 -*-
"""
XAN — Certificação de Justiça do Motor de Aleatoriedade.
========================================================

"Completamente aleatório e justo" não é uma intenção: é uma afirmação que este
módulo **mede**. Ele roda uma bateria de testes estatísticos sobre o motor real
(o mesmo código usado na mesa) e emite um certificado.

Bateria
-------
A. Uniformidade de faces          qui-quadrado para d4, d6, d8, d10, d12, d20, d100
B. Uniformidade de ``abaixo(n)``  qui-quadrado para n não-potência-de-2
                                  (3, 5, 6, 7, 13, 20, 100) — caça-viés de módulo
C. Distribuição exata de totais   qui-quadrado contra a distribuição teórica
                                  EXATA (enumeração/convolução em Fraction)
D. Média e variância              teste z contra valor teórico exato
E. Uniformidade contínua          Kolmogorov–Smirnov sobre [0,1)
F. Independência temporal         autocorrelação serial lag-1 (teste z)
G. Aleatoriedade de ordem         Wald–Wolfowitz (corridas acima/abaixo da mediana)
H. Testes de bits (NIST-like)     monobit, pôquer-4, maior corrida de uns
I. Independência entre chamadas   qui-quadrado sobre pares consecutivos
J. Imparcialidade de kh/kl        faces mantidas E descartadas conferidas
K. Escolha ponderada exata        qui-quadrado contra pesos inteiros
L. Embaralhamento uniforme        qui-quadrado sobre permutações e posições
M. Rejeição ativa                 bytes consumidos/resultado vs. taxa teórica
N. Determinismo por semente       mesma semente ⇒ mesmo mundo; sementes distintas ⇒
                                  sequências distintas
O. **Imparcialidade entre atores** dois atores com rótulos diferentes (herói,
                                  vilão, mestre, figurante) rolando a MESMA
                                  declaração: teste de homogeneidade qui-quadrado.
                                  É o teste direto de "sem vantagem narrativa".

Critério de veredito
--------------------
α = 0,001 por teste (NIST usa 0,01). Com ~20 testes, a taxa agregada de falso
alarme fica em ~2%. Um p-valor abaixo de α liga o alerta; abaixo de 1e-6 é
falha dura. Todos os p-valores são publicados no certificado — nada é escondido.

Implementação
-------------
Tudo em biblioteca padrão. As funções especiais (gama incompleta regularizada e
distribuição de Kolmogorov) são implementadas aqui com precisão dupla e
validadas contra valores conhecidos nos testes.
"""

from __future__ import annotations

import itertools
import math
from collections import Counter
from dataclasses import dataclass, asdict
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .dados import TermoDado, _parsear, rolar, valor_esperado
from .entropia import Aleatoriedade, FonteSemeada, FonteViva

__all__ = [
    "TesteEstatistico",
    "CertificadoDeJustica",
    "Indeterminado",
    "gamma_q",
    "chi2_p_valor",
    "ks_p_valor",
    "distribuicao_exata",
    "momentos_exatos",
    "normal_p_valor_bicaudal",
    "bateria_completa",
    "emitir_certificado",
]

ALFA = 0.001          # limiar de veredito por teste
ALFA_FALHA_DURA = 1e-6
_CAP_ENUMERACAO = 2_000_000


class Indeterminado(ValueError):
    """Não há forma exata implementada para esta distribuição."""


# ==========================================================================
# Funções especiais
# ==========================================================================
def _gser(a: float, x: float, itmax: int = 500, eps: float = 3e-16) -> float:
    """Série para P(a,x) (gama incompleta regularizada inferior)."""
    if x == 0.0:
        return 0.0
    ap = a
    soma = 1.0 / a
    delta = soma
    for _ in range(itmax):
        ap += 1.0
        delta *= x / ap
        soma += delta
        if abs(delta) < abs(soma) * eps:
            break
    return soma * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gcf(a: float, x: float, itmax: int = 500, eps: float = 3e-16) -> float:
    """Fração continuada (Lentz) para Q(a,x)."""
    minusc = 1e-300
    b = x + 1.0 - a
    c = 1.0 / minusc
    d = 1.0 / b
    h = d
    for i in range(1, itmax + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < minusc:
            d = minusc
        c = b + an / c
        if abs(c) < minusc:
            c = minusc
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def gamma_q(a: float, x: float) -> float:
    """Q(a,x) = 1 − P(a,x), gama incompleta superior regularizada."""
    if a <= 0 or x < 0:
        raise ValueError("domínio inválido")
    if x == 0.0:
        return 1.0
    if x < a + 1.0:
        return 1.0 - _gser(a, x)
    return _gcf(a, x)


def chi2_p_valor(x: float, gl: int) -> float:
    """P(X² >= x) com ``gl`` graus de liberdade."""
    if gl <= 0:
        raise ValueError("graus de liberdade devem ser positivos")
    if x <= 0:
        return 1.0
    return min(1.0, max(0.0, gamma_q(gl / 2.0, x / 2.0)))


def ks_p_valor(d: float, n: int) -> float:
    """p-valor assintótico da estatística de Kolmogorov–Smirnov."""
    if n <= 0:
        raise ValueError("n deve ser positivo")
    lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
    if lam <= 0:
        return 1.0
    if lam > 60:
        return 0.0
    soma = 0.0
    sinal = 1.0
    for j in range(1, 201):
        termo = math.exp(-2.0 * j * j * lam * lam)
        if termo < 1e-18:
            break
        soma += sinal * termo
        sinal = -sinal
    return min(1.0, max(0.0, 2.0 * soma))


def normal_p_valor_bicaudal(z: float) -> float:
    """P(|Z| >= |z|) para Z normal padrão — exato via erfc."""
    return math.erfc(abs(z) / math.sqrt(2.0))


# ==========================================================================
# Distribuição teórica exata
# ==========================================================================
def _faces_do_termo(t: TermoDado) -> Tuple[int, ...]:
    return (-1, 0, 1) if t.fudge else tuple(range(1, t.lados + 1))


def _dist_termo(t: TermoDado) -> Dict[int, Fraction]:
    """Distribuição exata da SOMA MANTIDA de um termo, por enumeração."""
    if t.explosao:
        raise Indeterminado(
            "dados explosivos não têm distribuição exata enumerável neste módulo; "
            "use o teste de média com tolerância"
        )
    faces = _faces_do_termo(t)
    espaco = len(faces) ** t.quantidade
    if espaco > _CAP_ENUMERACAO:
        raise Indeterminado(f"espaço amostral {espaco} acima do teto {_CAP_ENUMERACAO}")
    k = t.quantidade_manter or t.quantidade
    kh = t.modo_manter != "kl"
    cont: Counter = Counter()
    for combo in itertools.product(faces, repeat=t.quantidade):
        ordenado = sorted(combo, reverse=kh)
        cont[t.sinal * sum(ordenado[:k])] += 1
    return {v: Fraction(c, espaco) for v, c in cont.items()}


def distribuicao_exata(expressao: str) -> Dict[int, Fraction]:
    """Distribuição teórica exata do total de uma expressão (sem explosivos)."""
    termos, constante = _parsear(expressao)
    atual: Dict[int, Fraction] = {constante: Fraction(1)}
    for t in termos:
        d = _dist_termo(t)
        novo: Dict[int, Fraction] = {}
        for a, pa in atual.items():
            for b, pb in d.items():
                s = a + b
                novo[s] = novo.get(s, Fraction(0)) + pa * pb
        atual = novo
    total = sum(atual.values(), Fraction(0))
    if total != 1:
        raise AssertionError(f"distribuição não soma 1 (soma {total}) — erro interno")
    return dict(sorted(atual.items()))


def momentos_exatos(expressao: str) -> Tuple[Fraction, Fraction]:
    """(média, variância) exatas."""
    d = distribuicao_exata(expressao)
    mu = sum((Fraction(v) * p for v, p in d.items()), Fraction(0))
    var = sum((Fraction(v) * v * p for v, p in d.items()), Fraction(0)) - mu * mu
    return mu, var


# ==========================================================================
# Estruturas de resultado
# ==========================================================================
@dataclass(frozen=True)
class TesteEstatistico:
    nome: str
    familia: str
    descricao: str
    amostras: int
    estatistica: float
    p_valor: float
    limiar: float
    ok: bool
    nota: str = ""

    @property
    def falha_dura(self) -> bool:
        return self.p_valor < ALFA_FALHA_DURA


@dataclass(frozen=True)
class CertificadoDeJustica:
    versao_motor: str
    fonte: str
    alfa: float
    testes: Tuple[TesteEstatistico, ...]
    amostras_totais: int
    veredito: str
    resumo: str

    @property
    def aprovado(self) -> bool:
        return self.veredito == "APROVADO"

    def por_familia(self) -> Dict[str, List[TesteEstatistico]]:
        saida: Dict[str, List[TesteEstatistico]] = {}
        for t in self.testes:
            saida.setdefault(t.familia, []).append(t)
        return saida

    def markdown(self) -> str:
        linhas = [
            "# Certificado de Justiça — Motor de Aleatoriedade XAN",
            "",
            f"- **Motor:** {self.versao_motor}",
            f"- **Fonte de acaso:** `{self.fonte}`",
            f"- **Amostras totais:** {self.amostras_totais:,}".replace(",", "."),
            f"- **α por teste:** {self.alfa}",
            f"- **VEREDITO:** **{self.veredito}**",
            "",
            self.resumo,
            "",
            "| Família | Teste | Amostras | Estatística | p-valor | Veredito |",
            "|---|---|---:|---:|---:|:--:|",
        ]
        for t in self.testes:
            linhas.append(
                f"| {t.familia} | {t.nome} | {t.amostras:,} | {t.estatistica:.4f} "
                f"| {t.p_valor:.4g} | {'✅' if t.ok else '❌'} |".replace(",", ".")
            )
        linhas += ["", "## O que cada família garante", ""]
        linhas += [
            "- **A/B** — nenhuma face é favorecida; amostragem sem viés de módulo.",
            "- **C/D** — o total da expressão segue EXATAMENTE a distribuição teórica.",
            "- **E/F/G** — a sequência não tem padrão, tendência ou memória.",
            "- **H** — os bits brutos passam nos testes clássicos do NIST SP 800-22.",
            "- **I** — chamadas consecutivas são independentes entre si.",
            "- **J** — `kh`/`kl` não espiam nem filtram: mantidas e descartadas são ambas uniformes.",
            "- **K/L** — sorteio ponderado e embaralhamento são exatos.",
            "- **M** — a rejeição está realmente ativa (prova construtiva contra `% n`).",
            "- **N** — semente reproduz o mundo bit a bit (auditabilidade).",
            "- **O** — **nenhum ator tem vantagem**: rótulos diferentes produzem a mesma taxa de sucesso.",
        ]
        falhas = [t for t in self.testes if not t.ok]
        if falhas:
            linhas += ["", "## Testes reprovados", ""]
            linhas += [f"- **{t.nome}** (p={t.p_valor:.3g}): {t.descricao}" for t in falhas]
        return "\n".join(linhas) + "\n"

    def json(self) -> Dict[str, Any]:
        return {
            "versao_motor": self.versao_motor,
            "fonte": self.fonte,
            "alfa": self.alfa,
            "amostras_totais": self.amostras_totais,
            "veredito": self.veredito,
            "resumo": self.resumo,
            "testes": [asdict(t) for t in self.testes],
        }


# ==========================================================================
# Helpers de teste
# ==========================================================================
def _chi2_multinomial(
    observados: Dict[Any, int],
    probabilidades: Dict[Any, Fraction],
    n: int,
    min_esperado: float = 5.0,
) -> Tuple[float, int]:
    """Qui-quadrado com agrupamento de células de baixa frequência."""
    celulas: List[Tuple[Any, int, float]] = []
    for chave in sorted(probabilidades, key=lambda k: (str(type(k)), k)):
        esp = float(probabilidades[chave]) * n
        obs = observados.get(chave, 0)
        celulas.append((chave, obs, esp))
    # agrupa caudas com esperado < min_esperado
    agrupadas: List[List[Any]] = []
    atual: List[Any] = []
    acum = 0.0
    for c in celulas:
        atual.append(c)
        acum += c[2]
        if acum >= min_esperado:
            agrupadas.append(atual)
            atual, acum = [], 0.0
    if atual:
        if agrupadas:
            agrupadas[-1].extend(atual)
        else:
            agrupadas.append(atual)
    chi2 = 0.0
    for grupo in agrupadas:
        obs = sum(c[1] for c in grupo)
        esp = sum(c[2] for c in grupo)
        if esp > 0:
            chi2 += (obs - esp) ** 2 / esp
    gl = len(agrupadas) - 1
    return chi2, max(gl, 1)


def _t(nome: str, familia: str, desc: str, n: int, est: float, p: float,
       nota: str = "", limiar: float = ALFA) -> TesteEstatistico:
    return TesteEstatistico(
        nome=nome, familia=familia, descricao=desc, amostras=n,
        estatistica=est, p_valor=p, limiar=limiar,
        ok=(p >= limiar), nota=nota,
    )


# ==========================================================================
# A — uniformidade de faces
# ==========================================================================
def teste_faces(aleat: Aleatoriedade, lados: int, n: int) -> TesteEstatistico:
    cont: Counter = Counter()
    for _ in range(n):
        cont[aleat.abaixo(lados) + 1] += 1
    probs = {v: Fraction(1, lados) for v in range(1, lados + 1)}
    chi2, gl = _chi2_multinomial(dict(cont), probs, n)
    p = chi2_p_valor(chi2, gl)
    return _t(f"d{lados} uniforme", "A", f"qui-quadrado das faces de 1d{lados}",
              n, chi2, p, f"gl={gl}")


# ==========================================================================
# B — uniformidade de abaixo(n): caça-viés de módulo
# ==========================================================================
def teste_abaixo(aleat: Aleatoriedade, modulo: int, n: int) -> TesteEstatistico:
    cont: Counter = Counter()
    for _ in range(n):
        cont[aleat.abaixo(modulo)] += 1
    probs = {v: Fraction(1, modulo) for v in range(modulo)}
    chi2, gl = _chi2_multinomial(dict(cont), probs, n)
    p = chi2_p_valor(chi2, gl)
    nota = (
        "n é potência de 2 (sem rejeição necessária)"
        if modulo & (modulo - 1) == 0
        else f"n NÃO é potência de 2 — viés de módulo seria ~"
             f"{(2 ** (modulo - 1).bit_length()) % modulo / modulo:.4f} com '% n'"
    )
    return _t(f"abaixo({modulo})", "B",
              "uniformidade exata do sorteio limitado (rejeição)", n, chi2, p, nota)


# ==========================================================================
# C — distribuição exata do total
# ==========================================================================
def teste_distribuicao(aleat: Aleatoriedade, expressao: str, n: int) -> TesteEstatistico:
    teorica = distribuicao_exata(expressao)
    cont: Counter = Counter()
    for _ in range(n):
        cont[rolar(expressao, aleat).total] += 1
    chi2, gl = _chi2_multinomial(dict(cont), teorica, n)
    p = chi2_p_valor(chi2, gl)
    return _t(f"total de {expressao}", "C",
              f"qui-quadrado contra a distribuição teórica exata de {expressao}",
              n, chi2, p, f"gl={gl}, {len(teorica)} resultados possíveis")


# ==========================================================================
# D — média e variância (teste z)
# ==========================================================================
def teste_momentos(aleat: Aleatoriedade, expressao: str, n: int) -> TesteEstatistico:
    mu, var = momentos_exatos(expressao)
    mu_f = float(mu)
    sd = math.sqrt(float(var))
    soma = 0
    soma2 = 0
    for _ in range(n):
        v = rolar(expressao, aleat).total
        soma += v
        soma2 += v * v
    media = soma / n
    variancia_emp = (soma2 - n * media * media) / (n - 1)
    z = (media - mu_f) / (sd / math.sqrt(n))
    p = normal_p_valor_bicaudal(z)
    nota = (f"média teórica {mu} = {mu_f:.4f}, empírica {media:.4f}; "
            f"variância teórica {var} = {float(var):.4f}, empírica {variancia_emp:.4f}")
    return _t(f"média/variância de {expressao}", "D",
              "teste z da média contra o valor exato em Fraction", n, z, p, nota)


# ==========================================================================
# E — Kolmogorov–Smirnov sobre [0,1)
# ==========================================================================
def teste_ks(aleat: Aleatoriedade, n: int) -> TesteEstatistico:
    vals = sorted(
        int.from_bytes(aleat.bytes(8), "big") / float(1 << 64) for _ in range(n)
    )
    d = 0.0
    for i, v in enumerate(vals, start=1):
        d = max(d, i / n - v, v - (i - 1) / n)
    p = ks_p_valor(d, n)
    return _t("KS uniforme [0,1)", "E",
              "Kolmogorov–Smirnov contra a uniforme contínua", n, d, p,
              f"D={d:.5f}, crítico(0,001)≈{1.95/math.sqrt(n):.5f}")


# ==========================================================================
# F — autocorrelação serial lag-1
# ==========================================================================
def teste_correlacao_serial(aleat: Aleatoriedade, n: int) -> TesteEstatistico:
    ant = None
    soma = 0.0
    pares = 0
    for _ in range(n):
        v = int.from_bytes(aleat.bytes(8), "big") / float(1 << 64)
        if ant is not None:
            soma += (v - 0.5) * (ant - 0.5)
            pares += 1
        ant = v
    r = 12.0 * soma / pares
    z = r * math.sqrt(pares)
    p = normal_p_valor_bicaudal(z)
    return _t("autocorrelação lag-1", "F",
              "correlação entre sorteios consecutivos deve ser 0", n, r, p,
              f"r={r:+.5f}, z={z:+.2f}")


# ==========================================================================
# G — corridas (Wald–Wolfowitz)
# ==========================================================================
def teste_corridas(aleat: Aleatoriedade, n: int) -> TesteEstatistico:
    vals = [int.from_bytes(aleat.bytes(4), "big") / float(1 << 32) for _ in range(n)]
    mediana = sorted(vals)[n // 2]
    acima = [v > mediana for v in vals]
    n1 = sum(acima)
    n2 = n - n1
    corridas = 1
    for i in range(1, n):
        if acima[i] != acima[i - 1]:
            corridas += 1
    if n1 == 0 or n2 == 0:
        return _t("corridas", "G", "Wald–Wolfowitz", n, float(corridas), 0.0,
                  "degenerado")
    mu = 2.0 * n1 * n2 / n + 1.0
    var = (mu - 1.0) * (mu - 2.0) / (n - 1.0)
    z = (corridas - mu) / math.sqrt(var)
    p = normal_p_valor_bicaudal(z)
    return _t("corridas acima/abaixo da mediana", "G",
              "Wald–Wolfowitz: sequências longas indicam tendência", n, z, p,
              f"corridas={corridas}, esperado≈{mu:.1f}")


# ==========================================================================
# H — testes de bits (monobit, pôquer-4, maior corrida de uns)
# ==========================================================================
def teste_monobit(bits: Sequence[int]) -> TesteEstatistico:
    n = len(bits)
    s = abs(sum(1 if b else -1 for b in bits)) / math.sqrt(n)
    p = math.erfc(s / math.sqrt(2.0))
    return _t("monobit", "H", "equilíbrio 0/1 nos bits brutos", n, s, p)


def teste_poquer(bits: Sequence[int], m: int = 4) -> TesteEstatistico:
    n = len(bits) // m
    cont: Counter = Counter()
    for i in range(n):
        bloco = bits[i * m:(i + 1) * m]
        v = 0
        for b in bloco:
            v = (v << 1) | b
        cont[v] += 1
    soma = sum((c * c) for c in cont.values())
    chi2 = (2 ** m / n) * soma - n
    p = chi2_p_valor(chi2, 2 ** m - 1)
    return _t(f"pôquer-{m}", "H", f"frequência dos {2**m} blocos de {m} bits",
              n * m, chi2, p, f"gl={2**m-1}")


def _contagens_sem_corrida(M: int, k: int) -> int:
    """Quantas sequências binárias de comprimento M têm corrida máxima de 1s <= k.

    Programação dinâmica exata em inteiros: estado = comprimento da corrida
    corrente de 1s. Sem aproximação e sem tabela decorada.
    """
    if k < 0:
        return 0
    f = [0] * (k + 1)
    f[0] = 1
    for _ in range(M):
        g = [0] * (k + 1)
        g[0] = sum(f)                 # appending 0 zera a corrida
        for j in range(k):            # appending 1 estende, se couber
            g[j + 1] = f[j]
        f = g
    return sum(f)


def distribuicao_maior_corrida(M: int) -> Dict[int, Fraction]:
    """P(maior corrida de 1s == v) em M bits, exata, para v = 0..M."""
    espaco = 1 << M
    acumulado_ate = 0
    saida: Dict[int, Fraction] = {}
    for v in range(0, M + 1):
        ate_v = _contagens_sem_corrida(M, v)
        saida[v] = Fraction(ate_v - acumulado_ate, espaco)
        acumulado_ate = ate_v
    if acumulado_ate != espaco:
        raise AssertionError("DP da maior corrida não fecha o espaço amostral")
    if sum(saida.values()) != 1:
        raise AssertionError("distribuição da maior corrida não soma 1")
    return saida


def teste_maior_corrida(bits: Sequence[int], M: int = 128) -> TesteEstatistico:
    """Maior corrida de 1s por bloco de M bits, contra a distribuição EXATA."""
    n = len(bits) // M
    if n < 50:
        return _t("maior corrida de uns", "H", "distribuição da maior corrida",
                  len(bits), 0.0, 1.0, "amostra insuficiente")
    probs = distribuicao_maior_corrida(M)
    cont: Counter = Counter()
    for i in range(n):
        bloco = bits[i * M:(i + 1) * M]
        maior = atual = 0
        for b in bloco:
            atual = atual + 1 if b else 0
            if atual > maior:
                maior = atual
        cont[maior] += 1
    chi2, gl = _chi2_multinomial(dict(cont), probs, n)
    p = chi2_p_valor(chi2, gl)
    observadas = sorted(cont)
    return _t(f"maior corrida de uns (M={M})", "H",
              "qui-quadrado contra a distribuição exata obtida por PD",
              n * M, chi2, p,
              f"gl={gl}, {n} blocos, corridas observadas {observadas[0]}–{observadas[-1]}")


# ==========================================================================
# I — independência entre chamadas consecutivas
# ==========================================================================
def teste_independencia(aleat: Aleatoriedade, n: int, lados: int = 6) -> TesteEstatistico:
    cont: Counter = Counter()
    ant = aleat.abaixo(lados)
    for _ in range(n):
        v = aleat.abaixo(lados)
        cont[(ant, v)] += 1
        ant = v
    probs = {(a, b): Fraction(1, lados * lados)
             for a in range(lados) for b in range(lados)}
    chi2, gl = _chi2_multinomial(dict(cont), probs, n)
    p = chi2_p_valor(chi2, gl)
    return _t(f"pares consecutivos d{lados}", "I",
              "independência entre o resultado atual e o anterior", n, chi2, p,
              f"gl={gl} ({lados*lados} células)")


# ==========================================================================
# J — imparcialidade de kh/kl (mantidas E descartadas)
# ==========================================================================
def teste_manter_imparcial(aleat: Aleatoriedade, expressao: str, n: int) -> TesteEstatistico:
    """Confere a distribuição da face MANTIDA e a soma das DESCARTADAS.

    Se o motor "escolhesse" quais dados mostrar, as descartadas deixariam de ser
    uniformes. Verificar as duas pontas fecha a porta.
    """
    termos, _ = _parsear(expressao)
    if len(termos) != 1:
        raise Indeterminado("teste J exige um único termo")
    t = termos[0]
    faces = _faces_do_termo(t)
    k = t.quantidade_manter or t.quantidade
    kh = t.modo_manter != "kl"
    mantidas: Counter = Counter()
    descartadas: Counter = Counter()
    espaco = len(faces) ** t.quantidade
    for _ in range(n):
        r = rolar(expressao, aleat)
        termo = r.termos[0]
        for f in termo.mantidas:
            mantidas[f] += 1
        for f in termo.descartadas:
            descartadas[f] += 1
    # distribuição marginal exata de "estar entre as k mantidas"
    prob_mantida: Dict[int, Fraction] = {f: Fraction(0) for f in faces}
    prob_descartada: Dict[int, Fraction] = {f: Fraction(0) for f in faces}
    for combo in itertools.product(faces, repeat=t.quantidade):
        ordenado = sorted(range(t.quantidade), key=lambda i: (combo[i], i), reverse=kh)
        for pos, idx in enumerate(ordenado):
            alvo = prob_mantida if pos < k else prob_descartada
            alvo[t.sinal * combo[idx]] += Fraction(1, espaco)
    # As marginais somam k e (n-k): normaliza para virar distribuição de verdade.
    soma_m = sum(prob_mantida.values()) or Fraction(1)
    soma_d = sum(prob_descartada.values()) or Fraction(1)
    prob_mantida = {v: p / soma_m for v, p in prob_mantida.items()}
    prob_descartada = {v: p / soma_d for v, p in prob_descartada.items()}
    mantidas = {t.sinal * f: c for f, c in mantidas.items()}
    descartadas = {t.sinal * f: c for f, c in descartadas.items()}
    total_m = sum(mantidas.values())
    total_d = sum(descartadas.values())
    chi2m, glm = _chi2_multinomial(dict(mantidas), prob_mantida, total_m)
    p_m = chi2_p_valor(chi2m, glm) if total_m else 1.0
    if total_d:
        chi2d, gld = _chi2_multinomial(dict(descartadas), prob_descartada, total_d)
        p_d = chi2_p_valor(chi2d, gld)
    else:
        chi2d, gld, p_d = 0.0, 1, 1.0
    pior = min(p_m, p_d)
    return _t(f"kh/kl imparcial em {expressao}", "J",
              "mantidas e descartadas conferidas contra a marginal exata",
              n, max(chi2m, chi2d), pior,
              f"p(mantidas)={p_m:.4g} p(descartadas)={p_d:.4g}")


# ==========================================================================
# K — escolha ponderada exata
# ==========================================================================
def teste_ponderado(aleat: Aleatoriedade, pesos: Sequence[int], n: int) -> TesteEstatistico:
    itens = list(range(len(pesos)))
    total = sum(pesos)
    cont: Counter = Counter()
    for _ in range(n):
        cont[aleat.escolher_ponderado(itens, list(pesos))] += 1
    probs = {i: Fraction(p, total) for i, p in enumerate(pesos)}
    chi2, gl = _chi2_multinomial(dict(cont), probs, n)
    p = chi2_p_valor(chi2, gl)
    return _t(f"ponderado {list(pesos)}", "K",
              "probabilidade real = peso/Σpesos, sem arredondamento", n, chi2, p,
              f"gl={gl}")


# ==========================================================================
# L — embaralhamento uniforme
# ==========================================================================
def teste_baralhar(aleat: Aleatoriedade, tamanho: int, n: int) -> TesteEstatistico:
    baralho = list(range(tamanho))
    cont: Counter = Counter()
    for _ in range(n):
        cont[tuple(aleat.baralhar(baralho))] += 1
    perms = math.factorial(tamanho)
    probs = {p: Fraction(1, perms) for p in itertools.permutations(baralho)}
    chi2, gl = _chi2_multinomial(dict(cont), probs, n)
    p = chi2_p_valor(chi2, gl)
    # distribuição posicional (cada elemento em cada posição)
    pos: Counter = Counter()
    for _ in range(n):
        for i, v in enumerate(aleat.baralhar(baralho)):
            pos[(v, i)] += 1
    probs_pos = {(v, i): Fraction(1, tamanho * tamanho)
                 for v in baralho for i in range(tamanho)}
    chi2p, glp = _chi2_multinomial(dict(pos), probs_pos, n * tamanho)
    pp = chi2_p_valor(chi2p, glp)
    pior = min(p, pp)
    return _t(f"Fisher-Yates {tamanho} cartas", "L",
              f"todas as {perms} permutações igualmente prováveis", n,
              max(chi2, chi2p), pior,
              f"p(permutações)={p:.4g} p(posições)={pp:.4g}")


# ==========================================================================
# M — prova construtiva de que a rejeição está ativa
# ==========================================================================
def teste_eficiencia_rejeicao(aleat: Aleatoriedade, modulo: int, n: int) -> TesteEstatistico:
    """Mede bytes consumidos por resultado e compara com a taxa teórica.

    Com rejeição e ``k = bit_length(n-1)`` bits, cada tentativa gasta
    ``ceil(k/8)`` bytes e é aceita com probabilidade ``n / 2**k``. Logo o custo
    esperado é ``ceil(k/8) * 2**k / n`` bytes por resultado. Um ``% n`` ingênuo
    gastaria exatamente ``ceil(k/8)`` — e seria enviesado.
    """
    k = (modulo - 1).bit_length()
    nbytes = (k + 7) // 8
    teorico = nbytes * (2 ** k) / modulo
    antes = aleat.consumo()
    for _ in range(n):
        aleat.abaixo(modulo)
    depois = aleat.consumo()
    usado = (depois.bytes_solicitados - antes.bytes_solicitados) / n
    # teste z contra o valor teórico (variância do número de tentativas ~ geométrica)
    var_tentativas = (1.0 - modulo / 2 ** k) / (modulo / 2 ** k) ** 2
    sd = math.sqrt(var_tentativas) * nbytes / math.sqrt(n)
    z = (usado - teorico) / sd if sd > 0 else 0.0
    p = normal_p_valor_bicaudal(z)
    return _t(f"rejeição ativa para abaixo({modulo})", "M",
              "bytes/resultado devem bater com a taxa teórica da rejeição",
              n, z, p,
              f"teórico={teorico:.4f} B/resultado, medido={usado:.4f}; "
              f"ingênuo seria {nbytes:.0f} B")


# ==========================================================================
# N — determinismo por semente
# ==========================================================================
def teste_determinismo(semente: str = "xan-teste", amostra: int = 4096) -> TesteEstatistico:
    a = Aleatoriedade(FonteSemeada(semente, "mundo"))
    b = Aleatoriedade(FonteSemeada(semente, "mundo"))
    c = Aleatoriedade(FonteSemeada(semente + "!", "mundo"))
    d = Aleatoriedade(FonteSemeada(semente, "npcs"))
    x, y, z, w = a.bytes(amostra), b.bytes(amostra), c.bytes(amostra), d.bytes(amostra)
    identico = x == y
    divergente = (x != z) and (x != w)
    ok = identico and divergente
    p = 1.0 if ok else 0.0
    nota = (f"mesma semente reproduz {amostra} bytes: {identico}; "
            f"semente/derivação distintas divergem: {divergente}")
    return _t("determinismo e separação por semente", "N",
              "reprodutibilidade bit a bit + derivações independentes",
              amostra, float(identico and divergente), p, nota)


# ==========================================================================
# O — imparcialidade entre atores (o teste direto contra vantagem narrativa)
# ==========================================================================
def teste_imparcialidade_entre_atores(n: int = 40_000) -> TesteEstatistico:
    """Atores com rótulos opostos rolando a MESMA declaração.

    Se o motor favorecesse alguém por nome, papel ou importância narrativa, as
    taxas de sucesso divergiriam. Teste de homogeneidade qui-quadrado.
    """
    from .resolucao import Declaracao, resolver  # import tardio: evita ciclo

    rotulos = [
        "Herói Predestinado",
        "Figurante Descartável nº 42",
        "Mestre da Sessão",
        "Vilão Final",
        "NPC aleatório sem nome",
        "PROTAGONISTA",
    ]
    aleat = Aleatoriedade(FonteSemeada("imparcialidade-entre-atores", "teste"))
    sucessos: Counter = Counter()
    for rotulo in rotulos:
        decl = Declaracao(
            acao="golpe de espada",
            ator=rotulo,
            atributo="con",
            valor_atributo=14,
            bonus_atributo=2,
            pericia="espada",
            graduacao=3,
            dificuldade=17,
            regras=("ELEMENTO:RELACAO",),
            fatos={"elemento_atacante": "metal", "elemento_alvo": "madeira"},
            contexto={"reino": 4},
        )
        for _ in range(n):
            r = resolver(decl, aleat)
            if r.sucesso:
                sucessos[rotulo] += 1
    total = n * len(rotulos)
    taxa_global = Fraction(sum(sucessos.values()), total)
    esperados = {r: taxa_global * n for r in rotulos}
    chi2 = 0.0
    for r in rotulos:
        e = float(esperados[r])
        chi2 += (sucessos[r] - e) ** 2 / e
    gl = len(rotulos) - 1
    p = chi2_p_valor(chi2, gl)
    detalhe = "; ".join(f"{r[:18]}={sucessos[r]/n*100:.2f}%" for r in rotulos)
    return _t("atores distintos, mesma taxa", "O",
              "homogeneidade das taxas de sucesso entre rótulos de ator",
              total, chi2, p,
              f"gl={gl}, taxa global {float(taxa_global)*100:.2f}% → {detalhe}")


# ==========================================================================
# Bateria completa
# ==========================================================================
def bateria_completa(
    aleat: Optional[Aleatoriedade] = None,
    amostras: int = 60_000,
    amostras_leves: int = 20_000,
    incluir_atores: bool = True,
    atores_amostras: int = 5_000,
    versao_motor: str = "",
) -> CertificadoDeJustica:
    """Roda a bateria inteira e devolve o certificado."""
    if aleat is None:
        aleat = Aleatoriedade(FonteViva())
    if not versao_motor:
        from . import __version__ as versao_motor  # type: ignore

    testes: List[TesteEstatistico] = []

    for lados in (4, 6, 8, 10, 12, 20, 100):
        testes.append(teste_faces(aleat, lados, amostras_leves))
    for mod in (3, 5, 6, 7, 13, 20, 100):
        testes.append(teste_abaixo(aleat, mod, amostras_leves))
    for expr in ("1d20", "2d6", "3d6", "4d6kh1", "2d20kh1", "1d20+5", "3dF"):
        testes.append(teste_distribuicao(aleat, expr, amostras_leves))
    for expr in ("1d20", "2d6", "4d6kh1", "2d20kh1"):
        testes.append(teste_momentos(aleat, expr, amostras))
    testes.append(teste_ks(aleat, amostras_leves))
    testes.append(teste_correlacao_serial(aleat, amostras_leves))
    testes.append(teste_corridas(aleat, amostras_leves))

    bits = [b for byte in aleat.bytes(amostras_leves * 8) for b in
            ((byte >> i) & 1 for i in range(7, -1, -1))]
    testes.append(teste_monobit(bits))
    testes.append(teste_poquer(bits, 4))
    testes.append(teste_maior_corrida(bits))

    testes.append(teste_independencia(aleat, amostras_leves, 6))
    testes.append(teste_manter_imparcial(aleat, "4d6kh1", amostras_leves))
    testes.append(teste_ponderado(aleat, (1, 2, 3, 4, 5), amostras_leves))
    testes.append(teste_ponderado(aleat, (7, 1), amostras_leves))
    testes.append(teste_baralhar(aleat, 4, amostras_leves // 4))
    testes.append(teste_eficiencia_rejeicao(aleat, 7, amostras_leves))
    testes.append(teste_eficiencia_rejeicao(aleat, 100, amostras_leves))
    testes.append(teste_determinismo())
    if incluir_atores:
        testes.append(teste_imparcialidade_entre_atores(atores_amostras))

    reprovados = [t for t in testes if not t.ok]
    duras = [t for t in reprovados if t.falha_dura]
    if duras:
        veredito = "REPROVADO"
    elif reprovados:
        veredito = "APROVADO COM RESSALVA"
    else:
        veredito = "APROVADO"
    total_amostras = sum(t.amostras for t in testes)
    resumo = (
        f"{len(testes)} testes, {total_amostras:,} amostras. "
        f"{len(testes) - len(reprovados)} aprovados, {len(reprovados)} abaixo de "
        f"α={ALFA}, {len(duras)} falhas duras (p<{ALFA_FALHA_DURA:g})."
    ).replace(",", ".")

    return CertificadoDeJustica(
        versao_motor=versao_motor,
        fonte=aleat.fonte.descricao(),
        alfa=ALFA,
        testes=tuple(testes),
        amostras_totais=total_amostras,
        veredito=veredito,
        resumo=resumo,
    )


def emitir_certificado(
    destino_base: str,
    aleat: Optional[Aleatoriedade] = None,
    **kwargs: Any,
) -> Tuple[CertificadoDeJustica, str, str]:
    """Gera o certificado e grava ``.md`` + ``.json`` ao lado."""
    import os
    cert = bateria_completa(aleat, **kwargs)
    pasta = os.path.dirname(os.path.abspath(destino_base))
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    md = destino_base + ".md"
    js = destino_base + ".json"
    import json
    with open(md, "w", encoding="utf-8") as fh:
        fh.write(cert.markdown())
    with open(js, "w", encoding="utf-8") as fh:
        json.dump(cert.json(), fh, ensure_ascii=False, indent=2, sort_keys=True)
    return cert, md, js
