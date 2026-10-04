# -*- coding: utf-8 -*-
"""
XAN — Espinha dorsal de aleatoriedade (camada 3: auditoria).
============================================================

Diário **append-only** encadeado por hash. Cada registro contém o SHA-256 do
registro anterior; portanto:

    * apagar um registro no meio quebra a cadeia inteira;
    * editar um registro (ex.: trocar a Dificuldade depois de ver o dado)
      quebra a cadeia a partir dali;
    * ``verificar()`` refaz todos os hashes e aponta exatamente onde houve
      adulteração.

Como isso impede manipulação na mesa
------------------------------------
O mestre publica o ``hash da cabeça`` (ou o sela em arquivo/commit) ANTES da
rolagem. Depois da rolagem, qualquer pessoa pode rodar ``xan auditoria
verificar`` e comparar a cabeça: se o número não bater, alguém mexeu. O dado é
público e imutável — não existe "vantagem narrativa" possível sem deixar rastro.

O formato é JSONL (um JSON canônico por linha) para ser legível por humanos,
difável no git e processável por qualquer linguagem.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

__all__ = [
    "canonico", "hash_de",
    "canonico",
    "hash_de",
    "Registro",
    "RelatorioDeVerificacao",
    "DiarioDeAuditoria",
    "HASH_GENESIS",
]

HASH_GENESIS = "0" * 64
_ALGORITMO = "sha256"


def _chave_canonica(chave: Any) -> str:
    """Converte uma chave de dicionário na string que o JSON produziria.

    Espelha exatamente o que ``json.dumps`` faz com chaves não-string:
    ``True``→"true", ``False``→"false", ``None``→"null", ``int``→repr,
    ``float``→repr. Qualquer outro tipo é recusado.
    """
    if isinstance(chave, str):
        return chave
    if isinstance(chave, bool):
        return "true" if chave else "false"
    if isinstance(chave, int):
        return repr(chave)
    if isinstance(chave, float):
        if not math.isfinite(chave):
            raise ValueError(
                f"chave de dicionário não-finita ({chave!r}) não tem forma "
                "canônica portátil")
        return repr(chave)
    if chave is None:
        return "null"
    raise TypeError(
        f"chave de dicionário do tipo {type(chave).__name__} não é "
        "serializável de forma canônica; use str, int, float, bool ou None")


def _normalizar(objeto: Any) -> Any:
    """Reescreve o objeto para que a serialização seja estável sob round-trip.

    O problema que isto resolve é sutil e foi encontrado em uso real:
    ``json.dumps({1: "a", 10: "j"}, sort_keys=True)`` ordena as chaves
    **numericamente** (1, 10), mas depois do round-trip as chaves viram strings e
    ``sort_keys`` ordena **lexicograficamente** (1, 10 → "1", "10" continua, mas
    {1,2,10,20} vira "1","10","2","20"). O hash calculado na escrita não bate
    com o recalculado na leitura — um falso positivo de adulteração, que é pior
    que adulteração de verdade porque destrói a confiança na cadeia.

    Normalizar as chaves para ``str`` ANTES de serializar torna as duas formas
    idênticas. Colisões (por exemplo ``{1: "a", "1": "b"}``) são recusadas em
    vez de silently sobrescritas.
    """
    if isinstance(objeto, dict):
        saida: Dict[str, Any] = {}
        for chave, valor in objeto.items():
            k = _chave_canonica(chave)
            if k in saida:
                raise ValueError(
                    f"chaves {chave!r} e outra anterior colidem na forma "
                    f"canônica {k!r}; o registro seria ambíguo")
            saida[k] = _normalizar(valor)
        return saida
    if isinstance(objeto, (list, tuple)):
        return [_normalizar(v) for v in objeto]
    if isinstance(objeto, float) and not math.isfinite(objeto):
        raise ValueError(f"valor não-finito {objeto!r} não é JSON portátil")
    return objeto


def canonico(objeto: Any) -> str:
    """Serialização JSON determinística (chaves ordenadas, sem espaços).

    É a ÚNICA função de serialização usada para hashing em todo o projeto:
    assim o hash não depende de versão de biblioteca nem de ordem de dicionário.

    **Invariantes** (cobertas por teste):
      * ``canonico(x) == canonico(json.loads(canonico(x)))`` para todo x aceito;
      * a ordem das chaves no dict de origem não importa;
      * chave não-serializável ou colisão de chaves levanta erro, nunca passa.
    """
    return json.dumps(_normalizar(objeto), sort_keys=True,
                      separators=(",", ":"), ensure_ascii=False)


def hash_de(texto: str) -> str:
    return hashlib.new(_ALGORITMO, texto.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Registro:
    indice: int
    tempo_ns: int
    tipo: str
    ator: str
    conteudo: Dict[str, Any]
    hash_anterior: str
    hash: str

    def payload_canonico(self) -> str:
        """O que efetivamente entra no hash (sem o próprio campo ``hash``)."""
        return canonico(
            {
                "i": self.indice,
                "t": self.tempo_ns,
                "tipo": self.tipo,
                "ator": self.ator,
                "conteudo": self.conteudo,
                "prev": self.hash_anterior,
            }
        )

    def como_dict(self) -> Dict[str, Any]:
        return {
            "i": self.indice,
            "t": self.tempo_ns,
            "tipo": self.tipo,
            "ator": self.ator,
            "conteudo": self.conteudo,
            "prev": self.hash_anterior,
            "hash": self.hash,
        }


@dataclass(frozen=True)
class RelatorioDeVerificacao:
    ok: bool
    total: int
    primeira_falha: Optional[int]
    motivo: str
    hash_cabeca: str
    raiz_merkle: str

    def texto(self) -> str:
        if self.ok:
            return (
                f"INTEGRIDADE OK — {self.total} registros verificados.\n"
                f"  cabeça   : {self.hash_cabeca}\n"
                f"  raiz merkle: {self.raiz_merkle}"
            )
        return (
            f"INTEGRIDADE VIOLADA — {self.total} registros, falha no índice "
            f"{self.primeira_falha}.\n  motivo: {self.motivo}"
        )


class DiarioDeAuditoria:
    """Arquivo JSONL encadeado por hash."""

    def __init__(self, caminho: str | os.PathLike, criar: bool = True) -> None:
        self.caminho = os.fspath(caminho)
        self._registros: List[Registro] = []
        self._cabeca = HASH_GENESIS
        if os.path.exists(self.caminho):
            self._carregar()
        elif criar:
            pasta = os.path.dirname(os.path.abspath(self.caminho))
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            open(self.caminho, "a", encoding="utf-8").close()
        else:
            raise FileNotFoundError(self.caminho)

    # -- leitura -----------------------------------------------------------
    def _carregar(self) -> None:
        with open(self.caminho, "r", encoding="utf-8") as fh:
            for linha in fh:
                linha = linha.strip()
                if not linha:
                    continue
                bruto = json.loads(linha)
                reg = Registro(
                    indice=bruto["i"],
                    tempo_ns=bruto["t"],
                    tipo=bruto["tipo"],
                    ator=bruto.get("ator", ""),
                    conteudo=bruto.get("conteudo", {}),
                    hash_anterior=bruto["prev"],
                    hash=bruto["hash"],
                )
                self._registros.append(reg)
        if self._registros:
            self._cabeca = self._registros[-1].hash

    # -- escrita -----------------------------------------------------------
    def registrar(
        self,
        tipo: str,
        conteudo: Dict[str, Any],
        ator: str = "",
        tempo_ns: Optional[int] = None,
    ) -> Registro:
        """Anexa um registro. Nunca reescreve o passado."""
        if not isinstance(tipo, str) or not tipo:
            raise ValueError("tipo é obrigatório")
        if not isinstance(conteudo, dict):
            raise TypeError("conteúdo deve ser um dicionário JSON-serializável")
        indice = len(self._registros)
        reg = Registro(
            indice=indice,
            tempo_ns=int(time.time_ns() if tempo_ns is None else tempo_ns),
            tipo=tipo,
            ator=ator,
            conteudo=conteudo,
            hash_anterior=self._cabeca,
            hash="",
        )
        reg = Registro(
            indice=reg.indice,
            tempo_ns=reg.tempo_ns,
            tipo=reg.tipo,
            ator=reg.ator,
            conteudo=reg.conteudo,
            hash_anterior=reg.hash_anterior,
            hash=hash_de(reg.payload_canonico()),
        )
        with open(self.caminho, "a", encoding="utf-8") as fh:
            fh.write(canonico(reg.como_dict()) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        self._registros.append(reg)
        self._cabeca = reg.hash
        return reg

    # -- consultas ---------------------------------------------------------
    @property
    def registros(self) -> Tuple[Registro, ...]:
        return tuple(self._registros)

    @property
    def cabeca(self) -> str:
        return self._cabeca

    def __len__(self) -> int:
        return len(self._registros)

    def por_tipo(self, tipo: str) -> List[Registro]:
        return [r for r in self._registros if r.tipo == tipo]

    def raiz_merkle(self) -> str:
        """Raiz de Merkle de todos os registros — atestação compacta."""
        nivel = [hash_de(r.payload_canonico()) for r in self._registros]
        if not nivel:
            return HASH_GENESIS
        while len(nivel) > 1:
            proximo = []
            for i in range(0, len(nivel) - 1, 2):
                proximo.append(hash_de(nivel[i] + nivel[i + 1]))
            if len(nivel) % 2:
                proximo.append(hash_de(nivel[-1] + nivel[-1]))
            nivel = proximo
        return nivel[0]

    # -- verificação -------------------------------------------------------
    def verificar(self) -> RelatorioDeVerificacao:
        anterior = HASH_GENESIS
        for pos, reg in enumerate(self._registros):
            if reg.indice != pos:
                return RelatorioDeVerificacao(
                    ok=False,
                    total=len(self._registros),
                    primeira_falha=pos,
                    motivo=f"índice esperado {pos}, encontrado {reg.indice}",
                    hash_cabeca=self._cabeca,
                    raiz_merkle=self.raiz_merkle(),
                )
            if reg.hash_anterior != anterior:
                return RelatorioDeVerificacao(
                    ok=False,
                    total=len(self._registros),
                    primeira_falha=pos,
                    motivo="elo quebrado: hash anterior não confere",
                    hash_cabeca=self._cabeca,
                    raiz_merkle=self.raiz_merkle(),
                )
            recalculado = hash_de(reg.payload_canonico())
            if recalculado != reg.hash:
                return RelatorioDeVerificacao(
                    ok=False,
                    total=len(self._registros),
                    primeira_falha=pos,
                    motivo="conteúdo adulterado: hash não bate com o payload",
                    hash_cabeca=self._cabeca,
                    raiz_merkle=self.raiz_merkle(),
                )
            anterior = reg.hash
        cabeca = anterior
        ok = cabeca == self._cabeca
        return RelatorioDeVerificacao(
            ok=ok,
            total=len(self._registros),
            primeira_falha=None if ok else len(self._registros),
            motivo="" if ok else "cabeça em memória difere da cadeia recalculada",
            hash_cabeca=cabeca,
            raiz_merkle=self.raiz_merkle(),
        )

    # -- selagem pública ---------------------------------------------------
    def selar(self, destino: str | os.PathLike, nota: str = "") -> str:
        """Anexa a cabeça atual a um arquivo de selos públicos.

        Selos servem para publicação externa (chat, git, cartório digital):
        quem tem o selo anterior à sessão prova que nada foi alterado depois.
        """
        destino = os.fspath(destino)
        pasta = os.path.dirname(os.path.abspath(destino))
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        linha = canonico(
            {
                "t": int(time.time_ns()),
                "registros": len(self._registros),
                "cabeca": self._cabeca,
                "raiz_merkle": self.raiz_merkle(),
                "nota": nota,
            }
        )
        with open(destino, "a", encoding="utf-8") as fh:
            fh.write(linha + "\n")
        return self._cabeca
