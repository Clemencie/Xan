# -*- coding: utf-8 -*-
"""
XAN — Espinha dorsal de aleatoriedade (camada 5: resolução).
============================================================

A Mecânica Central do jogo e a prova estrutural de imparcialidade.

    Resultado = d20 + Bônus de Atributo + Graduação de Perícia
                    + Σ (regras recalculadas a partir de fatos objetivos)
                ≥ Dificuldade

Por que aqui não cabe vantagem narrativa
----------------------------------------
1. A declaração é **congelada e comprometida por hash antes do dado**
   (``compromisso.py`` + ``auditoria.py``).
2. Os modificadores não são números informados: são **códigos de regra** que o
   motor re-deriva dos fatos (``regras.py``). Declarar +2 sem fato que o
   sustente é impossível.
3. ``Resultado`` é ``frozen``; ``__post_init__`` refaz a conta e aborta se
   houver divergência. Não existe setter, nem cópia mutável, nem método de
   ajuste.
4. Esta API não expõe — e ``verificar_invariantes()`` prova que não expõe —
   funções de re-rolagem, substituição de resultado ou "melhor de N".
5. O dado e o sal do compromisso vêm da mesma fonte; não há "dado do mestre" e
   "dado do jogador".

O que é um modificador legítimo, então? Uma **regra publicada**, citada por
código, aplicável a qualquer personagem nas mesmas condições. Sorte não é
narrativa: Sorte é atributo, entra na conta antes do dado e vale para todos.
"""

from __future__ import annotations

import inspect
import sys
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .auditoria import DiarioDeAuditoria, canonico, hash_de
from .compromisso import comprometer
from .dados import Rolagem, rolar
from .entropia import Aleatoriedade
from .regras import ModificadorIlegal, REGISTRO, conflitos, valor_de

__all__ = [
    "ATRIBUTOS",
    "Atributo",
    "DIFICULDADES",
    "GRAUS",
    "Declaracao",
    "ModificadorAplicado",
    "Resultado",
    "ResultadoOposto",
    "DeclaracaoInvalida",
    "resolver",
    "teste_oposto",
    "verificar_invariantes",
    "RelatorioDeInvariantes",
]


class DeclaracaoInvalida(ValueError):
    """A declaração da ação viola as regras e foi recusada antes de qualquer dado."""


# --------------------------------------------------------------------------
# Atributos — LIVRO cap. 4
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Atributo:
    chave: str
    nome: str
    chines: str
    pinyin: str
    elemento: str
    virtude: str
    virtude_chines: str
    governa: str


ATRIBUTOS: Dict[str, Atributo] = {a.chave: a for a in (
    Atributo("per", "Percepção", "感知", "Gǎnzhī", "agua",
             "Sabedoria", "智 Zhì",
             "Sentidos, Sense Qi, iniciativa, alquimia, diagnóstico, percepção de formações."),
    Atributo("con", "Constituição", "體質", "Tǐzhì", "metal",
             "Retidão", "義 Yì",
             "Vitalidade, Qi máximo, resistência a dano, veneno e frio/calor, cultivo corporal."),
    Atributo("cha", "Carisma", "魅力", "Mèilì", "fogo",
             "Propriedade", "禮 Lǐ",
             "Face, persuasão, liderança, diplomacia entre seitas, Fé (Shendao)."),
    Atributo("int", "Inteligência", "悟性", "Wùxìng", "madeira",
             "Benevolência", "仁 Rén",
             "Compreensão (悟), estudo de manuais, formações, talismãs, estratégia."),
    Atributo("luk", "Sorte", "氣運", "Qìyùn", "nenhum",
             "Fio do Destino", "緣 Yuán",
             "Encontros fortuitos, qualidade de tesouros, eventos do mundo. Fora do ciclo Wuxing."),
    Atributo("pot", "Potencial", "根骨", "Gēngǔ", "terra",
             "Integridade", "信 Xìn",
             "Qualidade da Raiz Espiritual: velocidade de cultivo e teto do reino alcançável."),
)}

_ATRIBUTO_MIN = 1
_ATRIBUTO_MAX = 30
_BONUS_MIN = -5
_BONUS_MAX = 10
_GRADUACAO_MAX = 5
_DIFICULDADE_MIN = 1
_DIFICULDADE_MAX = 60


def bonus_de_atributo(valor: int) -> int:
    """Bônus = floor((Atributo − 10) / 2).

    Atributo 10 é o mortal mediano (+0). A divisão inteira do Python arredonda
    para −∞, o que dá a escada padrão: 1→−5, 8→−1, 10→0, 12→+1, 20→+5, 30→+10.
    """
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise DeclaracaoInvalida("atributo deve ser inteiro")
    if not (_ATRIBUTO_MIN <= valor <= _ATRIBUTO_MAX):
        raise DeclaracaoInvalida(
            f"atributo {valor} fora da faixa [{_ATRIBUTO_MIN},{_ATRIBUTO_MAX}]"
        )
    return (valor - 10) // 2


_bonus = bonus_de_atributo


# --------------------------------------------------------------------------
# Dificuldades — LIVRO cap. 3.3
# --------------------------------------------------------------------------
DIFICULDADES: Dict[str, int] = {
    "trivial": 5,
    "facil": 10,
    "media": 15,
    "dificil": 20,
    "muito_dificil": 25,
    "heroica": 30,
    "sobrenatural": 35,
    "imortal": 40,
    "proibida": 50,
}

# --------------------------------------------------------------------------
# Graus de sucesso — LIVRO cap. 3.4 (pura aritmética de margem)
# --------------------------------------------------------------------------
FRACASSO_CRITICO = "fracasso_critico"
FRACASSO = "fracasso"
SUCESSO = "sucesso"
SUCESSO_MAIOR = "sucesso_maior"
TRIUNFO = "triunfo"
SUCESSO_CRITICO = "sucesso_critico"

GRAUS: Tuple[str, ...] = (
    FRACASSO_CRITICO, FRACASSO, SUCESSO, SUCESSO_MAIOR, TRIUNFO, SUCESSO_CRITICO,
)
_GRAUS_SUCESSO = frozenset({SUCESSO, SUCESSO_MAIOR, TRIUNFO, SUCESSO_CRITICO})


def grau_por_margem(margem: int) -> str:
    if margem < 0:
        return FRACASSO
    if margem <= 4:
        return SUCESSO
    if margem <= 9:
        return SUCESSO_MAIOR
    return TRIUNFO


@dataclass(frozen=True)
class ModificadorAplicado:
    codigo: str
    valor: int
    capitulo: str
    descricao: str


# --------------------------------------------------------------------------
# Declaração (pré-rolagem, congelada)
# --------------------------------------------------------------------------
def _validar_json_seguro(objeto: Any, caminho: str = "fatos") -> None:
    if isinstance(objeto, bool):
        return
    if objeto is None or isinstance(objeto, str) or isinstance(objeto, int):
        return
    if isinstance(objeto, float):
        raise DeclaracaoInvalida(
            f"{caminho}: float proibido no caminho crítico (use int)"
        )
    if isinstance(objeto, (list, tuple)):
        for i, v in enumerate(objeto):
            _validar_json_seguro(v, f"{caminho}[{i}]")
        return
    if isinstance(objeto, dict):
        for k, v in objeto.items():
            if not isinstance(k, str):
                raise DeclaracaoInvalida(f"{caminho}: chave não textual {k!r}")
            _validar_json_seguro(v, f"{caminho}.{k}")
        return
    raise DeclaracaoInvalida(f"{caminho}: tipo não serializável {type(objeto).__name__}")


@dataclass(frozen=True)
class Declaracao:
    """Tudo que precisa existir ANTES do dado. Nada pode ser acrescentado depois."""

    acao: str
    ator: str
    atributo: str
    dificuldade: int
    alvo: str = ""
    pericia: str = ""
    graduacao: int = 0
    bonus_atributo: int = 0
    valor_atributo: int = 10
    regras: Tuple[str, ...] = ()
    fatos: Mapping[str, Any] = field(default_factory=dict)
    expressao: str = "1d20"
    contexto: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.acao, str) or not self.acao.strip():
            raise DeclaracaoInvalida("ação precisa de um nome")
        if not isinstance(self.ator, str) or not self.ator.strip():
            raise DeclaracaoInvalida("ator precisa de um nome")
        if self.atributo not in ATRIBUTOS:
            raise DeclaracaoInvalida(
                f"atributo {self.atributo!r} inexistente; opções {sorted(ATRIBUTOS)}"
            )
        if not isinstance(self.valor_atributo, int) or isinstance(self.valor_atributo, bool):
            raise DeclaracaoInvalida("valor_atributo deve ser int")
        if not (_ATRIBUTO_MIN <= self.valor_atributo <= _ATRIBUTO_MAX):
            raise DeclaracaoInvalida(
                f"valor_atributo {self.valor_atributo} fora de "
                f"[{_ATRIBUTO_MIN},{_ATRIBUTO_MAX}]"
            )
        esperado = _bonus(self.valor_atributo)
        if self.bonus_atributo != esperado:
            raise DeclaracaoInvalida(
                f"bônus de atributo declarado {self.bonus_atributo} não confere com o "
                f"valor {self.valor_atributo} (correto: {esperado}). "
                "O motor não aceita bônus negociado."
            )
        if not (_BONUS_MIN <= self.bonus_atributo <= _BONUS_MAX):
            raise DeclaracaoInvalida(
                f"bônus {self.bonus_atributo} fora da faixa [{_BONUS_MIN},{_BONUS_MAX}]"
            )
        if not isinstance(self.graduacao, int) or isinstance(self.graduacao, bool):
            raise DeclaracaoInvalida("graduacao deve ser int")
        if not (0 <= self.graduacao <= _GRADUACAO_MAX):
            raise DeclaracaoInvalida(
                f"graduação {self.graduacao} fora de [0,{_GRADUACAO_MAX}]"
            )
        if not isinstance(self.dificuldade, int) or isinstance(self.dificuldade, bool):
            raise DeclaracaoInvalida("dificuldade deve ser int")
        if not (_DIFICULDADE_MIN <= self.dificuldade <= _DIFICULDADE_MAX):
            raise DeclaracaoInvalida(
                f"dificuldade {self.dificuldade} fora de "
                f"[{_DIFICULDADE_MIN},{_DIFICULDADE_MAX}]"
            )
        if not isinstance(self.regras, tuple):
            object.__setattr__(self, "regras", tuple(self.regras))
        vistos: Dict[str, int] = {}
        for codigo in self.regras:
            if not isinstance(codigo, str):
                raise DeclaracaoInvalida("código de regra deve ser texto")
            if codigo not in REGISTRO:
                raise ModificadorIlegal(
                    f"regra {codigo!r} não existe no Registro. Não há modificador "
                    "fora das regras publicadas."
                )
            vistos[codigo] = vistos.get(codigo, 0) + 1
            if vistos[codigo] > 1:
                raise DeclaracaoInvalida(f"regra {codigo} declarada duas vezes")
        choque = conflitos(self.regras)
        if choque:
            raise DeclaracaoInvalida(f"regras mutuamente exclusivas: {choque}")
        _validar_json_seguro(dict(self.fatos))
        _validar_json_seguro(dict(self.contexto))
        # pré-calcula todos os modificadores: se algum fato faltar, falha AQUI,
        # antes de gastar entropia — nada de rolagem "meia declarada".
        for codigo in self.regras:
            valor_de(codigo, self.fatos)

    # -- derivações --------------------------------------------------------
    def modificadores(self) -> Tuple[ModificadorAplicado, ...]:
        saida = []
        for codigo in self.regras:
            regra = REGISTRO[codigo]
            v = regra.valor(self.fatos)
            if v == 0:
                continue
            saida.append(ModificadorAplicado(codigo, v, regra.capitulo, regra.descricao))
        return tuple(saida)

    def soma_modificadores(self) -> int:
        return sum(m.valor for m in self.modificadores())

    def para_auditoria(self) -> Dict[str, Any]:
        return {
            "acao": self.acao,
            "ator": self.ator,
            "alvo": self.alvo,
            "atributo": self.atributo,
            "valor_atributo": self.valor_atributo,
            "bonus_atributo": self.bonus_atributo,
            "pericia": self.pericia,
            "graduacao": self.graduacao,
            "dificuldade": self.dificuldade,
            "regras": list(self.regras),
            "fatos": dict(self.fatos),
            "contexto": dict(self.contexto),
            "expressao": self.expressao,
        }


# --------------------------------------------------------------------------
# Resultado (pós-rolagem, congelado e auto-verificável)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Resultado:
    declaracao: Declaracao
    rolagem: Rolagem
    modificadores: Tuple[ModificadorAplicado, ...]
    total: int
    margem: int
    grau: str
    face_d20: Optional[int]
    critico: str
    sucesso: bool
    token: str = ""
    hash_declaracao: str = ""
    hash_resultado: str = ""
    indice_no_diario: Optional[int] = None

    def __post_init__(self) -> None:
        # Invariante 1: o total é exatamente a soma declarada + o dado.
        esperado = (
            self.rolagem.total
            + self.declaracao.bonus_atributo
            + self.declaracao.graduacao
            + sum(m.valor for m in self.modificadores)
        )
        if esperado != self.total:
            raise AssertionError(
                f"Resultado adulterado: total={self.total}, aritmética diz {esperado}"
            )
        # Invariante 2: margem coerente.
        if self.margem != self.total - self.declaracao.dificuldade:
            raise AssertionError("margem não confere com total - dificuldade")
        # Invariante 3: grau derivado só de (margem, face).
        esperado_grau, esperado_critico = _classificar(self.face_d20, self.margem)
        if self.grau != esperado_grau or self.critico != esperado_critico:
            raise AssertionError(
                f"grau {self.grau!r}/{self.critico!r} não decorre da margem "
                f"{self.margem} e da face {self.face_d20}"
            )
        if self.sucesso != (self.grau in _GRAUS_SUCESSO):
            raise AssertionError("campo sucesso não corresponde ao grau")
        # Invariante 4: os modificadores batem com o recálculo das regras.
        for m in self.modificadores:
            if m.valor != valor_de(m.codigo, self.declaracao.fatos):
                raise AssertionError(
                    f"modificador {m.codigo} com valor {m.valor}; a regra diz "
                    f"{valor_de(m.codigo, self.declaracao.fatos)}"
                )

    def verificar(self) -> bool:
        """Revalida tudo do zero. Retorna True se íntegro."""
        try:
            recalc = _montar(self.declaracao, self.rolagem, self.token,
                             self.hash_declaracao, self.indice_no_diario)
        except Exception:
            return False
        return recalc.hash_resultado == self.hash_resultado

    def resumo(self) -> str:
        mods = ", ".join(f"{m.codigo}{m.valor:+d}" for m in self.modificadores) or "—"
        d = self.declaracao
        crit = {"toque_do_dao": " ✦ TOQUE DO DAO (20 natural)",
                "desvio": " ✖ DESVIO DE QI (1 natural)"}.get(self.critico, "")
        dado = f"d20={self.face_d20}" if self.face_d20 is not None else f"{d.expressao}={self.rolagem.total}"
        return (
            f"{d.ator}: {d.acao}  |  {dado} "
            f"+ attr{d.bonus_atributo:+d} + pericia{d.graduacao:+d} + regras[{mods}] "
            f"= {self.total}  vs DD {d.dificuldade}  →  margem {self.margem:+d}  "
            f"= {self.grau.upper()}{crit}"
        )


def _classificar(face_d20: Optional[int], margem: int) -> Tuple[str, str]:
    if face_d20 == 1:
        return FRACASSO_CRITICO, "desvio"
    if face_d20 == 20:
        return SUCESSO_CRITICO, "toque_do_dao"
    return grau_por_margem(margem), ""


def _face_do_d20(rolagem: Rolagem) -> Optional[int]:
    """Só existe 'natural' quando há exatamente um d20 sem descarte."""
    if len(rolagem.termos) != 1:
        return None
    t = rolagem.termos[0]
    if t.lados != 20 or t.quantidade != 1 or t.modo_manter or t.explosao or t.fudge:
        return None
    return t.faces[0]


def _montar(
    declaracao: Declaracao,
    rolagem: Rolagem,
    token: str = "",
    hash_declaracao: str = "",
    indice: Optional[int] = None,
) -> Resultado:
    mods = declaracao.modificadores()
    total = (
        rolagem.total
        + declaracao.bonus_atributo
        + declaracao.graduacao
        + sum(m.valor for m in mods)
    )
    margem = total - declaracao.dificuldade
    face = _face_do_d20(rolagem)
    grau, critico = _classificar(face, margem)
    base = Resultado(
        declaracao=declaracao,
        rolagem=rolagem,
        modificadores=mods,
        total=total,
        margem=margem,
        grau=grau,
        face_d20=face,
        critico=critico,
        sucesso=grau in _GRAUS_SUCESSO,
        token=token,
        hash_declaracao=hash_declaracao,
        hash_resultado="",
        indice_no_diario=indice,
    )
    selo = hash_de(
        canonico(
            {
                "total": base.total,
                "margem": base.margem,
                "grau": base.grau,
                "critico": base.critico,
                "faces": list(base.rolagem.faces()),
                "token": base.token,
                "declaracao": base.hash_declaracao,
            }
        )
    )
    return Resultado(
        declaracao=base.declaracao,
        rolagem=base.rolagem,
        modificadores=base.modificadores,
        total=base.total,
        margem=base.margem,
        grau=base.grau,
        face_d20=base.face_d20,
        critico=base.critico,
        sucesso=base.sucesso,
        token=base.token,
        hash_declaracao=base.hash_declaracao,
        hash_resultado=selo,
        indice_no_diario=base.indice_no_diario,
    )


# --------------------------------------------------------------------------
# A rolagem
# --------------------------------------------------------------------------
def resolver(
    declaracao: Declaracao,
    aleat: Aleatoriedade,
    diario: Optional[DiarioDeAuditoria] = None,
) -> Resultado:
    """Executa a Mecânica Central. Pura: mesmas entradas → mesmas saídas.

    Ordem obrigatória e inalterável: comprometer → rolar → registrar → revelar.
    """
    payload = declaracao.para_auditoria()
    token = ""
    indice = None
    if diario is not None:
        comp = comprometer(payload, aleat)
        token = comp.token
        diario.registrar(
            "compromisso",
            {"token": comp.token, "acao": declaracao.acao,
             "ator": declaracao.ator, "hash_declaracao": comp.hash_payload},
            ator=declaracao.ator,
        )
        rolagem = rolar(declaracao.expressao, aleat, identificador=comp.token)
        resultado = _montar(declaracao, rolagem, token, comp.hash_payload)
        reg = diario.registrar(
            "rolagem",
            {
                "token": comp.token,
                "expressao": declaracao.expressao,
                "faces": list(rolagem.faces()),
                "dado": rolagem.total,
                "modificadores": [[m.codigo, m.valor] for m in resultado.modificadores],
                "total": resultado.total,
                "dificuldade": declaracao.dificuldade,
                "margem": resultado.margem,
                "grau": resultado.grau,
                "critico": resultado.critico,
                "sucesso": resultado.sucesso,
                "selo": resultado.hash_resultado,
            },
            ator=declaracao.ator,
        )
        indice = reg.indice
        diario.registrar(
            "revelacao",
            {"token": comp.token, "sal": comp.sal_hex, "payload": payload},
            ator=declaracao.ator,
        )
        resultado = _montar(declaracao, rolagem, token, comp.hash_payload, indice)
    else:
        rolagem = rolar(declaracao.expressao, aleat)
        resultado = _montar(declaracao, rolagem)
    return resultado


@dataclass(frozen=True)
class ResultadoOposto:
    atacante: Resultado
    defensor: Resultado
    vencedor: str          # "atacante" | "defensor" | "empate"
    diferenca: int
    criterio: str          # por que venceu — sempre uma regra, nunca uma opinião

    def resumo(self) -> str:
        return (
            f"OPOSTO  {self.atacante.declaracao.ator} {self.atacante.total} vs "
            f"{self.defensor.declaracao.ator} {self.defensor.total}  →  "
            f"{self.vencedor.upper()} (diferença {self.diferenca:+d}; {self.criterio})"
        )


def teste_oposto(
    declaracao_atacante: Declaracao,
    declaracao_defensor: Declaracao,
    aleat: Aleatoriedade,
    diario: Optional[DiarioDeAuditoria] = None,
) -> ResultadoOposto:
    """Disputa: ambos declaram, ambos rolam, o maior total vence.

    Desempate em cascata, 100% determinístico:
      1. maior graduação na perícia usada;
      2. maior valor de atributo bruto;
      3. maior nível de cultivo declarado em ``contexto['reino']``;
      4. o DEFENSOR prevalece (regra da casa: quem age contra o estado
         existente precisa superá-lo).
    """
    a = resolver(declaracao_atacante, aleat, diario)
    d = resolver(declaracao_defensor, aleat, diario)
    if a.total != d.total:
        return ResultadoOposto(
            a, d,
            "atacante" if a.total > d.total else "defensor",
            a.total - d.total,
            "total maior",
        )
    if a.declaracao.graduacao != d.declaracao.graduacao:
        quem = "atacante" if a.declaracao.graduacao > d.declaracao.graduacao else "defensor"
        return ResultadoOposto(a, d, quem, 0, "desempate por graduação de perícia")
    if a.declaracao.valor_atributo != d.declaracao.valor_atributo:
        quem = "atacante" if a.declaracao.valor_atributo > d.declaracao.valor_atributo else "defensor"
        return ResultadoOposto(a, d, quem, 0, "desempate por valor de atributo")
    ra = int(a.declaracao.contexto.get("reino", 0))
    rd = int(d.declaracao.contexto.get("reino", 0))
    if ra != rd:
        quem = "atacante" if ra > rd else "defensor"
        return ResultadoOposto(a, d, quem, 0, "desempate por nível de cultivo")
    return ResultadoOposto(a, d, "defensor", 0,
                           "empate absoluto: o defensor prevalece (regra 3.6)")


# --------------------------------------------------------------------------
# Prova estrutural de ausência de manipulação
# --------------------------------------------------------------------------
NOMES_PROIBIDOS = frozenset({
    "rerolar", "rolar_de_novo", "repetir_rolagem", "ajustar_resultado",
    "modificar_resultado", "forcar_resultado", "substituir_resultado",
    "melhor_de_n", "melhor_de_dois", "fudge", "trapaca", "fraude",
    "narrativa", "sorte_do_mestre", "favor_narrativo", "bencao",
    "intervir", "sobrescrever", "editar_resultado", "resultado_desejado",
})
PARAMETROS_PROIBIDOS = frozenset({
    "resultado_desejado", "forcar", "sucesso_garantido", "narrativa",
    "plot_armor", "favor", "violar", "trapaca", "reescrever", "ajuste",
})


@dataclass(frozen=True)
class RelatorioDeInvariantes:
    ok: bool
    violacoes: Tuple[str, ...]
    verificacoes: int

    def texto(self) -> str:
        if self.ok:
            return (
                f"INVARIANTES OK — {self.verificacoes} verificações estruturais.\n"
                "  • nenhuma API de re-rolagem/ajuste existe no motor;\n"
                "  • Declaracao, Resultado, Rolagem e Compromisso são imutáveis;\n"
                "  • nenhum parâmetro de função aceita intenção narrativa;\n"
                "  • modificadores só nascem do Registro de Regras."
            )
        return "INVARIANTES VIOLADOS:\n" + "\n".join("  • " + v for v in self.violacoes)


def verificar_invariantes(modulos: Optional[Sequence[Any]] = None) -> RelatorioDeInvariantes:
    """Inspeciona o próprio motor procurando portas para trapaça.

    Roda em todo ``xan motor autoteste`` e na suíte de testes: se alguém
    acrescentar uma função de re-rolagem, isto falha.
    """
    from . import auditoria, compromisso, dados, entropia, regras

    alvo = list(modulos) if modulos else [
        sys.modules[__name__], dados, entropia, compromisso, auditoria, regras,
    ]
    violacoes: List[str] = []
    checks = 0

    # 1) nomes proibidos em qualquer módulo do motor
    for mod in alvo:
        for nome in dir(mod):
            checks += 1
            baixo = nome.lower()
            for proibido in NOMES_PROIBIDOS:
                if proibido in baixo and not nome.startswith("_"):
                    violacoes.append(
                        f"{mod.__name__}.{nome} contém o termo proibido '{proibido}'"
                    )

    # 2) parâmetros proibidos em funções públicas
    for mod in alvo:
        for nome, obj in vars(mod).items():
            if nome.startswith("_") or not callable(obj):
                continue
            try:
                sig = inspect.signature(obj)
            except (TypeError, ValueError):
                continue
            for p in sig.parameters:
                checks += 1
                if p.lower() in PARAMETROS_PROIBIDOS:
                    violacoes.append(
                        f"{mod.__name__}.{nome}() aceita o parâmetro proibido '{p}'"
                    )

    # 3) imutabilidade dos tipos críticos
    este = sys.modules[__name__]
    criticos = [
        (dados, "Rolagem"), (dados, "TermoDado"),
        (este, "Resultado"), (este, "Declaracao"),
        (este, "ModificadorAplicado"), (este, "ResultadoOposto"),
        (compromisso, "Compromisso"),
        (auditoria, "Registro"),
        (regras, "RegraModificadora"),
    ]
    for mod, nome in criticos:
        checks += 1
        classe = getattr(mod, nome)
        if not is_dataclass(classe):
            violacoes.append(f"{mod.__name__}.{nome} deixou de ser dataclass")
        elif not classe.__dataclass_params__.frozen:
            violacoes.append(f"{mod.__name__}.{nome} não é frozen (mutável!)")

    # 4) nenhuma classe crítica expõe setter
    for mod, nome in criticos:
        classe = getattr(mod, nome)
        for f in fields(classe):
            checks += 1
            if hasattr(classe, f"set_{f.name}") or hasattr(classe, f"with_{f.name}"):
                violacoes.append(f"{classe.__name__} expõe mutador para '{f.name}'")

    # 5) Aleatoriedade não pode ter método de repetição
    checks += 1
    for nome in dir(entropia.Aleatoriedade):
        if nome.startswith("_"):
            continue
        if any(p in nome.lower() for p in ("repet", "ultim", "anterior", "desfaz", "volta")):
            violacoes.append(f"Aleatoriedade.{nome} permite acesso/repetição do passado")

    # 6) resolver() não pode receber nada além de (declaração, acaso, diário)
    checks += 1
    params = list(inspect.signature(resolver).parameters)
    if params != ["declaracao", "aleat", "diario"]:
        violacoes.append(
            f"resolver() mudou de assinatura para {params}; apenas declaração, "
            "acaso e diário são aceitáveis"
        )

    return RelatorioDeInvariantes(
        ok=not violacoes, violacoes=tuple(violacoes), verificacoes=checks
    )
