# -*- coding: utf-8 -*-
"""
XAN — Espinha dorsal de aleatoriedade (camada 4: compromisso e revelação).
==========================================================================

Este módulo é o que torna a imparcialidade **provável de verificar**, e não uma
promessa.

O problema clássico do RPG de mesa
----------------------------------
O mestre anuncia "Dificuldade 18". O jogador rola 17. O mestre diz "ah, na
verdade era 16". Ninguém consegue provar nada. Qualquer vantagem narrativa vive
exatamente nesse vão entre *declarar* e *rolar*.

A solução: protocolo commit-reveal
-----------------------------------
1. **ANTES** de qualquer dado, o motor serializa a declaração completa da ação
   (atributo, perícia, dificuldade, modificadores e a regra que autoriza cada
   um), sorteia um sal de 128 bits e publica ``token = SHA-256(sal || declaração)``
   no diário de auditoria.
2. O dado é rolado. O resultado é publicado no diário **amarrado ao token**.
3. **DEPOIS** o motor revela sal + declaração. Qualquer pessoa refaz o hash e
   confere: se a declaração publicada não gera o token anterior ao dado, houve
   adulteração — e o hash aponta onde.

Consequências
-------------
* A dificuldade e os modificadores ficam **fisicamente congelados** antes do
  sorteio. Alterá-los depois exige quebrar SHA-256.
* O sal impede que alguém descubra o conteúdo antes da hora (e impede força
  bruta sobre números pequenos como "DD 17").
* Não existe API para "revelar antes de rolar" nem para "comprometer depois".
  A ordem é imposta por ``resolucao.resolver()`` e verificada por
  ``conferir_diario()``.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .auditoria import DiarioDeAuditoria, canonico, hash_de
from .entropia import Aleatoriedade

__all__ = [
    "Compromisso",
    "comprometer",
    "conferir",
    "verificar_compromisso",
    "rolagem_auditada",
    "RelatorioDeCompromisso",
]


def _token(sal: bytes, payload: str) -> str:
    return hashlib.sha256(sal + payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Compromisso:
    """Um compromisso selado antes da rolagem."""

    token: str
    sal_hex: str
    payload: Dict[str, Any]
    hash_payload: str

    @property
    def canonical(self) -> str:
        return canonico(self.payload)


def comprometer(payload: Dict[str, Any], aleat: Aleatoriedade) -> Compromisso:
    """Cria um compromisso de ocultação (hiding) e integridade (binding)."""
    if not isinstance(payload, dict) or not payload:
        raise ValueError("compromisso exige um dicionário não vazio")
    sal = aleat.bytes(16)
    canon = canonico(payload)
    return Compromisso(
        token=_token(sal, canon),
        sal_hex=sal.hex(),
        payload=payload,
        hash_payload=hash_de(canon),
    )


def rolagem_auditada(
    expressao: str,
    aleat: "Aleatoriedade",
    diario: "DiarioDeAuditoria",
    *,
    ator: str = "mesa",
    contexto: Optional[Dict[str, Any]] = None,
) -> Tuple["Rolagem", Compromisso, int]:
    """Rolagem simples (sem teste de perícia) com o MESMO protocolo de auditoria.

    Ordem: compromisso (hash da expressão antes do dado) → rolagem → revelação
    (sal + payload). Assim nem um ``1d20`` solto na mesa pode ser trocado
    depois de visto: o token já estava gravado no diário encadeado.

    Retorna ``(rolagem, compromisso, indice_no_diario)``.
    """
    from .dados import Rolagem, rolar as _rolar
    payload: Dict[str, Any] = {
        "tipo": "rolagem_simples",
        "expressao": expressao,
        "ator": ator,
        "contexto": dict(contexto or {}),
    }
    comp = comprometer(payload, aleat)
    diario.registrar(
        "compromisso",
        {"token": comp.token, "acao": f"rolar {expressao}", "ator": ator,
         "hash_declaracao": comp.hash_payload},
        ator=ator,
    )
    r = _rolar(expressao, aleat, identificador=comp.token)
    reg = diario.registrar(
        "rolagem",
        {"token": comp.token, "expressao": expressao,
         "faces": list(r.faces()), "dado": r.total, "total": r.total,
         "selo": hash_de(canonico({"expressao": expressao,
                                   "faces": list(r.faces()),
                                   "token": comp.token}))},
        ator=ator,
    )
    diario.registrar(
        "revelacao",
        {"token": comp.token, "sal": comp.sal_hex, "payload": payload},
        ator=ator,
    )
    return r, comp, reg.indice


def verificar_compromisso(compromisso: Compromisso) -> bool:
    """Refaz o hash — usado por terceiros para auditar."""
    try:
        sal = bytes.fromhex(compromisso.sal_hex)
    except ValueError:
        return False
    return _token(sal, canonico(compromisso.payload)) == compromisso.token


@dataclass(frozen=True)
class RelatorioDeCompromisso:
    ok: bool
    compromissos: int
    rolagens: int
    revelacoes: int
    problemas: Tuple[str, ...]

    def texto(self) -> str:
        cab = (
            f"compromissos={self.compromissos} rolagens={self.rolagens} "
            f"revelacoes={self.revelacoes}"
        )
        if self.ok:
            return f"PROTOCOLO OK — {cab}. Toda rolagem foi declarada antes do dado."
        linhas = "\n".join("  • " + p for p in self.problemas)
        return f"PROTOCOLO VIOLADO — {cab}\n{linhas}"


def conferir(diario: DiarioDeAuditoria) -> RelatorioDeCompromisso:
    """Audita a ordem compromisso → rolagem → revelação em todo o diário."""
    problemas: List[str] = []
    compromissos: Dict[str, int] = {}      # token -> índice
    revelacoes: Dict[str, int] = {}        # token -> índice
    rolagens: List[Tuple[str, int]] = []   # (token, índice)

    for reg in diario.registros:
        if reg.tipo == "compromisso":
            tok = reg.conteudo.get("token")
            if tok in compromissos:
                problemas.append(f"token duplicado no índice {reg.indice}")
            compromissos[tok] = reg.indice
        elif reg.tipo == "revelacao":
            tok = reg.conteudo.get("token")
            sal_hex = reg.conteudo.get("sal", "")
            payload = reg.conteudo.get("payload")
            if tok not in compromissos:
                problemas.append(f"revelação sem compromisso no índice {reg.indice}")
            elif payload is not None:
                if not isinstance(payload, dict):
                    problemas.append(f"payload não é dicionário no índice {reg.indice}")
                else:
                    esperado = _token(bytes.fromhex(sal_hex), canonico(payload))
                    if esperado != tok:
                        problemas.append(
                            f"revelação não bate com o token no índice {reg.indice}"
                        )
            revelacoes[tok] = reg.indice
        elif reg.tipo == "rolagem":
            tok = reg.conteudo.get("token")
            if tok not in compromissos:
                problemas.append(
                    f"rolagem no índice {reg.indice} sem compromisso anterior"
                )
            elif compromissos[tok] > reg.indice:
                problemas.append(
                    f"rolagem no índice {reg.indice} ANTES do compromisso "
                    f"(índice {compromissos[tok]})"
                )
            rolagens.append((tok, reg.indice))

    for tok, idx in rolagens:
        if tok in revelacoes and revelacoes[tok] < idx:
            problemas.append(
                f"revelação do token {tok[:12]}… apareceu antes da rolagem {idx}"
            )

    return RelatorioDeCompromisso(
        ok=not problemas,
        compromissos=len(compromissos),
        rolagens=len(rolagens),
        revelacoes=len(revelacoes),
        problemas=tuple(problemas),
    )
