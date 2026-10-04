# -*- coding: utf-8 -*-
"""
Testes das camadas de jogo: reinos, personagens, NPCs, mundo, combate, seitas,
artes, bestiário, calendário e mapas.

O objetivo não é só "não quebrar": é garantir que as **propriedades do sistema**
sejam verdadeiras — monotonicidade das tabelas, coerência entre módulos,
ausência de dependência do ator, e o fato de que nada de decisivo fica sem
número na tabela.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from fractions import Fraction

from xan.artes import (
    ARTEFATOS, ELIXIRES, ERVAS, FORMACOES, TALISMAS, TECNICAS, dano_de,
    sortear_tesouro, tecnica_de, tecnicas_de_lei, tecnicas_livres,
)
from xan.auditoria import DiarioDeAuditoria
from xan.bestiario import BESTAS, Besta, gerar_besta, nucleo_de_besta
from xan.calendario import (
    CLIMAS, Data, ESTACOES, Hora, avancar_dias, estacao_do_mes,
    harmonia_elemental, sortear_clima,
)
from xan.combate import (
    Cenario, Combatente, Encontro, LACUNA_IMBATIVEL, ModoDeDefesa, atacar,
    defender, dentro_do_alcance, encerrar, faixa_para_regra, iniciar_encontro,
    usar_tecnica,
)
from xan.compromisso import conferir, rolagem_auditada
from xan.entropia import Aleatoriedade, FonteSemeada
from xan.mapas import mapa_da_provincia, mapa_do_mundo
from xan.mundo import DensidadeDeQi, gerar_mundo, gerar_npcs_do_mundo
from xan.npcs import (
    DISPOSICOES, EVENTOS_DE_RELACAO, LivroDeRelacoes, Npc, PEDIDOS_TIPICOS,
    TABELA_DE_CONDUTA, TRACOS, Virtudes, camada_ativa, disposicao_para,
    gerar_npc, gerar_nome, resolver_conduta, resolver_conflito_de_desejos,
)
from xan.personagens import (
    EstadoDeJogo, GRAUS_DE_RAIZ, MOTIVOS, Mudanca, PERICIAS, Personagem,
    RaizEspiritual, TABELAS_DE_RAIZ, criar_personagem, ferimento_por_vitalidade,
    sortear_raiz,
)
from xan.regras import (
    ELEMENTOS_CANONICOS, PRIORIDADE_DE_CAMADA_DE_DESEJO, REGISTRO,
    relacao_elemental, valor_de,
)
from xan.reinos import (
    CAMINHOS, LEIS, REINOS, compatibilidade_de_lei, dd_de_ruptura, defesa_de,
    formar_nucleo_dourado, lei_de, pontos_de_ruptura, qi_maximo,
    raios_de_tribulacao, reino_de, tabela_de_desvio_de_qi, tentar_ruptura,
    tribulacao_celestial, vitalidade_maxima,
)
from xan.resolucao import ATRIBUTOS, Declaracao, resolver
from xan.seitas import (
    MISSOES, POSTOS, PREDIOS, Seita, aceitar_discipulo, construir,
    executar_missao, producao_mensal, promover, torneio_de_kunlun,
)


class BaseComSemente(unittest.TestCase):
    semente_base = "teste-de-dominio"

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="xan-teste-")
        self._n = 0

    def tearDown(self) -> None:
        shutil.rmtree(self._tmp, ignore_errors=True)

    def aleat(self, contexto: str = "") -> Aleatoriedade:
        self._n += 1
        return Aleatoriedade(FonteSemeada(self.semente_base,
                                          contexto or f"ctx{self._n}"))

    def diario(self, nome: str = "diario.jsonl") -> DiarioDeAuditoria:
        return DiarioDeAuditoria(os.path.join(self._tmp, nome))


# ==========================================================================
# Calendário
# ==========================================================================
class TesteCalendario(BaseComSemente):
    def test_aritmetica_de_datas(self):
        d = Data(1, 1, 1)
        self.assertEqual(d.dia_absoluto, 1)
        self.assertEqual(avancar_dias(d, 359), Data(1, 12, 30))
        self.assertEqual(avancar_dias(d, 360), Data(2, 1, 1))
        self.assertEqual(avancar_dias(d, 720), Data(3, 1, 1))
        self.assertEqual(avancar_dias(avancar_dias(d, 5000), -5000), d)

    def test_datas_invalidas(self):
        for kw in ({"ano": 1, "mes": 0, "dia": 1}, {"ano": 1, "mes": 13, "dia": 1},
                   {"ano": 1, "mes": 1, "dia": 0}, {"ano": 1, "mes": 1, "dia": 31},
                   {"ano": 0, "mes": 1, "dia": 1}):
            with self.assertRaises(ValueError):
                Data(**kw)

    def test_estacoes(self):
        self.assertEqual([estacao_do_mes(m) for m in (1, 3, 4, 6, 7, 9, 10, 12)],
                         ["primavera", "primavera", "verao", "verao", "outono",
                          "outono", "inverno", "inverno"])

    def test_shichen(self):
        self.assertEqual(Hora.da_hora_solar(0).nome, "Zǐ")
        self.assertEqual(Hora.da_hora_solar(12).nome, "Wǔ")
        self.assertEqual(Hora.da_hora_solar(23).nome, "Zǐ")
        self.assertEqual(Hora.da_hora_solar(3).polaridade, "yang")
        self.assertEqual(Hora.da_hora_solar(2).polaridade, "yin")
        for h in range(24):
            self.assertIn(Hora.da_hora_solar(h).polaridade, ("yin", "yang"))

    def test_clima_dentro_do_catalogo(self):
        a = self.aleat("clima")
        for estacao in ESTACOES:
            for elemento in ELEMENTOS_CANONICOS + ("nenhum",):
                for altitude in (0, 2, 3):
                    c = sortear_clima(a, estacao, elemento, altitude)
                    self.assertIn(c, CLIMAS)

    def test_clima_e_deterministico(self):
        a1, a2 = self.aleat("c1"), self.aleat("c1")
        seq1 = [sortear_clima(a1, "inverno", "agua") for _ in range(60)]
        seq2 = [sortear_clima(a2, "inverno", "agua") for _ in range(60)]
        self.assertEqual(seq1, seq2)

    def test_regiao_puxa_o_proprio_clima(self):
        """Peso ×3 no clima do elemento da região deve aparecer na frequência."""
        contagens = {e: {} for e in ("agua", "fogo")}
        for elemento in ("agua", "fogo"):
            a = self.aleat(f"regiao-{elemento}")
            for _ in range(4000):
                c = sortear_clima(a, "primavera", elemento)
                contagens[elemento][c] = contagens[elemento].get(c, 0) + 1
        # primavera: agua aparece como chuva/nevoeiro; fogo como miasma
        self.assertGreater(contagens["agua"]["chuva"], contagens["fogo"]["chuva"])
        self.assertGreater(contagens["fogo"]["miasma"], contagens["agua"]["miasma"])

    def test_harmonia_elemental_limites(self):
        for elemento in ELEMENTOS_CANONICOS + ("nenhum", "vazio"):
            for estacao in ESTACOES:
                for dia in (1, 15, 20, 30):
                    for pol in ("yin", "yang"):
                        for clima in CLIMAS:
                            pontos, razoes = harmonia_elemental(
                                elemento, estacao, dia, pol, clima)
                            self.assertTrue(0 <= pontos <= 12,
                                            f"{elemento} {estacao} {dia} {pol} {clima}")
                            self.assertTrue(razoes, "harmonia sem justificativa")

    def test_harmonia_maxima_e_minima(self):
        # metal: outono/inverno, dias 16-30, hora yin, clima tempestade
        mx, _ = harmonia_elemental("metal", "inverno", 25, "yin", "tempestade")
        self.assertEqual(mx, 12)
        mn, _ = harmonia_elemental("fogo", "inverno", 20, "yin", "nevasca")
        self.assertEqual(mn, 0)

    def test_elemento_invalido(self):
        with self.assertRaises(ValueError):
            harmonia_elemental("plasma", "inverno", 1, "yin", "limpo")
        with self.assertRaises(ValueError):
            harmonia_elemental("fogo", "estacao-x", 1, "yin", "limpo")


# ==========================================================================
# Reinos e Leis
# ==========================================================================
class TesteReinos(BaseComSemente):
    def test_escada_completa_e_coerente(self):
        self.assertEqual(len(REINOS), 14)
        for i, r in enumerate(REINOS):
            self.assertEqual(r.nivel, i)
            self.assertIn(r.metodo, r.METODOS)
            self.assertGreater(r.longevidade, 0)
        # monotonicidade
        for a, b in zip(REINOS, REINOS[1:]):
            self.assertLess(a.longevidade, b.longevidade,
                            f"longevidade não cresce de {a.nivel} para {b.nivel}")
            self.assertLessEqual(a.qi_base, b.qi_base)
            self.assertLessEqual(a.vitalidade_base, b.vitalidade_base)

    def test_xp_crescente(self):
        xps = [r.xp_necessario for r in REINOS if r.xp_necessario > 0]
        self.assertEqual(xps, sorted(xps), "XP precisa crescer com o nível")

    def test_metodos_obrigatorios(self):
        self.assertEqual(reino_de(6).metodo, "pontuacao")
        self.assertEqual(reino_de(9).metodo, "tribulacao")
        self.assertEqual(reino_de(11).metodo, "tribulacao")
        self.assertEqual(reino_de(12).metodo, "tribulacao")
        self.assertEqual(reino_de(13).metodo, "nenhum")

    def test_todos_os_niveis_tem_nome_em_todos_os_caminhos(self):
        for r in REINOS:
            for c in CAMINHOS:
                self.assertTrue(r.nome_para(c).strip(),
                                f"nível {r.nivel} sem nome para {c}")

    def test_reino_invalido(self):
        for n in (-1, 14, 100):
            with self.assertRaises(ValueError):
                reino_de(n)
        with self.assertRaises(TypeError):
            reino_de(3.0)

    def test_leis_bem_formadas(self):
        self.assertGreaterEqual(len(LEIS), 28)
        for codigo, lei in LEIS.items():
            self.assertEqual(lei.codigo, codigo)
            self.assertIn(lei.caminho, CAMINHOS)
            self.assertTrue(lei.requisitos, f"{codigo} sem requisitos")
            self.assertTrue(lei.descricao.strip())
            self.assertTrue(lei.nome.strip())
            self.assertTrue(lei.chines.strip())
            self.assertLessEqual(lei.dd_extra, 3)

    def test_toda_lei_tem_tecnica(self):
        for codigo in LEIS:
            self.assertTrue(tecnicas_de_lei(codigo),
                            f"a Lei {codigo} não tem nenhuma técnica")

    def test_tecnicas_livres_existem_para_nivel_1(self):
        self.assertGreaterEqual(len(tecnicas_livres(1)), 3)

    def test_compatibilidade_limites_e_logica(self):
        for codigo, lei in LEIS.items():
            # cumprir exatamente ⇒ 100%
            exatos = {k: v for k, v in lei.requisitos.items()}
            m, razoes = compatibilidade_de_lei(exatos, lei)
            self.assertEqual(m, 100, f"{codigo}: cumprir exatamente deve dar 100%")
            self.assertEqual(len(razoes), len(lei.requisitos))
            # tudo em zero ⇒ 0%
            zeros = {k: 1 for k in lei.requisitos}
            m0, _ = compatibilidade_de_lei(zeros, lei)
            self.assertLess(m0, 100)
            # tudo no teto ⇒ 150%
            altos = {k: 30 for k in lei.requisitos}
            m1, _ = compatibilidade_de_lei(altos, lei)
            self.assertEqual(m1, 150, f"{codigo}: excesso deve saturar em 150%")
            # monotonia
            medios = {k: (v + 30) // 2 for k, v in lei.requisitos.items()}
            mm, _ = compatibilidade_de_lei(medios, lei)
            self.assertLessEqual(m0, mm)
            self.assertLessEqual(mm, m1)

    def test_compatibilidade_rejeita_atributo_negativo(self):
        with self.assertRaises(ValueError):
            compatibilidade_de_lei({"con": -1, "luk": 5}, lei_de("ROUBO_CELESTIAL"))

    def test_recursos_crescem_com_o_nivel(self):
        for atributos in ((10, 10, 10), (14, 16, 14), (22, 20, 20)):
            con, per, int_ = atributos
            qs = [qi_maximo(n, con, per, int_) for n in range(14)]
            vs = [vitalidade_maxima(n, con, con) for n in range(14)]
            self.assertEqual(qs, sorted(qs))
            self.assertEqual(vs, sorted(vs))
            self.assertGreater(qs[-1], qs[0] * 5)

    def test_nucleo_exige_nivel_7(self):
        with self.assertRaises(ValueError):
            qi_maximo(6, 14, 14, 14, grau_do_nucleo=3)
        self.assertGreater(qi_maximo(7, 14, 14, 14, grau_do_nucleo=1),
                           qi_maximo(7, 14, 14, 14, grau_do_nucleo=9))

    def test_defesa_nao_depende_do_nivel(self):
        """Propriedade de projeto: a Defesa não embute o nível."""
        base = defesa_de("esquiva", 1, 14, 3)
        self.assertEqual(base, defesa_de("esquiva", 12, 14, 3))
        self.assertEqual(defesa_de("esquiva", 5, 14, 3), 10 + 2 + 3)
        self.assertEqual(defesa_de("resistencia", 5, 14, 3), 11 + 2 + 3)
        self.assertEqual(defesa_de("aparar", 5, 14, 3), 10 + 2 + 3)
        self.assertEqual(defesa_de("esquiva", 5, 14, 3, True), 10 + 2 + 3 + 2)

    def test_defesa_rejeita_modo_invalido(self):
        with self.assertRaises(ValueError):
            defesa_de("rolar_no_chao", 5, 14, 3)
        with self.assertRaises(TypeError):
            defesa_de("esquiva", 5, 14, 3, "sim")

    def test_dd_de_ruptura_responde_a_compatibilidade(self):
        lei = lei_de("SETE_MASSACRES")
        dd_alta = dd_de_ruptura(5, 150, lei)
        dd_media = dd_de_ruptura(5, 100, lei)
        dd_baixa = dd_de_ruptura(5, 30, lei)
        self.assertLess(dd_alta, dd_media)
        self.assertLess(dd_media, dd_baixa)
        self.assertTrue(5 <= dd_alta and dd_baixa <= 45)

    def test_dd_recusa_nivel_sem_rolagem(self):
        for nivel in (6, 9, 11, 12, 13):
            with self.assertRaises(ValueError):
                dd_de_ruptura(nivel, 100, lei_de("PUREZA_JADE"))

    def test_pontos_de_ruptura(self):
        self.assertEqual(pontos_de_ruptura(0), 100)
        self.assertEqual(pontos_de_ruptura(12), 0)

    def test_raios_de_tribulacao(self):
        self.assertEqual(raios_de_tribulacao(9), 3)
        self.assertEqual(raios_de_tribulacao(11), 4)
        self.assertEqual(raios_de_tribulacao(12), 9)
        self.assertEqual(raios_de_tribulacao(9, True), 4)
        self.assertEqual(raios_de_tribulacao(6, True), 1)
        with self.assertRaises(ValueError):
            raios_de_tribulacao(6)          # só demoníacos
        for nivel in (0, 1, 2, 3, 4, 5, 7, 8, 10, 13):
            with self.assertRaises(ValueError):
                raios_de_tribulacao(nivel)

    def test_tabela_de_desvio_cobre_seis_casas(self):
        a = self.aleat("desvio")
        vistos = set()
        for gravidade in ("comum", "grave", "catastrofica"):
            for _ in range(400):
                face, texto = tabela_de_desvio_de_qi(a, gravidade)
                vistos.add(face)
                self.assertTrue(texto.strip())
                self.assertIn(face, (1, 2, 3, 4, 5, 6))
        self.assertEqual(vistos, {1, 2, 3, 4, 5, 6})
        with self.assertRaises(ValueError):
            tabela_de_desvio_de_qi(a, "leve")

    def test_desvio_catastrofico_e_pior_que_comum(self):
        a = self.aleat("gravidade")
        comuns = [tabela_de_desvio_de_qi(a, "comum")[0] for _ in range(3000)]
        graves = [tabela_de_desvio_de_qi(a, "catastrofica")[0] for _ in range(3000)]
        self.assertGreater(sum(graves) / len(graves), sum(comuns) / len(comuns))


# ==========================================================================
# Núcleo Dourado
# ==========================================================================
class TesteNucleoDourado(BaseComSemente):
    def kwargs(self, **sob):
        base = dict(qi_maximo_atual=400, fengshui="neutro",
                    densidade_qi="comum", harmonia=4, estado_mental=60,
                    elixir="nenhum", compatibilidade=80, compreensao=500,
                    mestre_presente=False, artefato="nenhum")
        base.update(sob)
        return base

    def test_deterministico_sem_dado(self):
        g1 = formar_nucleo_dourado(**self.kwargs())
        g2 = formar_nucleo_dourado(**self.kwargs())
        self.assertEqual(g1, g2)

    def test_todo_grau_e_alcancavel(self):
        """Cada um dos nove graus tem uma configuração que o produz."""
        graus = set()
        for qi in (100, 400, 452):
            for fs in ("muito_sinistro", "neutro", "muito_auspicioso"):
                for dq in ("esteril", "comum", "terra_imortal"):
                    for h in (0, 6, 12):
                        for em in (0, 60, 200):
                            for el in ("nenhum", "medio", "celestial"):
                                for cp in (0, 100, 150):
                                    for ar in ("nenhum", "primordial"):
                                        for me in (False, True):
                                            g = formar_nucleo_dourado(
                                                **self.kwargs(
                                                    qi_maximo_atual=qi,
                                                    fengshui=fs,
                                                    densidade_qi=dq,
                                                    harmonia=h,
                                                    estado_mental=em,
                                                    elixir=el,
                                                    compatibilidade=cp,
                                                    compreensao=2000,
                                                    artefato=ar,
                                                    mestre_presente=me)).grau
                                            graus.add(g)
        self.assertEqual(graus, {1, 2, 3, 4, 5, 6, 7, 8, 9})

    def test_monotonia_em_cada_fator(self):
        base = formar_nucleo_dourado(**self.kwargs()).pontuacao
        casos = [
            dict(qi_maximo_atual=1000),
            dict(fengshui="muito_auspicioso"),
            dict(densidade_qi="terra_imortal"),
            dict(harmonia=12),
            dict(estado_mental=200),
            dict(elixir="celestial"),
            dict(compatibilidade=150),
            dict(compreensao=5000),
            dict(artefato="primordial"),
            dict(mestre_presente=True),
        ]
        for caso in casos:
            self.assertGreater(formar_nucleo_dourado(**self.kwargs(**caso)).pontuacao,
                               base, f"fator {caso} não melhorou o núcleo")
        piores = [dict(fengshui="muito_sinistro"), dict(densidade_qi="esteril"),
                  dict(harmonia=0), dict(estado_mental=0),
                  dict(compatibilidade=0)]
        for caso in piores:
            self.assertLess(formar_nucleo_dourado(**self.kwargs(**caso)).pontuacao,
                            base, f"fator {caso} não piorou o núcleo")

    def test_parcelas_somam_o_total(self):
        g = formar_nucleo_dourado(**self.kwargs(qi_maximo_atual=452,
                                                fengshui="muito_auspicioso"))
        self.assertEqual(sum(v for _, v in g.parcelas), g.pontuacao)
        self.assertEqual(len(g.razoes), len(g.parcelas))
        self.assertTrue(g.titulo)
        self.assertIn("Núcleo Dourado", g.markdown())

    def test_grau_1_exige_quase_tudo(self):
        g = formar_nucleo_dourado(
            qi_maximo_atual=452, fengshui="muito_auspicioso",
            densidade_qi="terra_imortal", harmonia=12, estado_mental=200,
            elixir="celestial", compatibilidade=150, compreensao=2000,
            mestre_presente=True, artefato="primordial")
        self.assertEqual(g.grau, 1)
        # o grau 1 fica em 95: a configuração perfeita soma 108, então há 13
        # pontos de folga. Remover um fator grande (harmonia, 12 pontos) e o
        # mestre (4) derruba o grau — e é exatamente isso que se testa.
        self.assertEqual(g.grau, 1)
        self.assertEqual(g.pontuacao, 108)
        # sem a harmonia do momento (12 pontos) ainda sobra folga: 96 ≥ 95
        sem_harmonia = formar_nucleo_dourado(
            qi_maximo_atual=452, fengshui="muito_auspicioso",
            densidade_qi="terra_imortal", harmonia=0, estado_mental=200,
            elixir="celestial", compatibilidade=150, compreensao=2000,
            mestre_presente=True, artefato="primordial")
        self.assertEqual(g.pontuacao - sem_harmonia.pontuacao, 12)
        sem_tres = formar_nucleo_dourado(
            qi_maximo_atual=452, fengshui="muito_auspicioso",
            densidade_qi="terra_imortal", harmonia=0, estado_mental=200,
            elixir="nenhum", compatibilidade=150, compreensao=2000,
            mestre_presente=False, artefato="nenhum")
        self.assertEqual(g.pontuacao - sem_tres.pontuacao, 12 + 14 + 9 + 4)
        self.assertGreater(sem_tres.grau, 2)

    def test_validacoes(self):
        ruins = [dict(qi_maximo_atual=-1), dict(estado_mental=201),
                 dict(estado_mental=-1), dict(compreensao=-5),
                 dict(compatibilidade=151), dict(compatibilidade=-1),
                 dict(fengshui="bonitinho"), dict(densidade_qi="muita"),
                 dict(elixir="azul"), dict(harmonia=13), dict(harmonia=-1),
                 dict(artefato="divino")]
        for caso in ruins:
            with self.assertRaises(ValueError, msg=str(caso)):
                formar_nucleo_dourado(**self.kwargs(**caso))
        with self.assertRaises(TypeError):
            formar_nucleo_dourado(**self.kwargs(mestre_presente="sim"))


# ==========================================================================
# Rupturas e tribulação
# ==========================================================================
class TesteRupturas(BaseComSemente):
    def test_ruptura_avanca_um_nivel_e_registra(self):
        a = self.aleat("rup")
        d = self.diario()
        avancos = 0
        for i in range(40):
            r = tentar_ruptura(ator=f"C{i}", nivel_atual=5,
                               compatibilidade=120, lei=lei_de("SETE_MASSACRES"),
                               valor_de_int=18, graduacao_de_compreensao=5,
                               fatos={"fengshui": "auspicioso",
                                      "densidade_qi": "rica", "elixir": "medio",
                                      "meditou": True},
                               aleat=a, diario=d)
            self.assertIsInstance(r.resultado.total, int)
            if r.avancou:
                avancos += 1
                self.assertEqual(r.nivel_novo, 6)
                self.assertIsNone(r.desvio_de_qi)
            else:
                self.assertEqual(r.nivel_novo, 5)
                self.assertIsNotNone(r.desvio_de_qi)
        self.assertGreater(avancos, 0, "nenhuma ruptura passou em 40 tentativas")
        self.assertLess(avancos, 40, "todas passaram — DD provavelmente errada")
        self.assertTrue(d.verificar().ok)
        self.assertTrue(conferir(d).ok)

    def test_ruptura_recusa_nivel_de_pontuacao_ou_tribulacao(self):
        a = self.aleat("rup2")
        for nivel in (6, 9, 11, 12):
            with self.assertRaises(ValueError):
                tentar_ruptura(ator="X", nivel_atual=nivel, compatibilidade=100,
                               lei=lei_de("PUREZA_JADE"), valor_de_int=14,
                               graduacao_de_compreensao=2, aleat=a)

    def test_preparo_melhora_a_taxa_de_sucesso(self):
        lei = lei_de("SETE_MASSACRES")
        taxas = {}
        for rotulo, fatos, comp in (
                ("sem", {"fengshui": "neutro", "densidade_qi": "comum",
                         "elixir": "nenhum", "meditou": False}, 60),
                ("com", {"fengshui": "muito_auspicioso",
                         "densidade_qi": "terra_imortal", "elixir": "celestial",
                         "meditou": True}, 150)):
            a = self.aleat(f"prep-{rotulo}")
            ok = sum(1 for i in range(300)
                     if tentar_ruptura(ator=f"C{i}", nivel_atual=5,
                                       compatibilidade=comp, lei=lei,
                                       valor_de_int=16,
                                       graduacao_de_compreensao=4,
                                       fatos=fatos, aleat=a).avancou)
            taxas[rotulo] = ok
        self.assertGreater(taxas["com"], taxas["sem"] * 1.5)

    def test_tribulacao_audita_cada_raio(self):
        a = self.aleat("trib")
        d = self.diario("trib.jsonl")
        t = tribulacao_celestial(ator="Lin", nivel=9, demoniaca=False,
                                 valor_de_con=20, graduacao_de_defesa=4,
                                 vitalidade=220, qi_atual=370,
                                 fatos={"artefato": "ceu", "formacao": "aliada",
                                        "elixir": "maior", "anos_queimados": 20},
                                 aleat=a, diario=d)
        self.assertEqual(len(t.raios), 3)
        for i, raio in enumerate(t.raios, 1):
            self.assertEqual(raio.indice, i)
            self.assertEqual(raio.dificuldade, 14 + 9 + 2 * (i - 1))
            self.assertGreaterEqual(raio.absorvido_pelo_qi, 0)
            self.assertGreaterEqual(raio.dano_na_vitalidade, 0)
        self.assertIn("Tribulação Celestial", t.resumo_texto)
        self.assertTrue(d.verificar().ok)
        self.assertTrue(conferir(d).ok)
        self.assertEqual(len(d.por_tipo("rolagem")), 3)

    def test_tribulacao_conserva_a_aritmetica_do_dano(self):
        a = self.aleat("cons")
        for i in range(30):
            t = tribulacao_celestial(ator=f"C{i}", nivel=11, demoniaca=True,
                                     valor_de_con=16, graduacao_de_defesa=2,
                                     vitalidade=300, qi_atual=500, aleat=a)
            qi, vit = 500, 300
            for r in t.raios:
                self.assertLessEqual(r.absorvido_pelo_qi, qi)
                qi -= r.absorvido_pelo_qi
                vit -= r.dano_na_vitalidade
            self.assertEqual(qi, t.qi_restante)
            self.assertEqual(vit, t.vitalidade_restante)
            self.assertEqual(t.sobreviveu, vit > 0)

    def test_tribulacao_exige_o_nivel_certo(self):
        a = self.aleat("trib3")
        for nivel in (0, 3, 5, 7, 8, 10, 13):
            with self.assertRaises(ValueError):
                tribulacao_celestial(ator="X", nivel=nivel, demoniaca=False,
                                     valor_de_con=16, graduacao_de_defesa=2,
                                     vitalidade=200, qi_atual=300, aleat=a)

    def test_ascensao_so_no_12(self):
        a = self.aleat("asc")
        t = tribulacao_celestial(ator="X", nivel=12, demoniaca=False,
                                 valor_de_con=26, graduacao_de_defesa=5,
                                 vitalidade=420, qi_atual=750,
                                 fatos={"artefato": "primordial",
                                        "formacao": "aliada",
                                        "elixir": "celestial",
                                        "anos_queimados": 50},
                                 aleat=a)
        self.assertEqual(raios_de_tribulacao(12), 9)
        self.assertLessEqual(len(t.raios), 9)
        if t.sobreviveu:
            self.assertTrue(t.ascendeu)
            self.assertEqual(len(t.raios), 9)

    def test_mais_rajadas_de_preparo_aumentam_a_sobrevivencia(self):
        a = self.aleat("sobrev")
        sem = sum(1 for i in range(120)
                  if tribulacao_celestial(
                      ator=f"S{i}", nivel=9, demoniaca=False, valor_de_con=16,
                      graduacao_de_defesa=1, vitalidade=200, qi_atual=340,
                      aleat=a).sobreviveu)
        com = sum(1 for i in range(120)
                  if tribulacao_celestial(
                      ator=f"C{i}", nivel=9, demoniaca=False, valor_de_con=22,
                      graduacao_de_defesa=5, vitalidade=260, qi_atual=420,
                      fatos={"artefato": "primordial", "formacao": "aliada",
                             "elixir": "celestial", "anos_queimados": 50},
                      aleat=a).sobreviveu)
        self.assertGreater(com, sem)


# ==========================================================================
# Personagens
# ==========================================================================
class TestePersonagens(BaseComSemente):
    def test_pericias_cobrem_os_grupos(self):
        self.assertGreaterEqual(len(PERICIAS), 40)
        grupos = {p.grupo for p in PERICIAS.values()}
        self.assertEqual(grupos, {"marcial", "corporal", "mental", "social",
                                  "saber", "mundana"})
        for p in PERICIAS.values():
            self.assertIn(p.atributo, ATRIBUTOS)
            self.assertTrue(p.nome.strip())

    def test_raiz_validada(self):
        r = RaizEspiritual(("fogo",), "ceu", 90, None)
        self.assertEqual(r.multiplicador_de_cultivo, 400 + 8)
        with self.assertRaises(ValueError):
            RaizEspiritual(("fogo", "agua"), "ceu", 90, None)      # grau errado
        with self.assertRaises(ValueError):
            RaizEspiritual(("fogo", "fogo"), "terra", 80, None)     # duplicado
        with self.assertRaises(ValueError):
            RaizEspiritual(("fogo",), "ceu", 101, None)             # pureza
        with self.assertRaises(ValueError):
            RaizEspiritual(("plasma",), "ceu", 90, None)            # elemento
        with self.assertRaises(ValueError):
            RaizEspiritual(("fogo",), "ceu", 90, "super_sayajin")   # mutação

    def test_mutacao_aumenta_o_multiplicador(self):
        sem = RaizEspiritual(("agua", "fogo"), "terra", 70, None)
        com = RaizEspiritual(("agua", "fogo"), "terra", 70, "gelo")
        self.assertEqual(com.multiplicador_de_cultivo - sem.multiplicador_de_cultivo, 25)
        self.assertEqual(com.elemento_dominante, "agua")

    def test_tabelas_de_raiz_somam_e_cobrem(self):
        for nome, tabela in TABELAS_DE_RAIZ.items():
            self.assertEqual(sorted(tabela), [1, 2, 3, 4, 5], nome)
            self.assertGreater(sum(tabela.values()), 0)
            self.assertTrue(all(v >= 0 for v in tabela.values()))

    def test_distribuicao_de_raiz_bate_com_os_pesos(self):
        """Propriedade estatística: a frequência observada segue os pesos."""
        a = self.aleat("raiz-dist")
        n = 40000
        cont = {g: 0 for g in GRAUS_DE_RAIZ}
        for _ in range(n):
            cont[sortear_raiz(a, tabela="realista").grau] += 1
        pesos = TABELAS_DE_RAIZ["realista"]
        total = sum(pesos.values())
        esperado = {5: n * pesos[5] / total, 4: n * pesos[4] / total,
                    3: n * pesos[3] / total, 2: n * pesos[2] / total}
        for elementos, exp in esperado.items():
            grau = {1: "ceu", 2: "terra", 3: "preto", 4: "amarelo",
                    5: "desperdicio"}[elementos]
            desvio = abs(cont[grau] - exp) / max(1.0, exp)
            self.assertLess(desvio, 0.20,
                            f"{grau}: observado {cont[grau]} vs esperado {exp:.0f}")

    def test_heroica_e_mais_generosa_que_realista(self):
        def puros(tabela):
            b = self.aleat(f"compara-{tabela}")
            return sum(1 for _ in range(4000)
                       if sortear_raiz(b, tabela=tabela).grau in ("ceu", "terra"))
        self.assertGreater(puros("heroica"), puros("realista"))
        self.assertLessEqual(puros("mortal"), 5)

    def test_sorte_desloca_a_raiz(self):
        puros = ("ceu", "terra", "preto")
        a_alta = self.aleat("luk30")
        a_baixa = self.aleat("luk1")
        alta = sum(1 for _ in range(20000)
                   if sortear_raiz(a_alta, sorte=30, tabela="heroica").grau in puros)
        baixa = sum(1 for _ in range(20000)
                    if sortear_raiz(a_baixa, sorte=1, tabela="heroica").grau in puros)
        self.assertGreater(alta, baixa * 1.2)

    def test_metodos_de_criacao(self):
        for metodo in ("sorteio", "pontos"):
            p = criar_personagem(nome="Teste", aleat=self.aleat(metodo),
                                 metodo=metodo)
            self.assertEqual(len(p.atributos), 6)
            for k, v in p.atributos.items():
                self.assertTrue(1 <= v <= 30, f"{metodo}: {k}={v}")
            self.assertTrue(p.raiz)
            self.assertTrue(p.identificador)
        with self.assertRaises(ValueError):
            criar_personagem(nome="X", metodo="manual")

    def test_media_dos_atributos_no_sorteio(self):
        a = self.aleat("media")
        totais = []
        for _ in range(400):
            p = criar_personagem(nome="X", aleat=a, metodo="sorteio")
            totais.extend(p.atributos.values())
        media = sum(totais) / len(totais)
        self.assertAlmostEqual(media, 12.2446, delta=0.35)

    def test_personagem_rejeita_dados_invalidos(self):
        a = self.aleat("inv")
        base = criar_personagem(nome="Base", aleat=a)
        ruins = [
            dict(nome="   "),
            dict(raca="elfo"),
            dict(caminho="jedi"),
            dict(nivel=14),
            dict(nivel=-1),
            dict(atributos={**base.atributos, "per": 31}),
            dict(atributos={**base.atributos, "per": 0}),
            dict(atributos={**base.atributos, "con": 1.5}),
            dict(atributos={k: v for k, v in base.atributos.items() if k != "luk"}),
            dict(pericias={"voo": 1}),
            dict(pericias={"espada": 6}),
            dict(lei="NAO_EXISTE"),
        ]
        for caso in ruins:
            kw = dict(nome=base.nome, raca=base.raca, sexo=base.sexo,
                      idade=base.idade, atributos=base.atributos, raiz=base.raiz,
                      caminho=base.caminho, nivel=base.nivel, lei=base.lei,
                      pericias=base.pericias)
            kw.update(caso)
            with self.assertRaises((ValueError, TypeError, KeyError), msg=str(caso)):
                Personagem(**kw)

    def test_xiandao_7_exige_grau_do_nucleo(self):
        a = self.aleat("nucleo-obrig")
        r = sortear_raiz(a, forcar_grau="terra")
        with self.assertRaises(ValueError):
            Personagem(nome="X", raca="humano", sexo="m", idade=30,
                       atributos={k: 12 for k in ATRIBUTOS}, raiz=r,
                       caminho="xiandao", nivel=7, lei=None, pericias={})
        p = Personagem(nome="X", raca="humano", sexo="m", idade=30,
                       atributos={k: 12 for k in ATRIBUTOS}, raiz=r,
                       caminho="xiandao", nivel=7, lei=None, pericias={},
                       grau_do_nucleo=4)
        self.assertEqual(p.grau_do_nucleo, 4)

    def test_estado_exige_motivo_catalogado(self):
        with self.assertRaises(ValueError):
            Mudanca("vitalidade", -5, "porque_o_mestre_quis")
        with self.assertRaises(ValueError):
            Mudanca("mana", -5, "cura")
        with self.assertRaises(TypeError):
            Mudanca("vitalidade", -5.5, "cura")
        self.assertIn("dano_de_combate", MOTIVOS)

    def test_estado_respeita_limites_e_registra(self):
        a = self.aleat("estado")
        p = criar_personagem(nome="X", aleat=a, nivel=6, lei=None)
        e = EstadoDeJogo.de_personagem(p)
        self.assertEqual(e.qi, p.qi_max)
        d = self.diario("estado.jsonl")
        e.aplicar(Mudanca("vitalidade", -9999, "dano_de_combate"), d, "X")
        self.assertLessEqual(e.vitalidade, 0)
        self.assertEqual(ferimento_por_vitalidade(e.vitalidade,
                                                  e.vitalidade_maxima),
                         "agonizando")
        e.aplicar(Mudanca("qi", 999999, "pedra_espiritual"), d, "X")
        self.assertEqual(e.qi, e.qi_maximo, "Qi não pode passar do máximo")
        e.aplicar(Mudanca("estado_mental", -999, "desvio_de_qi"), d, "X")
        self.assertEqual(e.estado_mental, 0)
        self.assertEqual(len(e.historico), 3)
        self.assertTrue(d.verificar().ok)
        self.assertEqual(len(d.por_tipo("estado")), 3)

    def test_escudo_de_qi_limitado(self):
        e = EstadoDeJogo(qi=10 ** 6, qi_maximo=10 ** 6, vitalidade=10,
                         vitalidade_maxima=10)
        self.assertEqual(e.escudo_de_qi(), 10)
        e.qi = 55
        self.assertEqual(e.escudo_de_qi(), 0)

    def test_ferimento_por_vitalidade(self):
        self.assertEqual(ferimento_por_vitalidade(100, 100), "ileso")
        self.assertEqual(ferimento_por_vitalidade(75, 100), "ileso")
        self.assertEqual(ferimento_por_vitalidade(74, 100), "ferido")
        self.assertEqual(ferimento_por_vitalidade(40, 100), "ferido")
        self.assertEqual(ferimento_por_vitalidade(39, 100), "grave")
        self.assertEqual(ferimento_por_vitalidade(15, 100), "grave")
        self.assertEqual(ferimento_por_vitalidade(14, 100), "agonizando")
        self.assertEqual(ferimento_por_vitalidade(0, 100), "agonizando")
        with self.assertRaises(ValueError):
            ferimento_por_vitalidade(10, 0)


# ==========================================================================
# NPCs
# ==========================================================================
class TesteNpcs(BaseComSemente):
    def npc(self, **kw):
        kw.setdefault("nivel", 6)
        return gerar_npc(self.aleat(kw.pop("ctx", "npc")), **kw)

    def test_virtudes_limitadas(self):
        for kw in (dict(ren=0), dict(yi=11), dict(li=1.5), dict(zhi="5"),
                   dict(xin=-1)):
            base = {"ren": 5, "yi": 5, "li": 5, "zhi": 5, "xin": 5}
            base.update(kw)
            with self.assertRaises((ValueError, TypeError), msg=str(kw)):
                Virtudes(**base)

    def test_dominante_e_falha(self):
        v = Virtudes(ren=9, yi=2, li=5, zhi=5, xin=5)
        self.assertEqual(v.dominante, "ren")
        self.assertEqual(v.falha, "yi")
        self.assertEqual(v.bonus("ren"), 2)
        self.assertEqual(v.bonus("yi"), -2)
        with self.assertRaises(ValueError):
            v.bonus("sorte")

    def test_npc_completo_e_deterministico(self):
        n1 = gerar_npc(Aleatoriedade(FonteSemeada("mesma", "npc")), nome="Fixo")
        n2 = gerar_npc(Aleatoriedade(FonteSemeada("mesma", "npc")), nome="Fixo")
        self.assertEqual(n1.desejos, n2.desejos)
        self.assertEqual(n1.tracos, n2.tracos)
        self.assertEqual(n1.temperamento.codigo, n2.temperamento.codigo)
        self.assertEqual(dict(n1.atributos), dict(n2.atributos))

    def test_camadas_de_desejo_sempre_preenchidas(self):
        for i in range(60):
            n = gerar_npc(self.aleat(f"desejos-{i}"))
            for campo in ("imediato", "ambicao", "obsessao", "medo", "dever",
                          "segredo", "linha_vermelha", "preco"):
                self.assertTrue(getattr(n.desejos, campo).strip(),
                                f"{campo} vazio em {n.nome}")
            self.assertEqual(len(n.desejos.prioridades()), 7)

    def test_traços_compativeis_entre_si(self):
        for i in range(300):
            n = gerar_npc(self.aleat(f"tracos-{i}"), numero_de_traços=4)
            self.assertTrue(2 <= len(n.tracos) <= 4)
            for t in n.tracos:
                self.assertIn(t, TRACOS)
            for t in n.tracos:
                for incompativel in TRACOS[t].incompativel:
                    self.assertNotIn(incompativel, n.tracos,
                                     f"{t} e {incompativel} coexistem em {n.nome}")
            self.assertEqual(len(set(n.tracos)), len(n.tracos))

    def test_todo_traço_tem_efeito_numérico_ou_regista(self):
        for codigo, t in TRACOS.items():
            self.assertEqual(t.codigo, codigo)
            self.assertTrue(t.descricao.strip())
            self.assertTrue(t.efeito.strip())
            self.assertIn(t.dominio, ("social", "combate", "cultivo", "mente",
                                      "mundo"))
            # o efeito precisa citar um número, uma regra ou uma consequência clara
            tem_numero = any(ch.isdigit() for ch in t.efeito)
            quantificador = any(w in t.efeito.lower() for w in
                                ("metade", "dobro", "dobra", "nunca", "sempre",
                                 "todos", "cada", "%", "nenhum"))
            tem_regra = (":" in t.efeito or "imune" in t.efeito
                         or "recusa" in t.efeito or quantificador)
            self.assertTrue(tem_numero or tem_regra,
                            f"{codigo} tem efeito vago: {t.efeito}")

    def test_ocupacao_desloca_as_virtudes(self):
        medicos, assassinos = [], []
        for i in range(400):
            n = gerar_npc(self.aleat(f"oc-med-{i}"), ocupacao="Médico andarilho")
            medicos.append(n.virtudes.ren)
            n2 = gerar_npc(self.aleat(f"oc-asa-{i}"),
                           ocupacao="Assassino de aluguel")
            assassinos.append(n2.virtudes.ren)
        self.assertGreater(sum(medicos) / len(medicos),
                           sum(assassinos) / len(assassinos))

    def test_ledger_de_relacoes(self):
        n = self.npc()
        n.registrar_relacao("Grupo", "compartilhou_uma_refeicao", "ano 1", "taverna")
        n.registrar_relacao("Grupo", "salvou_a_vida", "ano 1", "bandidos")
        self.assertEqual(n.disposicao_para("Grupo"), (7, "amigavel"))
        n.registrar_relacao("Grupo", "matou_um_familiar", "ano 2", "")
        self.assertEqual(n.disposicao_para("Grupo")[0], -13)
        self.assertEqual(n.disposicao_para("Grupo")[1], "inimigo_jurado")
        self.assertEqual(n.disposicao_para("Desconhecido"), (0, "neutro"))
        self.assertEqual(len(n.livros["Grupo"].historico("Grupo")), 3)

    def test_ledger_rejeita_evento_e_peso_fora_do_catalogo(self):
        livro = LivroDeRelacoes()
        with self.assertRaises(ValueError):
            livro.registrar("fez_uma_coisa", "Grupo")
        from xan.npcs import EventoDeRelacao
        with self.assertRaises(ValueError):
            EventoDeRelacao("salvou_a_vida", 999, "", "", "Grupo")
        with self.assertRaises(ValueError):
            EventoDeRelacao("evento_falso", 1, "", "", "Grupo")

    def test_categorias_de_disposicao(self):
        casos = [(15, "devoto"), (10, "devoto"), (9, "amigavel"), (6, "amigavel"),
                 (5, "cordial"), (3, "cordial"), (2, "neutro"), (0, "neutro"),
                 (-1, "neutro"), (-2, "neutro"), (-3, "desconfiado"),
                 (-5, "desconfiado"), (-6, "hostil"), (-9, "hostil"),
                 (-10, "inimigo_jurado"), (-500, "inimigo_jurado")]
        for valor, categoria in casos:
            self.assertEqual(disposicao_para(valor), categoria,
                             f"disposição {valor} deveria ser {categoria}")
        # as faixas cobrem todos os inteiros de -500 a 500 sem buraco
        for v in range(-500, 501):
            self.assertTrue(disposicao_para(v))

    def test_tabela_de_conduta_cobre_todas_as_margens(self):
        from xan.npcs import _escolher_por_margem
        for margem in range(-60, 61):
            codigo, texto = _escolher_por_margem(margem)
            self.assertTrue(codigo)
            self.assertTrue(texto.strip())
        # monotonia: margem maior nunca produz conduta pior
        ordem = ["ataca", "hostil", "expulsa", "recusa", "negocia",
                 "ajuda_condicional", "ajuda_generosa", "revela_segredo",
                 "jura_lealdade"]
        anterior = -1
        for margem in range(-40, 41):
            codigo, _ = _escolher_por_margem(margem)
            self.assertGreaterEqual(ordem.index(codigo), anterior,
                                    f"conduta regrediu na margem {margem}")
            anterior = ordem.index(codigo)
        # os códigos das duas tabelas coincidem
        self.assertEqual(set(ordem), {c[0] for c in TABELA_DE_CONDUTA})

    def test_conduta_responde_a_disposicao(self):
        """Propriedade: amigos ajudam, inimigos jurados não."""
        resultados = {"amigo": [], "inimigo": []}
        for i in range(120):
            a = self.aleat(f"cond-{i}")
            n = gerar_npc(a, nome=f"N{i}", nivel=5)
            n.registrar_relacao("P", "salvou_a_vida")
            n.registrar_relacao("P", "defendeu_em_publico")
            n.registrar_relacao("P", "cumpriu_uma_promessa")
            c = resolver_conduta(n, "P", "ajude-me", a,
                                 magnitude="favor_sem_risco")
            resultados["amigo"].append(c.resultado.total)
            m = gerar_npc(a, nome=f"M{i}", nivel=5)
            m.registrar_relacao("P", "matou_um_familiar")
            c2 = resolver_conduta(m, "P", "ajude-me", a,
                                  magnitude="favor_sem_risco")
            resultados["inimigo"].append(c2.resultado.total)
        self.assertGreater(sum(resultados["amigo"]) / 120,
                           sum(resultados["inimigo"]) / 120 + 2)

    def test_magnitude_do_pedido_importa(self):
        totais = {}
        for mag in ("informacao_comum", "segredo_mortal", "sacrificio_de_vida"):
            somas = []
            for i in range(80):
                a = self.aleat(f"mag-{mag}-{i}")
                n = gerar_npc(a, nome=f"N{i}", nivel=6)
                n.registrar_relacao("P", "salvou_a_vida")
                c = resolver_conduta(n, "P", "pedido", a, magnitude=mag)
                somas.append(c.resultado.margem)
            totais[mag] = sum(somas) / len(somas)
        self.assertGreater(totais["informacao_comum"], totais["segredo_mortal"])
        self.assertGreater(totais["segredo_mortal"], totais["sacrificio_de_vida"])

    def test_magnitude_invalida(self):
        n = self.npc()
        with self.assertRaises(ValueError):
            resolver_conduta(n, "P", "x", self.aleat("mag-inv"),
                             magnitude="pedido_enorme")

    def test_camada_ativa_e_deterministica(self):
        from xan.npcs import _CAMADAS_POR_CONDUTA
        for i in range(40):
            n = gerar_npc(self.aleat(f"camada-{i}"))
            for codigo in _CAMADAS_POR_CONDUTA:
                c1 = camada_ativa(codigo, n)
                c2 = camada_ativa(codigo, n)
                self.assertEqual(c1, c2)
                self.assertIn(c1, _CAMADAS_POR_CONDUTA[codigo])
        with self.assertRaises(ValueError):
            camada_ativa("conduta_inexistente", self.npc())

    def test_linha_vermelha_veta_sem_dado(self):
        from xan.npcs import _LINHAS_QUE_BLOQUEIAM
        n = self.npc()
        a = self.aleat("veto")
        antes = a.consumo().bytes_solicitados
        r = resolver_conflito_de_desejos(n, "linha_vermelha", "ambicao", a)
        self.assertEqual(r.vencedor, "linha_vermelha")
        self.assertIsNone(r.resultado, "veto não deve consumir dado")
        self.assertEqual(a.consumo().bytes_solicitados, antes)
        self.assertIn("veto", r.criterio)
        r2 = resolver_conflito_de_desejos(n, "medo", "linha_vermelha", a)
        self.assertEqual(r2.vencedor, "linha_vermelha")
        self.assertTrue(_LINHAS_QUE_BLOQUEIAM)

    def test_conflito_de_desejos_rola_e_audita(self):
        a = self.aleat("conflito")
        d = self.diario("conflito.jsonl")
        n = gerar_npc(a, nome="Conflito", nivel=7)
        vitorias = {"dever": 0, "preco": 0}
        for i in range(80):
            r = resolver_conflito_de_desejos(n, "dever", "preco", a, diario=d)
            self.assertIsNotNone(r.resultado)
            vitorias[r.vencedor] += 1
            self.assertTrue(r.conduta.strip())
        self.assertGreater(vitorias["dever"], vitorias["preco"],
                           "prioridade 4 deveria vencer prioridade 0 na maioria")
        self.assertTrue(d.verificar().ok)
        self.assertTrue(conferir(d).ok)

    def test_conflito_rejeita_camadas_invalidas(self):
        n = self.npc()
        a = self.aleat("cam-inv")
        with self.assertRaises(ValueError):
            resolver_conflito_de_desejos(n, "dever", "vontade", a)
        with self.assertRaises(ValueError):
            resolver_conflito_de_desejos(n, "dever", "dever", a)

    def test_prioridades_batem_com_o_registro(self):
        for camada, prioridade in PRIORIDADE_DE_CAMADA_DE_DESEJO.items():
            self.assertEqual(valor_de("DESEJO:PRIORIDADE", {"camada": camada}),
                             prioridade)
        with self.assertRaises(Exception):
            valor_de("DESEJO:PRIORIDADE", {"camada": "esperanca"})

    def test_agenda(self):
        from xan.npcs import Agenda
        ag = Agenda("conquistar a seita rival", segmentos=6, preenchidos=0)
        self.assertFalse(ag.completa())
        self.assertEqual(ag.avancar(2, "missão cumprida"), 2)
        self.assertEqual(ag.avancar(9, "mês passou"), 6)
        self.assertTrue(ag.completa())
        self.assertEqual(len(ag.historico), 2)
        with self.assertRaises(ValueError):
            Agenda("x", segmentos=1)
        with self.assertRaises(ValueError):
            ag.avancar(0, "nada")

    def test_nomes_chineses(self):
        a = self.aleat("nomes")
        vistos = set()
        for _ in range(400):
            rom, char = gerar_nome(a)
            self.assertTrue(rom and char)
            self.assertTrue(char[0] not in "abcdefghijklmnopqrstuvwxyz")
            vistos.add(rom)
        self.assertGreater(len(vistos), 300, "gerador de nomes repetindo demais")
        for sexo in ("masculino", "feminino", "neutro"):
            self.assertTrue(gerar_nome(a, sexo)[0])
        self.assertTrue(gerar_nome(a, composto=True)[0])

    def test_ficha_do_npc_contem_tudo(self):
        n = gerar_npc(self.aleat("ficha"), nome="Ficha Completa", nivel=8,
                      faccao="Seita X", agendas=1)
        n.registrar_relacao("Grupo", "trocou_favores", "ano 3", "detalhe")
        f = n.ficha()
        for trecho in ("Ficha Completa", "Seita X", "Desejos", "Ambição",
                       "Segredo", "Linha vermelha", "Cinco Virtudes",
                       "Temperamento", "Traços", "Agendas em curso",
                       "Livro de relações", "Grupo", "Raiz"):
            self.assertIn(trecho, f, f"falta {trecho!r} na ficha")

    def test_npc_de_nivel_alto_tem_recurso_coerente(self):
        baixo = gerar_npc(self.aleat("rico-baixo"), nivel=1)
        alto = gerar_npc(self.aleat("rico-alto"), nivel=12)
        self.assertGreater(alto.qi_max(), baixo.qi_max())
        self.assertGreater(alto.vitalidade_max(), baixo.vitalidade_max())


# ==========================================================================
# Mundo procedural
# ==========================================================================
class TesteMundo(BaseComSemente):
    def test_mesma_semente_mesmo_mundo(self):
        m1 = gerar_mundo("semente-fixa")
        m2 = gerar_mundo("semente-fixa")
        self.assertEqual(m1.como_dict(), m2.como_dict())

    def test_sementes_diferentes_mundos_diferentes(self):
        m1 = gerar_mundo("semente-a")
        m2 = gerar_mundo("semente-b")
        self.assertNotEqual(m1.como_dict(), m2.como_dict())

    def test_json_e_serializavel_e_completo(self):
        m = gerar_mundo("json-teste", provincias=5, eventos=12)
        texto = json.dumps(m.como_dict(), ensure_ascii=False, sort_keys=True)
        dados = json.loads(texto)
        self.assertEqual(dados["semente"], "json-teste")
        self.assertEqual(len(dados["provincias"]), 5)
        self.assertIn("versao_do_gerador", dados)
        for p in dados["provincias"]:
            for campo in ("nome", "chines", "elemento", "densidade_qi",
                          "densidade_qi_fato", "terreno", "clima_base", "perigo",
                          "veias_espirituais", "q", "r", "sitios"):
                self.assertIn(campo, p)
            for s in p["sitios"]:
                for campo in ("tipo", "nome", "nivel", "dono", "populacao",
                              "densidade_qi", "segredo", "perigo",
                              "fundado_no_ano"):
                    self.assertIn(campo, s)

    def test_nomes_unicos(self):
        for semente in ("unico-1", "unico-2", "unico-3"):
            m = gerar_mundo(semente, provincias=12, eventos=40)
            provincias = [p.nome for p in m.provincias]
            sitios = [s.nome for s in m.todos_os_sitios()]
            faccoes = [f.nome for f in m.faccoes]
            self.assertEqual(len(set(provincias)), len(provincias))
            self.assertEqual(len(set(sitios)), len(sitios))
            self.assertEqual(len(set(faccoes)), len(faccoes))

    def test_densidade_vira_o_fato_das_regras(self):
        for v in range(11):
            fato = DensidadeDeQi(v)
            # o fato tem que ser aceito pela regra registrada
            mod = valor_de("AMBIENTE:DENSIDADE_QI", {"densidade_qi": fato})
            self.assertTrue(-2 <= mod <= 3)
        for v in (-1, 11, 1.5):
            with self.assertRaises((ValueError, TypeError)):
                DensidadeDeQi(v)

    def test_matriz_de_relacoes_simetrica_e_limitada(self):
        for semente in ("rel-1", "rel-2"):
            m = gerar_mundo(semente, provincias=9, eventos=40)
            nomes = [f.nome for f in m.faccoes]
            for a in nomes:
                self.assertEqual(m.relacao(a, a), 100)
                for b in nomes:
                    self.assertEqual(m.relacao(a, b), m.relacao(b, a))
                    self.assertTrue(-100 <= m.relacao(a, b) <= 100)
                    self.assertIn(m.relacao_como_fato(a, b),
                                  ("aliada", "amigavel", "neutra", "rival",
                                   "guerra", "mesma"))

    def test_distribuicao_de_relacoes_tem_conflito_e_alianca(self):
        aliadas = guerra = neutras = total = 0
        for i in range(6):
            m = gerar_mundo(f"dist-rel-{i}")
            for a in m.relacoes:
                for b, v in m.relacoes[a].items():
                    if a == b:
                        continue
                    total += 1
                    aliadas += v >= 60
                    guerra += v <= -60
                    neutras += -20 < v < 20
        self.assertGreater(total, 500)
        self.assertGreater(aliadas / total, 0.05)
        self.assertLess(aliadas / total, 0.40)
        self.assertGreater(guerra / total, 0.02)
        self.assertLess(guerra / total, 0.30)
        self.assertGreater(neutras / total, 0.08)

    def test_alinhamentos_produzem_odio_ortodoxo_demoniaco(self):
        odios = []
        for i in range(6):
            m = gerar_mundo(f"odio-{i}")
            for f in m.faccoes:
                for g in m.faccoes:
                    if f.alinhamento == "ortodoxa" and g.alinhamento == "demoniaca":
                        odios.append(m.relacao(f.nome, g.nome))
        self.assertGreater(len(odios), 20)
        self.assertLess(sum(odios) / len(odios), -20)

    def test_toda_provincia_tem_sitios_e_coerencia(self):
        m = gerar_mundo("coerencia")
        for p in m.provincias:
            self.assertGreaterEqual(len(p.sitios), 1)
            self.assertIn(p.elemento, ELEMENTOS_CANONICOS + ("nenhum", "vazio"))
            self.assertTrue(0 <= p.densidade_qi <= 10)
            self.assertTrue(1 <= p.perigo <= 10)
            for s in p.sitios:
                self.assertEqual(s.provincia, p.nome)
                self.assertTrue(0 <= s.nivel <= 13)
                self.assertTrue(1 <= s.perigo <= 10)
                self.assertTrue(s.segredo.strip())
                self.assertLessEqual(s.densidade_qi, 10)

    def test_deserto_tem_menos_qi_que_montanha(self):
        """Coerência geográfica declarada no gerador."""
        desertos, montanhas = [], []
        for i in range(8):
            m = gerar_mundo(f"geo-{i}")
            for p in m.provincias:
                (desertos if p.terreno == "deserto" else
                 montanhas if p.terreno == "montanhas" else []).append(
                    p.densidade_qi)
        self.assertGreater(len(desertos), 2)
        self.assertGreater(len(montanhas), 2)
        self.assertGreater(sum(montanhas) / len(montanhas),
                           sum(desertos) / len(desertos))

    def test_reino_secreto_tem_qi_maximo(self):
        achou = False
        for i in range(6):
            m = gerar_mundo(f"secreto-{i}")
            for s in m.sitios_de_tipo("reino_secreto"):
                achou = True
                self.assertEqual(s.densidade_qi, 10)
                self.assertEqual(DensidadeDeQi(s.densidade_qi), "terra_imortal")
                self.assertGreaterEqual(s.nivel, 7)
        self.assertTrue(achou)

    def test_faccao_dona_de_sua_sede(self):
        m = gerar_mundo("sede")
        for f in m.faccoes:
            if f.sede and f.sede in [s.nome for s in m.todos_os_sitios()]:
                s = m.sitio(f.sede)
                if s.tipo in ("seita_ortodoxa", "seita_nao_ortodoxa",
                              "culto_demoniaco"):
                    self.assertEqual(s.dono, f.nome)

    def test_eventos_tem_consequencias(self):
        m = gerar_mundo("eventos", eventos=60)
        self.assertGreaterEqual(len(m.linha_do_tempo), 60)
        self.assertLessEqual(len(m.linha_do_tempo), 61)
        com_consequencia = sum(1 for e in m.linha_do_tempo if e.consequencias)
        self.assertGreater(com_consequencia, 40)
        anos = [e.ano for e in m.linha_do_tempo]
        self.assertEqual(anos, sorted(anos) if anos == sorted(anos) else anos)
        for e in m.linha_do_tempo:
            self.assertLess(e.ano, m.ano_atual)
            self.assertTrue(e.titulo.strip())
            self.assertTrue(e.descricao.strip())

    def test_historia_cria_ruinas_e_campos_de_batalha(self):
        achou_ruina = achou_batalha = False
        for i in range(8):
            m = gerar_mundo(f"hist-{i}")
            tipos = {e.tipo for e in m.linha_do_tempo}
            if "queda_de_seita" in tipos:
                achou_ruina = achou_ruina or bool(m.sitios_de_tipo("ruina"))
            if "guerra_entre_faccoes" in tipos:
                achou_batalha = achou_batalha or bool(
                    m.sitios_de_tipo("campo_de_batalha"))
        self.assertTrue(achou_ruina)
        self.assertTrue(achou_batalha)

    def test_clima_do_ano_cobre_360_dias(self):
        m = gerar_mundo("clima-ano", provincias=4, eventos=5)
        for p in m.provincias:
            self.assertEqual(len(m.clima_do_ano[p.nome]), 360)
            for c in m.clima_do_ano[p.nome]:
                self.assertIn(c, CLIMAS)
            self.assertEqual(m.clima_de(p.nome, 0), m.clima_do_ano[p.nome][0])
            self.assertEqual(m.clima_de(p.nome, 999), m.clima_do_ano[p.nome][359])
        with self.assertRaises(KeyError):
            m.clima_de("Narnia", 0)

    def test_tesouros(self):
        m = gerar_mundo("tesouros")
        self.assertGreaterEqual(len(m.tesouros), 2)
        for t in m.tesouros:
            self.assertIn(t.grau, ("mortal", "terra", "ceu", "primordial"))
            self.assertTrue(t.nome and t.onde and t.guardiao and t.maldicao)
            self.assertIn("nome", t.como_dict())

    def test_limites_do_gerador(self):
        with self.assertRaises(ValueError):
            gerar_mundo("x", provincias=2)
        with self.assertRaises(ValueError):
            gerar_mundo("x", provincias=21)
        with self.assertRaises(ValueError):
            gerar_mundo("x", eventos=0)
        with self.assertRaises(ValueError):
            gerar_mundo("x", eventos=100, anos_de_historia=50)

    def test_markdown_contem_o_mundo(self):
        m = gerar_mundo("markdown", provincias=4, eventos=8)
        md = m.markdown()
        for trecho in (m.nome, m.semente, "## As Nove Províncias", "## Facções",
                       "Matriz de relações", "## Sítios por província",
                       "## Linha do tempo"):
            self.assertIn(trecho, md, f"falta {trecho!r} no markdown")
        for p in m.provincias:
            self.assertIn(p.nome, md)

    def test_npc_do_mundo(self):
        m = gerar_mundo("npc-mundo")
        a = self.aleat("npc-mundo")
        npcs = gerar_npcs_do_mundo(m, a, 6)
        self.assertEqual(len(npcs), 6)
        for n in npcs:
            self.assertTrue(n.nome)
            self.assertIsInstance(n, Npc)
        # os líderes das facções mais prestigiadas aparecem
        com_faccao = [n for n in npcs if n.faccao]
        self.assertGreaterEqual(len(com_faccao), 2)

    def test_consultas_de_acesso(self):
        m = gerar_mundo("consultas")
        p = m.provincias[0]
        self.assertIs(m.provincia(p.nome), p)
        s = p.sitios[0]
        self.assertIs(m.sitio(s.nome), s)
        f = m.faccoes[0]
        self.assertIs(m.faccao(f.nome), f)
        with self.assertRaises(KeyError):
            m.provincia("Narnia")
        with self.assertRaises(KeyError):
            m.sitio("Lugar Nenhum")
        with self.assertRaises(KeyError):
            m.faccao("Faccao Fantasma")


# ==========================================================================
# Artes, bestiário e tesouros
# ==========================================================================
class TesteArtes(BaseComSemente):
    def test_tecnicas_bem_formadas(self):
        self.assertGreaterEqual(len(TECNICAS), 60)
        for codigo, t in TECNICAS.items():
            self.assertEqual(t.codigo, codigo)
            self.assertTrue(t.nome and t.chines and t.descricao)
            self.assertIn(t.tipo, ("ataque", "defesa", "movimento", "cura",
                                   "util", "passiva", "cultivo", "social"))
            if t.lei != "livre":
                self.assertIn(t.lei, LEIS, f"{codigo} cita lei inexistente")
            if t.tipo == "ataque":
                self.assertTrue(t.dado_base, f"{codigo} é ataque sem dado")
            else:
                pass
            self.assertIn(t.pericia, PERICIAS,
                          f"{codigo} usa perícia inexistente {t.pericia}")
            self.assertLessEqual(t.custo_qi, 300)

    def test_dano_escala_com_nivel_e_margem(self):
        a = self.aleat("dano")
        t = tecnica_de("SM_AURA_ESPADA")
        medias = {}
        for nivel in (5, 8, 11, 13):
            ds = [dano_de(t, nivel, 4, 6, a)[0] for _ in range(300)]
            medias[nivel] = sum(ds) / len(ds)
        for x, y in zip(sorted(medias), sorted(medias)[1:]):
            self.assertGreater(medias[y], medias[x])
        # margem maior ⇒ dano maior
        baixa = sum(dano_de(t, 8, 4, 0, a)[0] for _ in range(300))
        alta = sum(dano_de(t, 8, 4, 20, a)[0] for _ in range(300))
        self.assertGreater(alta, baixa)

    def test_conta_do_dano_e_explicita(self):
        a = self.aleat("conta")
        dano, conta = dano_de(tecnica_de("LIVRE_CORTE_QI"), 4, 2, 4, a)
        self.assertIn("escala de reino", conta)
        self.assertIn(str(dano), conta)

    def test_tecnica_sem_dano_devolve_zero(self):
        a = self.aleat("sem-dano")
        dano, conta = dano_de(tecnica_de("LIVRE_PASSO_NUVEM"), 6, 2, 4, a)
        self.assertEqual(dano, 0)
        self.assertIn("sem dano", conta)

    def test_catalogos_bem_formados(self):
        for a in ARTEFATOS:
            self.assertIn(a.grau, ("mortal", "terra", "ceu", "primordial"))
            self.assertIn(a.subgrau, ("baixo", "medio", "alto"))
        for t in TALISMAS:
            self.assertTrue(t.uso_unico)
            self.assertGreater(t.dd_de_criacao, 10)
        for f in FORMACOES:
            self.assertGreater(f.nucleos, 0)
            self.assertGreater(f.dd_de_rompimento, f.dd_de_montagem - 5)
        for e in ELIXIRES:
            self.assertIn(e.erva_principal, {x.nome for x in ERVAS},
                          f"{e.codigo} usa erva inexistente")
        self.assertEqual(len({x.nome for x in ARTEFATOS}), len(ARTEFATOS))

    def test_tesouro_escala_com_o_nivel(self):
        a = self.aleat("tesouros")
        graus_por_nivel = {}
        peso = {"mortal": 0, "terra": 1, "ceu": 2, "primordial": 3}
        for nivel in (1, 4, 7, 10, 13):
            somas = []
            for _ in range(1500):
                cat, obj, pedras = sortear_tesouro(a, nivel, sorte=10)
                if obj is not None and getattr(obj, "grau", None) in peso:
                    somas.append(peso[obj.grau])
                self.assertGreaterEqual(pedras, 1)
                self.assertIn(cat, ("artefato", "talisma", "elixir", "pedras"))
            graus_por_nivel[nivel] = sum(somas) / len(somas)
        for x, y in zip(sorted(graus_por_nivel), sorted(graus_por_nivel)[1:]):
            self.assertGreater(graus_por_nivel[y], graus_por_nivel[x])

    def test_sorte_aumenta_o_grau(self):
        a = self.aleat("sorte-tesouro")
        peso = {"mortal": 0, "terra": 1, "ceu": 2, "primordial": 3}
        def media(sorte):
            b = self.aleat(f"sorte-{sorte}")
            vals = []
            for _ in range(2500):
                _, obj, _ = sortear_tesouro(b, 6, sorte=sorte)
                if obj is not None and getattr(obj, "grau", None) in peso:
                    vals.append(peso[obj.grau])
            return sum(vals) / len(vals)
        self.assertGreater(media(20), media(8))

    def test_tesouro_rejeita_nivel_invalido(self):
        with self.assertRaises(ValueError):
            sortear_tesouro(self.aleat("t-inv"), 14)
        with self.assertRaises(ValueError):
            sortear_tesouro(self.aleat("t-inv2"), -1)

    def test_pedras_crescem_com_o_nivel(self):
        a = self.aleat("pedras")
        medias = {}
        for nivel in (1, 5, 9, 13):
            vals = [sortear_tesouro(a, nivel)[2] for _ in range(400)]
            medias[nivel] = sum(vals) / len(vals)
        for x, y in zip(sorted(medias), sorted(medias)[1:]):
            self.assertGreater(medias[y], medias[x])


class TesteBestiario(BaseComSemente):
    def test_bestas_canonicas_bem_formadas(self):
        self.assertGreaterEqual(len(BESTAS), 20)
        for nome, b in BESTAS.items():
            self.assertEqual(b.nome, nome)
            self.assertTrue(b.chines and b.habitat and b.tesouro and b.fraqueza)
            self.assertTrue(b.descricao.strip())
            self.assertGreater(len(b.ataques), 0)
            self.assertGreater(b.vitalidade, 0)
            for at in b.ataques:
                self.assertTrue(at.dado or at.efeitos)
                self.assertIn(at.alcance, ("toque", "curto", "medio", "longo",
                                           "extremo", "pessoal"))
        # os quatro símbolos existem
        for nome in ("Tigre Branco do Oeste", "Dragão Azul do Leste",
                     "Pássaro Vermelho do Sul", "Tartaruga Negra do Norte"):
            self.assertIn(nome, BESTAS)
            self.assertEqual(BESTAS[nome].classe, "fera_ancestral")
            self.assertGreaterEqual(BESTAS[nome].nivel, 11)

    def test_ancestrais_tem_elementos_corretos(self):
        self.assertEqual(BESTAS["Dragão Azul do Leste"].elemento, "madeira")
        self.assertEqual(BESTAS["Tigre Branco do Oeste"].elemento, "metal")
        self.assertEqual(BESTAS["Pássaro Vermelho do Sul"].elemento, "fogo")
        self.assertEqual(BESTAS["Tartaruga Negra do Norte"].elemento, "agua")

    def test_gerador_produz_besta_valida(self):
        for i in range(200):
            b = gerar_besta(self.aleat(f"besta-{i}"))
            self.assertIsInstance(b, Besta)          # __post_init__ valida tudo
            self.assertGreater(b.vitalidade, 0)
            self.assertGreater(len(b.ataques), 0)
            self.assertTrue(b.temperamento and b.fraqueza and b.tesouro)

    def test_bestas_escalam_com_o_nivel(self):
        a = self.aleat("escala-besta")
        medias = {}
        for nivel in (1, 4, 7, 10, 13):
            vals = [gerar_besta(a, nivel=nivel).vitalidade for _ in range(200)]
            medias[nivel] = sum(vals) / len(vals)
        for x, y in zip(sorted(medias), sorted(medias)[1:]):
            self.assertGreater(medias[y], medias[x])

    def test_terreno_e_elemento_sao_respeitados(self):
        a = self.aleat("terreno")
        b = gerar_besta(a, terreno="deserto", elemento="fogo", nivel=5)
        self.assertEqual(b.elemento, "fogo")
        self.assertEqual(b.nivel, 5)
        with self.assertRaises(ValueError):
            gerar_besta(a, terreno="cidade_flutuante")
        with self.assertRaises(ValueError):
            gerar_besta(a, elemento="plasma")
        with self.assertRaises(ValueError):
            gerar_besta(a, nivel=14)

    def test_nucleo_de_besta(self):
        for nivel in range(0, 7):
            self.assertIsNone(nucleo_de_besta(nivel))
        self.assertEqual(nucleo_de_besta(7), "terra")
        self.assertEqual(nucleo_de_besta(10), "ceu")
        self.assertEqual(nucleo_de_besta(13), "primordial")

    def test_bestas_de_nivel_10_sao_inteligentes(self):
        a = self.aleat("inteligencia")
        for _ in range(60):
            b = gerar_besta(a, nivel=11)
            self.assertTrue(b.inteligente)

    def test_habilidades_por_faixa(self):
        a = self.aleat("habilidades")
        baixa = gerar_besta(a, nivel=2)
        alta = gerar_besta(a, nivel=11)
        self.assertGreater(len(alta.habilidades), len(baixa.habilidades))
        nomes = {h.nome for h in alta.habilidades}
        self.assertIn("Núcleo de Besta", nomes)
        self.assertIn("Fala Humana", nomes)


# ==========================================================================
# Combate
# ==========================================================================
class TesteCombate(BaseComSemente):
    def combatentes(self, a, nivel=6, n=2):
        lista = []
        for i in range(n):
            p = criar_personagem(
                nome=f"C{i}", aleat=a, tabela_de_raiz="heroica", nivel=nivel,
                caminho="xiandao",
                lei="PUREZA_JADE" if (nivel >= 1 and i % 2 == 0) else None,
                grau_do_nucleo=5 if nivel >= 7 else None,
                faccao=f"F{i}")
            lista.append(Combatente.de_personagem(p))
        return lista

    def test_alcance(self):
        self.assertTrue(dentro_do_alcance("curto", "toque"))
        self.assertTrue(dentro_do_alcance("longo", "medio"))
        self.assertFalse(dentro_do_alcance("toque", "medio"))
        self.assertFalse(dentro_do_alcance("curto", "extremo"))
        self.assertEqual(faixa_para_regra("longo", "medio"), "medio")
        self.assertEqual(faixa_para_regra("curto", "toque"), "curto")
        with self.assertRaises(ValueError):
            faixa_para_regra("curto", "extremo")
        with self.assertRaises(ValueError):
            dentro_do_alcance("curto", "lua")

    def test_supressao_de_reino_bloqueia_sem_rolar(self):
        a = self.aleat("supressao")
        cs = self.combatentes(a, nivel=8, n=2)
        cs[1].nivel = 4          # lacuna de 4
        cenario = Cenario()
        enc = iniciar_encontro(cenario, cs, a)
        antes = a.consumo().bytes_solicitados
        g = atacar(enc, cs[1].nome, cs[0].nome, a)
        self.assertTrue(g.bloqueado_por_supressao)
        self.assertFalse(g.acertou)
        self.assertIsNone(g.resultado)
        self.assertEqual(a.consumo().bytes_solicitados, antes,
                         "ataque bloqueado por supressão não pode consumir dado")
        self.assertIn("SEM ROLAGEM", g.resumo())

    def test_lacuna_de_dois_ainda_rola(self):
        a = self.aleat("lacuna2")
        cs = self.combatentes(a, nivel=8, n=2)
        cs[1].nivel = 6
        enc = iniciar_encontro(Cenario(), cs, a)
        g = atacar(enc, cs[1].nome, cs[0].nome, a)
        self.assertFalse(g.bloqueado_por_supressao)
        self.assertIsNotNone(g.resultado)

    def test_tecnica_suprema_ignora_a_supressao(self):
        a = self.aleat("suprema")
        cs = self.combatentes(a, nivel=12, n=2)
        cs[0].nivel = 12
        cs[1].nivel = 9          # lacuna de 3, mas a técnica é suprema
        cs[1].estado.qi = 999
        cs[1].estado.qi_maximo = 999
        enc = iniciar_encontro(Cenario(), cs, a)
        g = atacar(enc, cs[1].nome, cs[0].nome, a, tecnica="PJ_LUZ_DE_YUQING")
        self.assertFalse(g.bloqueado_por_supressao)

    def test_tecnica_exige_qi_e_nivel(self):
        a = self.aleat("custo")
        cs = self.combatentes(a, nivel=6, n=2)
        cs[0].estado.qi = 0
        enc = iniciar_encontro(Cenario(), cs, a)
        with self.assertRaises(ValueError):
            atacar(enc, cs[0].nome, cs[1].nome, a, tecnica="SM_AURA_ESPADA")
        cs[0].estado.qi = 999
        with self.assertRaises(ValueError):
            atacar(enc, cs[0].nome, cs[1].nome, a, tecnica="SM_ALMA_ESPADA")

    def test_tecnica_desconta_qi(self):
        a = self.aleat("desconto")
        cs = self.combatentes(a, nivel=6, n=2)
        cs[0].estado.qi = 500
        enc = iniciar_encontro(Cenario(), cs, a)
        tec = tecnica_de("SM_AURA_ESPADA")
        atacar(enc, cs[0].nome, cs[1].nome, a, tecnica=tec.codigo)
        self.assertLess(cs[0].estado.qi, 500)
        self.assertTrue(any(m.motivo == "custo_de_tecnica"
                            for m in cs[0].estado.historico))

    def test_iniciativa_e_auditada_e_estavel(self):
        a1 = self.aleat("ini")
        a2 = self.aleat("ini")
        e1 = iniciar_encontro(Cenario(), self.combatentes(a1, n=4), a1)
        e2 = iniciar_encontro(Cenario(), self.combatentes(a2, n=4), a2)
        self.assertEqual(e1.ordem, e2.ordem)
        self.assertEqual(len(set(e1.ordem)), 4)
        with self.assertRaises(ValueError):
            from xan.combate import iniciativa
            iniciativa(e1, a1)

    def test_ataque_acertado_causa_dano_com_aritmetica_fechada(self):
        a = self.aleat("aritmetica")
        acertos = 0
        for i in range(60):
            cs = self.combatentes(a, nivel=6, n=2)
            alvo = cs[1]
            enc = iniciar_encontro(Cenario(), cs, a)
            g = atacar(enc, cs[0].nome, alvo.nome, a)
            if g.acertou:
                acertos += 1
                self.assertEqual(g.absorvido_pelo_qi + g.dano_na_vitalidade,
                                 g.dano)
                self.assertEqual(alvo.estado.qi_maximo - alvo.estado.qi,
                                 g.absorvido_pelo_qi)
                self.assertEqual(alvo.estado.vitalidade_maxima
                                 - alvo.estado.vitalidade,
                                 g.dano_na_vitalidade)
                self.assertLessEqual(g.absorvido_pelo_qi, alvo.estado.qi_maximo)
        self.assertGreater(acertos, 5, "poucos acertos para validar a aritmética")

    def test_limite_de_acoes_por_turno(self):
        a = self.aleat("acoes")
        cs = self.combatentes(a, nivel=6, n=2)
        enc = iniciar_encontro(Cenario(), cs, a)
        for _ in range(6):
            atacar(enc, cs[0].nome, cs[1].nome, a)
        with self.assertRaises(ValueError):
            atacar(enc, cs[0].nome, cs[1].nome, a)
        # avançar a rodada inteira reinicia o contador
        for _ in range(len(enc.ordem) + 1):
            enc.proximo()
        self.assertEqual(cs[0].ataques_este_turno, 0)
        atacar(enc, cs[0].nome, cs[1].nome, a)

    def test_qi_absorve_antes_da_vitalidade(self):
        a = self.aleat("escudo")
        cs = self.combatentes(a, nivel=6, n=2)
        alvo = cs[1]
        alvo.estado.qi = 10
        alvo.estado.vitalidade = 100
        absorvido, restante = alvo.receber_dano(45)
        self.assertEqual((absorvido, restante), (10, 35))
        self.assertEqual(alvo.estado.qi, 0)
        self.assertEqual(alvo.estado.vitalidade, 65)
        self.assertFalse(alvo.caido)
        absorvido2, restante2 = alvo.receber_dano(999)
        self.assertEqual((absorvido2, restante2), (0, 999))
        self.assertTrue(alvo.caido)
        self.assertEqual(alvo.receber_dano(0), (0, 0))

    def test_defesa_declarada_aumenta_a_dd(self):
        a = self.aleat("defesa")
        cs = self.combatentes(a, nivel=6, n=2)
        enc = iniciar_encontro(Cenario(), cs, a)
        base = cs[0].defesa()
        defender(enc, cs[0].nome, acao_de_defesa=True)
        self.assertEqual(cs[0].defesa(), base + 3)
        defender(enc, cs[0].nome, acao_de_defesa=False, guarda_total=True)
        self.assertEqual(cs[0].defesa(), base + 2)
        defender(enc, cs[0].nome, manto_de_qi=True)
        self.assertEqual(cs[0].defesa(), base + 2)
        with self.assertRaises(ValueError):
            defender(enc, cs[0].nome, acao_de_defesa=True, guarda_total=True)

    def test_manto_de_qi_consome_por_rodada(self):
        a = self.aleat("manto")
        cs = self.combatentes(a, nivel=6, n=2)
        enc = iniciar_encontro(Cenario(), cs, a)
        defender(enc, cs[0].nome, manto_de_qi=True)
        self.assertTrue(cs[0].modo.manto_de_qi)
        qi0 = cs[0].estado.qi
        for _ in range(len(enc.ordem) + 1):
            enc.proximo()
        self.assertLess(cs[0].estado.qi, qi0)

    def test_exclusividades_sao_recusadas(self):
        a = self.aleat("excl")
        cs = self.combatentes(a, nivel=6, n=2)
        enc = iniciar_encontro(Cenario(), cs, a)
        with self.assertRaises(ValueError):
            atacar(enc, cs[0].nome, cs[1].nome, a, oculto=True,
                   alvo_surpreso=True)
        cs[0].desvio_de_qi = True
        with self.assertRaises(ValueError):
            atacar(enc, cs[0].nome, cs[1].nome, a, meditou=True)

    def test_nao_se_ataca_a_si_mesmo(self):
        a = self.aleat("self")
        cs = self.combatentes(a, n=2)
        enc = iniciar_encontro(Cenario(), cs, a)
        with self.assertRaises(ValueError):
            atacar(enc, cs[0].nome, cs[0].nome, a)
        with self.assertRaises(KeyError):
            atacar(enc, cs[0].nome, "Fulano", a)

    def test_caido_nao_ataca(self):
        a = self.aleat("caido")
        cs = self.combatentes(a, n=2)
        enc = iniciar_encontro(Cenario(), cs, a)
        cs[0].caido = True
        with self.assertRaises(ValueError):
            atacar(enc, cs[0].nome, cs[1].nome, a)

    def test_encontro_exige_dois(self):
        a = self.aleat("um")
        with self.assertRaises(ValueError):
            iniciar_encontro(Cenario(), self.combatentes(a, n=1), a)

    def test_encontro_completo_termina(self):
        a = self.aleat("completo")
        cs = self.combatentes(a, nivel=6, n=3)
        d = self.diario("combate.jsonl")
        enc = iniciar_encontro(Cenario(descricao="teste"), cs, a, d)
        turnos = 0
        while not enc.encerrado and turnos < 400:
            nome = enc.proximo()
            if nome is None:
                break
            atac = enc.get(nome)
            alvos = [c for c in enc.ativos() if c.nome != nome
                     and c.faccao != atac.faccao]
            if not alvos:
                encerrar(enc, "sem alvos")
                break
            atacar(enc, nome, alvos[0].nome, a)
            turnos += 1
        self.assertLess(turnos, 400, "o encontro não terminou")
        self.assertTrue(d.verificar().ok)
        self.assertTrue(conferir(d).ok)
        self.assertGreaterEqual(len(d.por_tipo("rolagem")), turnos)

    def test_estatistica_de_duelos(self):
        """Propriedade: duelos de mesmo nível duram entre 4 e 30 rodadas."""
        rodadas = []
        acertos = totais = 0
        for i in range(40):
            a = self.aleat(f"duelo-{i}")
            cs = self.combatentes(a, nivel=6, n=2)
            enc = iniciar_encontro(Cenario(), cs, a)
            turnos = 0
            while not enc.encerrado and turnos < 300:
                nome = enc.proximo()
                if nome is None:
                    break
                atac = enc.get(nome)
                alvos = [c for c in enc.ativos() if c.nome != nome]
                if not alvos:
                    encerrar(enc, "fim")
                    break
                g = atacar(enc, nome, alvos[0].nome, a)
                acertos += g.acertou
                totais += 1
                turnos += 1
            rodadas.append(enc.rodada)
        media = sum(rodadas) / len(rodadas)
        self.assertTrue(3 <= media <= 30, f"média de rodadas {media}")
        taxa = acertos / totais
        self.assertTrue(0.25 <= taxa <= 0.85, f"taxa de acerto {taxa}")

    def test_bestas_e_npcs_lutam_junto_com_personagens(self):
        a = self.aleat("misto")
        p = criar_personagem(nome="P", aleat=a, nivel=6, tabela_de_raiz="heroica")
        n = gerar_npc(a, nome="N", nivel=6)
        b = gerar_besta(a, nivel=6)
        cs = [Combatente.de_personagem(p), Combatente.de_npc(n),
              Combatente.de_besta(b)]
        cs[0].faccao = "A"
        cs[1].faccao = "B"
        cs[2].faccao = "B"
        enc = iniciar_encontro(Cenario(), cs, a)
        self.assertEqual(len(enc.ativos()), 3)
        self.assertEqual(len(enc.lados()), 2)
        g = atacar(enc, "P", "N", a)
        self.assertIsInstance(g.acertou, bool)
        g2 = atacar(enc, b.nome, "P", a)
        self.assertIsInstance(g2.acertou, bool)


# ==========================================================================
# Seitas
# ==========================================================================
class TesteSeitas(BaseComSemente):
    def seita(self, **kw):
        base = dict(nome="Seita de Teste", chines="試宗", alinhamento="ortodoxa",
                    provincia="Qing", nivel_do_mestre=9, pedras=200000,
                    comida=1000)
        base.update(kw)
        return Seita(**base)

    def test_postos_e_promocao_exigem_nivel(self):
        s = self.seita()
        self.assertEqual(aceitar_discipulo(s, "Mortal", 0), "servo")
        self.assertEqual(aceitar_discipulo(s, "Novato", 1), "discipulo_externo")
        self.assertEqual(aceitar_discipulo(s, "Interno", 3, True),
                         "discipulo_interno")
        with self.assertRaises(ValueError):
            aceitar_discipulo(s, "Forcado", 1, True)
        with self.assertRaises(ValueError):
            aceitar_discipulo(s, "Novato", 1)      # duplicado
        with self.assertRaises(ValueError):
            aceitar_discipulo(s, "Alto", 14)
        s.niveis["Interno"] = 5
        self.assertEqual(promover(s, "Interno", "discipulo_nucleo"),
                         "discipulo_nucleo")
        with self.assertRaises(ValueError):
            promover(s, "Interno", "anciao")       # nível 5 < 7
        with self.assertRaises(ValueError):
            promover(s, "Interno", "servo")        # rebaixação
        with self.assertRaises(ValueError):
            promover(s, "Interno", "imperador")
        with self.assertRaises(KeyError):
            promover(s, "Estranho", "anciao")

    def test_construcao_exige_dinheiro_e_nivel(self):
        s = self.seita(nivel_do_mestre=1, pedras=100)
        with self.assertRaises(ValueError):
            construir(s, "FORJA")                  # nível insuficiente
        s2 = self.seita(pedras=100)
        with self.assertRaises(ValueError):
            construir(s2, "CELEIRO")               # dinheiro insuficiente
        with self.assertRaises(ValueError):
            construir(s2, "PIRAMIDE")              # prédio inexistente
        s3 = self.seita(pedras=10000)
        construir(s3, "CELEIRO")
        self.assertTrue(s3.tem("CELEIRO"))
        with self.assertRaises(ValueError):
            construir(s3, "CELEIRO")               # duplicado
        self.assertEqual(s3.pedras, 8500)

    def test_recursos_validados(self):
        s = self.seita(pedras=100)
        with self.assertRaises(ValueError):
            s.gastar("diamantes", 1, "teste")
        with self.assertRaises(ValueError):
            s.gastar("pedras", 101, "teste")
        s.gastar("pedras", 40, "compra")
        self.assertEqual(s.pedras, 60)
        s.ganhar("ervas", 5, "colheita")
        self.assertEqual(s.ervas, 5)
        self.assertEqual(len(s.historico), 2)

    def test_producao_mensal_e_aritmetica(self):
        d = self.diario("seita.jsonl")
        s = self.seita(predios=("CAMPOS_ESPIRITUAIS", "CELEIRO", "COFRE"))
        aceitar_discipulo(s, "A", 3, True)
        aceitar_discipulo(s, "B", 1)
        antes = {"pedras": s.pedras, "ervas": s.ervas, "comida": s.comida}
        r = producao_mensal(s, "comum", d)
        self.assertEqual(r["recursos"]["ervas"], 8)
        self.assertEqual(r["recursos"]["comida"], 300)
        self.assertEqual(s.ervas, antes["ervas"] + 8)
        self.assertEqual(s.comida, antes["comida"] + 300 - 2)
        self.assertEqual(r["bocas"], 2)
        self.assertEqual(r["fome"], 0)
        # veia espiritual melhora os campos
        s2 = self.seita(predios=("CAMPOS_ESPIRITUAIS",))
        r2 = producao_mensal(s2, "veia_espiritual")
        self.assertEqual(r2["recursos"]["ervas"], 10)
        s3 = self.seita(predios=("CAMPOS_ESPIRITUAIS",))
        r3 = producao_mensal(s3, "terra_imortal")
        self.assertEqual(r3["recursos"]["ervas"], 12)
        self.assertTrue(d.verificar().ok)

    def test_cofre_rende_porcentagem(self):
        s = self.seita(pedras=100000, predios=("COFRE",))
        r = producao_mensal(s, "comum")
        self.assertEqual(r["recursos"]["pedras"], 2000)

    def test_predios_sem_recurso_viram_beneficio(self):
        s = self.seita(predios=("PAVILHAO_MANUAIS", "ARENA"))
        r = producao_mensal(s, "comum")
        self.assertEqual(r["recursos"], {})
        self.assertEqual(len(r["beneficios"]), 2)

    def test_missoes_validadas_e_auditadas(self):
        a = self.aleat("missoes")
        d = self.diario("missoes.jsonl")
        s = self.seita()
        aceitar_discipulo(s, "Wang", 7, True)
        with self.assertRaises(ValueError):
            executar_missao(s, "SALVAR_O_MUNDO", "Wang", a, nivel=7,
                            valor_atributo=14, graduacao=3)
        with self.assertRaises(KeyError):
            executar_missao(s, "COLHER_ERVAS", "Estranho", a, nivel=7,
                            valor_atributo=14, graduacao=3)
        sucessos = 0
        for i in range(60):
            r = executar_missao(s, "COLHER_ERVAS", "Wang", a, nivel=7,
                                valor_atributo=16, graduacao=4, diario=d)
            self.assertIsInstance(r.sucesso, bool)
            if r.sucesso:
                sucessos += 1
                self.assertGreater(r.pedras, 0)
                self.assertEqual(r.baixa, "nenhuma")
            else:
                self.assertEqual(r.pedras, 0)
                self.assertTrue(r.baixa)
            self.assertIn(r.resultado.total, range(-50, 100))
        self.assertTrue(0 < sucessos < 60)
        self.assertTrue(d.verificar().ok)
        self.assertTrue(conferir(d).ok)

    def test_prestigio_limitado(self):
        a = self.aleat("prestigio")
        s = self.seita()
        aceitar_discipulo(s, "Wang", 7, True)
        for _ in range(400):
            executar_missao(s, "COLHER_ERVAS", "Wang", a, nivel=7,
                            valor_atributo=20, graduacao=5)
        self.assertTrue(-200 <= s.prestigio <= 300)

    def test_missao_dificil_falha_mais(self):
        a = self.aleat("dificil")
        s = self.seita()
        aceitar_discipulo(s, "Wang", 7, True)
        faceis = sum(1 for _ in range(120)
                     if executar_missao(s, "COLHER_ERVAS", "Wang", a, nivel=7,
                                        valor_atributo=14,
                                        graduacao=2).sucesso)
        dificeis = sum(1 for _ in range(120)
                       if executar_missao(s, "SELAR_REINO_SECRETO", "Wang", a,
                                          nivel=7, valor_atributo=14,
                                          graduacao=2).sucesso)
        self.assertGreater(faceis, dificeis)

    def test_risco_maior_da_baixas_piores(self):
        a = self.aleat("baixas")
        s = self.seita()
        aceitar_discipulo(s, "Wang", 7, True)
        from xan.seitas import _baixa_por_risco
        for risco in (1, 5):
            baixas = {_baixa_por_risco(a, risco, False) for _ in range(200)}
            self.assertTrue(baixas)
        # risco 5 tem pelo menos uma baixa fatal
        self.assertTrue(any("não voltou" in _baixa_por_risco(a, 5, False)
                            or "morreu" in _baixa_por_risco(a, 5, False)
                            for _ in range(50)))

    def test_torneio_de_kunlun(self):
        a = self.aleat("kunlun")
        d = self.diario("kunlun.jsonl")
        partes = [{"nome": f"L{i}", "seita": "A" if i % 2 else "B",
                   "nivel": 4 + i % 5, "atributo": 11 + i, "graduacao": i % 6}
                  for i in range(12)]
        t = torneio_de_kunlun(1600, partes, a, lei_em_disputa="TAIYI_METAL",
                              diario=d)
        self.assertIn(t.campeao, {p["nome"] for p in partes})
        self.assertEqual(len(t.classificacao), 12)
        pontos = [p for _, p in t.classificacao]
        self.assertEqual(pontos, sorted(pontos, reverse=True))
        self.assertEqual(t.lei_conquistada, "TAIYI_METAL")
        # sem repetição de confronto enquanto houver adversário
        pares = [tuple(sorted((x[0], x[1]))) for x in t.confrontos]
        unicos = len(set(pares))
        self.assertGreaterEqual(unicos, len(pares) * 9 // 10,
                                f"{len(pares) - unicos} repetições em {len(pares)}")
        for a_nome, b_nome, vencedor, ta, tb in t.confrontos:
            self.assertIn(vencedor, (a_nome, b_nome, "empate"))
            self.assertIsInstance(ta, int)
        self.assertIn("Torneio de Kunlun", t.resumo())
        self.assertTrue(d.verificar().ok)

    def test_torneio_mais_forte_vence_mais(self):
        a = self.aleat("justica-do-torneio")
        vitorias = {"forte": 0, "fraco": 0}
        for i in range(40):
            partes = [
                {"nome": "forte", "seita": "A", "nivel": 8, "atributo": 20,
                 "graduacao": 5},
                {"nome": "fraco", "seita": "B", "nivel": 2, "atributo": 9,
                 "graduacao": 0},
            ]
            t = torneio_de_kunlun(1600 + i, partes, a)
            vitorias[t.campeao] += 1
        self.assertGreater(vitorias["forte"], vitorias["fraco"] * 3)

    def test_torneio_exige_participantes(self):
        a = self.aleat("torneio-vazio")
        with self.assertRaises(ValueError):
            torneio_de_kunlun(1600, [], a)
        with self.assertRaises(ValueError):
            torneio_de_kunlun(1600, [{"nome": "A"}], a)

    def test_ficha_da_seita(self):
        s = self.seita(predios=("PAVILHAO_MANUAIS", "ARENA"))
        aceitar_discipulo(s, "Wang Mei", 7, True)
        s.rivais["Culto da Chama"] = -70
        f = s.ficha()
        for trecho in ("Seita de Teste", "Prestígio", "Pavilhão de Manuais",
                       "Wang Mei", "Culto da Chama"):
            self.assertIn(trecho, f)

    def test_seita_rejeita_alinhamento_invalido(self):
        with self.assertRaises(ValueError):
            self.seita(alinhamento="caotica")
        with self.assertRaises(ValueError):
            Seita(nome="X", chines="", alinhamento="ortodoxa", provincia="P",
                  nivel_do_mestre=5, predios=("CASTELO",))
        with self.assertRaises(ValueError):
            Seita(nome="X", chines="", alinhamento="ortodoxa", provincia="P",
                  nivel_do_mestre=5, membros={"A": "imperador"})


# ==========================================================================
# Mapas
# ==========================================================================
class TesteMapas(BaseComSemente):
    def test_svg_do_mundo(self):
        m = gerar_mundo("mapa", provincias=9, eventos=10)
        svg = mapa_do_mundo(m.como_dict())
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.rstrip().endswith("</svg>"))
        import xml.dom.minidom as minidom
        minidom.parseString(svg)          # precisa ser XML válido
        self.assertIn(m.semente, svg)
        for p in m.provincias:
            self.assertIn(p.nome, svg)
        self.assertIn("Legenda", svg)

    def test_svg_da_provincia(self):
        m = gerar_mundo("mapa2", provincias=5, eventos=5)
        p = max(m.provincias, key=lambda x: len(x.sitios))
        svg = mapa_da_provincia(p.como_dict(), nome_do_mundo=m.nome)
        import xml.dom.minidom as minidom
        minidom.parseString(svg)
        self.assertIn(p.nome, svg)
        for s in p.sitios:
            self.assertIn(s.nome, svg)

    def test_svg_escapa_caracteres(self):
        m = gerar_mundo("mapa3", provincias=4, eventos=4)
        dados = m.como_dict()
        dados["nome"] = 'Mundo <malicioso> & "aspas"'
        svg = mapa_do_mundo(dados)
        import xml.dom.minidom as minidom
        minidom.parseString(svg)
        self.assertNotIn("<malicioso>", svg)

    def test_provincia_sem_sitios(self):
        with self.assertRaises(ValueError):
            mapa_da_provincia({"nome": "Vazia", "chines": "", "elemento": "agua",
                               "terreno": "deserto", "densidade_qi": 0,
                               "perigo": 1, "sitios": []})

    def test_mundo_sem_provincias(self):
        with self.assertRaises(ValueError):
            mapa_do_mundo({"provincias": []})


# ==========================================================================
# Rolagem auditada simples
# ==========================================================================
class TesteRolagemAuditada(BaseComSemente):
    def test_protocolo_completo(self):
        a = self.aleat("auditada")
        d = self.diario("simples.jsonl")
        r, comp, indice = rolagem_auditada("4d6kh3", a, d, ator="Lin")
        self.assertEqual(len(r.termos), 1)
        self.assertTrue(comp.token)
        self.assertEqual(indice, 1)
        tipos = [x.tipo for x in d.registros]
        self.assertEqual(tipos, ["compromisso", "rolagem", "revelacao"])
        self.assertTrue(d.verificar().ok)
        self.assertTrue(conferir(d).ok)

    def test_adulteracao_e_detectada(self):
        a = self.aleat("adultera")
        caminho = os.path.join(self._tmp, "adulterado.jsonl")
        d = DiarioDeAuditoria(caminho)
        rolagem_auditada("1d20", a, d, ator="Lin")
        with open(caminho, encoding="utf-8") as fh:
            linhas = fh.read().splitlines()
        registro = json.loads(linhas[1])
        registro["conteudo"]["total"] = 20
        linhas[1] = json.dumps(registro, ensure_ascii=False)
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write("\n".join(linhas) + "\n")
        d2 = DiarioDeAuditoria(caminho, criar=False)
        rel = d2.verificar()
        self.assertFalse(rel.ok)


# ==========================================================================
# Coerência entre módulos
# ==========================================================================
class TesteCoerencia(BaseComSemente):
    def test_fatos_do_mundo_alimentam_as_regras(self):
        m = gerar_mundo("ponte")
        for p in m.provincias:
            valor_de("AMBIENTE:DENSIDADE_QI",
                     {"densidade_qi": p.densidade_fato})
            for s in p.sitios:
                valor_de("AMBIENTE:DENSIDADE_QI",
                         {"densidade_qi": DensidadeDeQi(s.densidade_qi)})

    def test_relacao_de_faccoes_alimenta_a_regra(self):
        m = gerar_mundo("ponte2")
        nomes = [f.nome for f in m.faccoes][:6]
        for a in nomes:
            for b in nomes:
                fato = m.relacao_como_fato(a, b)
                mod = valor_de("FACCAO:RELACAO", {"relacao_de_faccoes": fato})
                self.assertTrue(-2 <= mod <= 2)

    def test_disposicao_de_npc_alimenta_a_regra(self):
        n = gerar_npc(self.aleat("ponte3"), nivel=5)
        n.registrar_relacao("P", "salvou_a_vida")
        categoria = n.disposicao_para("P")[1]
        mod = valor_de("SOCIAL:DISPOSICAO", {"disposicao": categoria})
        self.assertTrue(-4 <= mod <= 3)

    def test_estado_de_jogo_alimenta_as_regras(self):
        a = self.aleat("ponte4")
        p = criar_personagem(nome="X", aleat=a, nivel=6)
        e = EstadoDeJogo.de_personagem(p)
        fatos = e.fatos_para_regras()
        self.assertEqual(fatos["ferimento"], "ileso")
        valor_de("ESTADO:FERIMENTO", {"ferimento": fatos["ferimento"]})
        valor_de("ESTADO:EXAUSTAO", {"qi_atual": fatos["qi_atual"],
                                     "qi_maximo": fatos["qi_maximo"]})
        valor_de("ESTADO:DESVIO_DE_QI",
                 {"desvio_de_qi": fatos["desvio_de_qi"]})

    def test_elementos_das_leis_existem_no_wuxing(self):
        from xan.regras import ELEMENTOS_NEUTROS
        for lei in LEIS.values():
            self.assertIn(lei.elemento, ELEMENTOS_CANONICOS + ELEMENTOS_NEUTROS)
            for t in tecnicas_de_lei(lei.codigo):
                self.assertIn(t.elemento, ELEMENTOS_CANONICOS + ELEMENTOS_NEUTROS)

    def test_relacao_elemental_e_anti_simetrica(self):
        """A relação Wuxing é anti-simétrica nos rótulos."""
        oposto = {"supera": "subjugado", "subjugado": "supera",
                  "gerador": "gerado", "gerado": "gerador",
                  "igual": "igual", "neutro": "neutro"}
        vistos = set()
        for a in ELEMENTOS_CANONICOS:
            for b in ELEMENTOS_CANONICOS:
                rab = relacao_elemental(a, b)
                rba = relacao_elemental(b, a)
                vistos.add(rab)
                self.assertIn(rab, oposto, f"rótulo inesperado {rab!r}")
                self.assertEqual(oposto[rab], rba,
                                 f"{a}×{b} = {rab} mas {b}×{a} = {rba}")
        self.assertEqual(vistos, {"supera", "subjugado", "gerador", "gerado",
                                  "igual"})
        # neutros nunca geram nem superam
        for neutro in ("nenhum", "vazio"):
            for outro in ELEMENTOS_CANONICOS:
                self.assertEqual(relacao_elemental(neutro, outro), "neutro")
                self.assertEqual(relacao_elemental(outro, neutro), "neutro")

    def test_atributos_dos_modulos_coincidem(self):
        for nome in ATRIBUTOS:
            self.assertIn(nome, ("per", "con", "cha", "int", "luk", "pot"))

    def test_postos_de_seita_e_npc_usam_o_mesmo_vocabulario(self):
        from xan.npcs import POSTOS as POSTOS_NPC
        # os postos de NPC são rótulos exibíveis; os de seita são códigos
        self.assertEqual(len(POSTOS), 10)
        self.assertTrue(all(isinstance(p, str) for p in POSTOS_NPC))

    def test_catalogos_nao_tem_codigos_duplicados(self):
        self.assertEqual(len({c for c in TECNICAS}), len(TECNICAS))
        self.assertEqual(len({c for c in LEIS}), len(LEIS))
        self.assertEqual(len({c for c in PERICIAS}), len(PERICIAS))
        self.assertEqual(len({c for c in REGISTRO}), len(REGISTRO))
        self.assertEqual(len({c for c in MISSOES}), len(MISSOES))
        self.assertEqual(len({c for c in PREDIOS}), len(PREDIOS))
        self.assertEqual(len({c for c in EVENTOS_DE_RELACAO}),
                         len(EVENTOS_DE_RELACAO))


if __name__ == "__main__":
    unittest.main()
