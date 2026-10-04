# -*- coding: utf-8 -*-
"""
XAN — Registro de Regras (a única fonte legal de modificadores).
===============================================================

Princípio: **nenhum modificador existe se não estiver aqui.**

O motor não aceita "dá +2 porque a cena pede". Ele aceita um *código de regra*
e **recalcula** o valor a partir de **fatos objetivos** declarados antes do
dado. Se alguém declarar ``POSICAO:TERRENO`` afirmando cota alta enquanto o fato
registrado é ``terreno="baixo"``, o motor devolve -1 — não +1. A conta obedece
ao fato, nunca à intenção.

Duas exigências do sistema realizadas aqui:
    1. *sempre use lógica* — todo bônus tem causa verificável e recalculável;
    2. *sem vantagem narrativa* — não existe ponto de entrada para intenção.

Tipagem estrita de fatos
------------------------
Fatos booleanos precisam ser ``bool`` de verdade, categóricos precisam estar na
tabela da regra e numéricos precisam ser ``int``. Texto aproximado ("mais ou
menos alto") é rejeitado com ``ModificadorIlegal``: ambiguidade é o esconderijo
favorito da trapaça.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

__all__ = [
    "ModificadorIlegal",
    "RegraModificadora",
    "REGISTRO",
    "registrar",
    "valor_de",
    "listar_regras",
    "conflitos",
    "EXCLUSIVAS",
    "relacao_elemental",
    "ELEMENTOS_GERADORES",
    "ELEMENTOS_SUPERADORES",
]


class ModificadorIlegal(ValueError):
    """Tentativa de aplicar um modificador que a regra não autoriza."""


@dataclass(frozen=True)
class RegraModificadora:
    codigo: str
    capitulo: str
    descricao: str
    requer: Tuple[str, ...]
    calcular: Callable[[Mapping[str, Any]], int]
    limite: Tuple[int, int] = (-10, 10)
    dominio: str = ""

    def __post_init__(self) -> None:
        if ":" not in self.codigo:
            raise ValueError("código de regra deve ter a forma DOMINIO:NOME")
        object.__setattr__(self, "dominio", self.codigo.split(":", 1)[0])

    def valor(self, fatos: Mapping[str, Any]) -> int:
        ausentes = [r for r in self.requer if r not in fatos]
        if ausentes:
            raise ModificadorIlegal(
                f"{self.codigo} exige o(s) fato(s) {ausentes}; "
                f"a declaração traz {sorted(fatos)}"
            )
        v = self.calcular(fatos)
        if isinstance(v, bool) or not isinstance(v, int):
            raise ModificadorIlegal(f"{self.codigo} não produziu um inteiro")
        lo, hi = self.limite
        if not (lo <= v <= hi):
            raise ModificadorIlegal(
                f"{self.codigo} produziu {v}, fora da faixa legal [{lo},{hi}]"
            )
        return v


REGISTRO: Dict[str, RegraModificadora] = {}


def registrar(
    codigo: str,
    capitulo: str,
    descricao: str,
    requer: Tuple[str, ...] = (),
    calcular: Optional[Callable[[Mapping[str, Any]], int]] = None,
    limite: Tuple[int, int] = (-10, 10),
) -> RegraModificadora:
    if calcular is None:
        raise ValueError("toda regra precisa de uma função de cálculo")
    if codigo in REGISTRO:
        raise ValueError(f"regra {codigo} já registrada")
    regra = RegraModificadora(codigo, capitulo, descricao, tuple(requer), calcular, limite)
    REGISTRO[codigo] = regra
    return regra


# --------------------------------------------------------------------------
# Auxiliares puros e estritos
# --------------------------------------------------------------------------
def _bool(nome: str, v: Any) -> bool:
    if not isinstance(v, bool):
        raise ModificadorIlegal(
            f"fato {nome!r} deve ser True/False (veio {v!r}: {type(v).__name__})"
        )
    return v


def _categoria(nome: str, v: Any, tabela: Dict[str, int]) -> int:
    if not isinstance(v, str):
        raise ModificadorIlegal(f"fato {nome!r} deve ser texto (veio {v!r})")
    chave = v.strip().lower()
    if chave not in tabela:
        raise ModificadorIlegal(
            f"fato {nome!r}={v!r} não existe; opções: {sorted(tabela)}"
        )
    return tabela[chave]


def _inteiro(nome: str, v: Any, lo: int, hi: int) -> int:
    if isinstance(v, bool) or not isinstance(v, int):
        raise ModificadorIlegal(f"fato {nome!r} deve ser inteiro (veio {v!r})")
    if not (lo <= v <= hi):
        raise ModificadorIlegal(f"fato {nome!r}={v} fora de [{lo},{hi}]")
    return v


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


# ==========================================================================
# WUXING — os Cinco Elementos (LIVRO cap. 9)
# ==========================================================================
ELEMENTOS_GERADORES = {          # X gera Y   (相生 shēng)
    "madeira": "fogo",
    "fogo": "terra",
    "terra": "metal",
    "metal": "agua",
    "agua": "madeira",
}
ELEMENTOS_SUPERADORES = {        # X supera Y (相克 kè)
    "madeira": "terra",
    "terra": "agua",
    "agua": "fogo",
    "fogo": "metal",
    "metal": "madeira",
}
ELEMENTOS_CANONICOS = ("metal", "madeira", "agua", "fogo", "terra")
ELEMENTOS_NEUTROS = ("nenhum", "vazio")

TABELA_RELACAO = {
    "supera": 2,        # A克B — o ataque domina o alvo
    "gerado": 1,        # B生A — o ataque se nutre do alvo
    "igual": 0,
    "neutro": 0,
    "gerador": -1,      # A生B — o ataque alimenta o alvo
    "subjugado": -2,    # B克A — o alvo domina o ataque
}


def relacao_elemental(atacante: str, defensor: str) -> str:
    """Relação Wuxing de A contra B. Pura, total e verificável."""
    a = str(atacante).strip().lower()
    b = str(defensor).strip().lower()
    validos = set(ELEMENTOS_CANONICOS) | set(ELEMENTOS_NEUTROS)
    if a not in validos or b not in validos:
        raise ModificadorIlegal(
            f"elemento inválido: {atacante!r}/{defensor!r}; opções {sorted(validos)}"
        )
    if a in ELEMENTOS_NEUTROS or b in ELEMENTOS_NEUTROS:
        return "neutro"
    if a == b:
        return "igual"
    if ELEMENTOS_SUPERADORES[a] == b:
        return "supera"
    if ELEMENTOS_SUPERADORES[b] == a:
        return "subjugado"
    if ELEMENTOS_GERADORES[b] == a:
        return "gerado"
    if ELEMENTOS_GERADORES[a] == b:
        return "gerador"
    return "neutro"  # inalcançável com 5 elementos, mantém a função total


registrar(
    "ELEMENTO:RELACAO", "9.2",
    "Ciclo Wuxing entre o elemento do ataque e o do alvo (克/生).",
    requer=("elemento_atacante", "elemento_alvo"),
    calcular=lambda f: TABELA_RELACAO[
        relacao_elemental(f["elemento_atacante"], f["elemento_alvo"])
    ],
    limite=(-2, 2),
)

# ==========================================================================
# SUPRESSÃO DE REINO (LIVRO cap. 6.6)
# ==========================================================================
registrar(
    "REINO:SUPRESSAO", "6.6",
    "Diferença de nível de cultivo: ±2 por nível, teto ±10. Reflete o abismo "
    "entre reinos que define o gênero.",
    requer=("reino_atacante", "reino_alvo"),
    calcular=lambda f: _clamp(
        2 * (_inteiro("reino_atacante", f["reino_atacante"], 0, 13)
             - _inteiro("reino_alvo", f["reino_alvo"], 0, 13)),
        -10, 10,
    ),
    limite=(-10, 10),
)

# ==========================================================================
# POSIÇÃO, TERRENO E ALVO (LIVRO cap. 10.5)
# ==========================================================================
registrar(
    "POSICAO:TERRENO", "10.5",
    "Cota relativa do atacante: alto +1, neutro 0, baixo -1.",
    requer=("terreno",),
    calcular=lambda f: _categoria("terreno", f["terreno"],
                                  {"alto": 1, "neutro": 0, "baixo": -1}),
    limite=(-1, 1),
)
registrar(
    "POSICAO:FLANCO", "10.5",
    "+2 se o alvo está flanqueado por um aliado do atacante.",
    requer=("flanqueado",),
    calcular=lambda f: 2 if _bool("flanqueado", f["flanqueado"]) else 0,
    limite=(0, 2),
)
registrar(
    "POSICAO:EMBOSCADA", "10.5",
    "+2 quando o atacante está oculto E o alvo ainda não o percebeu.",
    requer=("oculto", "percebido"),
    calcular=lambda f: 2 if (_bool("oculto", f["oculto"])
                             and not _bool("percebido", f["percebido"])) else 0,
    limite=(0, 2),
)
registrar(
    "ALVO:COBERTURA", "10.5",
    "Cobertura do alvo: nenhuma 0, parcial -2, três-quartos -4, total -5.",
    requer=("cobertura",),
    calcular=lambda f: _categoria("cobertura", f["cobertura"],
                                  {"nenhuma": 0, "parcial": -2,
                                   "tres_quartos": -4, "total": -5}),
    limite=(-5, 0),
)
registrar(
    "ALVO:PASSOS_LEVES", "10.5",
    "-2 contra alvo em Arte de Passos Leves (輕功 qinggong) ativa.",
    requer=("passos_leves",),
    calcular=lambda f: -2 if _bool("passos_leves", f["passos_leves"]) else 0,
    limite=(-2, 0),
)
registrar(
    "ALCANCE:FAIXA", "10.4",
    "Faixa de alcance do ataque: curto/medio 0, longo -2, extremo -4.",
    requer=("alcance",),
    calcular=lambda f: _categoria("alcance", f["alcance"],
                                  {"curto": 0, "medio": 0, "longo": -2,
                                   "extremo": -4}),
    limite=(-4, 0),
)

# ==========================================================================
# ESTADO DO ATOR (LIVRO cap. 10.8 / 10.9)
# ==========================================================================
registrar(
    "ESTADO:FERIMENTO", "10.8",
    "ileso 0, ferido -1, grave -2, agonizando -3.",
    requer=("ferimento",),
    calcular=lambda f: _categoria("ferimento", f["ferimento"],
                                  {"ileso": 0, "ferido": -1, "grave": -2,
                                   "agonizando": -3}),
    limite=(-3, 0),
)
registrar(
    "ESTADO:VISAO", "10.8",
    "normal 0, parcial -2, cego -4.",
    requer=("visao",),
    calcular=lambda f: _categoria("visao", f["visao"],
                                  {"normal": 0, "parcial": -2, "cego": -4}),
    limite=(-4, 0),
)
registrar(
    "ESTADO:EXAUSTAO", "10.8",
    "-1 quando o Qi atual está abaixo de 25% do máximo.",
    requer=("qi_atual", "qi_maximo"),
    calcular=lambda f: (
        -1 if _inteiro("qi_atual", f["qi_atual"], 0, 10 ** 9) * 4
        < _inteiro("qi_maximo", f["qi_maximo"], 1, 10 ** 9) else 0
    ),
    limite=(-1, 0),
)
registrar(
    "ESTADO:DESVIO_DE_QI", "10.9",
    "-3 sob Desvio de Qi (走火入魔).",
    requer=("desvio_de_qi",),
    calcular=lambda f: -3 if _bool("desvio_de_qi", f["desvio_de_qi"]) else 0,
    limite=(-3, 0),
)
registrar(
    "ESTADO:DEMONIO_INTERIOR", "10.9",
    "-2 com o Demônio Interior (心魔) atiçado.",
    requer=("demonio_interior",),
    calcular=lambda f: -2 if _bool("demonio_interior", f["demonio_interior"]) else 0,
    limite=(-2, 0),
)
registrar(
    "ESTADO:IMOBILIZADO", "10.8",
    "-4 preso por formação, laço ou garra.",
    requer=("imobilizado",),
    calcular=lambda f: -4 if _bool("imobilizado", f["imobilizado"]) else 0,
    limite=(-4, 0),
)

# ==========================================================================
# AMBIENTE (LIVRO cap. 9.3–9.5 / 15.4)
# ==========================================================================
registrar(
    "AMBIENTE:LUZ", "9.4",
    "plena 0, penumbra -1, escuridao -3, trevas -4.",
    requer=("luz",),
    calcular=lambda f: _categoria("luz", f["luz"],
                                  {"plena": 0, "penumbra": -1,
                                   "escuridao": -3, "trevas": -4}),
    limite=(-4, 0),
)
registrar(
    "AMBIENTE:CLIMA", "9.5",
    "Clima local no momento da ação.",
    requer=("clima",),
    calcular=lambda f: _categoria(
        "clima", f["clima"],
        {"limpo": 0, "nublado": 0, "chuva": -1, "nevoeiro": -2,
         "nevasca": -2, "tempestade": -2, "miasma": -2,
         "calor_extremo": -1, "frio_extremo": -1},
    ),
    limite=(-2, 0),
)
registrar(
    "AMBIENTE:FENGSHUI", "9.4",
    "muito_auspicioso +2, auspicioso +1, neutro 0, sinistro -1, "
    "muito_sinistro -2. Vale para cultivo, alquimia, forja, talismãs e rituais.",
    requer=("fengshui",),
    calcular=lambda f: _categoria(
        "fengshui", f["fengshui"],
        {"muito_auspicioso": 2, "auspicioso": 1, "neutro": 0,
         "sinistro": -1, "muito_sinistro": -2},
    ),
    limite=(-2, 2),
)
registrar(
    "AMBIENTE:DENSIDADE_QI", "9.3",
    "esteril -2, pobre -1, comum 0, rica +1, veia_espiritual +2, "
    "terra_imortal +3.",
    requer=("densidade_qi",),
    calcular=lambda f: _categoria(
        "densidade_qi", f["densidade_qi"],
        {"esteril": -2, "pobre": -1, "comum": 0, "rica": 1,
         "veia_espiritual": 2, "terra_imortal": 3},
    ),
    limite=(-2, 3),
)
registrar(
    "AMBIENTE:FORMACAO", "15.4",
    "nenhuma 0, aliada +2, hostil -2.",
    requer=("formacao",),
    calcular=lambda f: _categoria("formacao", f["formacao"],
                                  {"nenhuma": 0, "aliada": 2, "hostil": -2}),
    limite=(-2, 2),
)

# ==========================================================================
# RECURSOS E PREPARO (LIVRO cap. 11 e 15)
# ==========================================================================
registrar(
    "RECURSO:ELIXIR", "15.1",
    "nenhum 0, menor +1, medio +2, maior +3, celestial +4.",
    requer=("elixir",),
    calcular=lambda f: _categoria("elixir", f["elixir"],
                                  {"nenhum": 0, "menor": 1, "medio": 2,
                                   "maior": 3, "celestial": 4}),
    limite=(0, 4),
)
registrar(
    "RECURSO:TALISMA", "15.3",
    "nenhum 0, menor +1, medio +2, maior +3.",
    requer=("talisma",),
    calcular=lambda f: _categoria("talisma", f["talisma"],
                                  {"nenhum": 0, "menor": 1, "medio": 2,
                                   "maior": 3}),
    limite=(0, 3),
)
registrar(
    "RECURSO:ARTEFATO", "15.2",
    "Grau do artefato em uso: nenhum/mortal 0, terra +1, ceu +2, primordial +3.",
    requer=("artefato",),
    calcular=lambda f: _categoria("artefato", f["artefato"],
                                  {"nenhum": 0, "mortal": 0, "terra": 1,
                                   "ceu": 2, "primordial": 3}),
    limite=(0, 3),
)
registrar(
    "PREPARO:MEDITACAO", "11.2",
    "+1 se houve sessão de meditação concluída antes da ação.",
    requer=("meditou",),
    calcular=lambda f: 1 if _bool("meditou", f["meditou"]) else 0,
    limite=(0, 1),
)
registrar(
    "PREPARO:ESTUDO_PREVIO", "11.2",
    "+1 se o alvo/assunto foi estudado com antecedência real.",
    requer=("estudou",),
    calcular=lambda f: 1 if _bool("estudou", f["estudou"]) else 0,
    limite=(0, 1),
)
registrar(
    "PREPARO:QUEIMA_LONGEVIDADE", "11.5",
    "Queimar anos de vida por poder: +1 a cada 5 anos, teto +5. "
    "O custo é pago na ficha, sem devolução.",
    requer=("anos_queimados",),
    calcular=lambda f: _clamp(
        _inteiro("anos_queimados", f["anos_queimados"], 0, 1000) // 5 + (
            1 if _inteiro("anos_queimados", f["anos_queimados"], 0, 1000) > 0 else 0
        ), 0, 5),
    limite=(0, 5),
)

# ==========================================================================
# SOCIAL, FACE E FACÇÕES (LIVRO cap. 12 e 14)
# ==========================================================================
registrar(
    "SOCIAL:FACE", "12.6",
    "gloriosa +2, respeitada +1, neutra 0, arranhada -1, desonrada -3.",
    requer=("face",),
    calcular=lambda f: _categoria("face", f["face"],
                                  {"gloriosa": 2, "respeitada": 1, "neutra": 0,
                                   "arranhada": -1, "desonrada": -3}),
    limite=(-3, 2),
)
registrar(
    "SOCIAL:DISPOSICAO", "12.4",
    "Disposição do alvo, derivada do livro-razão de relações (não é opinião): "
    "devoto +3, amigavel +2, cordial +1, neutro 0, desconfiado -1, hostil -2, "
    "inimigo_jurado -4.",
    requer=("disposicao",),
    calcular=lambda f: _categoria(
        "disposicao", f["disposicao"],
        {"devoto": 3, "amigavel": 2, "cordial": 1, "neutro": 0,
         "desconfiado": -1, "hostil": -2, "inimigo_jurado": -4},
    ),
    limite=(-4, 3),
)
registrar(
    "SOCIAL:HIERARQUIA", "12.6",
    "superior +2, igual 0, inferior -1.",
    requer=("hierarquia",),
    calcular=lambda f: _categoria("hierarquia", f["hierarquia"],
                                  {"superior": 2, "igual": 0, "inferior": -1}),
    limite=(-1, 2),
)
registrar(
    "SOCIAL:DIVIDA_DE_HONRA", "12.6",
    "nenhuma 0, menor +1, grande +3.",
    requer=("divida_de_honra",),
    calcular=lambda f: _categoria("divida_de_honra", f["divida_de_honra"],
                                  {"nenhuma": 0, "menor": 1, "grande": 3}),
    limite=(0, 3),
)
registrar(
    "SOCIAL:SEGREDO_EXPOSTO", "12.7",
    "-4 se o ator expôs publicamente o segredo do alvo.",
    requer=("segredo_exposto",),
    calcular=lambda f: -4 if _bool("segredo_exposto", f["segredo_exposto"]) else 0,
    limite=(-4, 0),
)
registrar(
    "FACCAO:RELACAO", "14.3",
    "mesma +2, aliada +1, amigável +1, neutra 0, rival -1, guerra -2.",
    requer=("relacao_de_faccoes",),
    calcular=lambda f: _categoria(
        "relacao_de_faccoes", f["relacao_de_faccoes"],
        {"mesma": 2, "aliada": 1, "amigavel": 1, "neutra": 0, "rival": -1,
         "guerra": -2},
    ),
    limite=(-2, 2),
)

# ==========================================================================
# COMBATE (LIVRO cap. 10)
# ==========================================================================
registrar(
    "COMBATE:SURPRESA", "10.2",
    "+4 contra alvo surpreendido no primeiro turno do encontro.",
    requer=("alvo_surpreso",),
    calcular=lambda f: 4 if _bool("alvo_surpreso", f["alvo_surpreso"]) else 0,
    limite=(0, 4),
)
registrar(
    "COMBATE:GUARDA_TOTAL", "10.3",
    "+2 de defesa para quem declarou guarda total (abdica do ataque no turno).",
    requer=("guarda_total",),
    calcular=lambda f: 2 if _bool("guarda_total", f["guarda_total"]) else 0,
    limite=(0, 2),
)
registrar(
    "COMBATE:ACOES_MULTIPLOS", "10.6",
    "-2 cumulativo para cada ataque além do primeiro no mesmo turno.",
    requer=("acoes_no_turno",),
    calcular=lambda f: -2 * max(
        0, _inteiro("acoes_no_turno", f["acoes_no_turno"], 1, 6) - 1),
    limite=(-10, 0),
)
registrar(
    "COMBATE:DEFESA_DECLARADA", "10.3",
    "Defender-se como ação dedicada: +3 (não cumulativo com GUARDA_TOTAL).",
    requer=("acao_de_defesa",),
    calcular=lambda f: 3 if _bool("acao_de_defesa", f["acao_de_defesa"]) else 0,
    limite=(0, 3),
)
registrar(
    "DESEJO:PRIORIDADE", "12.6",
    "Quando dois desejos do mesmo NPC mandam condutas incompatíveis, cada lado "
    "soma a prioridade da sua camada: linha vermelha 6, medo 5, dever 4, "
    "obsessão/segredo 3, ambição 2, imediato 1, preço 0. É tabela, não gosto do "
    "mestre.",
    requer=("camada",),
    calcular=lambda f: _categoria("camada", f["camada"],
                                  PRIORIDADE_DE_CAMADA_DE_DESEJO),
    limite=(0, 6),
)

# Conflitos de regras explícitos: estas duplas não podem coexistir.
EXCLUSIVAS: Tuple[Tuple[str, str], ...] = (
    ("COMBATE:GUARDA_TOTAL", "COMBATE:DEFESA_DECLARADA"),
    ("POSICAO:EMBOSCADA", "COMBATE:SURPRESA"),
    ("ESTADO:DESVIO_DE_QI", "PREPARO:MEDITACAO"),
)


# --------------------------------------------------------------------------
# Desejos — prioridade aritmética entre camadas de motivação (Cap. 12)
# --------------------------------------------------------------------------
PRIORIDADE_DE_CAMADA_DE_DESEJO: Dict[str, int] = {
    "medo": 5,             # sobrevivência imediata
    "linha_vermelha": 6,   # o que jamais fará: vence qualquer oferta
    "dever": 4,            # compromisso com terceiros
    "obsessao": 3,
    "segredo": 3,
    "ambicao": 2,
    "imediato": 1,
    "preco": 0,
}

# --------------------------------------------------------------------------
# Consultas
# --------------------------------------------------------------------------
def valor_de(codigo: str, fatos: Mapping[str, Any]) -> int:
    """Recalcula o valor de uma regra a partir dos fatos declarados."""
    if codigo not in REGISTRO:
        raise ModificadorIlegal(
            f"regra desconhecida {codigo!r}. Só existe o que está no REGISTRO "
            f"({len(REGISTRO)} regras registradas)."
        )
    return REGISTRO[codigo].valor(fatos)


def listar_regras() -> Tuple[RegraModificadora, ...]:
    return tuple(REGISTRO[k] for k in sorted(REGISTRO))


def conflitos(codigos: Tuple[str, ...]) -> Tuple[str, ...]:
    """Aponta pares de regras mutuamente exclusivas declarados juntos."""
    conjunto = set(codigos)
    achados = []
    for a, b in EXCLUSIVAS:
        if a in conjunto and b in conjunto:
            achados.append(f"{a} e {b}")
    return tuple(achados)
