# -*- coding: utf-8 -*-
"""
XAN — Mundo procedural.
=======================

Um mundo inteiro gerado por regras, reproducible a partir da semente:

    continente → 9 províncias (九州) → sítios → facções → relações → história
                 → NPCs notáveis → tesouros → clima do ano corrente

O princípio é o mesmo do motor de dados: **a semente decide, ninguém mais**.
Duas mesas com a mesma semente encontram a mesma montanha, o mesmo rancor de
trezentos anos e o mesmo poço envenenado. Mudar a semente muda o mundo inteiro,
não o detalhe que incomoda o mestre.

A história não é decoração: cada evento do passado **causa** um fato do presente
(uma guerra antiga gera uma ruína no campo de batalha e ódio entre duas facções;
a queda de uma seita gera um reino secreto perdido; a tribulação de um imortal
gera uma terra devastada). O mundo é lido de trás para frente.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .calendario import Data, ESTACOES, Hora, sortear_clima
from .entropia import Aleatoriedade, FonteSemeada
from .regras import (
    ELEMENTOS_CANONICOS, ELEMENTOS_GERADORES, ELEMENTOS_NEUTROS,
    ELEMENTOS_SUPERADORES, relacao_elemental,
)

__all__ = [
    "TERRENOS", "TIPOS_DE_SITIO", "DENSIDADES_DE_QI",
    "nome_de_provincia", "nome_de_sitio", "nome_de_faccao",
    "Provincia", "Sitio", "Faccao", "Evento", "TesouroLendario", "Mundo",
    "gerar_mundo", "carregar_mundo", "DensidadeDeQi",
]

TERRENOS: Tuple[str, ...] = (
    "montanhas", "planicies", "florestas", "deserto", "tundra", "litoral",
    "arquipelago", "pantano", "vales", "planalto", "vulcanico", "estepe",
)

TIPOS_DE_SITIO: Tuple[str, ...] = (
    "seita_ortodoxa", "seita_nao_ortodoxa", "culto_demoniaco", "cla_nobre",
    "cidade", "vila", "mercado_negro", "ruina", "caverna_de_bestas",
    "floresta_proibida", "pico_de_cultivo", "lago_espiritual", "templo",
    "reino_secreto", "fortaleza", "porto", "passo_de_montanha", "campo_de_batalha",
    "veia_espiritual", "tumba_antiga", "mosteiro", "torre_de_observacao",
)

# Categoria para a regra AMBIENTE:DENSIDADE_QI
DENSIDADES_DE_QI: Tuple[str, ...] = (
    "esteril", "pobre", "comum", "rica", "veia_espiritual", "terra_imortal",
)


def DensidadeDeQi(valor: int) -> str:
    """Converte densidade numérica 0–10 no fato categórico usado pelas regras."""
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise TypeError("densidade deve ser int")
    if not (0 <= valor <= 10):
        raise ValueError("densidade de Qi vai de 0 a 10")
    if valor <= 1:
        return "esteril"
    if valor <= 3:
        return "pobre"
    if valor <= 5:
        return "comum"
    if valor <= 7:
        return "rica"
    if valor <= 9:
        return "veia_espiritual"
    return "terra_imortal"


# ==========================================================================
# Geradores de nomes
# ==========================================================================
_PREFIXOS: Tuple[Tuple[str, str], ...] = (
    ("Qing", "青"), ("Cang", "蒼"), ("Dong", "東"), ("Xi", "西"), ("Nan", "南"),
    ("Bei", "北"), ("Yun", "雲"), ("Long", "龍"), ("Hu", "虎"), ("Feng", "鳳"),
    ("Yu", "玉"), ("Jin", "金"), ("Yin", "銀"), ("Tie", "鐵"), ("Bing", "冰"),
    ("Huo", "火"), ("Lei", "雷"), ("Feng", "風"), ("Yue", "月"), ("Ri", "日"),
    ("Xing", "星"), ("Tian", "天"), ("Di", "地"), ("Shan", "山"), ("Shui", "水"),
    ("Hua", "花"), ("Zhu", "竹"), ("Song", "松"), ("Mei", "梅"), ("Lan", "蘭"),
    ("Lian", "蓮"), ("Jian", "劍"), ("Xue", "血"), ("You", "幽"), ("Xuan", "玄"),
    ("Bi", "碧"), ("Zi", "紫"), ("Bai", "白"), ("Hei", "黑"), ("Hong", "紅"),
    ("Chang", "長"), ("Tai", "太"), ("Wu", "無"), ("Jiu", "九"), ("Qian", "千"),
    ("Wan", "萬"), ("San", "三"), ("Wu", "五"), ("Qi", "七"), ("Su", "素"),
    ("Mo", "墨"), ("Huang", "荒"), ("Gu", "古"), ("Xin", "新"), ("Ling", "靈"),
)

_SUFIXOS_LUGAR: Tuple[Tuple[str, str], ...] = (
    ("shan", "山"), ("feng", "峰"), ("ling", "嶺"), ("ya", "崖"), ("gu", "谷"),
    ("hu", "湖"), ("hai", "海"), ("jiang", "江"), ("quan", "泉"), ("tan", "潭"),
    ("lin", "林"), ("sen", "森"), ("yuan", "原"), ("ye", "野"), ("zhou", "洲"),
    ("dao", "島"), ("cheng", "城"), ("du", "都"), ("zhen", "鎮"), ("cun", "村"),
    ("dong", "洞"), ("ku", "窟"), ("jing", "境"),
)

_SUFIXOS_INSTITUICAO: Tuple[Tuple[str, str], ...] = (
    ("pai", "派"), ("zong", "宗"), ("men", "門"), ("jiao", "教"), ("jia", "家"),
    ("tang", "堂"), ("ge", "閣"), ("gong", "宮"), ("dian", "殿"), ("si", "寺"),
    ("guan", "觀"), ("miao", "廟"), ("lou", "樓"), ("ta", "塔"), ("meng", "盟"),
    ("bang", "幫"), ("hui", "會"), ("fu", "府"),
)

_SUSTANTIVOS_FACCAO = {
    "seita_ortodoxa": ("Seita", "宗門"),
    "seita_nao_ortodoxa": ("Seita", "邪派"),
    "culto_demoniaco": ("Culto", "魔教"),
    "cla_nobre": ("Clã", "世家"),
    "mosteiro": ("Mosteiro", "寺院"),
    "templo": ("Templo", "神殿"),
    "mercado_negro": ("Sindicato", "黑市"),
    "fortaleza": ("Fortaleza", "堡"),
}

_ELEMENTO_DE_PREFIXO: Dict[str, str] = {
    "Bing": "agua", "Shui": "agua", "Hai": "agua", "Yue": "agua", "Yin": "agua",
    "You": "agua", "Su": "agua", "Mo": "agua",
    "Huo": "fogo", "Ri": "fogo", "Lei": "fogo", "Hong": "fogo", "Zi": "fogo",
    "Xue": "fogo",
    "Jin": "metal", "Tie": "metal", "Jian": "metal", "Xing": "metal",
    "Bai": "metal", "Qiu": "metal",
    "Song": "madeira", "Zhu": "madeira", "Mei": "madeira", "Lan": "madeira",
    "Lian": "madeira", "Hua": "madeira", "Qing": "madeira", "Bi": "madeira",
    "Cang": "madeira", "Lin": "madeira",
    "Shan": "terra", "Di": "terra", "Huang": "terra", "Gu": "terra",
    "Tian": "terra", "Tai": "terra",
    "Long": "nenhum", "Feng": "nenhum", "Hu": "nenhum", "Yun": "nenhum",
    "Wu": "vazio", "Xuan": "vazio", "Kong": "vazio", "Jing": "vazio",
}


def _elemento_do_nome(prefixo: str) -> str:
    return _ELEMENTO_DE_PREFIXO.get(prefixo, "nenhum")


def nome_de_provincia(aleat: Aleatoriedade, usados: Sequence[str] = ()) -> Tuple[str, str, str]:
    """Retorna (nome romanizado, caracteres, elemento sugerido)."""
    for _ in range(200):
        p_rom, p_char = aleat.escolher(list(_PREFIXOS))
        s_rom, s_char = aleat.escolher(list(_SUFIXOS_LUGAR))
        nome = f"{p_rom}{s_rom.capitalize()}"
        if nome in usados:
            continue
        return nome, p_char + s_char, _elemento_do_nome(p_rom)
    raise RuntimeError("não foi possível gerar um nome de província único")


def nome_de_sitio(aleat: Aleatoriedade, tipo: str,
                  usados: Sequence[str] = ()) -> Tuple[str, str]:
    sufixos = _SUFIXOS_INSTITUICAO if tipo in _SUSTANTIVOS_FACCAO else _SUFIXOS_LUGAR
    for _ in range(200):
        p_rom, p_char = aleat.escolher(list(_PREFIXOS))
        s_rom, s_char = aleat.escolher(list(sufixos))
        nome = f"{p_rom}{s_rom.capitalize()}"
        if nome in usados:
            continue
        return nome, p_char + s_char
    raise RuntimeError("não foi possível gerar um nome de sítio único")


def nome_de_faccao(aleat: Aleatoriedade, tipo: str, provincia: str,
                   usados: Sequence[str] = ()) -> Tuple[str, str]:
    subst, char_subst = _SUSTANTIVOS_FACCAO.get(tipo, ("Ordem", "門"))
    for _ in range(200):
        p_rom, p_char = aleat.escolher(list(_PREFIXOS))
        s_rom, s_char = aleat.escolher(list(_SUFIXOS_INSTITUICAO))
        if aleat.moeda():
            nome = f"{subst} {p_rom}{s_rom.capitalize()} de {provincia}"
            char = p_char + s_char + char_subst
        else:
            nome = f"{subst} do {p_rom}{s_rom.capitalize()}"
            char = p_char + s_char + char_subst
        if nome in usados:
            continue
        return nome, char
    return f"{subst} Anônimo de {provincia}", char_subst


# ==========================================================================
# Estruturas
# ==========================================================================
@dataclass(frozen=True)
class TesouroLendario:
    nome: str
    chines: str
    grau: str
    tipo: str
    onde: str
    guardiao: str
    maldicao: str

    def como_dict(self) -> Dict[str, Any]:
        return {
            "nome": self.nome, "chines": self.chines, "grau": self.grau,
            "tipo": self.tipo, "onde": self.onde, "guardiao": self.guardiao,
            "maldicao": self.maldicao,
        }


@dataclass
class Sitio:
    tipo: str
    nome: str
    chines: str
    provincia: str
    q: int                        # coordenada axial de hexágono
    r: int
    nivel: int                    # nível médio dos habitantes/amenças (0–13)
    dono: str                     # nome da facção, ou "" se independente
    populacao: int
    densidade_qi: int             # 0–10
    terreno: str
    recurso: str
    segredo: str
    perigo: int                   # 1–10
    fundado_no_ano: int
    historia: str = ""
    tesouro: Optional[str] = None

    def como_dict(self) -> Dict[str, Any]:
        return {
            "tipo": self.tipo, "nome": self.nome, "chines": self.chines,
            "provincia": self.provincia, "q": self.q, "r": self.r,
            "nivel": self.nivel, "dono": self.dono, "populacao": self.populacao,
            "densidade_qi": self.densidade_qi, "densidade_qi_fato":
            DensidadeDeQi(self.densidade_qi), "terreno": self.terreno,
            "recurso": self.recurso, "segredo": self.segredo,
            "perigo": self.perigo, "fundado_no_ano": self.fundado_no_ano,
            "historia": self.historia, "tesouro": self.tesouro,
        }

    def linha(self) -> str:
        dono = f" · {self.dono}" if self.dono else " · independente"
        return (f"- **{self.nome}** ({self.chines}) — {self.tipo.replace('_',' ')}"
                f"{dono}, nível {self.nivel}, perigo {self.perigo}/10, "
                f"Qi {self.densidade_qi}/10 ({DensidadeDeQi(self.densidade_qi)})\n"
                f"  - População {self.populacao:,} · terreno {self.terreno} ·"
                f" recurso: {self.recurso}\n"
                f"  - Segredo: {self.segredo}\n"
                f"  - {self.historia}").replace(",", ".")


@dataclass
class Provincia:
    nome: str
    chines: str
    elemento: str
    densidade_qi: int
    terreno: str
    clima_base: str
    perigo: int
    veias_espirituais: int
    q: int
    r: int
    sitios: List[Sitio] = field(default_factory=list)
    historia: str = ""

    @property
    def densidade_fato(self) -> str:
        return DensidadeDeQi(self.densidade_qi)

    def como_dict(self) -> Dict[str, Any]:
        return {
            "nome": self.nome, "chines": self.chines, "elemento": self.elemento,
            "densidade_qi": self.densidade_qi,
            "densidade_qi_fato": self.densidade_fato,
            "terreno": self.terreno, "clima_base": self.clima_base,
            "perigo": self.perigo, "veias_espirituais": self.veias_espirituais,
            "q": self.q, "r": self.r, "historia": self.historia,
            "sitios": [s.como_dict() for s in self.sitios],
        }


RECOURSOS: Tuple[str, ...] = (
    "minério de ferro espiritual", "veio de prata lunar", "campo de ervas de 100 anos",
    "fonte termal de Qi", "pedreira de jade", "bosque de bambu de ferro",
    "colônia de abelhas espirituais", "leito de pérolas", "sal de rocha ardente",
    "madeira de árvore do trovão", "argila de formação", "nenhum recurso notável",
    "carvão de fogo solar", "água de poço gelado eterno", "rebanho de bestas mansas",
    "ruína de biblioteca antiga", "veio de pedra espiritual", "cemitério de espadas",
)

SEGREDOS: Tuple[str, ...] = (
    "Um Ancião morto ainda dá ordens: alguém falsifica a caligrafia dele.",
    "O poço da vila envenena devagar quem bebe por mais de um ano.",
    "Há um túnel selado que leva a um reino secreto menor.",
    "O fundador da seita era um demônio disfarçado, e o selo está enfraquecendo.",
    "Metade das pedras espirituais do cofre são falsas.",
    "Alguém daqui vende informações para uma facção inimiga.",
    "Uma criança da vila nasceu com raiz de um único elemento e ninguém sabe.",
    "O manual guardado no pavilhão é uma cópia; o original sumiu há 40 anos.",
    "Um tributo anual é pago em segredo para evitar um ataque.",
    "Há um corpo preservado no subsolo que respira uma vez por mês.",
    "A formação protetora tem uma porta deixada aberta de propósito.",
    "O mapa local está errado: uma montanha inteira foi omitida.",
    "Nada. O lugar é exatamente o que parece — e isso é o mais raro de tudo.",
    "Dois anciões são a mesma pessoa usando dois nomes.",
    "A fonte de Qi local está morrendo e será estéril em uma década.",
    "Um imortal ascendeu daqui e deixou uma pegada que não envelhece.",
    "Todo mundo aqui deve dinheiro à mesma pessoa.",
    "As bestas da região estão fugindo de algo que ainda não chegou.",
)

CLIMAS_BASE: Tuple[str, ...] = ("temperado", "arido", "umido", "frio", "quente",
                                "montanhoso", "maritimo", "continental")


@dataclass
class Faccao:
    nome: str
    chines: str
    tipo: str
    provincia: str
    alinhamento: str              # ortodoxa | nao_ortodoxa | demoniaca | neutra | imperial
    nivel_do_lider: int
    membros: int
    prestigio: int                # -100..+100
    elemento: str
    lei_principal: Optional[str]
    sede: str
    renda_anual: int
    reputacao: str
    objetivos: Tuple[str, ...] = ()

    def como_dict(self) -> Dict[str, Any]:
        return {
            "nome": self.nome, "chines": self.chines, "tipo": self.tipo,
            "provincia": self.provincia, "alinhamento": self.alinhamento,
            "nivel_do_lider": self.nivel_do_lider, "membros": self.membros,
            "prestigio": self.prestigio, "elemento": self.elemento,
            "lei_principal": self.lei_principal, "sede": self.sede,
            "renda_anual": self.renda_anual, "reputacao": self.reputacao,
            "objetivos": list(self.objetivos),
        }


@dataclass(frozen=True)
class Evento:
    ano: int
    tipo: str
    titulo: str
    descricao: str
    consequencias: Tuple[str, ...]

    def como_dict(self) -> Dict[str, Any]:
        return {"ano": self.ano, "tipo": self.tipo, "titulo": self.titulo,
                "descricao": self.descricao,
                "consequencias": list(self.consequencias)}


@dataclass
class Mundo:
    nome: str
    semente: str
    continente: str
    ano_atual: int
    data_atual: Data
    provincias: List[Provincia] = field(default_factory=list)
    faccoes: List[Faccao] = field(default_factory=list)
    relacoes: Dict[str, Dict[str, int]] = field(default_factory=dict)
    linha_do_tempo: List[Evento] = field(default_factory=list)
    tesouros: List[TesouroLendario] = field(default_factory=list)
    clima_do_ano: Dict[str, List[str]] = field(default_factory=dict)

    # ---------------- consultas ----------------
    def faccao(self, nome: str) -> Faccao:
        """Busca pelo nome. (``faccao`` = facção em ASCII.)"""
        for f in self.faccoes:
            if f.nome == nome:
                return f
        raise KeyError(f"facção {nome!r} não existe neste mundo")

    def provincia(self, nome: str) -> Provincia:
        for p in self.provincias:
            if p.nome == nome:
                return p
        raise KeyError(f"província {nome!r} não existe neste mundo")

    def sitio(self, nome: str) -> Sitio:
        for p in self.provincias:
            for s in p.sitios:
                if s.nome == nome:
                    return s
        raise KeyError(f"sítio {nome!r} não existe neste mundo")

    def relacao(self, a: str, b: str) -> int:
        """Relação inteira −100..+100 entre duas facções."""
        return self.relacoes.get(a, {}).get(b, 0)

    def relacao_como_fato(self, a: str, b: str) -> str:
        """Traduz o número no fato usado pela regra ``FACCAO:RELACAO``.

        O vocabulário é exatamente o da regra: mesma, aliada, amigavel, neutra,
        rival, guerra. Nada aqui inventa categoria que o Registro não aceite.
        """
        if a == b:
            return "mesma"
        v = self.relacao(a, b)
        if v >= 60:
            return "aliada"
        if v >= 20:
            return "amigavel"
        if v > -20:
            return "neutra"
        if v > -60:
            return "rival"
        return "guerra"

    def todos_os_sitios(self) -> List[Sitio]:
        return [s for p in self.provincias for s in p.sitios]

    def sitios_de_tipo(self, tipo: str) -> List[Sitio]:
        return [s for s in self.todos_os_sitios() if s.tipo == tipo]

    # ---------------- clima ----------------
    def gerar_clima_do_ano(self, aleat: Aleatoriedade) -> None:
        """Clima de cada província para os 360 dias do ano corrente.

        Sorteia UMA vez por dia/região e guarda: o mesmo dia nunca muda de
        clima no meio da sessão, porque isso seria interferência.
        """
        self.clima_do_ano = {}
        base = Data(self.ano_atual, 1, 1)
        for p in self.provincias:
            dias = []
            for d in range(360):
                data = _soma_dias(base, d)
                dias.append(sortear_clima(aleat, data.estacao, p.elemento,
                                          altitude=_altitude(p.terreno)))
            self.clima_do_ano[p.nome] = dias

    def clima_de(self, provincia: str, dia_do_ano: int) -> str:
        if provincia not in self.clima_do_ano:
            raise KeyError(f"clima de {provincia!r} não foi gerado")
        return self.clima_do_ano[provincia][max(0, min(359, dia_do_ano))]

    # ---------------- exportação ----------------
    def como_dict(self) -> Dict[str, Any]:
        return {
            "nome": self.nome, "semente": self.semente,
            "continente": self.continente, "ano_atual": self.ano_atual,
            "data_atual": {"ano": self.data_atual.ano, "mes": self.data_atual.mes,
                           "dia": self.data_atual.dia},
            "provincias": [p.como_dict() for p in self.provincias],
            "faccoes": [f.como_dict() for f in self.faccoes],
            "relacoes": self.relacoes,
            "linha_do_tempo": [e.como_dict() for e in self.linha_do_tempo],
            "tesouros": [t.como_dict() for t in self.tesouros],
            "clima_do_ano": self.clima_do_ano,
            "versao_do_gerador": VERSAO_DO_GERADOR,
        }

    def exportar_json(self, caminho: str) -> str:
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(self.como_dict(), fh, ensure_ascii=False, indent=2,
                      sort_keys=True)
        return caminho

    def markdown(self) -> str:
        L: List[str] = [
            f"# {self.nome} 世界",
            "",
            f"**Semente:** `{self.semente}`  ",
            f"**Gerador:** {VERSAO_DO_GERADOR} — esta semente sempre produz "
            "exatamente este mundo.",
            f"**Continente:** {self.continente}  ",
            f"**Ano corrente:** {self.ano_atual} ({self.data_atual.texto()})",
            "",
            "## As Nove Províncias",
            "",
            "| Província | 字 | Elemento | Terreno | Qi | Densidade | Perigo | Veias |",
            "|---|---|---|---|---:|---|---:|---:|",
        ]
        for p in self.provincias:
            L.append(f"| {p.nome} | {p.chines} | {p.elemento} | {p.terreno} | "
                     f"{p.densidade_qi} | {p.densidade_fato} | {p.perigo}/10 | "
                     f"{p.veias_espirituais} |")
        L += ["", "## Facções", ""]
        L += ["| Facção | 字 | Tipo | Alinhamento | Província | Líder | Membros | Prestígio |",
              "|---|---|---|---|---|---:|---:|---:|"]
        for f in sorted(self.faccoes, key=lambda x: -x.prestigio):
            L.append(f"| {f.nome} | {f.chines} | {f.tipo.replace('_',' ')} | "
                     f"{f.alinhamento} | {f.provincia} | nível {f.nivel_do_lider} | "
                     f"{f.membros:,} | {f.prestigio:+d} |".replace(",", "."))
        L += ["", "### Matriz de relações (−100 guerra … +100 aliança)", ""]
        nomes = sorted({f.nome for f in self.faccoes})
        if nomes:
            L.append("| | " + " | ".join(_curto(n) for n in nomes) + " |")
            L.append("|" + "---|" * (len(nomes) + 1))
            for a in nomes:
                celulas = []
                for b in nomes:
                    if a == b:
                        celulas.append("—")
                    else:
                        v = self.relacao(a, b)
                        celulas.append(f"{v:+d}")
                L.append(f"| **{_curto(a)}** | " + " | ".join(celulas) + " |")
        L += ["", "## Sítios por província", ""]
        for p in self.provincias:
            L += [f"### {p.nome} ({p.chines}) — {p.elemento}, {p.terreno}", "",
                  p.historia, ""]
            for s in sorted(p.sitios, key=lambda x: -x.nivel):
                L.append(s.linha())
            L.append("")
        L += ["## Linha do tempo", ""]
        for e in sorted(self.linha_do_tempo, key=lambda x: x.ano):
            L.append(f"### Ano {e.ano} — {e.titulo}")
            L.append("")
            L.append(e.descricao)
            if e.consequencias:
                L.append("")
                L += [f"- {c}" for c in e.consequencias]
            L.append("")
        if self.tesouros:
            L += ["## Tesouros lendários", ""]
            for t in self.tesouros:
                L += [f"### {t.nome} ({t.chines})", "",
                      f"- Grau **{t.grau}** · tipo {t.tipo}",
                      f"- Onde: {t.onde}",
                      f"- Guardião: {t.guardiao}",
                      f"- Maldição: {t.maldicao}", ""]
        return "\n".join(L)


VERSAO_DO_GERADOR = "1.0.0"


def _curto(nome: str) -> str:
    partes = nome.split()
    return " ".join(partes[:3]) if len(partes) > 3 else nome


def _soma_dias(data: Data, dias: int) -> Data:
    from .calendario import avancar_dias
    return avancar_dias(data, dias)


def _altitude(terreno: str) -> int:
    return {"montanhas": 3, "planalto": 2, "vales": 1, "vulcanico": 2,
            "tundra": 1}.get(terreno, 0)


# ==========================================================================
# Gramática de eventos — o passado causa o presente
# ==========================================================================
_TIPOS_DE_EVENTO: Tuple[Tuple[str, int], ...] = (
    ("fundacao_de_seita", 14),
    ("guerra_entre_faccoes", 12),
    ("queda_de_seita", 7),
    ("tribulacao_de_imortal", 5),
    ("praga_demoniaca", 6),
    ("manual_supremo_perdido", 6),
    ("queda_de_dinastia", 4),
    ("grande_torneio", 9),
    ("cometa_e_pressagio", 8),
    ("descoberta_de_veia", 7),
    ("invasao_do_templo_daemonia", 5),
    ("alianca_do_murim", 6),
    ("seca_ou_inundacao", 8),
    ("nascimento_de_um_genio", 6),
    ("besta_ancestral_desperta", 5),
    ("reino_secreto_aparece", 6),
)


@dataclass
class MundoEmConstrucao:
    """Estado mutável durante a geração; só existe dentro de ``gerar_mundo``."""

    aleat: Aleatoriedade
    usados_provincia: List[str] = field(default_factory=list)
    usados_sitio: List[str] = field(default_factory=list)
    usados_faccao: List[str] = field(default_factory=list)
    eventos: List[Evento] = field(default_factory=list)
    consequencias_pendentes: List[Tuple[str, Any]] = field(default_factory=list)
    # efeito histórico acumulado por PAR DE ALINHAMENTOS, aplicado uma única vez
    delta_global: Dict[Tuple[str, str], int] = field(default_factory=dict)
    genio_registrado: bool = False


def _sortear_evento(mc: MundoEmConstrucao, ano: int, mundo: Mundo) -> Evento:
    tipos = [t for t, _ in _TIPOS_DE_EVENTO]
    pesos = [w for _, w in _TIPOS_DE_EVENTO]
    tipo = mc.aleat.escolher_ponderado(tipos, pesos)
    provincias = [p.nome for p in mundo.provincias]
    prov = mc.aleat.escolher(provincias) if provincias else "desconhecida"
    faccoes = [f.nome for f in mundo.faccoes]
    consequencias: List[str] = []
    pendencias: List[Tuple[str, Any]] = []

    def duas_faccoes() -> Tuple[str, str]:
        if len(faccoes) < 2:
            return ("", "")
        a, b = mc.aleat.amostrar(faccoes, 2)
        return a, b

    if tipo == "fundacao_de_seita":
        nome, char = nome_de_faccao(mc.aleat, "seita_ortodoxa", prov, mc.usados_faccao)
        mc.usados_faccao.append(nome)
        titulo = f"Fundação da {nome}"
        desc = (f"Um cultivador errante reúne discípulos em {prov} e funda a "
                f"{nome}. O primeiro salão é erguido com madeira local e teimosia.")
        consequencias.append(f"facção {nome} registrada em {prov}")
        pendencias.append(("criar_faccao", (nome, char, "seita_ortodoxa", prov, ano)))
    elif tipo == "guerra_entre_faccoes":
        a, b = duas_faccoes()
        if not a:
            return Evento(ano, tipo, "Guerra esquecida",
                          "Houve uma guerra. Ninguém registrou quem lutou.", ()), []
        vencedor = a if mc.aleat.moeda() else b
        perdedor = b if vencedor == a else a
        titulo = f"Guerra entre {a} e {b}"
        desc = (f"Três anos de escaramuças, dois de guerra aberta. {vencedor} "
                f"venceu tomando o passo de montanha e queimando os celeiros.")
        consequencias += [
            f"ódio permanente entre {a} e {b} (relação −60)",
            f"campo de batalha abandonado em {prov}",
        ]
        pendencias += [("relacao", (a, b, -60)),
                       ("criar_sitio", ("campo_de_batalha", prov, ano, 4))]
    elif tipo == "queda_de_seita":
        if not faccoes:
            return Evento(ano, tipo, "Uma seita que ninguém nomeia caiu",
                          "Restaram só as pedras.", ()), []
        vitima = mc.aleat.escolher(faccoes)
        titulo = f"Extermínio da {vitima}"
        desc = (f"A {vitima} foi apagada em uma única noite. Os registros dizem "
                "que o portão estava aberto por dentro.")
        consequencias += [f"ruína da sede da {vitima} em {prov}",
                          "um manual supremo perdido nos escombros",
                          f"membros sobreviventes caçados por décadas"]
        pendencias += [("criar_sitio", ("ruina", prov, ano, 7)),
                       ("criar_tesouro", (prov, ano))]
    elif tipo == "tribulacao_de_imortal":
        titulo = f"Tribulação Celestial sobre {prov}"
        desc = (f"Nove raios caíram durante três dias. Quem estava a menos de "
                "trinta léguas ficou surdo para sempre.")
        sobreviv = mc.aleat.escolher(["sobreviveu e ascendeu",
                                      "falhou e o corpo virou uma estátua de vidro",
                                      "falhou e o vale inteiro virou deserto"])
        consequencias.append(sobreviv)
        pendencias.append(("criar_sitio", ("pico_de_cultivo", prov, ano, 10)))
        if "deserto" in sobreviv:
            pendencias.append(("criar_sitio", ("floresta_proibida", prov, ano, 9)))
    elif tipo == "praga_demoniaca":
        titulo = f"Praga demoníaca em {prov}"
        desc = ("Algo saiu de baixo da terra e comeu quatro vilas antes de "
                "alguém entender o que era.")
        consequencias += ["culto demoníaco estabelecido na região",
                          "bestas espirituais corrompidas à solta"]
        pendencias += [("criar_faccao_demoniaca", (prov, ano)),
                       ("criar_sitio", ("caverna_de_bestas", prov, ano, 6))]
    elif tipo == "manual_supremo_perdido":
        titulo = "Um manual supremo desaparece"
        desc = ("A última cópia de uma Lei Taiyi saiu de um pavilhão e nunca "
                "chegou ao destinatário.")
        consequencias += ["quem o encontrar aprende uma Lei suprema",
                          "todas as grandes facções passam a procurar"]
        pendencias.append(("criar_tesouro", (prov, ano)))
    elif tipo == "queda_de_dinastia":
        titulo = "Queda da dinastia reinante"
        desc = ("O Império perdeu o mandato. O Murim deixou de pagar impostos "
                "e ninguém veio cobrar.")
        consequencias += ["autoridade imperial reduzida a zero nas províncias",
                          "as seitas passam a legislar"]
        pendencias.append(("relacao_global", ("imperial", -20)))
    elif tipo == "grande_torneio":
        titulo = f"Grande Torneio de Kunlun em {prov}"
        desc = ("As nove grandes seitas enviaram discípulos. Três morreram em "
                "duelos 'acidentais'.")
        consequencias += ["prestígio redistribuído entre as facções",
                          "rivalidades jovens que vão durar décadas"]
        pendencias.append(("prestigio_aleatorio", (prov,)))
    elif tipo == "cometa_e_pressagio":
        titulo = "Um cometa varre o céu"
        desc = ("Passou por três noites. Todo astrólogo do continente deu uma "
                "interpretação diferente e todos foram acreditados.")
        consequencias += ["densidade de Qi alterada por uma década",
                          "nascimentos com raízes mutantes em alta"]
        pendencias.append(("densidade_temporaria", (prov, 2)))
    elif tipo == "descoberta_de_veia":
        titulo = f"Veia espiritual descoberta em {prov}"
        desc = ("Um pastor caiu num buraco e achou um rio de luz sob a terra.")
        consequencias += ["corrida de facções pelo controle da veia",
                          "densidade de Qi da província aumentada"]
        pendencias += [("criar_sitio", ("veia_espiritual", prov, ano, 5)),
                       ("densidade_permanente", (prov, 2))]
    elif tipo == "invasao_do_templo_daemonia":
        titulo = "Invasão do Templo Daemonia"
        desc = ("As portas do templo se abriram sozinhas. O que saiu marchou em "
                "formação.")
        consequencias += ["duas facções ortodoxas destruídas",
                          "aliança temporária do Murim"]
        pendencias += [("criar_sitio", ("floresta_proibida", prov, ano, 11)),
                       ("relacao_global", ("demoniaca", -20))]
    elif tipo == "alianca_do_murim":
        titulo = "Aliança do Murim"
        desc = ("Sete seitas assinaram o Pacto dos Rios e Lagos. Durou até a "
                "primeira partilha de espólio.")
        consequencias.append("relações temporariamente melhores entre ortodoxos")
        pendencias.append(("relacao_global", ("ortodoxa", 15)))
    elif tipo == "seca_ou_inundacao":
        qual = mc.aleat.escolher(["seca", "inundacao"])
        titulo = f"{qual.capitalize()} de três anos em {prov}"
        desc = (f"A {qual} matou mais gente que qualquer guerra do período. "
                "As seitas abriram os celeiros — algumas.")
        consequencias += [f"população de {prov} reduzida",
                          "ressentimento duradouro contra quem fechou os celeiros"]
        pendencias.append(("populacao_reduzida", (prov,)))
    elif tipo == "nascimento_de_um_genio":
        titulo = f"Nasce um gênio em {prov}"
        desc = ("Raiz espiritual de elemento único, pura como vidro. Três seitas "
                "chegaram antes do sétimo dia.")
        consequencias += ["disputa pela tutela do gênio",
                          "um NPC notável entra no mundo"]
        pendencias.append(("criar_npc_genio", (prov, ano)))
    elif tipo == "besta_ancestral_desperta":
        titulo = f"Uma besta ancestral desperta em {prov}"
        desc = ("A montanha se moveu. Depois voltou ao lugar, mas não do mesmo jeito.")
        consequencias += ["zona interditada", "bestas menores fogem da região"]
        pendencias.append(("criar_sitio", ("floresta_proibida", prov, ano, 12)))
    else:  # reino_secreto_aparece
        titulo = f"Um reino secreto aparece sobre {prov}"
        desc = ("Por nove dias houve uma cidade no céu. No décimo, sumiu, e "
                "quatrocentas pessoas que entraram nunca voltaram.")
        consequencias += ["reino secreto catalogado e perdido",
                          "abre uma vez por geração"]
        pendencias.append(("criar_sitio", ("reino_secreto", prov, ano, 9)))

    return Evento(ano, tipo, titulo, desc, tuple(consequencias)), pendencias


def gerar_mundo(
    semente: str,
    *,
    nome: Optional[str] = None,
    provincias: int = 9,
    sitios_por_provincia: Tuple[int, int] = (4, 9),
    faccoes_alvo: int = 14,
    anos_de_historia: int = 900,
    eventos: int = 40,
    gerar_clima: bool = True,
) -> Mundo:
    """Gera um mundo completo e determinístico para a semente informada."""
    if not isinstance(provincias, int) or not (3 <= provincias <= 20):
        raise ValueError("o mundo tem de 3 a 20 províncias")
    if not (1 <= eventos <= 400):
        raise ValueError("número de eventos fora de 1..400")
    if anos_de_historia < eventos:
        raise ValueError("história mais curta que o número de eventos")

    aleat = Aleatoriedade(FonteSemeada(semente, "mundo"))
    ano_atual = aleat.entre(1200, 3400)
    if nome is None:
        nome, _, _ = nome_de_provincia(aleat)
        nome = f"Continente de {nome}"
    continente = nome

    mundo = Mundo(
        nome=nome, semente=semente, continente=continente, ano_atual=ano_atual,
        data_atual=Data(ano_atual, aleat.entre(1, 12), aleat.entre(1, 30)),
    )
    mc = MundoEmConstrucao(aleat)

    # --- províncias em grade hexagonal (anel central + anel externo) ---------
    coordenadas = _anel_hexagonal(provincias)
    for (q, r) in coordenadas:
        p_nome, p_char, p_elem = nome_de_provincia(aleat, mc.usados_provincia)
        mc.usados_provincia.append(p_nome)
        if p_elem == "vazio":
            p_elem = aleat.escolher(list(ELEMENTOS_CANONICOS))
        terreno = aleat.escolher(list(TERRENOS))
        # províncias montanhosas/vulcânicas tendem a ter mais Qi (lógica, não acaso cego)
        bonus_terreno = {"montanhas": 2, "vulcanico": 2, "planalto": 1,
                         "litoral": 1, "deserto": -2, "tundra": -1}.get(terreno, 0)
        densidade = max(0, min(10, aleat.entre(2, 7) + bonus_terreno))
        mundo.provincias.append(Provincia(
            nome=p_nome, chines=p_char, elemento=p_elem,
            densidade_qi=densidade, terreno=terreno,
            clima_base=aleat.escolher(list(CLIMAS_BASE)),
            perigo=max(1, min(10, aleat.entre(1, 6) + (10 - densidade) // 4)),
            veias_espirituais=max(0, densidade // 3),
            q=q, r=r,
            historia=(f"Elemento dominante {p_elem}; terreno {terreno}; "
                      f"Qi {densidade}/10 ({DensidadeDeQi(densidade)})."),
        ))

    # --- sítios iniciais: cada província recebe uma mistura ------------------
    for p in mundo.provincias:
        n = aleat.entre(*sitios_por_provincia)
        tipos = _mix_de_tipos(aleat, p)
        for tipo in tipos[:n]:
            _criar_sitio(mc, mundo, tipo, p.nome, ano_atual - aleat.entre(5, 400),
                         nivel=None)

    # --- facções a partir dos sítios de facção ------------------------------
    for p in mundo.provincias:
        for s in list(p.sitios):
            if len(mundo.faccoes) >= faccoes_alvo + 6:
                break
            if s.tipo not in _SUSTANTIVOS_FACCAO:
                continue
            alinh = {"seita_ortodoxa": "ortodoxa",
                     "seita_nao_ortodoxa": "nao_ortodoxa",
                     "culto_demoniaco": "demoniaca",
                     "cla_nobre": "neutra",
                     "mosteiro": "ortodoxa",
                     "templo": "neutra",
                     "mercado_negro": "nao_ortodoxa",
                     "fortaleza": "neutra"}[s.tipo]
            nome_f, char_f = nome_de_faccao(aleat, s.tipo, p.nome, mc.usados_faccao)
            mc.usados_faccao.append(nome_f)
            lei = _lei_para(aleat, alinh)
            mundo.faccoes.append(Faccao(
                nome=nome_f, chines=char_f, tipo=s.tipo, provincia=p.nome,
                alinhamento=alinh, nivel_do_lider=s.nivel,
                membros=max(20, s.populacao // max(1, aleat.entre(2, 12))),
                prestigio=aleat.entre(-20, 60) + s.nivel * 3,
                elemento=p.elemento, lei_principal=lei, sede=s.nome,
                renda_anual=aleat.entre(200, 4000) * (s.nivel + 1) ** 2,
                reputacao=aleat.escolher(_REPUTACOES),
                objetivos=tuple(aleat.amostrar(list(_OBJETIVOS_FACCAO),
                                               aleat.entre(1, 3))),
            ))
            s.dono = nome_f
            s.historia = (s.historia + f" Sede da {nome_f}.").strip()

    # Império, se houver cidades
    if mundo.sitios_de_tipo("cidade") and len(mundo.faccoes) < faccoes_alvo + 2:
        dinastia_rom, dinastia_char = aleat.escolher(list(_PREFIXOS))
        nome_f = f"Império {dinastia_rom}"
        char_f = dinastia_char + "朝"
        while nome_f in mc.usados_faccao:
            dinastia_rom, dinastia_char = aleat.escolher(list(_PREFIXOS))
            nome_f = f"Império {dinastia_rom}"
            char_f = dinastia_char + "朝"
        mc.usados_faccao.append(nome_f)
        mundo.faccoes.append(Faccao(
            nome=nome_f, chines=char_f, tipo="imperio",
            provincia=mundo.provincias[0].nome, alinhamento="imperial",
            nivel_do_lider=aleat.entre(3, 9), membros=aleat.entre(100000, 9000000),
            prestigio=aleat.entre(10, 80), elemento="terra", lei_principal=None,
            sede="Capital", renda_anual=aleat.entre(10 ** 6, 10 ** 8),
            reputacao="burocrática e distante",
            objetivos=("cobrar impostos do Murim", "manter as seitas divididas"),
        ))

    # --- matriz de relações --------------------------------------------------
    _gerar_relacoes(mc, mundo)

    # --- linha do tempo (o passado causa o presente) -------------------------
    faixa = list(range(ano_atual - anos_de_historia, ano_atual - 4))
    if eventos > len(faixa):
        raise ValueError("eventos demais para o período histórico pedido")
    anos = sorted(aleat.amostrar(faixa, eventos))
    for ano in anos:
        evento, pendencias = _sortear_evento(mc, ano, mundo)
        mundo.linha_do_tempo.append(evento)
        mc.consequencias_pendentes.extend(pendencias)

    _aplicar_consequencias(mc, mundo, ano_atual)

    # --- tesouros lendários extras -------------------------------------------
    for _ in range(aleat.entre(2, 5)):
        _criar_tesouro(mc, mundo, aleat.escolher([p.nome for p in mundo.provincias]),
                       ano_atual - aleat.entre(50, 800))

    # --- clima do ano corrente ------------------------------------------------
    if gerar_clima:
        mundo.gerar_clima_do_ano(Aleatoriedade(FonteSemeada(semente, "clima")))

    return mundo


# --------------------------------------------------------------------------
# Auxiliares de geração
# --------------------------------------------------------------------------
_REPUTACOES: Tuple[str, ...] = (
    "honrada e rígida", "temida e silenciosa", "rica e corrupta",
    "pobre e orgulhosa", "antiga e decadente", "nova e ambiciosa",
    "traidora por reputação injusta", "protetora dos camponeses",
    "obcecada por pureza de linhagem", "aberta a estrangeiros",
)
_OBJETIVOS_FACCAO: Tuple[str, ...] = (
    "recuperar um manual roubado",
    "dominar a veia espiritual da província vizinha",
    "vencer o próximo Torneio de Kunlun",
    "extinguir uma facção rival",
    "formar um Núcleo Dourado de grau 1 para o seu Ancião",
    "abrir o reino secreto antes dos outros",
    "conseguir um discípulo com raiz de elemento único",
    "pagar uma dívida de sangue antiga",
    "tornar-se a seita número um do Murim",
    "esconder que o Mestre está morto há três anos",
    "comprar o apoio do Império",
    "destruir o culto demoníaco da região",
)


def _anel_hexagonal(n: int) -> List[Tuple[int, int]]:
    """Coordenadas axiais: centro + anéis concêntricos, em ordem determinística."""
    coords = [(0, 0)]
    anel = 1
    while len(coords) < n:
        for q in range(-anel, anel + 1):
            for r in range(-anel, anel + 1):
                if max(abs(q), abs(r), abs(-q - r)) == anel:
                    coords.append((q, r))
        coords = coords[:1] + sorted(coords[1:])
        anel += 1
    return coords[:n]


def _mix_de_tipos(aleat: Aleatoriedade, p: Provincia) -> List[str]:
    """Cada província recebe uma mistura coerente com terreno, Qi e perigo."""
    tipos: List[str] = []
    n_civilizacao = 1 + p.densidade_qi // 4 + (2 if p.terreno in ("planicies", "vales", "litoral") else 0)
    for _ in range(max(1, min(4, n_civilizacao))):
        tipos.append(aleat.escolher_ponderado(
            ["cidade", "vila", "vila", "porto", "mercado_negro", "passo_de_montanha"],
            [3, 8, 6, 2, 1, 2]))
    # facções: quanto mais Qi, mais seitas
    n_seitas = p.densidade_qi // 3
    for _ in range(n_seitas):
        pesos = [8, 4, 1, 3, 2]
        if p.perigo >= 7:
            pesos = [5, 5, 4, 3, 2]
        tipos.append(aleat.escolher_ponderado(
            ["seita_ortodoxa", "seita_nao_ortodoxa", "culto_demoniaco",
             "cla_nobre", "mosteiro"], pesos))
    # sítios naturais
    for _ in range(aleat.entre(1, 3)):
        tipos.append(aleat.escolher_ponderado(
            ["pico_de_cultivo", "lago_espiritual", "floresta_proibida",
             "caverna_de_bestas", "veia_espiritual", "ruina", "tumba_antiga",
             "reino_secreto", "templo", "campo_de_batalha", "fortaleza",
             "torre_de_observacao"],
            [6, 5, 4, 5, 3, 4, 3, 1, 3, 2, 2, 2]))
    if p.veias_espirituais >= 2 and aleat.moeda():
        tipos.append("veia_espiritual")
    return tipos


def _criar_sitio(mc: MundoEmConstrucao, mundo: Mundo, tipo: str, provincia: str,
                 ano: int, nivel: Optional[int]) -> Optional[Sitio]:
    try:
        prov = mundo.provincia(provincia)
    except KeyError:
        return None
    nome, char = nome_de_sitio(mc.aleat, tipo, mc.usados_sitio)
    mc.usados_sitio.append(nome)
    if nivel is None:
        nivel = max(0, min(13, mc.aleat.entre(0, 4) + prov.densidade_qi // 2
                           + (3 if tipo in ("reino_secreto", "floresta_proibida",
                                            "culto_demoniaco") else 0)))
    # nível de habitantes coerente com o tipo
    if tipo in ("vila", "porto", "passo_de_montanha"):
        nivel = min(nivel, 3)
    if tipo in ("cidade", "mercado_negro"):
        nivel = min(nivel, 6)
    if tipo in ("seita_ortodoxa", "seita_nao_ortodoxa", "cla_nobre", "mosteiro"):
        nivel = max(nivel, 5)
    if tipo in ("reino_secreto", "floresta_proibida", "tumba_antiga"):
        nivel = max(nivel, 7)
    populacao = {
        "cidade": mc.aleat.entre(20000, 900000),
        "vila": mc.aleat.entre(200, 4000),
        "porto": mc.aleat.entre(3000, 90000),
        "mercado_negro": mc.aleat.entre(50, 900),
        "seita_ortodoxa": mc.aleat.entre(300, 9000),
        "seita_nao_ortodoxa": mc.aleat.entre(150, 5000),
        "culto_demoniaco": mc.aleat.entre(80, 3000),
        "cla_nobre": mc.aleat.entre(200, 3000),
        "mosteiro": mc.aleat.entre(60, 900),
        "templo": mc.aleat.entre(20, 500),
    }.get(tipo, mc.aleat.entre(0, 40))

    densidade = max(0, min(10, prov.densidade_qi + mc.aleat.entre(-2, 2)))
    if tipo in ("veia_espiritual", "pico_de_cultivo", "lago_espiritual"):
        densidade = min(10, densidade + 3)
    if tipo in ("ruina", "campo_de_batalha", "deserto"):
        densidade = max(0, densidade - 3)
    if tipo == "reino_secreto":
        densidade = 10

    perigo = max(1, min(10, prov.perigo + nivel // 2 + mc.aleat.entre(-1, 2)))
    if tipo in ("vila", "cidade", "porto"):
        perigo = max(1, perigo - 3)

    s = Sitio(
        tipo=tipo, nome=nome, chines=char, provincia=provincia,
        q=prov.q, r=prov.r, nivel=nivel, dono="", populacao=populacao,
        densidade_qi=densidade, terreno=prov.terreno,
        recurso=mc.aleat.escolher(list(RECOURSOS)),
        segredo=mc.aleat.escolher(list(SEGREDOS)),
        perigo=perigo, fundado_no_ano=ano,
        historia=_historia_de_sitio(mc.aleat, tipo, nome, ano, nivel),
    )
    prov.sitios.append(s)
    return s


def _historia_de_sitio(aleat: Aleatoriedade, tipo: str, nome: str, ano: int,
                       nivel: int) -> str:
    idades = max(1, 3400 - ano)
    if tipo == "ruina":
        return (f"Fundado há {idades} anos; destruído por "
                f"{aleat.escolher(['uma guerra entre seitas', 'uma tribulação mal contida', 'uma praga demoníaca', 'uma traição interna', 'motivo desconhecido'])}.")
    if tipo == "reino_secreto":
        return ("Abre uma vez por geração. Quem entra não escolhe quando sai.")
    if tipo in ("seita_ortodoxa", "seita_nao_ortodoxa", "mosteiro"):
        return f"Fundada há {idades} anos; nível mais alto já alcançado: {nivel}."
    if tipo == "campo_de_batalha":
        return "A terra ainda não aceita Qi: nada cresce aqui desde a batalha."
    if tipo == "culto_demoniaco":
        return "Nasceu de uma dissidência e de um manual que ninguém devia ler."
    if tipo == "cidade":
        return f"Cresceu em volta de {aleat.escolher(['um porto', 'um templo', 'uma mina', 'um cruzamento de estradas', 'uma guarnição'])} há {idades} anos."
    if tipo == "tumba_antiga":
        return "Alguém importante foi enterrado aqui com tudo o que tinha."
    if tipo == "veia_espiritual":
        return "Um rio de Qi corre sob a terra; quem o controla controla a região."
    return f"Ativo há {idades} anos."


def _lei_para(aleat: Aleatoriedade, alinhamento: str) -> Optional[str]:
    from .reinos import LEIS
    if alinhamento == "demoniaca":
        pool = [c for c, l in LEIS.items() if l.familia == "demoniaca"]
    elif alinhamento == "ortodoxa":
        pool = [c for c, l in LEIS.items()
                if l.caminho == "xiandao" and l.familia != "demoniaca"]
    elif alinhamento == "nao_ortodoxa":
        pool = [c for c, l in LEIS.items() if l.caminho in ("xiandao", "marcial")]
    else:
        pool = [c for c, l in LEIS.items() if l.caminho != "shendao"]
    if not pool:
        return None
    return aleat.escolher(sorted(pool))


def _gerar_relacoes(mc: MundoEmConstrucao, mundo: Mundo,
                    apenas_faltantes: bool = False) -> None:
    """Matriz de relações simétrica, derivada de alinhamento e distância.

    Com ``apenas_faltantes`` só preenche os pares ainda ausentes — usado depois
    que a linha do tempo cria facções novas.
    """
    nomes = [f.nome for f in mundo.faccoes]
    for a in nomes:
        mundo.relacoes.setdefault(a, {})
    for i, a in enumerate(nomes):
        fa = mundo.faccoes[i]
        for j, b in enumerate(nomes):
            if i == j:
                mundo.relacoes[a][b] = 100
                continue
            if apenas_faltantes and b in mundo.relacoes[a]:
                continue
            fb = mundo.faccoes[j]
            base = _base_de_alinhamento(fa.alinhamento, fb.alinhamento)
            mesma = 8 if fa.provincia == fb.provincia else 0
            elemento = 6 if fa.elemento == fb.elemento else (
                -8 if ELEMENTOS_SUPERADORES.get(fa.elemento) == fb.elemento else 0)
            ruido = mc.aleat.entre(-30, 30)
            v = max(-100, min(100, base + mesma + elemento + ruido))
            # simetria: grava o mesmo valor nos dois sentidos
            mundo.relacoes[a][b] = v
            mundo.relacoes[b][a] = v


def _base_de_alinhamento(a: str, b: str) -> int:
    par = tuple(sorted((a, b)))
    tabela = {
        ("ortodoxa", "ortodoxa"): 10,
        ("demoniaca", "ortodoxa"): -70,
        ("demoniaca", "demoniaca"): -20,
        ("demoniaca", "nao_ortodoxa"): -10,
        ("nao_ortodoxa", "ortodoxa"): -25,
        ("nao_ortodoxa", "nao_ortodoxa"): 0,
        ("imperial", "ortodoxa"): -10,
        ("imperial", "demoniaca"): -60,
        ("imperial", "imperial"): 40,
        ("imperial", "nao_ortodoxa"): -30,
        ("neutra", "neutra"): 10,
    }
    v = tabela.get(par)
    if v is not None:
        return v
    if "neutra" in par:
        return 5
    return 0


def _criar_tesouro(mc: MundoEmConstrucao, mundo: Mundo, provincia: str,
                   ano: int) -> TesouroLendario:
    from .artes import ARTEFATOS
    nome_p, char_p, _ = nome_de_provincia(mc.aleat, [])
    artefato = mc.aleat.escolher(list(ARTEFATOS))
    nome = f"{artefato.nome} de {nome_p}"
    guardioes = [
        "uma besta espiritual de nível 9 que nunca dorme",
        "a formação de selamento que ainda funciona",
        "o fantasma do último dono",
        "uma seita que nem sabe o que guarda",
        "ninguém — e é isso que assusta",
        "sete armadilhas e um enigma em língua antiga",
        "um clã inteiro que morreu defendendo-o",
    ]
    maldicoes = [
        "quem o tocar envelhece um ano por dia até devolvê-lo",
        "só aceita portadores com raiz de elemento único",
        "sussurra o nome de quem o portou antes — todos mortos",
        "exige um sacrifício de sangue a cada uso",
        "atrai tribulações antecipadas",
        "não pode ser retirado da província onde foi encontrado",
        "nenhuma conhecida; o que já é suspeito",
    ]
    t = TesouroLendario(
        nome=nome, chines=artefato.chines + char_p,
        grau=artefato.grau, tipo=artefato.tipo,
        onde=f"em algum lugar de {provincia}, perdido desde o ano {ano}",
        guardiao=mc.aleat.escolher(guardioes),
        maldicao=mc.aleat.escolher(maldicoes),
    )
    mundo.tesouros.append(t)
    return t


def _aplicar_consequencias(mc: MundoEmConstrucao, mundo: Mundo,
                           ano_atual: int) -> None:
    """Materializa as pendências deixadas pelos eventos históricos."""
    for codigo, args in mc.consequencias_pendentes:
        if codigo == "criar_faccao":
            nome, char, tipo, prov, ano = args
            try:
                p = mundo.provincia(prov)
            except KeyError:
                continue
            sede = _criar_sitio(mc, mundo, "seita_ortodoxa", prov, ano,
                                nivel=mc.aleat.entre(4, 8))
            mundo.faccoes.append(Faccao(
                nome=nome, chines=char, tipo="seita_ortodoxa", provincia=prov,
                alinhamento="ortodoxa",
                nivel_do_lider=sede.nivel if sede else 5,
                membros=mc.aleat.entre(100, 3000),
                prestigio=mc.aleat.entre(-10, 50), elemento=p.elemento,
                lei_principal=_lei_para(mc.aleat, "ortodoxa"),
                sede=sede.nome if sede else prov,
                renda_anual=mc.aleat.entre(1000, 40000),
                reputacao=mc.aleat.escolher(_REPUTACOES),
                objetivos=tuple(mc.aleat.amostrar(list(_OBJETIVOS_FACCAO), 2)),
            ))
            if sede:
                sede.dono = nome
        elif codigo == "criar_faccao_demoniaca":
            prov, ano = args
            nome, char = nome_de_faccao(mc.aleat, "culto_demoniaco", prov,
                                        mc.usados_faccao)
            mc.usados_faccao.append(nome)
            sede = _criar_sitio(mc, mundo, "culto_demoniaco", prov, ano,
                                nivel=mc.aleat.entre(5, 10))
            mundo.faccoes.append(Faccao(
                nome=nome, chines=char, tipo="culto_demoniaco", provincia=prov,
                alinhamento="demoniaca",
                nivel_do_lider=sede.nivel if sede else 7,
                membros=mc.aleat.entre(60, 2000),
                prestigio=mc.aleat.entre(-60, 10),
                elemento=mundo.provincia(prov).elemento,
                lei_principal=_lei_para(mc.aleat, "demoniaca"),
                sede=sede.nome if sede else prov,
                renda_anual=mc.aleat.entre(500, 30000),
                reputacao="temida e silenciosa",
                objetivos=("reunir sangue suficiente para o próximo ritual",),
            ))
            if sede:
                sede.dono = nome
        elif codigo == "criar_sitio":
            tipo, prov, ano, nivel = args
            _criar_sitio(mc, mundo, tipo, prov, ano, nivel=nivel)
        elif codigo == "criar_tesouro":
            prov, ano = args
            _criar_tesouro(mc, mundo, prov, ano)
        elif codigo == "relacao":
            a, b, v = args
            mundo.relacoes.setdefault(a, {})[b] = v
            mundo.relacoes.setdefault(b, {})[a] = v
        elif codigo == "relacao_global":
            alinh, delta = args
            # Acumula por par de alinhamentos. O teto de ±30 garante que a
            # história inteira não consiga apagar um ódio concreto entre duas
            # facções específicas.
            for f in mundo.faccoes:
                if f.alinhamento != alinh:
                    continue
                for g in mundo.faccoes:
                    if g.alinhamento == alinh and g is not f:
                        continue
                    chave = tuple(sorted((alinh, g.alinhamento)))
                    atual = mc.delta_global.get(chave, 0)
                    mc.delta_global[chave] = max(-20, min(20, atual + delta))
        elif codigo == "densidade_permanente" or codigo == "densidade_temporaria":
            prov, delta = args
            p = mundo.provincia(prov)
            p.densidade_qi = max(0, min(10, p.densidade_qi + delta))
        elif codigo == "prestigio_aleatorio":
            for f in mundo.faccoes:
                f.prestigio = max(-100, min(100, f.prestigio + mc.aleat.entre(-8, 12)))
        elif codigo == "populacao_reduzida":
            prov = args[0]
            for s in mundo.provincia(prov).sitios:
                s.populacao = max(0, s.populacao * 6 // 10)
        elif codigo == "criar_npc_genio":
            prov, ano = args
            if not mc.genio_registrado:
                mc.genio_registrado = True
                mundo.linha_do_tempo.append(Evento(
                    ano_atual - 16, "registro_de_genio",
                    f"O gênio de {prov} agora é adulto",
                    "Aquele bebê de raiz pura cresceu, e o continente inteiro "
                    "está olhando para ele. Três seitas já tentaram raptá-lo.",
                    ("NPC notável incluído na lista do mundo",
                     f"{prov} passou a receber mais visitantes")))
        else:
            raise ValueError(f"consequência desconhecida {codigo!r}")

    # facções criadas pela linha do tempo ainda não têm relações: completa
    _gerar_relacoes(mc, mundo, apenas_faltantes=True)

    # aplica uma única vez o efeito histórico acumulado por alinhamento
    for i, f in enumerate(mundo.faccoes):
        for j, g in enumerate(mundo.faccoes):
            if i == j:
                continue
            delta = mc.delta_global.get(tuple(sorted((f.alinhamento,
                                                      g.alinhamento))), 0)
            if delta:
                mundo.relacoes.setdefault(f.nome, {}).setdefault(g.nome, 0)
                mundo.relacoes.setdefault(g.nome, {}).setdefault(f.nome, 0)
                mundo.relacoes[f.nome][g.nome] += delta
                mundo.relacoes[g.nome][f.nome] += delta

    # mantém a simetria da matriz e o intervalo legal
    for a in mundo.relacoes:
        for b in mundo.relacoes[a]:
            v = max(-100, min(100, mundo.relacoes[a][b]))
            mundo.relacoes[a][b] = v
            mundo.relacoes.setdefault(b, {})[a] = v


def gerar_npcs_do_mundo(mundo: Mundo, aleat: Aleatoriedade,
                        quantidade: int = 12) -> List[Any]:
    """Gera os NPCs notáveis do mundo, um por facção importante + errantes."""
    from .npcs import gerar_npc
    npcs = []
    faccoes = sorted(mundo.faccoes, key=lambda f: -f.prestigio)
    for f in faccoes[:max(1, quantidade // 2)]:
        prov = mundo.provincia(f.provincia)
        npcs.append(gerar_npc(
            aleat, faccao=f.nome, localizacao=f.provincia,
            nivel=min(13, f.nivel_do_lider),
            caminho={"ortodoxa": "xiandao", "demoniaca": "xiandao",
                     "nao_ortodoxa": "xiandao", "imperial": "marcial",
                     "neutra": "marcial"}[f.alinhamento],
            ocupacao="Mestre de seita" if f.tipo.startswith("seita") else None,
            agendas=1,
        ))
    restantes = max(0, quantidade - len(npcs))
    for _ in range(restantes):
        prov = aleat.escolher([p.nome for p in mundo.provincias])
        npcs.append(gerar_npc(aleat, localizacao=prov, agendas=aleat.entre(0, 2)))
    return npcs


def carregar_mundo(caminho: str) -> Dict[str, Any]:
    """Lê um mundo exportado em JSON (útil para o servidor web e a CLI)."""
    with open(caminho, "r", encoding="utf-8") as fh:
        return json.load(fh)
