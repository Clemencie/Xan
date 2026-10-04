# -*- coding: utf-8 -*-
"""
XAN — Seitas: estrutura, prédios, missões, prestígio e o Torneio de Kunlun.
============================================================================

O ciclo de gestão de seita do *Amazing Cultivation Simulator* traduzido para a
mesa: discípulos externos e internos, Anciões, Mestre de Seita, Ancestral;
prédios que produzem recursos; missões que rendem prestígio; rivalidades que
escalam; e o Torneio anual de Kunlun, onde Leis supremas trocam de dono.

Nada aqui é resolvido por opinião. Produções, custos, resultados de missão e o
torneio passam pelo motor imparcial, com compromisso por hash antes da rolagem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .auditoria import DiarioDeAuditoria
from .entropia import Aleatoriedade
from .resolucao import Declaracao, Resultado, resolver

__all__ = [
    "POSTOS", "Predio", "PREDIOS", "Missao", "MISSOES", "Seita",
    "construir", "executar_missao", "producao_mensal", "torneio_de_kunlun",
    "promover", "aceitar_discipulo", "ResultadoDeMissao", "LutasDoTorneio",
]

POSTOS: Tuple[str, ...] = (
    "servo", "discipulo_externo", "discipulo_interno", "discipulo_nucleo",
    "chefe_de_ramo", "mestre_de_pavilhao", "anciao", "grande_anciao",
    "ancestral", "mestre_da_seita",
)

_NIVEL_MINIMO_POR_POSTO: Dict[str, int] = {
    "servo": 0, "discipulo_externo": 0, "discipulo_interno": 3,
    "discipulo_nucleo": 5, "chefe_de_ramo": 6, "mestre_de_pavilhao": 7,
    "anciao": 7, "grande_anciao": 9, "ancestral": 10, "mestre_da_seita": 8,
}


@dataclass(frozen=True)
class Predio:
    codigo: str
    nome: str
    chines: str
    custo: int                 # pedras espirituais
    nivel_minimo_da_seita: int
    produz: str                # recurso produzido
    quantidade_base: int
    efeito: str
    descricao: str


PREDIOS: Dict[str, Predio] = {p.codigo: p for p in (
    Predio("PAVILHAO_MANUAIS", "Pavilhão de Manuais", "藏經閣", 5000, 1,
           "compreensao", 3,
           "+1 de Compreensão para todos os discípulos internos que estudarem aqui",
           "Estantes de bambu até o teto. Cada manual é copiado à mão."),
    Predio("CAMPOS_ESPIRITUAIS", "Campos Espirituais", "靈田", 3000, 0,
           "ervas", 8, "produz ervas de grau Terra; +2 com veia espiritual próxima",
           "Terra irrigada com Qi. Duas colheitas por ano."),
    Predio("SALA_DE_ALQUIMIA", "Sala de Alquimia", "丹房", 12000, 4,
           "elixires", 2, "refina 2 elixires por mês (DD conforme o Elixir)",
           "Fornalha de bronze e um teto que já explodiu três vezes."),
    Predio("FORJA", "Forja de Artefatos", "煉器房", 15000, 5,
           "artefatos", 1, "forja 1 artefato de grau Terra por mês",
           "Bigorna de meteorito. O calor derrete neve a cem passos."),
    Predio("SALA_DE_FORMACOES", "Sala de Formações", "陣法堂", 9000, 4,
           "formacoes", 1, "mantém uma formação de defesa sobre a sede",
           "Bússolas, bandeiras e um chão riscado de linhas que ninguém pisa."),
    Predio("OFICINA_DE_TALISMAS", "Oficina de Talismãs", "符籙坊", 7000, 3,
           "talismas", 4, "produz 4 talismãs de grau Terra por mês",
           "Papel de amoreira, cinábrio e caligrafia que não pode falhar."),
    Predio("ARENA", "Arena de Duelos", "演武場", 4000, 1,
           "treino", 5, "+1 de graduação em perícia marcial por temporada de treino",
           "Terra batida, bonecos de madeira e sangue velho."),
    Predio("SALA_DE_MEDITACAO", "Sala de Meditação", "靜室", 6000, 2,
           "estado_mental", 6, "+6 de estado mental por mês para quem a usa",
           "Silêncio absoluto. Proibido entrar armado."),
    Predio("ENFERMARIA", "Enfermaria", "醫館", 5000, 2,
           "curas", 6, "cura 6 pontos de Vitalidade por dia por paciente",
           "Cheiro de erva amarga e gemidos educados."),
    Predio("TORRE_DE_VIGIA", "Torre de Vigia", "望樓", 2500, 0,
           "alerta", 1, "detecta invasores a 5 km; +2 contra surpresa",
           "Um sino, um espelho e alguém que não dorme."),
    Predio("CELEIRO", "Celeiro", "糧倉", 1500, 0,
           "comida", 300, "alimenta 300 bocas por mês",
           "Se acabar, a seita acaba junto."),
    Predio("COFRE", "Cofre de Pedras", "庫房", 8000, 3,
           "rendimento", 2, "rende 2% ao mês sobre as pedras guardadas",
           "Selos de proteção e um Ancião de plantão."),
    Predio("ALTAR_SHENDAO", "Altar de Fé", "神壇", 20000, 6,
           "fe", 20, "gera 20 de Fé por mês por mil fiéis",
           "Só seitas Shendao constroem. O resto chama de heresia."),
    Predio("PRISAO", "Prisão de Selos", "封印牢", 10000, 5,
           "prisioneiros", 2, "mantém 2 prisioneiros selados",
           "As celas têm mais selos que portas."),
)}


@dataclass(frozen=True)
class Missao:
    codigo: str
    nome: str
    dificuldade: int            # DD base
    risco: int                  # 1 (baixo) a 5 (mortal)
    prestigio: int
    pedras: Tuple[int, int]
    xp: int
    pericia: str
    descricao: str


MISSOES: Dict[str, Missao] = {m.codigo: m for m in (
    Missao("COLHER_ERVAS", "Colher ervas na encosta", 12, 1, 2, (50, 300), 40,
           "ervas", "Ir, cortar, voltar. Quase sempre dá certo."),
    Missao("ESCOLTA_CARAVANA", "Escoltar uma caravana", 15, 2, 5, (200, 900), 90,
           "duelo", "Três dias de estrada, dois de bandidos."),
    Missao("EXPLORAR_RUINA", "Explorar uma ruína", 18, 3, 9, (400, 3000), 200,
           "percepcao_de_qi", "Dentro tem algo. Nunca é nada."),
    Missao("CACAR_BESTA", "Caçar uma besta espiritual", 17, 3, 8, (300, 2500), 180,
           "rastreamento", "Trazer o núcleo e a prova."),
    Missao("PROTEGER_VILA", "Proteger uma vila de saqueadores", 14, 2, 7,
           (100, 600), 130, "intimidacao", "A vila paga em comida e gratidão."),
    Missao("ENTREGAR_CARTA", "Entregar uma carta selada", 11, 2, 4, (80, 400), 70,
           "passos_leves", "Não abrir. Nunca abrir."),
    Missao("INFILTRAR_SEITA", "Infiltrar-se em seita rival", 22, 4, 14,
           (800, 5000), 400, "furtividade", "Se for pego, a seita nega tudo."),
    Missao("RESGATAR_REFEM", "Resgatar um refém", 20, 4, 12, (600, 4000), 350,
           "estrategia", "O refém pode já estar morto."),
    Missao("SELAR_REINO_SECRETO", "Fechar um reino secreto que vazou", 26, 5, 25,
           (2000, 20000), 900, "formacoes", "Se falhar, a província inteira cai."),
    Missao("ASSASSINAR_TRAIDOR", "Executar um traidor da seita", 24, 4, 18,
           (1000, 8000), 700, "arma_oculta", "Ele sabe onde estão os corpos."),
    Missao("COBRAR_DIVIDA", "Cobrar uma dívida de um clã", 16, 2, 6, (300, 2000),
           120, "negociacao", "O clã tem argumentos. Também tem espadas."),
    Missao("PARTICIPAR_TORNEIO", "Representar a seita em Kunlun", 20, 3, 20,
           (500, 5000), 600, "duelo", "Voltar vivo já conta como sucesso."),
)}


@dataclass(frozen=True)
class ResultadoDeMissao:
    resultado: Resultado
    missao: str
    sucesso: bool
    prestigio: int
    pedras: int
    xp: int
    baixa: str

    def resumo(self) -> str:
        cab = "SUCESSO" if self.sucesso else "FRACASSO"
        return (f"{cab} em {self.missao}: prestígio {self.prestigio:+d}, "
                f"{self.pedras} pedras, {self.xp} XP · baixa: {self.baixa}\n"
                f"  {self.resultado.resumo()}")


@dataclass
class Seita:
    nome: str
    chines: str
    alinhamento: str
    provincia: str
    nivel_do_mestre: int
    prestigio: int = 0
    pedras: int = 0
    ervas: int = 0
    elixires: int = 0
    artefatos: int = 0
    talismas: int = 0
    formacoes: int = 0
    fe: int = 0
    comida: int = 0
    predios: Tuple[str, ...] = ()
    membros: Dict[str, str] = field(default_factory=dict)   # nome → posto
    niveis: Dict[str, int] = field(default_factory=dict)    # nome → nível
    rivais: Dict[str, int] = field(default_factory=dict)    # nome → -100..100
    missoes_cumpridas: int = 0
    missoes_falhas: int = 0
    vitorias_em_kunlun: int = 0
    leis_possuidas: Tuple[str, ...] = ()
    historico: Tuple[str, ...] = ()

    RECURSOS = ("pedras", "ervas", "elixires", "artefatos", "talismas",
                "formacoes", "fe", "comida")

    def __post_init__(self) -> None:
        if self.alinhamento not in ("ortodoxa", "nao_ortodoxa", "demoniaca",
                                    "imperial", "neutra"):
            raise ValueError(f"alinhamento inválido {self.alinhamento!r}")
        for codigo in self.predios:
            if codigo not in PREDIOS:
                raise ValueError(f"prédio {codigo!r} não existe")
        for nome, posto in self.membros.items():
            if posto not in POSTOS:
                raise ValueError(f"posto {posto!r} inválido para {nome}")

    # -- consultas ---------------------------------------------------------
    def posto_de(self, nome: str) -> str:
        if nome not in self.membros:
            raise KeyError(f"{nome} não pertence a {self.nome}")
        return self.membros[nome]

    def contar(self, posto: Optional[str] = None) -> int:
        if posto is None:
            return len(self.membros)
        return sum(1 for p in self.membros.values() if p == posto)

    def tem(self, codigo: str) -> bool:
        return codigo in self.predios

    def recurso(self, nome: str) -> int:
        if nome not in self.RECURSOS:
            raise ValueError(f"recurso {nome!r} não existe")
        return int(getattr(self, nome))

    def gastar(self, nome: str, quantidade: int, motivo: str,
               diario: Optional[DiarioDeAuditoria] = None) -> None:
        if nome not in self.RECURSOS:
            raise ValueError(f"recurso {nome!r} não existe")
        atual = int(getattr(self, nome))
        if quantidade > atual:
            raise ValueError(
                f"{self.nome} tem {atual} de {nome} e tentou gastar {quantidade}"
                f" ({motivo})")
        setattr(self, nome, atual - quantidade)
        self.historico = self.historico + (f"−{quantidade} {nome}: {motivo}",)
        if diario is not None:
            diario.registrar("recurso_gasto",
                             {"seita": self.nome, "recurso": nome,
                              "quantidade": quantidade, "motivo": motivo,
                              "restante": atual - quantidade}, ator=self.nome)

    def ganhar(self, nome: str, quantidade: int, motivo: str,
               diario: Optional[DiarioDeAuditoria] = None) -> None:
        if nome not in self.RECURSOS:
            raise ValueError(f"recurso {nome!r} não existe")
        setattr(self, nome, int(getattr(self, nome)) + quantidade)
        self.historico = self.historico + (f"+{quantidade} {nome}: {motivo}",)
        if diario is not None:
            diario.registrar("recurso_ganho",
                             {"seita": self.nome, "recurso": nome,
                              "quantidade": quantidade, "motivo": motivo},
                             ator=self.nome)

    def ficha(self) -> str:
        L = [f"## {self.nome} ({self.chines})",
             f"*{self.alinhamento.replace('_',' ')} · {self.provincia} · "
             f"Mestre nível {self.nivel_do_mestre}*", "",
             f"- **Prestígio:** {self.prestigio:+d} · **Vitórias em Kunlun:** "
             f"{self.vitorias_em_kunlun}",
             f"- **Recursos:** " + " · ".join(
                 f"{r} {self.recurso(r):,}".replace(",", ".") for r in self.RECURSOS),
             f"- **Missões:** {self.missoes_cumpridas} cumpridas, "
             f"{self.missoes_falhas} falhas",
             f"- **Leis supremas possuídas:** "
             f"{', '.join(self.leis_possuidas) or 'nenhuma'}", "",
             "### Prédios"]
        if self.predios:
            for c in self.predios:
                p = PREDIOS[c]
                L.append(f"- **{p.nome}** ({p.chines}) — {p.efeito}")
        else:
            L.append("- nenhum")
        L += ["", "### Membros por posto"]
        for posto in POSTOS:
            nomes = sorted(n for n, p in self.membros.items() if p == posto)
            if nomes:
                L.append(f"- **{posto.replace('_',' ')}** ({len(nomes)}): "
                         + ", ".join(nomes[:12])
                         + (" …" if len(nomes) > 12 else ""))
        if self.rivais:
            L += ["", "### Rivais"]
            for r, v in sorted(self.rivais.items(), key=lambda kv: kv[1]):
                L.append(f"- {r}: {v:+d}")
        return "\n".join(L)


# --------------------------------------------------------------------------
# Ações de gestão
# --------------------------------------------------------------------------
def construir(seita: Seita, codigo: str,
              diario: Optional[DiarioDeAuditoria] = None) -> Predio:
    if codigo not in PREDIOS:
        raise ValueError(f"prédio {codigo!r} não existe")
    p = PREDIOS[codigo]
    if seita.tem(codigo):
        raise ValueError(f"{seita.nome} já tem {p.nome}")
    if seita.nivel_do_mestre < p.nivel_minimo_da_seita:
        raise ValueError(
            f"{p.nome} exige uma seita com mestre de nível "
            f"{p.nivel_minimo_da_seita}; o mestre está no nível "
            f"{seita.nivel_do_mestre}")
    seita.gastar("pedras", p.custo, f"construir {p.nome}", diario)
    seita.predios = seita.predios + (codigo,)
    seita.historico = seita.historico + (f"construiu {p.nome}",)
    return p


def aceitar_discipulo(seita: Seita, nome: str, nivel: int,
                      interno: bool = False) -> str:
    """Registra um novo membro. O posto mínimo depende do nível de cultivo."""
    if nome in seita.membros:
        raise ValueError(f"{nome} já pertence a {seita.nome}")
    if nivel < 0 or nivel > 13:
        raise ValueError("nível fora de 0..13")
    if interno and nivel < _NIVEL_MINIMO_POR_POSTO["discipulo_interno"]:
        raise ValueError(
            f"discípulo interno exige nível "
            f"{_NIVEL_MINIMO_POR_POSTO['discipulo_interno']}+; veio {nivel}")
    posto = "discipulo_interno" if interno else (
        "discipulo_externo" if nivel >= 1 else "servo")
    seita.membros[nome] = posto
    seita.niveis[nome] = nivel
    seita.historico = seita.historico + (f"aceitou {nome} como {posto}",)
    return posto


def promover(seita: Seita, nome: str, novo_posto: str) -> str:
    """Promoção exige o nível de cultivo mínimo do posto. Não há exceção."""
    if nome not in seita.membros:
        raise KeyError(f"{nome} não pertence a {seita.nome}")
    if novo_posto not in POSTOS:
        raise ValueError(f"posto {novo_posto!r} inválido")
    nivel = seita.niveis.get(nome, 0)
    minimo = _NIVEL_MINIMO_POR_POSTO[novo_posto]
    if nivel < minimo:
        raise ValueError(
            f"{novo_posto.replace('_',' ')} exige nível {minimo}; {nome} está "
            f"no nível {nivel}. Nenhuma promoção acontece por merecimento "
            "narrativo.")
    if POSTOS.index(novo_posto) <= POSTOS.index(seita.membros[nome]):
        raise ValueError("isso seria uma rebaixação ou uma promoção nula")
    anterior = seita.membros[nome]
    seita.membros[nome] = novo_posto
    seita.historico = seita.historico + (
        f"promoveu {nome}: {anterior} → {novo_posto}",)
    return novo_posto


_PRODUCAO_PARA_RECURSO: Dict[str, str] = {
    "CAMPOS_ESPIRITUAIS": "ervas",
    "SALA_DE_ALQUIMIA": "elixires",
    "FORJA": "artefatos",
    "OFICINA_DE_TALISMAS": "talismas",
    "SALA_DE_FORMACOES": "formacoes",
    "CELEIRO": "comida",
    "ALTAR_SHENDAO": "fe",
}


def producao_mensal(
    seita: Seita,
    densidade_qi: str = "comum",
    diario: Optional[DiarioDeAuditoria] = None,
) -> Dict[str, Any]:
    """Produção do mês, derivada dos prédios. É aritmética, não dado.

    ``densidade_qi`` é o fato declarado da região: em veia espiritual ou terra
    imortal os Campos Espirituais rendem mais. Regra escrita, aplicada a todos.
    """
    bonus_qi = {"terra_imortal": 2, "veia_espiritual": 1}.get(densidade_qi, 0)
    ganhos: Dict[str, int] = {}
    beneficios: List[str] = []

    for codigo in seita.predios:
        p = PREDIOS[codigo]
        if codigo == "COFRE":
            ganhos["pedras"] = ganhos.get("pedras", 0) + max(1, seita.pedras * 2 // 100)
            continue
        recurso = _PRODUCAO_PARA_RECURSO.get(codigo)
        if recurso is None:
            beneficios.append(f"{p.nome}: {p.efeito}")
            continue
        qtd = p.quantidade_base + (bonus_qi * 2 if codigo == "CAMPOS_ESPIRITUAIS"
                                   else bonus_qi)
        ganhos[recurso] = ganhos.get(recurso, 0) + qtd

    for chave, valor in ganhos.items():
        seita.ganhar(chave, valor, "produção mensal", diario)

    bocas = len(seita.membros)
    if seita.comida > 0:
        seita.gastar("comida", min(bocas, seita.comida), "consumo mensal", diario)
    fome = max(0, bocas - seita.comida)

    if diario is not None:
        diario.registrar("producao_mensal",
                         {"seita": seita.nome, "ganhos": ganhos,
                          "beneficios": beneficios, "densidade_qi": densidade_qi,
                          "bocas": bocas, "bocas_sem_comida": fome},
                         ator=seita.nome)
    return {"recursos": ganhos, "beneficios": beneficios, "bocas": bocas,
            "fome": fome}


def executar_missao(
    seita: Seita,
    codigo: str,
    executor: str,
    aleat: Aleatoriedade,
    *,
    nivel: int,
    valor_atributo: int,
    graduacao: int,
    fatos: Optional[Mapping[str, Any]] = None,
    regras: Sequence[str] = ("RECURSO:ELIXIR", "RECURSO:TALISMA",
                             "RECURSO:ARTEFATO", "ESTADO:FERIMENTO"),
    diario: Optional[DiarioDeAuditoria] = None,
) -> ResultadoDeMissao:
    """Executa uma missão da seita. O resultado sai do dado, nunca do enredo."""
    if codigo not in MISSOES:
        raise ValueError(f"missão {codigo!r} não existe")
    m = MISSOES[codigo]
    if executor not in seita.membros:
        raise KeyError(f"{executor} não pertence a {seita.nome}")
    base: Dict[str, Any] = {"elixir": "nenhum", "talisma": "nenhum",
                            "artefato": "nenhum", "ferimento": "ileso"}
    base.update(dict(fatos or {}))
    dd = m.dificuldade + max(0, (m.risco - 1)) - min(3, seita.prestigio // 25)
    decl = Declaracao(
        acao=f"missão {m.nome}",
        ator=executor,
        atributo="luk" if m.pericia == "negociacao" else "per",
        valor_atributo=valor_atributo,
        bonus_atributo=(valor_atributo - 10) // 2,
        pericia=m.pericia,
        graduacao=max(0, min(5, graduacao)),
        dificuldade=max(5, dd),
        regras=tuple(regras),
        fatos=base,
        contexto={"seita": seita.nome, "missao": codigo, "risco": m.risco,
                  "posto": seita.posto_de(executor)},
    )
    res = resolver(decl, aleat, diario)
    if res.sucesso:
        pedras = aleat.entre(*m.pedras)
        prestigio = m.prestigio + (2 if res.grau in ("sucesso_maior", "triunfo",
                                                      "toque_do_dao") else 0)
        baixa = "nenhuma"
        seita.missoes_cumpridas += 1
        seita.prestigio = max(-200, min(300, seita.prestigio + prestigio))
        seita.ganhar("pedras", pedras, f"missão {m.nome}", diario)
        seita.historico = seita.historico + (
            f"{executor} cumpriu {m.nome} (+{prestigio} prestígio)",)
    else:
        pedras = 0
        prestigio = -max(1, m.prestigio // 2)
        baixa = _baixa_por_risco(aleat, m.risco, res.critico == "desvio")
        seita.missoes_falhas += 1
        seita.prestigio = max(-200, min(300, seita.prestigio + prestigio))
        seita.historico = seita.historico + (
            f"{executor} falhou em {m.nome}: {baixa}",)
    if diario is not None:
        diario.registrar("missao",
                         {"seita": seita.nome, "missao": codigo,
                          "executor": executor, "sucesso": res.sucesso,
                          "pedras": pedras, "prestigio": prestigio,
                          "baixa": baixa}, ator=executor)
    return ResultadoDeMissao(res, m.nome, res.sucesso, prestigio, pedras,
                             m.xp if res.sucesso else m.xp // 4, baixa)


def _baixa_por_risco(aleat: Aleatoriedade, risco: int, critico: bool) -> str:
    tabela = {
        1: ["voltou de mãos vazias", "perdeu o equipamento",
            "voltou com vergonha e −5 de estado mental"],
        2: ["voltou ferido (2d6 de Vitalidade)", "perdeu um companheiro externo",
            "foi capturado e resgatado por pedras"],
        3: ["voltou gravemente ferido (4d6)", "um discípulo interno morreu",
            "trouxe uma maldição junto"],
        4: ["metade da equipe não voltou", "o executor perdeu 1 nível de cultivo",
            "a seita foi publicamente humilhada (−10 de prestígio extra)"],
        5: ["nenhum sobrevivente", "o executor morreu",
            "a missão despertou algo pior"],
    }[risco]
    if critico:
        return tabela[-1]
    return aleat.escolher(tabela)


# --------------------------------------------------------------------------
# Torneio de Kunlun — anual, decide a posse das Leis supremas
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class LutasDoTorneio:
    ano: int
    confrontos: Tuple[Tuple[str, str, str, int, int], ...]
    campeao: str
    seita_campea: str
    lei_conquistada: Optional[str]
    classificacao: Tuple[Tuple[str, int], ...]

    def resumo(self) -> str:
        L = [f"# Torneio de Kunlun — ano {self.ano}",
             f"**Campeão: {self.campeao} ({self.seita_campea})**"]
        if self.lei_conquistada:
            L.append(f"Lei suprema conquistada: **{self.lei_conquistada}**")
        L += ["", "## Confrontos"]
        for a, b, vencedor, ta, tb in self.confrontos:
            L.append(f"- {a} **{ta}** × **{tb}** {b} → venceu **{vencedor}**")
        L += ["", "## Classificação final"]
        for i, (nome, pontos) in enumerate(self.classificacao, 1):
            L.append(f"{i}. {nome} — {pontos} pontos")
        return "\n".join(L)


def torneio_de_kunlun(
    ano: int,
    participantes: Sequence[Mapping[str, Any]],
    aleat: Aleatoriedade,
    *,
    lei_em_disputa: Optional[str] = None,
    diario: Optional[DiarioDeAuditoria] = None,
) -> LutasDoTorneio:
    """Chaveamento e lutas do Torneio anual.

    Cada participante é um dicionário com ``nome``, ``seita``, ``nivel``,
    ``atributo`` (valor), ``graduacao`` e ``fatos`` opcionais. As lutas são
    testes opostos; o chaveamento é sorteado pela mesma entropia auditada.
    """
    if len(participantes) < 2:
        raise ValueError("o torneio precisa de pelo menos dois participantes")
    for p in participantes:
        for chave in ("nome", "seita", "nivel", "atributo", "graduacao"):
            if chave not in p:
                raise ValueError(f"participante sem o campo {chave!r}: {p}")

    ordem = list(participantes)
    aleat.baralhar(ordem)

    pontos: Dict[str, int] = {p["nome"]: 0 for p in ordem}
    confrontos: List[Tuple[str, str, str, int, int]] = []
    ja_lutaram: set = set()

    from .resolucao import teste_oposto

    # rodadas de suíça: cada participante luta contra o de pontuação mais próxima
    rodadas = max(1, (len(ordem) * 2) // 3)
    for _ in range(rodadas):
        disponiveis = sorted(ordem, key=lambda p: (-pontos[p["nome"]], p["nome"]))
        usados = set()
        pares: List[Tuple[Mapping[str, Any], Mapping[str, Any]]] = []
        # emparelhamento suíço evitando repetição de confronto quando possível
        fila = list(disponiveis)
        while len(fila) >= 2:
            a = fila.pop(0)
            b = None
            for k, candidato in enumerate(fila):
                chave = tuple(sorted((a["nome"], candidato["nome"])))
                if chave not in ja_lutaram:
                    b = fila.pop(k)
                    break
            if b is None:
                b = fila.pop(0)
            pares.append((a, b))
        for a, b in pares:
            ja_lutaram.add(tuple(sorted((a["nome"], b["nome"]))))
            usados.add(a["nome"]); usados.add(b["nome"])
            da = Declaracao(
                acao=f"duelo de Kunlun contra {b['nome']}",
                ator=a["nome"], atributo="con", valor_atributo=a["atributo"],
                bonus_atributo=(a["atributo"] - 10) // 2,
                pericia="duelo", graduacao=min(5, a["graduacao"]),
                dificuldade=15, regras=("REINO:SUPRESSAO",),
                fatos={"reino_atacante": a["nivel"], "reino_alvo": b["nivel"]},
                contexto={"torneio": ano, "rodada": _ + 1})
            db = Declaracao(
                acao=f"duelo de Kunlun contra {a['nome']}",
                ator=b["nome"], atributo="con", valor_atributo=b["atributo"],
                bonus_atributo=(b["atributo"] - 10) // 2,
                pericia="duelo", graduacao=min(5, b["graduacao"]),
                dificuldade=15, regras=("REINO:SUPRESSAO",),
                fatos={"reino_atacante": b["nivel"], "reino_alvo": a["nivel"]},
                contexto={"torneio": ano, "rodada": _ + 1})
            op = teste_oposto(da, db, aleat, diario)
            if op.vencedor == "atacante":
                vencedor_nome = a["nome"]
                pontos[a["nome"]] += 3
                pontos[b["nome"]] += 1
            elif op.vencedor == "defensor":
                vencedor_nome = b["nome"]
                pontos[b["nome"]] += 3
                pontos[a["nome"]] += 1
            else:
                # empate só é possível se a cascata de desempate falhar; ambos pontuam
                vencedor_nome = "empate"
                pontos[a["nome"]] += 2
                pontos[b["nome"]] += 2
            confrontos.append((a["nome"], b["nome"], vencedor_nome,
                               op.atacante.total, op.defensor.total))

    classificacao = tuple(sorted(pontos.items(), key=lambda kv: (-kv[1], kv[0])))
    campeao = classificacao[0][0]
    seita_campea = next(p["seita"] for p in participantes if p["nome"] == campeao)
    if diario is not None:
        diario.registrar("torneio_de_kunlun",
                         {"ano": ano, "campeao": campeao,
                          "seita": seita_campea,
                          "classificacao": [list(c) for c in classificacao],
                          "lei_em_disputa": lei_em_disputa}, ator="kunlun")
    return LutasDoTorneio(ano, tuple(confrontos), campeao, seita_campea,
                          lei_em_disputa if campeao else None, classificacao)
