# -*- coding: utf-8 -*-
"""
XAN — Personagens: Raiz Espiritual, Perícias, Ficha e Estado auditável.
======================================================================

Criação fiel ao gênero
----------------------
* **Raiz Espiritual (靈根)**: de 1 a 5 elementos. Quanto menos elementos, mais
  pura e mais rápida a ascensão — a raiz de cinco elementos ("falsa raiz") é o
  fundo do poço clássico dos protagonistas, e raízes mutantes (Gelo, Trovão,
  Vento, Trevas, Vazio, Caos) são a revelação que muda tudo.
* **Graus**: Céu / Terra / Preto / Amarelo / Desperdício, com raridades reais
  em pesos inteiros.
* **Seis atributos** do ACS (Percepção, Constituição, Carisma, Inteligência,
  Sorte) mais o Potencial (根骨).

Estado auditável
----------------
Atributos, Lei e Reino são **imutáveis** (``Personagem`` é frozen). O que muda
durante o jogo — Qi, Vitalidade, XP, longevidade — vive em ``EstadoDeJogo``,
onde **toda alteração exige um motivo catalogado** e pode ser gravada no diário
encadeado. Ou seja: ninguém "esquece" de anotar dano, e ninguém cura por
conveniência sem deixar rastro.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .auditoria import DiarioDeAuditoria
from .entropia import Aleatoriedade
from .reinos import (
    CAMINHOS, MONSTRO, Lei, REINOS, compatibilidade_de_lei, defesa_de, lei_de,
    longevidade_base, qi_maximo, reino_de, vitalidade_maxima,
)
from .regras import ELEMENTOS_CANONICOS

__all__ = [
    "Pericia", "PERICIAS", "pericia_de", "pericias_de_grupo",
    "GRAUS_DE_RAIZ", "MUTACOES", "RaizEspiritual", "sortear_raiz",
    "Personagem", "criar_personagem", "EstadoDeJogo", "Mudanca", "MOTIVOS",
    "RACAS", "TABELAS_DE_RAIZ", "ferimento_por_vitalidade", "GRUPOS_DE_PERICIA",
]

RACAS: Tuple[str, ...] = ("humano", "besta_espiritual", "espirito", "renascido",
                          "demonio", "meio_sangue")


# --------------------------------------------------------------------------
# Perícias
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Pericia:
    codigo: str
    nome: str
    atributo: str
    grupo: str
    chines: str = ""
    descricao: str = ""
    sem_treinamento: bool = True   # pode ser usada com graduação 0?


PERICIAS: Dict[str, Pericia] = {}


def _p(codigo, nome, atributo, grupo, chines="", descricao="", sem_treinamento=True):
    if codigo in PERICIAS:
        raise ValueError(f"perícia {codigo} duplicada")
    if atributo not in ("per", "con", "cha", "int", "luk", "pot"):
        raise ValueError(f"atributo inválido em {codigo}")
    p = Pericia(codigo, nome, atributo, grupo, chines, descricao, sem_treinamento)
    PERICIAS[codigo] = p
    return p


# --- Marciais (武) ---
_p("espada", "Espada", "con", "marcial", "劍", "Espada reta (jian): a arma do cavalheiro.")
_p("sabre", "Sabre", "con", "marcial", "刀", "Sabre (dao): cortes amplos e brutais.")
_p("lanca", "Lança", "con", "marcial", "槍", "Lança e alabarda; domina o alcance.")
_p("punho", "Punho", "con", "marcial", "拳", "Punhos e mãos nuas, artes externas.")
_p("palma", "Palma", "int", "marcial", "掌", "Palmas internas que transmitem Qi.")
_p("arma_oculta", "Armas Ocultas", "per", "marcial", "暗器",
   "Agulhas, dardos, facas de arremesso — a especialidade do Clã Tang.", False)
_p("arco", "Arco", "per", "marcial", "弓", "Arcos e bestas.")
_p("cajado", "Cajado", "con", "marcial", "棍", "Bastão, cajado e armas contundentes.")
_p("arma_exotica", "Arma Exótica", "per", "marcial", "奇門",
   "Leques, correntes, garras, fios de seda.", False)
_p("duelo", "Duelo", "per", "marcial", "對決", "Ler o adversário: um contra um.", False)

# --- Corporais (體) ---
_p("corpo_de_ferro", "Corpo de Ferro", "con", "corporal", "鐵布衫",
   "Endurecer a carne para absorver golpes.")
_p("passos_leves", "Passos Leves", "per", "corporal", "輕功",
   "Qinggong: correr sobre água, escalar paredes, saltar telhados.")
_p("resistencia_a_veneno", "Resistência a Veneno", "con", "corporal", "抗毒")
_p("folego_interno", "Fôlego Interno", "con", "corporal", "內息",
   "Prender a respiração, suportar frio/calor, recuperar Qi.")
_p("acupuntura_propria", "Pontos de Acupuntura", "per", "corporal", "穴道",
   "Selar/abrir os próprios pontos: parar sangramento, ignorar dor.", False)

# --- Mentais (心) ---
_p("compreensao", "Compreensão", "int", "mental", "悟",
   "Entender manuais e romper gargalos. A perícia das rupturas.")
_p("meditacao", "Meditação", "pot", "mental", "入定",
   "Entrar em transe: recuperar Qi e estabilizar o Coração do Dao.")
_p("estrategia", "Estratégia", "int", "mental", "兵法", "Batalhas, emboscadas, tropas.")
_p("percepcao_de_qi", "Sense de Qi", "per", "mental", "氣感",
   "Sentir Qi, auras, reino alheio e veias espirituais.", False)
_p("vontade_de_ferro", "Vontade de Ferro", "pot", "mental", "道心",
   "Resistir a medo, Demônios Interiores e ilusões.")

# --- Sociais (世) ---
_p("persuasao", "Persuasão", "cha", "social", "說服")
_p("intimidacao", "Intimidação", "cha", "social", "威壓")
_p("etiqueta", "Etiqueta do Murim", "cha", "social", "禮節",
   "Hierarquia de seitas, saudações, quem senta onde.")
_p("negociacao", "Negociação", "cha", "social", "交易")
_p("mentira", "Enganação", "cha", "social", "欺騙", False)
_p("leitura_de_pessoas", "Leitura de Pessoas", "per", "social", "察言",
   "Perceber intenção, medo e mentira.", False)
_p("lideranca", "Liderança", "cha", "social", "統領")

# --- Saberes (學) ---
_p("alquimia", "Alquimia", "int", "saber", "丹道", "Refinar elixires.", False)
_p("forja_de_artefatos", "Forja de Artefatos", "int", "saber", "煉器", False)
_p("talismas", "Talismãs", "int", "saber", "符籙", False)
_p("formacoes", "Formações", "int", "saber", "陣法",
   "Montar e desfazer matrizes de Qi.", False)
_p("medicina", "Medicina", "int", "saber", "醫術", False)
_p("ervas", "Ervas Espirituais", "per", "saber", "草藥")
_p("historia_das_seitas", "História das Seitas", "int", "saber", "宗門史")
_p("leitura_de_fengshui", "Leitura de Feng Shui", "per", "saber", "風水", False)
_p("astrologia", "Astrologia", "int", "saber", "星象", False)
_p("bestas_espirituais", "Bestas Espirituais", "int", "saber", "妖獸")
_p("linguas_antigas", "Línguas Antigas", "int", "saber", "古文", False)

# --- Mundanas (凡) ---
_p("sobrevivencia", "Sobrevivência", "per", "mundana", "求生")
_p("rastreamento", "Rastreamento", "per", "mundana", "追蹤")
_p("furtividade", "Furtividade", "per", "mundana", "潛行")
_p("prestidigitacao", "Prestidigitação", "per", "mundana", "手法", False)
_p("cavalgar", "Cavalgar", "pot", "mundana", "騎術")
_p("oficio", "Ofício", "int", "mundana", "工藝")
_p("comercio", "Comércio", "cha", "mundana", "商道")
_p("navegacao", "Navegação", "int", "mundana", "航海")
_p("jogos", "Jogos e Apostas", "luk", "mundana", "賭")
_p("cozinha", "Cozinha Espiritual", "per", "mundana", "靈廚")


def pericia_de(codigo: str) -> Pericia:
    if codigo not in PERICIAS:
        raise ValueError(
            f"perícia {codigo!r} não existe. Publicadas: {len(PERICIAS)}")
    return PERICIAS[codigo]


def pericias_de_grupo(grupo: str) -> Tuple[Pericia, ...]:
    return tuple(p for p in PERICIAS.values() if p.grupo == grupo)


GRUPOS_DE_PERICIA: Tuple[str, ...] = ("marcial", "corporal", "mental",
                                      "social", "saber", "mundana")


# --------------------------------------------------------------------------
# Raiz Espiritual (靈根)
# --------------------------------------------------------------------------
GRAUS_DE_RAIZ: Tuple[str, ...] = ("ceu", "terra", "preto", "amarelo", "desperdicio")

GRAU_POR_NUMERO_DE_ELEMENTOS: Dict[int, Tuple[str, int]] = {
    # nº de elementos → (grau, pureza máxima em %)
    1: ("ceu", 100),
    2: ("terra", 85),
    3: ("preto", 65),
    4: ("amarelo", 45),
    5: ("desperdicio", 30),
}

MUTACOES: Tuple[Tuple[str, str, str], ...] = (
    # (codigo, nome, elemento substituto / efeito)
    ("gelo", "Raiz de Gelo", "agua"),
    ("trovao", "Raiz do Trovão", "metal"),
    ("vento", "Raiz do Vento", "madeira"),
    ("trevas", "Raiz das Trevas", "agua"),
    ("vazio", "Raiz do Vazio", "vazio"),
    ("caos", "Raiz do Caos", "nenhum"),
    ("espaco", "Raiz do Espaço", "terra"),
    ("tempo", "Raiz do Tempo", "fogo"),
)

# Peso inteiro por número de elementos.
TABELAS_DE_RAIZ: Dict[str, Dict[int, int]] = {
    # População comum do mundo (NPCs, discípulos externos, figurantes).
    "realista": {1: 1, 2: 20, 3: 200, 4: 1200, 5: 8579},
    # PADRÃO PARA PERSONAGENS DOS JOGADORES: um grupo de protagonistas.
    # Raiz de cinco elementos ainda é a mais comum — ninguém é especial de graça.
    "heroica": {1: 40, 2: 360, 3: 1600, 4: 3000, 5: 5000},
    # Era de ouro do cultivo: gênios em cada vila.
    "lendária": {1: 300, 2: 1400, 3: 2800, 4: 3200, 5: 2300},
    # Wuxia puro: quase ninguém nasce com talento; o esforço decide tudo.
    "mortal": {1: 0, 2: 2, 3: 30, 4: 400, 5: 9568},
}
_PESOS_ELEMENTOS: Dict[int, int] = TABELAS_DE_RAIZ["realista"]
# Chance de mutação por grau (em 10 000)
_PESOS_MUTACAO: Dict[str, int] = {
    "ceu": 2500, "terra": 400, "preto": 80, "amarelo": 25, "desperdicio": 30,
}


@dataclass(frozen=True)
class RaizEspiritual:
    elementos: Tuple[str, ...]
    grau: str
    pureza: int            # 0..100 — teto de pureza do Qi
    mutacao: Optional[str]

    def __post_init__(self) -> None:
        if self.grau not in GRAUS_DE_RAIZ:
            raise ValueError(f"grau de raiz inválido {self.grau!r}")
        for e in self.elementos:
            if e not in ELEMENTOS_CANONICOS:
                raise ValueError(f"elemento inválido na raiz: {e!r}")
        if len(set(self.elementos)) != len(self.elementos):
            raise ValueError("elementos duplicados na raiz")
        esperado, teto = GRAU_POR_NUMERO_DE_ELEMENTOS[len(self.elementos)]
        if self.grau != esperado:
            raise ValueError(
                f"raiz com {len(self.elementos)} elementos deve ter grau "
                f"{esperado!r}, não {self.grau!r}"
            )
        if not (1 <= self.pureza <= teto):
            raise ValueError(f"pureza {self.pureza} fora de 1..{teto} para {self.grau}")
        if self.mutacao is not None and self.mutacao not in {m[0] for m in MUTACOES}:
            raise ValueError(f"mutação inválida {self.mutacao!r}")

    @property
    def elemento_dominante(self) -> str:
        if self.mutacao:
            return dict((m[0], m[2]) for m in MUTACOES)[self.mutacao]
        return self.elementos[0] if len(self.elementos) == 1 else self.elementos[0]

    @property
    def multiplicador_de_cultivo(self) -> int:
        """Percentual inteiro de velocidade de cultivo (100 = normal)."""
        base = {"ceu": 400, "terra": 220, "preto": 140,
                "amarelo": 90, "desperdicio": 40}[self.grau]
        ajuste = (self.pureza - 50) // 5          # −10..+10
        if self.mutacao:
            ajuste += 25
        return max(10, base + ajuste)

    def texto(self) -> str:
        els = ", ".join(self.elementos)
        mut = ""
        if self.mutacao:
            nome = dict((m[0], m[1]) for m in MUTACOES)[self.mutacao]
            mut = f" — MUTAÇÃO: {nome}"
        return (f"Raiz Espiritual {self.grau.title()} ({els}), pureza {self.pureza}%"
                f", cultivo a {self.multiplicador_de_cultivo}%{mut}")


def sortear_raiz(aleat: Aleatoriedade, *, forcar_grau: Optional[str] = None,
                 sorte: int = 10, tabela: str = "realista") -> RaizEspiritual:
    """Sorteia uma raiz espiritual.

    ``tabela`` escolhe o **regime de raridades da mesa** — realista, heroica,
    lendária ou mortal. É uma regra escolhida ANTES da criação e aplicada a
    todos os jogadores igualmente: diferente de vantagem narrativa, que é
    decidida depois de ver o dado.

    ``sorte`` (atributo LUK, 1..30) desloca os pesos: cada ponto acima de 10
    aumenta em 3% o peso das raízes puras.
    """
    if forcar_grau is not None and forcar_grau not in GRAUS_DE_RAIZ:
        raise ValueError(f"grau inválido {forcar_grau!r}")
    if tabela not in TABELAS_DE_RAIZ:
        raise ValueError(
            f"tabela {tabela!r} inexistente; opções {sorted(TABELAS_DE_RAIZ)}")
    fator = max(10, 100 + (int(sorte) - 10) * 3)
    pesos = dict(TABELAS_DE_RAIZ[tabela])
    # Com fator = 100 (Sorte 10) a tabela publicada é reproduzida exatamente;
    # Sorte acima de 10 só inclina as raízes puras, nunca as inventa.
    for k in (1, 2, 3):
        pesos[k] = max(1, pesos[k] * fator // 100)
    nums = sorted(pesos)
    n = aleat.escolher_ponderado(nums, [pesos[k] for k in nums])

    grau, teto = GRAU_POR_NUMERO_DE_ELEMENTOS[n]
    if forcar_grau:
        grau = forcar_grau
        n = [k for k, v in GRAU_POR_NUMERO_DE_ELEMENTOS.items() if v[0] == grau][0]
        _, teto = GRAU_POR_NUMERO_DE_ELEMENTOS[n]

    elementos = tuple(sorted(aleat.amostrar(list(ELEMENTOS_CANONICOS), n)))
    piso = max(1, teto - 40)
    pureza = aleat.entre(piso, teto)

    mutacao = None
    chance = _PESOS_MUTACAO[grau]
    if aleat.abaixo(10_000) < chance:
        mutacao = aleat.escolher([m[0] for m in MUTACOES])
    return RaizEspiritual(elementos, grau, pureza, mutacao)


# --------------------------------------------------------------------------
# Personagem (imutável)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Personagem:
    nome: str
    raca: str
    sexo: str
    idade: int
    atributos: Mapping[str, int]
    raiz: RaizEspiritual
    caminho: str
    nivel: int
    lei: Optional[str]
    pericias: Mapping[str, int]
    grau_do_nucleo: Optional[int] = None
    faccao: str = ""
    posto: str = ""
    origem: str = ""
    traços: Tuple[str, ...] = ()
    desejo: str = ""
    obsessao: str = ""
    segredo: str = ""
    tecnica_natal: str = ""
    identificador: str = ""

    def __post_init__(self) -> None:
        if not self.nome.strip():
            raise ValueError("personagem sem nome")
        if self.raca not in RACAS:
            raise ValueError(f"raça inválida {self.raca!r}")
        if self.caminho not in CAMINHOS:
            raise ValueError(f"caminho inválido {self.caminho!r}")
        if not (0 <= self.nivel <= 13):
            raise ValueError("nível fora de 0..13")
        for k, v in self.atributos.items():
            if k not in ("per", "con", "cha", "int", "luk", "pot"):
                raise ValueError(f"atributo desconhecido {k!r}")
            if not isinstance(v, int) or isinstance(v, bool):
                raise TypeError(f"atributo {k} deve ser int")
            if not (1 <= v <= 30):
                raise ValueError(f"atributo {k}={v} fora de 1..30")
        for k in ("per", "con", "cha", "int", "luk", "pot"):
            if k not in self.atributos:
                raise ValueError(f"atributo {k} ausente")
        for k, v in self.pericias.items():
            if k not in PERICIAS:
                raise ValueError(f"perícia desconhecida {k!r}")
            if not (0 <= v <= 5):
                raise ValueError(f"graduação de {k} fora de 0..5")
        if self.lei is not None:
            lei = lei_de(self.lei)
            if lei.caminho != self.caminho and self.caminho != MONSTRO:
                raise ValueError(
                    f"a Lei {lei.codigo} pertence ao caminho {lei.caminho}, "
                    f"não a {self.caminho}")
        if self.grau_do_nucleo is not None:
            if not (1 <= self.grau_do_nucleo <= 9):
                raise ValueError("grau do núcleo vai de 1 a 9")
            if self.nivel < 7:
                raise ValueError("só existe Núcleo Dourado a partir do nível 7")
        if self.nivel >= 7 and self.caminho == "xiandao" and self.grau_do_nucleo is None:
            raise ValueError("Xiandao nível 7+ exige o grau do Núcleo Dourado")

    # -- derivados ---------------------------------------------------------
    @property
    def lei_obj(self) -> Optional[Lei]:
        return lei_de(self.lei) if self.lei else None

    def bonus(self, atributo: str) -> int:
        return (int(self.atributos[atributo]) - 10) // 2

    def compatibilidade(self) -> Tuple[int, List[str]]:
        if self.lei is None:
            raise ValueError("personagem sem Lei não tem compatibilidade")
        return compatibilidade_de_lei(self.atributos, lei_de(self.lei))

    @property
    def qi_max(self) -> int:
        return qi_maximo(self.nivel, self.atributos["con"],
                         self.atributos["per"], self.atributos["int"],
                         self.grau_do_nucleo)

    @property
    def vitalidade_max(self) -> int:
        return vitalidade_maxima(self.nivel, self.atributos["con"],
                                 self.atributos["pot"])

    def defesa(self, modo: str, manto_de_qi: bool = False) -> int:
        atr = "per" if modo == "esquiva" else "con"
        per = ("passos_leves" if modo == "esquiva" else
               "corpo_de_ferro" if modo == "resistencia" else self._pericia_de_arma())
        return defesa_de(modo, self.nivel, self.atributos[atr],
                         self.pericias.get(per, 0), manto_de_qi)

    def _pericia_de_arma(self) -> str:
        for codigo in ("espada", "sabre", "lanca", "punho", "palma",
                       "cajado", "arma_oculta", "arco", "arma_exotica"):
            if self.pericias.get(codigo, 0) > 0:
                return codigo
        return "punho"

    @property
    def longevidade(self) -> int:
        return longevidade_base(self.nivel)

    @property
    def reino_nome(self) -> str:
        return reino_de(self.nivel).nome_para(self.caminho)

    def resumo(self) -> str:
        a = self.atributos
        attrs = " ".join(f"{k.upper()}{a[k]}" for k in ("per", "con", "cha", "int", "luk", "pot"))
        lei = f" | Lei: {lei_de(self.lei).nome}" if self.lei else ""
        nucleo = f" | Núcleo grau {self.grau_do_nucleo}" if self.grau_do_nucleo else ""
        return (f"{self.nome} ({self.raca}, {self.idade}a) — nível {self.nivel} "
                f"{self.reino_nome}{lei}{nucleo}\n  {attrs}\n  {self.raiz.texto()}"
                f"\n  Qi {self.qi_max} · Vitalidade {self.vitalidade_max}"
                f"\n  {self.faccao or 'sem facção'}{(' — ' + self.posto) if self.posto else ''}")


def criar_personagem(
    *,
    nome: str,
    aleat: Optional[Aleatoriedade] = None,
    raca: str = "humano",
    sexo: str = "",
    idade: Optional[int] = None,
    metodo: str = "sorteio",
    pontos: int = 78,
    atributos: Optional[Mapping[str, int]] = None,
    raiz: Optional[RaizEspiritual] = None,
    caminho: str = "xiandao",
    nivel: int = 1,
    lei: Optional[str] = None,
    pericias: Optional[Mapping[str, int]] = None,
    pontos_de_pericia: int = 12,
    tabela_de_raiz: str = "heroica",
    faccao: str = "",
    posto: str = "",
    origem: str = "",
    grau_do_nucleo: Optional[int] = None,
) -> Personagem:
    """Cria um personagem por sorteio (com a entropia do motor) ou por pontos.

    ``metodo="sorteio"``: 4d6kh3 por atributo (3–18), como manda a tradição.
    ``metodo="pontos"``: começa tudo em 8 e distribui ``pontos`` inteiros,
    com custo crescente acima de 14 — compra honesta, sem bônus escondido.
    """
    if metodo not in ("sorteio", "pontos", "manual"):
        raise ValueError("método deve ser sorteio, pontos ou manual")
    if metodo == "manual" and not atributos:
        raise ValueError("método manual exige atributos")
    aleat = aleat or Aleatoriedade()

    if atributos is not None:
        attrs: Dict[str, int] = dict(atributos)
        for k in ("per", "con", "cha", "int", "luk", "pot"):
            attrs.setdefault(k, 10)
    elif metodo == "sorteio":
        from .dados import rolar
        attrs = {}
        for k in ("per", "con", "cha", "int", "luk", "pot"):
            attrs[k] = max(3, min(18, rolar("4d6kh3", aleat).total))
    else:
        attrs = {k: 8 for k in ("per", "con", "cha", "int", "luk", "pot")}
        restantes = pontos - 6 * 8
        if restantes < 0:
            raise ValueError("pontos insuficientes para o mínimo de 8 por atributo")
        while restantes > 0:
            candidatas = [k for k in attrs
                          if attrs[k] < 20 and _custo(attrs[k] + 1) <= restantes]
            if not candidatas:
                break
            k = aleat.escolher(sorted(candidatas))
            custo = _custo(attrs[k] + 1)
            attrs[k] += 1
            restantes -= custo

    if raiz is None:
        raiz = sortear_raiz(aleat, sorte=attrs["luk"], tabela=tabela_de_raiz)

    if sexo == "":
        sexo = aleat.escolher(["masculino", "feminino"])
    if idade is None:
        idade = aleat.entre(14, 30) if raca == "humano" else aleat.entre(10, 120)

    per: Dict[str, int] = dict(pericias or {})
    if not per:
        # Distribui pontos de perícia: máximo 5 por perícia e no máximo 3
        # perícias distintas por grupo, para ninguém virar onisciente.
        TETO_POR_GRUPO = 3
        restantes = int(pontos_de_pericia)
        while restantes > 0:
            candidatas = sorted(
                c for c, p in PERICIAS.items()
                if per.get(c, 0) < 5
                and sum(1 for x, g in per.items() if PERICIAS[x].grupo == p.grupo
                        and per[x] > 0) < TETO_POR_GRUPO
                or (per.get(c, 0) > 0 and per.get(c, 0) < 5)
            )
            candidatas = sorted(set(candidatas))
            if not candidatas:
                break
            c = aleat.escolher(candidatas)
            per[c] = per.get(c, 0) + 1
            restantes -= 1

    return Personagem(
        nome=nome, raca=raca, sexo=sexo, idade=idade, atributos=attrs,
        raiz=raiz, caminho=caminho, nivel=nivel, lei=lei, pericias=per,
        grau_do_nucleo=grau_do_nucleo, faccao=faccao, posto=posto, origem=origem,
        identificador=(aleat.unico() if aleat else ""),
    )


def _custo(valor_alvo: int) -> int:
    """Custo do próximo ponto: 1 até 14, 2 até 17, 3 acima."""
    if valor_alvo <= 14:
        return 1
    if valor_alvo <= 17:
        return 2
    return 3


# --------------------------------------------------------------------------
# Estado de jogo auditável
# --------------------------------------------------------------------------
MOTIVOS: Tuple[str, ...] = (
    "dano_de_combate", "dano_de_tribulacao", "dano_ambiental", "veneno",
    "cura", "elixir", "medicina", "recuperacao_natural",
    "gasto_de_qi", "recuperacao_de_qi", "meditacao", "pedra_espiritual",
    "ganho_de_xp", "perda_de_xp", "treino", "recompensa", "formacao_de_nucleo",
    "envelhecimento", "queima_de_longevidade", "desvio_de_qi", "regressao",
    "custo_de_tecnica", "corrupcao", "bencao", "criacao",
)


@dataclass(frozen=True)
class Mudanca:
    campo: str
    delta: int
    motivo: str
    origem: str = ""     # código de regra, hash de Resultado, ou descrição curta

    def __post_init__(self) -> None:
        if self.campo not in ("qi", "vitalidade", "xp", "longevidade",
                              "estado_mental", "fe", "essencia"):
            raise ValueError(f"campo alterável inválido {self.campo!r}")
        if self.motivo not in MOTIVOS:
            raise ValueError(
                f"motivo {self.motivo!r} não catalogado. Motivos legais: "
                f"{len(MOTIVOS)}")
        if isinstance(self.delta, bool) or not isinstance(self.delta, int):
            raise TypeError("delta deve ser int")


@dataclass
class EstadoDeJogo:
    """Recursos que mudam durante a sessão. Cada mudança é motivada e logável."""

    qi: int = 0
    vitalidade: int = 0
    xp: int = 0
    longevidade: int = 0
    estado_mental: int = 70      # Coração do Dao, 0..200
    fe: int = 0                  # Shendao
    essencia: int = 0            # cultivo corporal
    face: int = 0                # Mianzi
    qi_maximo: int = 1
    vitalidade_maxima: int = 1
    desvio_de_qi: bool = False
    demonio_interior: Optional[str] = None
    meridianos_abertos: int = 0
    ferimentos: Tuple[str, ...] = ()
    historico: Tuple[Mudanca, ...] = ()

    LIMITES_FIXOS = {"estado_mental": (0, 200), "face": (-50, 50)}

    def limites(self) -> Dict[str, Tuple[int, int]]:
        """Limites derivados dos máximos declarados — nada de número mágico."""
        lim = dict(self.LIMITES_FIXOS)
        lim["qi"] = (0, max(1, self.qi_maximo))
        lim["vitalidade"] = (-10_000, max(1, self.vitalidade_maxima))
        lim["xp"] = (0, 10 ** 9)
        lim["longevidade"] = (0, 10 ** 6)
        lim["fe"] = (0, 10 ** 7)
        lim["essencia"] = (0, 10 ** 7)
        return lim

    @classmethod
    def de_personagem(cls, p: "Personagem") -> "EstadoDeJogo":
        return cls(
            qi=p.qi_max, vitalidade=p.vitalidade_max, xp=0,
            longevidade=p.longevidade, estado_mental=70,
            qi_maximo=p.qi_max, vitalidade_maxima=p.vitalidade_max,
            meridianos_abertos=min(12, p.nivel * 2),
        )

    def aplicar(self, mudanca: Mudanca,
                diario: Optional[DiarioDeAuditoria] = None,
                ator: str = "") -> "EstadoDeJogo":
        limites = self.limites()
        if mudanca.campo not in limites:
            raise ValueError(f"campo {mudanca.campo} não tem limite definido")
        lo, hi = limites[mudanca.campo]
        atual = int(getattr(self, mudanca.campo))
        novo = max(lo, min(hi, atual + mudanca.delta))
        setattr(self, mudanca.campo, novo)
        self.historico = self.historico + (mudanca,)
        if diario is not None:
            diario.registrar(
                "estado",
                {"campo": mudanca.campo, "de": atual, "para": novo,
                 "delta": mudanca.delta, "motivo": mudanca.motivo,
                 "origem": mudanca.origem},
                ator=ator,
            )
        return self

    def vivo(self) -> bool:
        return self.vitalidade > 0

    def escudo_de_qi(self) -> int:
        """Inteiro 0..10 para ``defesa_de``."""
        return max(0, min(10, self.qi // 100))

    def estado_de_ferimento(self) -> str:
        """Fato objetivo para ESTADO:FERIMENTO — derivado da aritmética."""
        return ferimento_por_vitalidade(self.vitalidade, self.vitalidade_maxima)

    def fatos_para_regras(self) -> Dict[str, Any]:
        """Fatos objetivos que este estado fornece ao Registro de Regras."""
        return {
            "ferimento": self.estado_de_ferimento(),
            "qi_atual": self.qi,
            "qi_maximo": self.qi_maximo,
            "desvio_de_qi": bool(self.desvio_de_qi),
            "demonio_interior": self.demonio_interior is not None,
        }


def ferimento_por_vitalidade(atual: int, maximo: int) -> str:
    """Traduz a fração de Vitalidade no fato usado por ESTADO:FERIMENTO."""
    if maximo <= 0:
        raise ValueError("vitalidade máxima deve ser positiva")
    if atual <= 0:
        return "agonizando"
    pct = (atual * 100) // maximo
    if pct >= 75:
        return "ileso"
    if pct >= 40:
        return "ferido"
    if pct >= 15:
        return "grave"
    return "agonizando"
