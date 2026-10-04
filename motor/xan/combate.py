# -*- coding: utf-8 -*-
"""
XAN — Motor de combate.
=======================

Um encontro é uma sequência de **Declarações comprometidas** e roladas pelo
motor imparcial. Nada aqui é decidido "pela cena".

Ordem das coisas
----------------
1. ``Encontro`` é criado com os **fatos de cenário** (terreno, luz, clima,
   feng shui, densidade de Qi, formação). Esses fatos são declarados **antes**
   da primeira iniciativa e ficam gravados no diário.
2. Cada combatente declara o **modo de defesa** (esquiva, resistência ou aparar)
   antes do primeiro ataque. Trocar de modo custa a ação do turno.
3. A **iniciativa** é rolada uma vez por encontro, auditada.
4. Cada ataque é uma ``resolver()`` com as regras do Registro recalculadas a
   partir dos fatos. O dano sai de ``artes.dano_de``.
5. O Qi absorve dano antes da Vitalidade. Vitalidade ≤ 0 → caído.

Regra de supressão de reino (gênero)
------------------------------------
Um cultivador 3+ níveis acima do alvo **não pode ser atingido** sem uma técnica
especial declarada. Isso não é opinião: é a regra ``REINO:SUPRESSAO`` somada à
cláusula de imbatibilidade abaixo, e o motor recusa o ataque antes de rolar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .artes import Tecnica, dano_de, tecnica_de
from .auditoria import DiarioDeAuditoria
from .dados import rolar
from .entropia import Aleatoriedade
from .personagens import Personagem, EstadoDeJogo, Mudanca, ferimento_por_vitalidade
from .regras import ELEMENTOS_CANONICOS
from .resolucao import (
    Declaracao, DeclaracaoInvalida, Resultado, resolver,
)

__all__ = [
    "ModoDeDefesa", "MODOS_DE_DEFESA", "Combatente", "Cenario", "Encontro",
    "GolpeAplicado", "atacar", "defender", "usar_tecnica",
    "iniciativa", "iniciar_encontro", "LACUNA_IMBATIVEL", "encerrar",
    "dentro_do_alcance", "faixa_para_regra",
]

MODOS_DE_DEFESA: Tuple[str, ...] = ("esquiva", "resistencia", "aparar")

# Diferença de reino a partir da qual o inferior simplesmente não acerta.
LACUNA_IMBATIVEL = 3

_PERICIAS_DE_ARMA: Tuple[str, ...] = (
    "espada", "sabre", "lanca", "punho", "palma", "cajado", "arma_oculta",
    "arco", "arma_exotica",
)
_PERICIAS_DE_ALCANCE: Tuple[str, ...] = ("arma_oculta", "arco", "lanca")


@dataclass
class ModoDeDefesa:
    """Modo declarado pelo combatente antes do primeiro ataque."""

    modo: str = "esquiva"
    acao_de_defesa: bool = False
    guarda_total: bool = False
    manto_de_qi: bool = False     # +2 de Defesa, custa 10 de Qi por rodada

    def __post_init__(self) -> None:
        if self.modo not in MODOS_DE_DEFESA:
            raise ValueError(f"modo de defesa deve ser um de {MODOS_DE_DEFESA}")
        if self.acao_de_defesa and self.guarda_total:
            raise ValueError(
                "GUARDA_TOTAL e DEFESA_DECLARADA são mutuamente exclusivas")


@dataclass
class Combatente:
    """Adaptador único para personagens, NPCs e bestas.

    O combate não sabe — nem pode saber — quem é "protagonista". Todos entram
    pela mesma porta e rolam na mesma entropia.
    """

    nome: str
    nivel: int
    elemento: str
    atributos: Mapping[str, int]
    pericias: Mapping[str, int]
    estado: EstadoDeJogo
    modo: ModoDeDefesa = field(default_factory=ModoDeDefesa)
    faccao: str = ""
    iniciativa: int = 0
    rodada: int = 0
    caido: bool = False
    imobilizado: bool = False
    oculto: bool = False
    exausto: bool = False
    desvio_de_qi: bool = False
    demonio_interior: bool = False
    anos_queimados: int = 0
    artefato: str = "nenhum"
    talisma: str = "nenhum"
    elixir: str = "nenhum"
    passos_leves_ativos: bool = False
    acoes_no_turno: int = 1
    origem: str = "personagem"
    ataques_este_turno: int = 0
    cego: bool = False
    visao_parcial: bool = False

    # -- construção --------------------------------------------------------
    @classmethod
    def de_personagem(cls, p: Personagem,
                      estado: Optional[EstadoDeJogo] = None) -> "Combatente":
        e = estado or EstadoDeJogo.de_personagem(p)
        elemento = p.raiz.elemento_dominante
        if p.lei:
            from .reinos import lei_de
            elemento = lei_de(p.lei).elemento
        return cls(
            nome=p.nome, nivel=p.nivel, elemento=elemento,
            atributos=dict(p.atributos), pericias=dict(p.pericias), estado=e,
            faccao=p.faccao, origem="personagem",
        )

    @classmethod
    def de_npc(cls, n: Any) -> "Combatente":
        e = EstadoDeJogo(qi=n.qi_max(), vitalidade=n.vitalidade_max(),
                         qi_maximo=n.qi_max(), vitalidade_maxima=n.vitalidade_max(),
                         longevidade=90, estado_mental=n.estado_mental)
        return cls(
            nome=n.nome, nivel=n.nivel, elemento=n.raiz.elemento_dominante,
            atributos=dict(n.atributos), pericias=dict(n.pericias), estado=e,
            faccao=n.faccao, origem="npc",
        )

    @classmethod
    def de_besta(cls, b: Any) -> "Combatente":
        per = {"punho": min(5, b.nivel // 2), "folego_interno": min(5, b.nivel // 3)}
        e = EstadoDeJogo(qi=b.qi, vitalidade=b.vitalidade, qi_maximo=max(1, b.qi),
                         vitalidade_maxima=max(1, b.vitalidade), longevidade=200,
                         estado_mental=50)
        return cls(
            nome=b.nome, nivel=b.nivel, elemento=b.elemento,
            atributos=dict(b.atributos), pericias=per, estado=e,
            origem="besta",
        )

    # -- derivados ---------------------------------------------------------
    def bonus(self, atributo: str) -> int:
        return (int(self.atributos.get(atributo, 10)) - 10) // 2

    def graduacao(self, pericia: str) -> int:
        return max(0, min(5, int(self.pericias.get(pericia, 0))))

    def pericia_de_arma(self) -> str:
        melhor, melhor_valor = "punho", -1
        for c in _PERICIAS_DE_ARMA:
            v = self.graduacao(c)
            if v > melhor_valor:
                melhor, melhor_valor = c, v
        return melhor

    def defesa(self) -> int:
        """Defesa passiva conforme o modo declarado."""
        from .reinos import defesa_de
        atr = "per" if self.modo.modo == "esquiva" else "con"
        per = {"esquiva": "passos_leves", "resistencia": "corpo_de_ferro",
               "aparar": self.pericia_de_arma()}[self.modo.modo]
        base = defesa_de(self.modo.modo, self.nivel, int(self.atributos.get(atr, 10)),
                         self.graduacao(per), self.modo.manto_de_qi)
        if self.modo.acao_de_defesa:
            base += 3
        if self.modo.guarda_total:
            base += 2
        if self.passos_leves_ativos:
            base += 2
        return base

    def fato_de_ferimento(self) -> str:
        return ferimento_por_vitalidade(self.estado.vitalidade,
                                        max(1, self.estado.vitalidade_maxima))

    def fatos_de_estado(self) -> Dict[str, Any]:
        """Fatos objetivos deste combatente para o Registro de Regras."""
        return {
            "ferimento": self.fato_de_ferimento(),
            "qi_atual": self.estado.qi,
            "qi_maximo": max(1, self.estado.qi_maximo),
            "desvio_de_qi": bool(self.desvio_de_qi),
            "demonio_interior": bool(self.demonio_interior),
            "imobilizado": bool(self.imobilizado),
            "visao": "cego" if self.cego else ("parcial" if self.visao_parcial
                                              else "normal"),
            "anos_queimados": self.anos_queimados,
            "artefato": self.artefato,
            "talisma": self.talisma,
            "elixir": self.elixir,
        }

    def receber_dano(self, valor: int, motivo: str = "dano_de_combate",
                     diario: Optional[DiarioDeAuditoria] = None,
                     origem: str = "") -> Tuple[int, int]:
        """Aplica dano: o Qi escudo absorve primeiro, como no ACS.

        Retorna (absorvido_pelo_qi, dano_na_vitalidade).
        """
        if valor <= 0:
            return 0, 0
        absorvido = min(self.estado.qi, valor)
        restante = valor - absorvido
        if absorvido:
            self.estado.aplicar(Mudanca("qi", -absorvido, "gasto_de_qi", origem),
                                diario, ator=self.nome)
        if restante:
            self.estado.aplicar(Mudanca("vitalidade", -restante, motivo, origem),
                                diario, ator=self.nome)
        if self.estado.vitalidade <= 0:
            self.caido = True
        return absorvido, restante


@dataclass(frozen=True)
class Cenario:
    """Fatos de cenário, declarados ANTES da primeira rolagem do encontro."""

    terreno: str = "neutro"
    luz: str = "plena"
    clima: str = "limpo"
    fengshui: str = "neutro"
    densidade_qi: str = "comum"
    formacao: str = "nenhuma"
    descricao: str = ""

    def fatos(self) -> Dict[str, Any]:
        return {
            "terreno": self.terreno, "luz": self.luz, "clima": self.clima,
            "fengshui": self.fengshui, "densidade_qi": self.densidade_qi,
            "formacao": self.formacao,
        }

    def regras(self) -> Tuple[str, ...]:
        r = ["AMBIENTE:LUZ", "AMBIENTE:CLIMA", "AMBIENTE:FENGSHUI",
             "AMBIENTE:DENSIDADE_QI", "AMBIENTE:FORMACAO", "POSICAO:TERRENO"]
        return tuple(r)


@dataclass
class Encontro:
    cenario: Cenario
    combatentes: Dict[str, Combatente] = field(default_factory=dict)
    ordem: Tuple[str, ...] = ()
    rodada: int = 0
    turno_atual: Optional[str] = None
    encerrado: bool = False
    motivo_do_encerramento: str = ""
    diario: Optional[DiarioDeAuditoria] = None

    def adicionar(self, c: Combatente) -> None:
        if c.nome in self.combatentes:
            raise ValueError(f"já existe um combatente chamado {c.nome!r}")
        self.combatentes[c.nome] = c

    def get(self, nome: str) -> Combatente:
        if nome not in self.combatentes:
            raise KeyError(f"{nome!r} não está neste encontro")
        return self.combatentes[nome]

    def ativos(self) -> List[Combatente]:
        return [c for c in self.combatentes.values() if not c.caido]

    def lados(self) -> Dict[str, List[Combatente]]:
        grupos: Dict[str, List[Combatente]] = {}
        for c in self.combatentes.values():
            grupos.setdefault(c.faccao or "sem facção", []).append(c)
        return grupos

    def proximo(self) -> Optional[str]:
        """Avança para o próximo combatente ativo na ordem de iniciativa."""
        if self.encerrado:
            return None
        if not self.ordem:
            raise ValueError("iniciativa ainda não foi rolada")
        i = -1
        if self.turno_atual is not None:
            i = self.ordem.index(self.turno_atual)
        for passo in range(1, len(self.ordem) + 1):
            candidato = self.ordem[(i + passo) % len(self.ordem)]
            if (i + passo) >= len(self.ordem):
                self.rodada += 1
                for c in self.combatentes.values():
                    c.ataques_este_turno = 0
                    c.acoes_no_turno = 1
                    if c.modo.manto_de_qi:
                        if c.estado.qi >= 10:
                            c.estado.aplicar(
                                Mudanca("qi", -10, "gasto_de_qi", "manto_de_qi"),
                                self.diario, ator=c.nome)
                        else:
                            c.modo.manto_de_qi = False
            c = self.combatentes[candidato]
            if not c.caido:
                self.turno_atual = candidato
                c.rodada = self.rodada
                return candidato
        self.encerrado = True
        self.motivo_do_encerramento = "nenhum combatente em condições"
        return None


@dataclass(frozen=True)
class GolpeAplicado:
    atacante: str
    alvo: str
    acertou: bool
    dano: int
    absorvido_pelo_qi: int
    dano_na_vitalidade: int
    conta_do_dano: str
    tecnica: Optional[str]
    bloqueado_por_supressao: bool
    motivo: str
    resultado: Optional[Resultado] = None

    def resumo(self) -> str:
        if self.resultado is None:
            return f"SEM ROLAGEM: {self.motivo}"
        cab = "ACERTO" if self.acertou else "ERRO"
        det = ""
        if self.acertou:
            det = (f" | dano {self.dano} (Qi absorveu {self.absorvido_pelo_qi}, "
                   f"Vitalidade perdeu {self.dano_na_vitalidade})")
        tec = f" [{self.tecnica}]" if self.tecnica else ""
        return (f"{cab}{tec}: {self.atacante} → {self.alvo}{det}\n"
                f"  {self.resultado.resumo()}")


def iniciativa(encontro: Encontro, aleat: Aleatoriedade) -> Tuple[str, ...]:
    """Rola a iniciativa de todos e grava no diário. Uma vez por encontro."""
    if encontro.ordem:
        raise ValueError("a iniciativa deste encontro já foi rolada")
    notas: List[Tuple[str, int, int]] = []
    for nome, c in encontro.combatentes.items():
        decl = Declaracao(
            acao=f"iniciativa no encontro",
            ator=nome,
            atributo="per",
            valor_atributo=int(c.atributos.get("per", 10)),
            bonus_atributo=c.bonus("per"),
            pericia="duelo",
            graduacao=c.graduacao("duelo"),
            dificuldade=10,
            regras=encontro.cenario.regras() + ("ESTADO:EXAUSTAO",),
            fatos={**encontro.cenario.fatos(),
                   "qi_atual": c.estado.qi,
                   "qi_maximo": max(1, c.estado.qi_maximo)},
            contexto={"rodada": 0, "origem": c.origem},
        )
        res = resolver(decl, aleat, encontro.diario)
        notas.append((nome, res.total, c.graduacao("duelo")))
    # desempate determinístico: total → graduação em Duelo → nome (alfabético).
    notas.sort(key=lambda t: (-t[1], -t[2], t[0]))
    encontro.ordem = tuple(n for n, _, _ in notas)
    if encontro.diario is not None:
        encontro.diario.registrar(
            "iniciativa",
            {"ordem": list(encontro.ordem),
             "totais": {n: t for n, t, _ in notas}},
            ator="encontro",
        )
    return encontro.ordem


def iniciar_encontro(
    cenario: Cenario,
    combatentes: Sequence[Combatente],
    aleat: Aleatoriedade,
    diario: Optional[DiarioDeAuditoria] = None,
) -> Encontro:
    """Monta o encontro, grava os fatos de cenário e rola a iniciativa."""
    if len(combatentes) < 2:
        raise ValueError("um encontro precisa de pelo menos dois combatentes")
    enc = Encontro(cenario=cenario, diario=diario)
    for c in combatentes:
        enc.adicionar(c)
    if diario is not None:
        diario.registrar("encontro_aberto",
                         {"cenario": cenario.fatos(),
                          "descricao": cenario.descricao,
                          "combatentes": [c.nome for c in combatentes],
                          "modos_de_defesa": {c.nome: c.modo.modo
                                              for c in combatentes}},
                         ator="encontro")
    iniciativa(enc, aleat)
    return enc


# --------------------------------------------------------------------------
# Ataques
# --------------------------------------------------------------------------
_REGRAS_DE_ATAQUE_BASE: Tuple[str, ...] = (
    "ELEMENTO:RELACAO", "REINO:SUPRESSAO", "ALCANCE:FAIXA",
    "POSICAO:TERRENO", "ALVO:COBERTURA", "ALVO:PASSOS_LEVES",
    "ESTADO:FERIMENTO", "ESTADO:EXAUSTAO", "ESTADO:IMOBILIZADO",
    "ESTADO:DESVIO_DE_QI", "ESTADO:DEMONIO_INTERIOR",
    "COMBATE:SURPRESA", "COMBATE:ACOES_MULTIPLOS",
    "RECURSO:ARTEFATO", "RECURSO:TALISMA", "PREPARO:QUEIMA_LONGEVIDADE",
)


_ORDEM_DE_ALCANCE: Tuple[str, ...] = ("toque", "curto", "medio", "longo", "extremo")
# ALCANCE:FAIXA conhece apenas as quatro faixas com penalidade.
_FAIXA_PARA_REGRA: Dict[str, str] = {
    "toque": "curto", "curto": "curto", "medio": "medio",
    "longo": "longo", "extremo": "extremo",
}


def _normaliza_distancia(distancia: str) -> str:
    if distancia in ("adjacente", "contato"):
        return "toque"
    if distancia not in _ORDEM_DE_ALCANCE:
        raise ValueError(f"distância {distancia!r} inválida; opções "
                         f"{_ORDEM_DE_ALCANCE + ('adjacente',)}")
    return distancia


def dentro_do_alcance(alcance: str, distancia: str) -> bool:
    """True se a arma/técnica alcança a distância declarada."""
    alcance = _normaliza_distancia(alcance) if alcance != "pessoal" else "toque"
    distancia = _normaliza_distancia(distancia)
    return _ORDEM_DE_ALCANCE.index(distancia) <= _ORDEM_DE_ALCANCE.index(alcance)


def faixa_para_regra(alcance: str, distancia: str) -> str:
    """Converte a distância declarada na categoria do fato ALCANCE:FAIXA."""
    if not dentro_do_alcance(alcance, distancia):
        raise ValueError(
            f"a distância {distancia} está fora do alcance {alcance}")
    return _FAIXA_PARA_REGRA[_normaliza_distancia(distancia)]


def atacar(
    encontro: Encontro,
    atacante: str,
    alvo: str,
    aleat: Aleatoriedade,
    *,
    pericia: Optional[str] = None,
    alcance: str = "curto",
    distancia: str = "toque",
    cobertura: str = "nenhuma",
    flanqueado: bool = False,
    oculto: bool = False,
    alvo_surpreso: bool = False,
    estudou: bool = False,
    meditou: bool = False,
    acoes_no_turno: Optional[int] = None,
    tecnica: Optional[str] = None,
    dado_alternativo: Optional[str] = None,
    elemento: Optional[str] = None,
) -> GolpeAplicado:
    """Resolve um ataque. Retorna tudo o que aconteceu, com a conta aberta."""
    if encontro.encerrado:
        raise ValueError(f"encontro encerrado: {encontro.motivo_do_encerramento}")
    atk = encontro.get(atacante)
    def_ = encontro.get(alvo)
    if atacante == alvo:
        raise ValueError("um combatente não pode atacar a si mesmo")
    if atk.caido:
        raise ValueError(f"{atacante} está caído e não pode atacar")

    tec: Optional[Tecnica] = tecnica_de(tecnica) if tecnica else None
    if tec is not None:
        if atk.estado.qi < tec.custo_qi:
            raise ValueError(
                f"{atacante} tem {atk.estado.qi} de Qi e a técnica exige "
                f"{tec.custo_qi}")
        if tec.nivel_minimo > atk.nivel:
            raise ValueError(
                f"a técnica {tec.codigo} exige nível {tec.nivel_minimo}; "
                f"{atacante} está no nível {atk.nivel}")
        alcance = tec.alcance if tec.alcance != "pessoal" else "toque"
        pericia = tec.pericia
        elemento = tec.elemento if tec.elemento != "nenhum" else atk.elemento
        atk.estado.aplicar(Mudanca("qi", -tec.custo_qi, "custo_de_tecnica",
                                   tec.codigo), encontro.diario, ator=atacante)

    elem_atacante = elemento or atk.elemento
    elem_alvo = def_.elemento
    if elem_atacante not in ELEMENTOS_CANONICOS + ("nenhum", "vazio"):
        raise ValueError(f"elemento atacante inválido {elem_atacante!r}")

    # --- cláusula de supressão de reino (gênero): não rola, recusa ----------
    lacuna = atk.nivel - def_.nivel
    if lacuna <= -LACUNA_IMBATIVEL and not (tec is not None and tec.ignora_supressao):
        return GolpeAplicado(
            resultado=None,  # type: ignore[arg-type]
            atacante=atacante, alvo=alvo, acertou=False, dano=0,
            absorvido_pelo_qi=0, dano_na_vitalidade=0, conta_do_dano="",
            tecnica=tecnica, bloqueado_por_supressao=True,
            motivo=(f"{atacante} (nível {atk.nivel}) não consegue atingir "
                    f"{alvo} (nível {def_.nivel}): a lacuna de "
                    f"{-lacuna} reinos torna o golpe impossível sem uma técnica "
                    "suprema declarada. Nenhum dado foi rolado."),
        )

    if not dentro_do_alcance(alcance, distancia):
        return GolpeAplicado(
            resultado=None, atacante=atacante, alvo=alvo, acertou=False, dano=0,
            absorvido_pelo_qi=0, dano_na_vitalidade=0, conta_do_dano="",
            tecnica=tecnica, bloqueado_por_supressao=False,
            motivo=(f"{atacante} não alcança {alvo}: alcance {alcance}, "
                    f"distância {distancia}. Nenhum dado foi rolado."),
        )
    pericia = pericia or atk.pericia_de_arma()
    if pericia not in _PERICIAS_DE_ARMA + ("folego_interno", "medicina",
                                            "intimidacao", "prestidigitacao",
                                            "passos_leves", "persuasao"):
        raise ValueError(f"perícia {pericia!r} não é uma perícia de combate")
    atributo = "per" if pericia in _PERICIAS_DE_ALCANCE else "con"

    n_acoes = int(acoes_no_turno if acoes_no_turno is not None
                  else max(1, atk.ataques_este_turno + 1))
    if not (1 <= n_acoes <= 6):
        raise ValueError(
            f"{atacante} já declarou {n_acoes} ações neste turno; o limite é 6 "
            "(COMBATE:ACOES_MULTIPLOS). Avance o turno com Encontro.proximo()."
        )
    atk.ataques_este_turno = n_acoes

    # --- fatos: só o que é objetivamente verdadeiro entra na declaração ------
    fatos: Dict[str, Any] = {
        "elemento_atacante": elem_atacante,
        "elemento_alvo": elem_alvo,
        "reino_atacante": atk.nivel,
        "reino_alvo": def_.nivel,
        "alcance": faixa_para_regra(alcance, distancia),
        "terreno": encontro.cenario.terreno,
        "cobertura": cobertura,
        "luz": encontro.cenario.luz,
        "clima": encontro.cenario.clima,
        "fengshui": encontro.cenario.fengshui,
        "densidade_qi": encontro.cenario.densidade_qi,
        "formacao": encontro.cenario.formacao,
        "ferimento": atk.fato_de_ferimento(),
        "qi_atual": atk.estado.qi,
        "qi_maximo": max(1, atk.estado.qi_maximo),
    }

    # --- regras: cada uma entra só quando o fato correspondente é real -------
    # Regras que valem para todo ataque (o mundo sempre tem terreno, luz, clima).
    regras = ["ELEMENTO:RELACAO", "REINO:SUPRESSAO", "ALCANCE:FAIXA",
              "POSICAO:TERRENO", "ALVO:COBERTURA", "ESTADO:FERIMENTO",
              "ESTADO:EXAUSTAO", "AMBIENTE:LUZ", "AMBIENTE:CLIMA",
              "AMBIENTE:FENGSHUI", "AMBIENTE:DENSIDADE_QI",
              "AMBIENTE:FORMACAO"]

    # Exclusividades declaradas no Registro de Regras (Cap. 3): não se pode
    # emboscar E surpreender, nem ter meditado E estar em desvio de Qi.
    if oculto and alvo_surpreso:
        raise ValueError(
            "POSICAO:EMBOSCADA e COMBATE:SURPRESA são mutuamente exclusivas: "
            "ou o alvo não percebeu a emboscada, ou foi pego de surpresa por "
            "outro motivo. Declare apenas uma.")
    if meditou and atk.desvio_de_qi:
        raise ValueError(
            "PREPARO:MEDITACAO e ESTADO:DESVIO_DE_QI são mutuamente exclusivas: "
            "quem está em desvio de Qi não consegue meditar.")

    def acrescentar(codigo: str, fato: str, valor: Any, quando: bool) -> None:
        if quando:
            fatos[fato] = valor
            regras.append(codigo)

    acrescentar("POSICAO:FLANCO", "flanqueado", True, bool(flanqueado))
    if oculto:
        fatos["oculto"] = True
        fatos["percebido"] = False
        regras.append("POSICAO:EMBOSCADA")
    acrescentar("COMBATE:SURPRESA", "alvo_surpreso", True, bool(alvo_surpreso))
    acrescentar("PREPARO:ESTUDO_PREVIO", "estudou", True, bool(estudou))
    acrescentar("PREPARO:MEDITACAO", "meditou", True, bool(meditou))
    acrescentar("ALVO:PASSOS_LEVES", "passos_leves", True,
                bool(def_.passos_leves_ativos))
    acrescentar("COMBATE:ACOES_MULTIPLOS", "acoes_no_turno", n_acoes, n_acoes > 1)
    acrescentar("ESTADO:IMOBILIZADO", "imobilizado", True, bool(atk.imobilizado))
    acrescentar("ESTADO:DESVIO_DE_QI", "desvio_de_qi", True,
                bool(atk.desvio_de_qi))
    acrescentar("ESTADO:DEMONIO_INTERIOR", "demonio_interior", True,
                bool(atk.demonio_interior))
    acrescentar("PREPARO:QUEIMA_LONGEVIDADE", "anos_queimados",
                atk.anos_queimados, atk.anos_queimados > 0)
    if atk.cego or atk.visao_parcial:
        fatos["visao"] = "cego" if atk.cego else "parcial"
        regras.append("ESTADO:VISAO")
    if atk.artefato != "nenhum":
        fatos["artefato"] = atk.artefato
        regras.append("RECURSO:ARTEFATO")
    if atk.talisma != "nenhum":
        fatos["talisma"] = atk.talisma
        regras.append("RECURSO:TALISMA")
    if atk.elixir != "nenhum":
        fatos["elixir"] = atk.elixir
        regras.append("RECURSO:ELIXIR")

    # sem duplicatas, mantendo a ordem declarada
    vistos: set = set()
    regras_unicas = [r for r in regras if not (r in vistos or vistos.add(r))]

    decl = Declaracao(
        acao=f"atacar {alvo}" + (f" com {tec.codigo}" if tec else
                                 f" com {pericia}"),
        ator=atacante,
        alvo=alvo,
        atributo=atributo,
        valor_atributo=int(atk.atributos.get(atributo, 10)),
        bonus_atributo=atk.bonus(atributo),
        pericia=pericia,
        graduacao=atk.graduacao(pericia),
        dificuldade=def_.defesa(),
        regras=tuple(regras_unicas),
        fatos=fatos,
        contexto={
            "rodada": encontro.rodada, "encontro": True,
            "modo_de_defesa_do_alvo": def_.modo.modo,
            "origem_do_atacante": atk.origem, "origem_do_alvo": def_.origem,
            "lacuna_de_reino": lacuna,
        },
    )
    res = resolver(decl, aleat, encontro.diario)

    if not res.sucesso:
        return GolpeAplicado(
            atacante, alvo, False, 0, 0, 0, "", tecnica, False,
            "o golpe não passou da defesa", res)

    if tec is not None:
        dano, conta = dano_de(tec, atk.nivel, atk.bonus(atributo), res.margem,
                              aleat)
    else:
        dado = dado_alternativo or f"1d{6 + max(0, atk.nivel // 2) * 2}"
        dano, conta = dano_de(
            Tecnica("LIVRE", "Golpe comum", "凡擊", "ataque", "livre", 0,
                    elem_atacante, 0, alcance, dado, pericia, 1, 0, (),
                    "Golpe sem técnica: o dado cresce com o reino."),
            atk.nivel, atk.bonus(atributo), res.margem, aleat)

    absorvido, restante = def_.receber_dano(dano, "dano_de_combate",
                                            encontro.diario, res.hash_resultado)
    if encontro.diario is not None:
        encontro.diario.registrar(
            "dano",
            {"atacante": atacante, "alvo": alvo, "dano": dano,
             "absorvido_pelo_qi": absorvido, "vitalidade_perdida": restante,
             "vitalidade_restante": def_.estado.vitalidade,
             "conta": conta, "hash_do_resultado": res.hash_resultado},
            ator=atacante,
        )
    motivo = "golpe aplicado"
    if def_.caido:
        motivo = f"{alvo} caiu (Vitalidade {def_.estado.vitalidade})"
    return GolpeAplicado(atacante, alvo, True, dano, absorvido, restante,
                         conta, tecnica, False, motivo, res)


def defender(
    encontro: Encontro,
    nome: str,
    *,
    modo: Optional[str] = None,
    acao_de_defesa: bool = False,
    guarda_total: bool = False,
    manto_de_qi: Optional[bool] = None,
) -> Combatente:
    """Usa o turno para defender. Trocar de modo consome a ação."""
    c = encontro.get(nome)
    if c.caido:
        raise ValueError(f"{nome} está caído")
    if modo is not None:
        c.modo.modo = modo
    if acao_de_defesa and guarda_total:
        raise ValueError("GUARDA_TOTAL e DEFESA_DECLARADA são exclusivas")
    c.modo.acao_de_defesa = bool(acao_de_defesa)
    c.modo.guarda_total = bool(guarda_total)
    if manto_de_qi is not None:
        c.modo.manto_de_qi = bool(manto_de_qi)
        if c.modo.manto_de_qi and c.estado.qi < 10:
            c.modo.manto_de_qi = False
    if encontro.diario is not None:
        encontro.diario.registrar("defesa_declarada",
                                  {"combatente": nome, "modo": c.modo.modo,
                                   "acao_de_defesa": c.modo.acao_de_defesa,
                                   "guarda_total": c.modo.guarda_total,
                                   "manto_de_qi": c.modo.manto_de_qi},
                                  ator=nome)
    return c


def usar_tecnica(
    encontro: Encontro,
    nome: str,
    codigo: str,
    aleat: Aleatoriedade,
    *,
    alvo: Optional[str] = None,
    distancia: str = "adjacente",
    cobertura: str = "nenhuma",
    flanqueado: bool = False,
) -> Any:
    """Usa uma técnica. Se for de ataque, delega para ``atacar``."""
    tec = tecnica_de(codigo)
    c = encontro.get(nome)
    if tec.tipo == "ataque":
        if alvo is None:
            raise ValueError("técnica de ataque exige um alvo")
        return atacar(encontro, nome, alvo, aleat, tecnica=codigo,
                      distancia=distancia, cobertura=cobertura,
                      flanqueado=flanqueado)
    # técnicas sem alvo pagam o custo e registram o efeito
    if c.estado.qi < tec.custo_qi:
        raise ValueError(f"{nome} não tem Qi suficiente ({c.estado.qi} < {tec.custo_qi})")
    c.estado.aplicar(Mudanca("qi", -tec.custo_qi, "custo_de_tecnica", codigo),
                     encontro.diario, ator=nome)
    efeitos = list(tec.efeitos)
    for eff in efeitos:
        if "Passos Leves" in eff or "Deslocamento" in eff or "movimento" in eff.lower():
            c.passos_leves_ativos = True
        if "recupera" in eff and "Vitalidade" in eff:
            cura = rolar("2d6", aleat).total + c.bonus("int")
            c.estado.aplicar(Mudanca("vitalidade", cura, "cura", codigo),
                             encontro.diario, ator=nome)
        if "recupera" in eff and "Qi" in eff:
            ganho = rolar("2d6", aleat).total + c.bonus("con")
            c.estado.aplicar(Mudanca("qi", ganho, "recuperacao_de_qi", codigo),
                             encontro.diario, ator=nome)
        if "Defesa" in eff:
            c.modo.guarda_total = True
    if encontro.diario is not None:
        encontro.diario.registrar("tecnica_utilizada",
                                  {"combatente": nome, "codigo": codigo,
                                   "tipo": tec.tipo, "alvo": alvo,
                                   "custo": tec.custo_qi, "efeitos": efeitos},
                                  ator=nome)
    return efeitos


def encerrar(encontro: Encontro, motivo: str) -> str:
    encontro.encerrado = True
    encontro.motivo_do_encerramento = motivo
    if encontro.diario is not None:
        encontro.diario.registrar("encontro_encerrado",
                                  {"motivo": motivo, "rodadas": encontro.rodada,
                                   "sobreviventes": [c.nome for c in encontro.ativos()]},
                                  ator="encontro")
    return motivo
