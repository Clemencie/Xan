# -*- coding: utf-8 -*-
"""
XAN — Espinha dorsal de aleatoriedade (camada 1: entropia).
===========================================================

Este módulo é o alicerce de TODO o acaso do sistema. Nada no XAN joga dados sem
passar por aqui. As propriedades garantidas são:

1. **Sem viés de módulo (modulo bias)**
   ``abaixo(n)`` usa *rejeição* (rejection sampling) sobre uma máscara de bits,
   nunca ``rand() % n``. Distribuição exatamente uniforme para qualquer ``n``.

2. **Inteiros apenas no caminho crítico**
   Nenhum ``float`` participa da geração ou da amostragem. Ponto flutuante é
   dependente de plataforma/compilador e destruiria a reprodutibilidade.

3. **Dois modos, uma única matemática**
   * ``FonteViva``    → entropia do sistema operacional (CSPRNG do kernel).
                        Imprevisível. Usada nas rolagens de mesa.
   * ``FonteSemeada`` → HMAC-DRBG (NIST SP 800-90A §10.1.2, SHA-256).
                        Reproduzível bit a bit a partir da semente.
                        Usada na geração procedural de mundo/NPCs.
   Ambas alimentam o MESMO ``Aleatoriedade``; portanto a imparcialidade é
   compartilhada e não existe "dado do jogador" diferente do "dado do mestre".

4. **Sem gancho narrativo**
   Não há aqui nenhuma função que aceite contexto, intenção, nome de personagem
   ou estado de história para influenciar o resultado. A API recebe apenas
   números e sequências. Impossível favorecer por narrativa usando este módulo.

5. **Contratos de reutilização**
   ``Aleatoriedade`` é *append-only* no consumo: cada chamada avança o estado.
   Não existe API de "desfazer", "repetir até sair o que eu quero" ou "escolher
   o melhor de N" fora das regras explícitas de rolagem (``kh``/``kl`` em dados).
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

__all__ = [
    "HMACDRBG",
    "FonteDeBytes",
    "FonteViva",
    "FonteSemeada",
    "Aleatoriedade",
    "normalizar_semente",
    "ERRO_AMOSTRA_VAZIA",
]

ERRO_AMOSTRA_VAZIA = "amostra vazia: não há como sortear sem favorecer ninguém"

_HASH = "sha256"
_HLEN = hashlib.sha256().digest_size  # 32
_MAX_REQUESTS = 2 ** 48  # limite de SP 800-90A antes de exigir reseed


class PrecisaRessemear(RuntimeError):
    """O DRBG atingiu o limite de requisições e precisa de nova entropia."""


# --------------------------------------------------------------------------
# HMAC-DRBG — NIST SP 800-90A, seção 10.1.2
# --------------------------------------------------------------------------
class HMACDRBG:
    """Gerador determinístico criptográfico (HMAC-DRBG / SHA-256).

    Implementação direta da construção do SP 800-90A. Determinística:
    a mesma (entropia, nonce, personalização) produz a mesma sequência
    de bytes para sempre, em qualquer plataforma.
    """

    __slots__ = ("_k", "_v", "reseed_counter", "personalizacao", "chamadas")

    def __init__(
        self,
        entropia: bytes,
        nonce: bytes = b"",
        personalizacao: bytes = b"",
    ) -> None:
        if not isinstance(entropia, bytes):
            raise TypeError("entropia deve ser bytes")
        if len(entropia) < 32:
            # SP 800-90A exige >= security_strength/8 bits de entropia real.
            raise ValueError(
                "entropia insuficiente: mínimo 32 bytes para força de 256 bits"
            )
        self._k = b"\x00" * _HLEN
        self._v = b"\x01" * _HLEN
        self.personalizacao = personalizacao
        self.reseed_counter = 1
        self.chamadas = 0
        self._update(entropia + nonce + personalizacao)

    # -- primitivas --------------------------------------------------------
    @staticmethod
    def _mac(chave: bytes, dado: bytes) -> bytes:
        return hmac.new(chave, dado, _HASH).digest()

    def _update(self, material: bytes = b"") -> None:
        self._k = self._mac(self._k, self._v + b"\x00" + material)
        self._v = self._mac(self._k, self._v)
        if material:
            self._k = self._mac(self._k, self._v + b"\x01" + material)
            self._v = self._mac(self._k, self._v)

    # -- API pública -------------------------------------------------------
    def ressemear(self, entropia: bytes, adicional: bytes = b"") -> None:
        if len(entropia) < 32:
            raise ValueError("reseed exige >= 32 bytes de entropia")
        self._update(entropia + adicional)
        self.reseed_counter = 1

    def gerar(self, n: int, adicional: bytes = b"") -> bytes:
        """Produz ``n`` bytes pseudoaleatórios."""
        if n <= 0:
            raise ValueError("n deve ser positivo")
        if self.reseed_counter > _MAX_REQUESTS:
            raise PrecisaRessemear("limite de requisições do DRBG excedido")
        if adicional:
            self._update(adicional)
        saida = bytearray()
        while len(saida) < n:
            self._v = self._mac(self._k, self._v)
            saida += self._v
        self._update(adicional)
        self.reseed_counter += 1
        self.chamadas += 1
        return bytes(saida[:n])

    def instantaneo(self) -> Tuple[bytes, bytes, int]:
        """Fotografia do estado interno — somente para testes/reprodução."""
        return self._k, self._v, self.reseed_counter


# --------------------------------------------------------------------------
# Fontes de bytes
# --------------------------------------------------------------------------
class FonteDeBytes:
    """Contrato: entregar ``n`` bytes imprevisíveis ou deterministicamente estáveis."""

    modo = "abstrato"
    previsivel = True

    def bytes(self, n: int) -> bytes:  # pragma: no cover - abstrato
        raise NotImplementedError

    def descricao(self) -> str:  # pragma: no cover - abstrato
        raise NotImplementedError


class FonteViva(FonteDeBytes):
    """Entropia do sistema operacional (CSPRNG do kernel).

    Usada nas rolagens de mesa: ninguém — nem o mestre, nem o código — consegue
    prever ou escolher a saída. A cada 1024 requisições fazemos um reseed
    explícito com entropia fresca para eliminar qualquer risco de estado
    comprometido.
    """

    modo = "vivo"
    previsivel = False
    _RESEED_A_CADA = 1024

    __slots__ = ("_drbg", "_contador", "_origem")

    def __init__(self, personalizacao: bytes = b"") -> None:
        self._origem = "os.urandom"
        seed = os.urandom(64)
        nonce = os.urandom(16) + str(time.time_ns()).encode()
        self._drbg = HMACDRBG(seed, nonce, b"xan/vivo|" + personalizacao)
        self._contador = 0

    def bytes(self, n: int) -> bytes:
        self._contador += 1
        if self._contador >= self._RESEED_A_CADA:
            self._drbg.ressemear(os.urandom(64), str(time.time_ns()).encode())
            self._contador = 0
        # Mistura adicional por chamada: mesmo que alguém conseguisse observar o
        # estado interno, o resultado desta chamada dependeria de entropia nova.
        return self._drbg.gerar(n, os.urandom(16))

    def descricao(self) -> str:
        return "FonteViva(os.urandom + HMAC-DRBG SHA-256, reseed a cada 1024)"


class FonteSemeada(FonteDeBytes):
    """HMAC-DRBG derivado de uma semente textual — 100% reprodutível.

    Usada para mundo procedural, NPCs e tudo que precise ser compartilhado,
    reaberto e auditado. Duas pessoas com a mesma semente geram o mesmo mundo.
    """

    modo = "semeado"
    previsivel = True

    __slots__ = ("_drbg", "semente", "derivacao", "personalizacao")

    def __init__(self, semente: str | bytes | int, derivacao: str = "") -> None:
        self.semente = semente
        self.derivacao = derivacao
        material = normalizar_semente(semente)
        self.personalizacao = b"xan/semeada|" + derivacao.encode("utf-8")
        # Derivação de chave: HKDF-extract/expand simplificado e determinístico.
        prk = hmac.new(b"xan-v1-salt", material, _HASH).digest()
        nonce = hmac.new(prk, b"nonce|" + derivacao.encode("utf-8"), _HASH).digest()[:16]
        entropia = hmac.new(prk, b"entropy|0", _HASH).digest() + hmac.new(
            prk, b"entropy|1", _HASH).digest()
        self._drbg = HMACDRBG(entropia, nonce, self.personalizacao)

    def bytes(self, n: int) -> bytes:
        return self._drbg.gerar(n)

    def descricao(self) -> str:
        s = self.semente
        if isinstance(s, bytes):
            s = s.hex()
        return f"FonteSemeada(HMAC-DRBG SHA-256, semente={s!r}, derivacao={self.derivacao!r})"


def normalizar_semente(semente: str | bytes | int) -> bytes:
    """Converte qualquer semente em 64 bytes determinísticos."""
    if isinstance(semente, bytes):
        material = semente
    elif isinstance(semente, int):
        material = str(semente).encode("utf-8")
    elif isinstance(semente, str):
        material = semente.encode("utf-8")
    else:
        raise TypeError("semente deve ser str, bytes ou int")
    if not material:
        raise ValueError("semente vazia")
    # Estica para 64 bytes com dois encadeamentos HMAC independentes.
    a = hashlib.sha512(b"xan|seed|" + material).digest()
    return a


# --------------------------------------------------------------------------
# Fachada de sorteio imparcial
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class RegistroDeConsumo:
    """Contabilidade transparente de quanto acaso foi consumido."""

    chamadas: int
    bytes_solicitados: int


class Aleatoriedade:
    """Todas as operações de sorteio do XAN passam por aqui.

    Regras de imparcialidade:
      * pesos devem ser **inteiros não negativos** (nada de float);
      * nenhuma função aceita texto livre que altere probabilidades;
      * toda função é exata: a probabilidade declarada é a probabilidade real.
    """

    __slots__ = ("fonte", "_chamadas", "_bytes")

    def __init__(self, fonte: FonteDeBytes | None = None) -> None:
        self.fonte = fonte if fonte is not None else FonteViva()
        self._chamadas = 0
        self._bytes = 0

    # -- primitiva raiz ----------------------------------------------------
    def bytes(self, n: int) -> bytes:
        if n <= 0:
            raise ValueError("n deve ser positivo")
        self._chamadas += 1
        self._bytes += n
        return self.fonte.bytes(n)

    def consumo(self) -> RegistroDeConsumo:
        return RegistroDeConsumo(self._chamadas, self._bytes)

    # -- inteiro uniforme sem viés ----------------------------------------
    def abaixo(self, n: int) -> int:
        """Inteiro uniforme em ``[0, n-1]`` via rejeição. Exatamente uniforme."""
        if n <= 0:
            raise ValueError("n deve ser positivo")
        if n == 1:
            return 0
        k = (n - 1).bit_length()          # bits necessários
        nbytes = (k + 7) // 8
        mascara = (1 << k) - 1
        while True:
            v = int.from_bytes(self.bytes(nbytes), "big") & mascara
            if v < n:
                return v

    def entre(self, minimo: int, maximo: int) -> int:
        """Inteiro uniforme em ``[minimo, maximo]`` (inclusivo)."""
        if minimo > maximo:
            raise ValueError("mínimo maior que máximo")
        return minimo + self.abaixo(maximo - minimo + 1)

    def moeda(self) -> bool:
        return self.abaixo(2) == 1

    # -- coleções ----------------------------------------------------------
    def escolher(self, sequencia: Sequence):
        """Sorteia um elemento. Sequência vazia é ERRO, nunca 'padrão silencioso'."""
        if not isinstance(sequencia, Sequence):
            sequencia = list(sequencia)
        if len(sequencia) == 0:
            raise ValueError(ERRO_AMOSTRA_VAZIA)
        return sequencia[self.abaixo(len(sequencia))]

    def escolher_ponderado(self, itens: Sequence, pesos: Sequence[int]):
        """Sorteia ``itens[i]`` com probabilidade ``pesos[i]/sum(pesos)``.

        Exato: reduz-se a ``abaixo(total)`` com pesos inteiros, logo não há
        erro de arredondamento nem viés.
        """
        if len(itens) != len(pesos):
            raise ValueError("itens e pesos precisam ter o mesmo tamanho")
        if len(itens) == 0:
            raise ValueError(ERRO_AMOSTRA_VAZIA)
        total = 0
        for p in pesos:
            if not isinstance(p, int) or isinstance(p, bool):
                raise TypeError(f"peso deve ser int, veio {type(p).__name__}")
            if p < 0:
                raise ValueError("peso negativo não existe")
            total += p
        if total <= 0:
            raise ValueError("soma dos pesos deve ser positiva")
        alvo = self.abaixo(total)
        acum = 0
        for item, p in zip(itens, pesos):
            acum += p
            if alvo < acum:
                return item
        raise AssertionError("falha lógica inalcançável em escolher_ponderado")

    def amostrar(self, sequencia: Sequence, k: int) -> List:
        """``k`` elementos distintos, sem reposição (seleção parcial de Fisher-Yates)."""
        pool = list(sequencia)
        if k < 0:
            raise ValueError("k negativo")
        if k > len(pool):
            raise ValueError("k maior que o tamanho da amostra")
        for i in range(k):
            j = i + self.abaixo(len(pool) - i)
            pool[i], pool[j] = pool[j], pool[i]
        return pool[:k]

    def baralhar(self, sequencia: Iterable) -> List:
        """Fisher-Yates completo — todas as permutações igualmente prováveis."""
        pool = list(sequencia)
        for i in range(len(pool) - 1, 0, -1):
            j = self.abaixo(i + 1)
            pool[i], pool[j] = pool[j], pool[i]
        return pool

    def unico(self) -> str:
        """Identificador aleatório de 128 bits (hex)."""
        return self.bytes(16).hex()
