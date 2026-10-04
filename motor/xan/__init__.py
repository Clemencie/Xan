# -*- coding: utf-8 -*-
"""
XAN — 仙道 · Rios e Lagos
=========================

Sistema completo de RPG de mesa ambientado no mundo de *murim/wuxia/xianxia*
inspirado em **Amazing Cultivation Simulator**, com uma espinha dorsal de
aleatoriedade auditável e **imune a vantagem narrativa**.

Camadas do motor (de baixo para cima):

    entropia    → HMAC-DRBG (SP 800-90A) e entropia viva do SO; amostragem
                  por rejeição, sem viés de módulo, só inteiros.
    dados       → notação de dados (1d20, 4d6kh1, 2d6!, d%, dF) com matemática
                  exata em ``fractions.Fraction``.
    auditoria   → diário append-only encadeado por SHA-256 + raiz de Merkle.
    compromisso → protocolo commit-reveal: a ação é selada ANTES do dado.
    regras      → registro fechado de modificadores, recalculados a partir de
                  fatos objetivos. Sem regra publicada, sem bônus.
    resolucao   → Mecânica Central (d20) e prova estrutural de invariantes.

Depois vêm as camadas de jogo: ``elementos``, ``reinos``, ``personagens``,
``npcs``, ``mundo``, ``combate``, ``seitas``, ``artes``, ``bestiario``,
``calendario``, ``justica`` e ``cli``.
"""

from __future__ import annotations

__version__ = "1.0.0"
__nome__ = "XAN — 仙道 · Rios e Lagos"
__motor__ = "Motor do Destino Imparcial (MDI)"

from .entropia import Aleatoriedade, FonteSemeada, FonteViva
from .dados import rolar, Rolagem
from .auditoria import DiarioDeAuditoria
from .resolucao import Declaracao, Resultado, resolver, teste_oposto

__all__ = [
    "__version__",
    "__nome__",
    "__motor__",
    "Aleatoriedade",
    "FonteSemeada",
    "FonteViva",
    "rolar",
    "Rolagem",
    "DiarioDeAuditoria",
    "Declaracao",
    "Resultado",
    "resolver",
    "teste_oposto",
]
