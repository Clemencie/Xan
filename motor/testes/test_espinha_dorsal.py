# -*- coding: utf-8 -*-
"""Testes da espinha dorsal de aleatoriedade: entropia, dados, auditoria,
compromisso, regras e resolução. Rodar com:

    cd motor && python3 -m unittest discover -s testes -t . -v
"""

from __future__ import annotations

import itertools
import json
import math
import os
import shutil
import tempfile
import unittest
from collections import Counter
from fractions import Fraction

from xan.auditoria import DiarioDeAuditoria, HASH_GENESIS, canonico, hash_de
from xan.compromisso import comprometer, conferir, verificar_compromisso
from xan.dados import (
    ErroDeNotacao, TermoDado, rolar, valor_esperado, minimo_maximo, _parsear,
)
from xan.entropia import (
    Aleatoriedade, FonteSemeada, FonteViva, HMACDRBG, ERRO_AMOSTRA_VAZIA,
)
from xan.justica import (
    chi2_p_valor, distribuicao_exata, momentos_exatos, teste_abaixo,
    teste_determinismo, teste_distribuicao, teste_manter_imparcial,
    teste_imparcialidade_entre_atores,
)
from xan.regras import (
    ModificadorIlegal, REGISTRO, conflitos, relacao_elemental, valor_de,
)
from xan.resolucao import (
    ATRIBUTOS, Declaracao, DeclaracaoInvalida, Resultado, bonus_de_atributo,
    resolver, teste_oposto, verificar_invariantes,
)


# ==========================================================================
# Camada 1 — entropia
# ==========================================================================
class TesteDRBG(unittest.TestCase):
    def test_determinismo_da_semente(self):
        a = HMACDRBG(b"x" * 32, b"nonce", b"pers")
        b = HMACDRBG(b"x" * 32, b"nonce", b"pers")
        self.assertEqual(a.gerar(1000), b.gerar(1000))

    def test_sementes_distintas_divergem(self):
        a = HMACDRBG(b"x" * 32)
        b = HMACDRBG(b"y" * 32)
        self.assertNotEqual(a.gerar(64), b.gerar(64))

    def test_entropia_insuficiente_e_recusada(self):
        with self.assertRaises(ValueError):
            HMACDRBG(b"curta")

    def test_tipos_invalidos(self):
        with self.assertRaises(TypeError):
            HMACDRBG("não é bytes")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            HMACDRBG(b"x" * 32).gerar(0)

    def test_estado_avanca_a_cada_chamada(self):
        d = HMACDRBG(b"z" * 32)
        v = {d.gerar(32) for _ in range(200)}
        self.assertEqual(len(v), 200, "o DRBG repetiu saída — estado não avançou")


class TesteFonteSemeada(unittest.TestCase):
    def test_mesma_semente_mesma_saida(self):
        a = Aleatoriedade(FonteSemeada("mundo-42", "regioes"))
        b = Aleatoriedade(FonteSemeada("mundo-42", "regioes"))
        self.assertEqual(a.bytes(512), b.bytes(512))

    def test_derivacoes_sao_independentes(self):
        a = Aleatoriedade(FonteSemeada("mundo-42", "regioes"))
        b = Aleatoriedade(FonteSemeada("mundo-42", "npcs"))
        self.assertNotEqual(a.bytes(128), b.bytes(128))

    def test_semente_int_str_bytes(self):
        x = Aleatoriedade(FonteSemeada(12345, "t")).bytes(32)
        y = Aleatoriedade(FonteSemeada("12345", "t")).bytes(32)
        self.assertEqual(x, y, "int e str equivalente devem dar a mesma semente")

    def test_semente_vazia_rejeitada(self):
        with self.assertRaises(ValueError):
            FonteSemeada("", "t")


class TesteAmostragemImparcial(unittest.TestCase):
    def setUp(self):
        self.aleat = Aleatoriedade(FonteSemeada("amostragem", "testes"))

    def test_abaixo_nunca_estoura_o_limite(self):
        for n in (2, 3, 5, 7, 13, 20, 100, 1000):
            for _ in range(2000):
                v = self.aleat.abaixo(n)
                self.assertTrue(0 <= v < n, f"abaixo({n}) devolveu {v}")

    def test_abaixo_invalido(self):
        for n in (0, -1):
            with self.assertRaises(ValueError):
                self.aleat.abaixo(n)
        self.assertEqual(self.aleat.abaixo(1), 0)

    def test_sem_vies_de_modulo_para_nao_potencia_de_dois(self):
        """O teste que pega `rand() % n`. n=3 é o pior caso em 1 byte (256%3=1)."""
        for modulo in (3, 5, 7, 13, 100):
            t = teste_abaixo(self.aleat, modulo, 30_000)
            self.assertGreater(
                t.p_valor, 1e-6,
                f"viés detectado em abaixo({modulo}): p={t.p_valor:g} nota={t.nota}",
            )

    def test_rejeicao_usa_mais_bytes_que_o_ingenu(self):
        """Prova construtiva: a rejeição está ativa."""
        aleat = Aleatoriedade(FonteSemeada("rejeicao", "t"))
        antes = aleat.consumo()
        for _ in range(20_000):
            aleat.abaixo(7)
        depois = aleat.consumo()
        por_resultado = (depois.bytes_solicitados - antes.bytes_solicitados) / 20_000
        self.assertGreater(por_resultado, 1.0,
                           "1 byte por resultado indicaria '% n' (enviesado)")
        self.assertAlmostEqual(por_resultado, 8 / 7, delta=0.02)

    def test_entre_inclusivo(self):
        vistos = {self.aleat.entre(3, 6) for _ in range(4000)}
        self.assertEqual(vistos, {3, 4, 5, 6})
        with self.assertRaises(ValueError):
            self.aleat.entre(6, 3)

    def test_sequencia_vazia_e_erro_nao_padrao_silencioso(self):
        with self.assertRaises(ValueError) as ctx:
            self.aleat.escolher([])
        self.assertIn(ERRO_AMOSTRA_VAZIA, str(ctx.exception))

    def test_escolha_ponderada_exata(self):
        pesos = [1, 2, 3, 4]
        itens = ["a", "b", "c", "d"]
        cont = Counter(self.aleat.escolher_ponderado(itens, pesos) for _ in range(40_000))
        total = sum(pesos)
        for item, p in zip(itens, pesos):
            esperado = 40_000 * p / total
            self.assertAlmostEqual(cont[item], esperado, delta=esperado * 0.08)

    def test_pesos_float_sao_recusados(self):
        with self.assertRaises(TypeError):
            self.aleat.escolher_ponderado(["a", "b"], [0.5, 0.5])
        with self.assertRaises(TypeError):
            self.aleat.escolher_ponderado(["a", "b"], [True, False])
        with self.assertRaises(ValueError):
            self.aleat.escolher_ponderado(["a", "b"], [-1, 5])
        with self.assertRaises(ValueError):
            self.aleat.escolher_ponderado(["a", "b"], [0, 0])

    def test_amostrar_sem_reposicao(self):
        base = list(range(10))
        for _ in range(500):
            amostra = self.aleat.amostrar(base, 4)
            self.assertEqual(len(set(amostra)), 4)
            self.assertTrue(set(amostra) <= set(base))
        with self.assertRaises(ValueError):
            self.aleat.amostrar(base, 11)

    def test_baralhar_e_permutacao(self):
        base = list(range(6))
        for _ in range(300):
            out = self.aleat.baralhar(base)
            self.assertEqual(sorted(out), base)
        self.assertEqual(base, list(range(6)), "baralhar não pode mutar a entrada")

    def test_baralhar_uniforme(self):
        cont = Counter(tuple(self.aleat.baralhar([0, 1, 2])) for _ in range(24_000))
        self.assertEqual(set(cont), set(itertools.permutations([0, 1, 2])))
        for v in cont.values():
            self.assertAlmostEqual(v, 4000, delta=400)

    def test_consumo_contabilizado(self):
        a = Aleatoriedade(FonteSemeada("contabil", "t"))
        c0 = a.consumo()
        a.abaixo(1_000_003)
        c1 = a.consumo()
        self.assertGreater(c1.bytes_solicitados, c0.bytes_solicitados)
        self.assertEqual(c1.chamadas - c0.chamadas, 1)


class TesteFonteViva(unittest.TestCase):
    def test_saida_nao_se_repete(self):
        a = Aleatoriedade(FonteViva(b"teste"))
        v = {a.bytes(32) for _ in range(500)}
        self.assertEqual(len(v), 500)

    def test_uniformidade_basica(self):
        a = Aleatoriedade(FonteViva(b"teste"))
        cont = Counter(a.abaixo(20) for _ in range(20_000))
        self.assertEqual(len(cont), 20)
        chi2 = sum((c - 1000) ** 2 / 1000 for c in cont.values())
        self.assertGreater(chi2_p_valor(chi2, 19), 1e-6)


# ==========================================================================
# Camada 2 — dados
# ==========================================================================
class TesteParserDeDados(unittest.TestCase):
    def setUp(self):
        self.aleat = Aleatoriedade(FonteSemeada("dados", "testes"))

    def test_expressoes_validas(self):
        for expr in ("1d20", "d20", "3d6", "2d10", "d%", "1d%", "4d6kh1",
                     "4d6kh3", "2d20kl1", "2d6!", "1d10!8", "3dF", "1d20+5",
                     "1d20 - 1d4 + 2", "10d6", "1d1000000",
                     "-1d6", "1d20-1d4", "-1d20+5", "1d20!", "d20!",
                     "2d6kh1", "1d4!2"):
            r = rolar(expr, self.aleat)
            self.assertIsInstance(r.total, int)

    def test_expressoes_invalidas(self):
        for expr in ("", "d", "1d", "d0", "1d1", "abc", "1d20 5", "1d20+",
                     "0d6", "1d6kh7", "1d6!7", "1d6!0",
                     "2d6kh-1", "1z20", "1d20kh", "1d20*2",
                     "-", "+", "1d20-", "1d20++2", "1d6kh0", "1d6kh0kh1",
                     "0d20", "1d20kl0"):
            with self.assertRaises(ErroDeNotacao, msg=f"{expr!r} deveria falhar"):
                rolar(expr, self.aleat)

    def test_termo_negativo_subtrai(self):
        """Regressão: '1d20-1d4' precisa SUBTRAIR o segundo termo."""
        aleat = Aleatoriedade(FonteSemeada("sinal", "t"))
        for _ in range(500):
            r = rolar("1d20-1d4", aleat)
            self.assertEqual(r.termos[0].sinal, 1)
            self.assertEqual(r.termos[1].sinal, -1)
            self.assertEqual(r.total, r.termos[0].soma + r.termos[1].soma)
            self.assertTrue(-3 <= r.total <= 19)
        termos, c = _parsear("1d20-1d4")
        self.assertEqual(valor_esperado(termos, c), Fraction(21, 2) - Fraction(5, 2))
        self.assertEqual(minimo_maximo(termos, c), (-3, 19))

    def test_espacos_aceitos_junto_de_operadores(self):
        r = rolar("1d20 + 5", self.aleat)
        self.assertTrue(6 <= r.total <= 25)
        r = rolar("4d6 kh 3", self.aleat)
        self.assertTrue(3 <= r.total <= 18)

    def test_intervalo_respeitado(self):
        for expr, lo, hi in (("1d20", 1, 20), ("2d6", 2, 12), ("3d6", 3, 18),
                             ("1d20+5", 6, 25), ("4d6kh1", 1, 6),
                             ("4d6kh3", 3, 18), ("3dF", -3, 3)):
            for _ in range(400):
                r = rolar(expr, self.aleat)
                self.assertEqual((r.minimo, r.maximo), (lo, hi), expr)
                self.assertTrue(lo <= r.total <= hi, f"{expr} → {r.total}")

    def test_todas_as_faces_sao_registradas(self):
        r = rolar("4d6kh1", self.aleat)
        t = r.termos[0]
        self.assertEqual(len(t.faces), 4)
        self.assertEqual(len(t.mantidas), 1)
        self.assertEqual(len(t.descartadas), 3)
        self.assertEqual(sorted(t.mantidas + t.descartadas), sorted(t.faces))
        self.assertEqual(t.mantidas[0], max(t.faces))

    def test_kl_mantem_as_menores(self):
        for _ in range(300):
            t = rolar("2d20kl1", self.aleat).termos[0]
            self.assertEqual(t.mantidas[0], min(t.faces))

    def test_explosao_encadeia_e_registra(self):
        aleat = Aleatoriedade(FonteSemeada("explosao", "t"))
        achou = False
        for _ in range(4000):
            r = rolar("1d6!", aleat)
            if len(r.termos[0].faces) > 1:
                achou = True
                faces = r.termos[0].faces
                for f in faces[:-1]:
                    self.assertEqual(f, 6, "só o 6 pode explodir")
                self.assertLess(faces[-1], 7)
                self.assertTrue(r.limite_aberto)
                break
        self.assertTrue(achou, "nenhuma explosão em 4000 rolagens de 1d6!")

    def test_fudge(self):
        vistos = Counter()
        for _ in range(3000):
            vistos.update(rolar("1dF", self.aleat).termos[0].faces)
        self.assertEqual(set(vistos), {-1, 0, 1})

    def test_percentil(self):
        vistos = {rolar("d%", self.aleat).total for _ in range(3000)}
        self.assertTrue(vistos <= set(range(1, 101)))
        self.assertGreater(len(vistos), 90)

    def test_rolagem_imutavel(self):
        r = rolar("1d20", self.aleat)
        with self.assertRaises(Exception):
            r.total = 20  # type: ignore[misc]

    def test_total_inconsistente_e_bloqueado(self):
        t = rolar("1d20", self.aleat)
        with self.assertRaises(AssertionError):
            type(t)(
                expressao="1d20", termos=t.termos, constante=0, total=t.total + 1,
                minimo=1, maximo=20, valor_esperado=Fraction(21, 2),
            )


class TesteMatematicaExata(unittest.TestCase):
    def _brute(self, expr):
        termos, c = _parsear(expr)
        self.assertEqual(len(termos), 1)
        t = termos[0]
        faces = (-1, 0, 1) if t.fudge else tuple(range(1, t.lados + 1))
        k = t.quantidade_manter or t.quantidade
        kh = t.modo_manter != "kl"
        espaco = list(itertools.product(faces, repeat=t.quantidade))
        soma = sum(sum(sorted(c2, reverse=kh)[:k]) for c2 in espaco)
        return Fraction(soma, len(espaco)) + c

    def test_valor_esperado_confere_com_enumeracao(self):
        for expr in ("1d20", "2d6", "3d6", "4d6kh1", "4d6kh3", "2d20kh1",
                     "4d6kl1", "3d6kh2", "5d6kl2", "2d6kh1", "3d8kl2",
                     "3dF", "1d20+5", "2d6-1"):
            termos, c = _parsear(expr)
            if any(t.explosao for t in termos):
                continue
            self.assertEqual(valor_esperado(termos, c), self._brute(expr), expr)

    def test_explosivos_serie_geometrica(self):
        # 1d6! : média = 3.5 / (1 - 1/6) = 4.2
        termos, c = _parsear("1d6!")
        self.assertEqual(valor_esperado(termos, c), Fraction(21, 5))
        # 1d10!8 : faces 8,9,10 explodem → p=3/10 → 5.5/0.7 = 55/7
        termos, c = _parsear("1d10!8")
        self.assertEqual(valor_esperado(termos, c), Fraction(55, 7))

    def test_distribuicao_exata_2d6(self):
        d = distribuicao_exata("2d6")
        self.assertEqual(d[7], Fraction(1, 6))
        self.assertEqual(d[2], Fraction(1, 36))
        self.assertEqual(sum(d.values()), Fraction(1))
        self.assertEqual(len(d), 11)

    def test_distribuicao_exata_1d20(self):
        d = distribuicao_exata("1d20")
        self.assertEqual(len(d), 20)
        self.assertTrue(all(v == Fraction(1, 20) for v in d.values()))

    def test_momentos_exatos(self):
        mu, var = momentos_exatos("2d6")
        self.assertEqual((mu, var), (Fraction(7), Fraction(35, 6)))
        mu, var = momentos_exatos("1d20")
        self.assertEqual((mu, var), (Fraction(21, 2), Fraction(133, 4)))

    def test_min_max(self):
        self.assertEqual(minimo_maximo(_parsear("4d6kh1")[0], 0), (1, 6))
        self.assertEqual(minimo_maximo(_parsear("4d6kh3")[0], 0), (3, 18))
        self.assertEqual(minimo_maximo(_parsear("2d6kl1")[0], 3), (4, 9))


# ==========================================================================
# Camada 3 — auditoria
# ==========================================================================
class TesteAuditoria(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xan-aud-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.caminho = os.path.join(self.tmp, "diario.jsonl")

    def test_cadeia_valida(self):
        d = DiarioDeAuditoria(self.caminho)
        for i in range(20):
            d.registrar("rolagem", {"i": i, "total": i + 10}, ator="teste")
        rel = d.verificar()
        self.assertTrue(rel.ok, rel.texto())
        self.assertEqual(rel.total, 20)
        self.assertNotEqual(rel.hash_cabeca, HASH_GENESIS)

    def test_reabrir_preserva_a_cadeia(self):
        d = DiarioDeAuditoria(self.caminho)
        for i in range(5):
            d.registrar("evento", {"i": i})
        cabeca = d.cabeca
        d2 = DiarioDeAuditoria(self.caminho, criar=False)
        self.assertEqual(d2.cabeca, cabeca)
        self.assertTrue(d2.verificar().ok)
        d2.registrar("evento", {"i": 5})
        self.assertEqual(len(d2), 6)

    def test_adulteracao_de_conteudo_e_detectada(self):
        d = DiarioDeAuditoria(self.caminho)
        for i in range(6):
            d.registrar("rolagem", {"total": 5 + i, "dificuldade": 15})
        with open(self.caminho, "r", encoding="utf-8") as fh:
            linhas = fh.readlines()
        bruto = json.loads(linhas[3])
        bruto["conteudo"]["dificuldade"] = 4   # o mestre baixou a DD depois
        linhas[3] = canonico(bruto) + "\n"
        with open(self.caminho, "w", encoding="utf-8") as fh:
            fh.writelines(linhas)
        rel = DiarioDeAuditoria(self.caminho, criar=False).verificar()
        self.assertFalse(rel.ok)
        self.assertEqual(rel.primeira_falha, 3)
        self.assertIn("adulterado", rel.motivo)

    def test_canonico_estavel_sob_roundtrip(self):
        """REGRESSÃO de bug real: chaves inteiras quebravam a verificação.

        ``json.dumps({1:..,10:..}, sort_keys=True)`` ordena numericamente na
        escrita e lexicograficamente depois do round-trip, então o hash gravado
        não batia com o recalculado — um falso positivo de adulteração que
        condenava um diário legítimo. Encontrado numa mesa de verdade ao gravar
        uma tabela de 20 entradas com chaves 1..20.
        """
        import json as _json
        casos = [
            {1: "a", 2: "b", 10: "j", 20: "t"},
            {20: "t", 10: "j", 2: "b", 1: "a"},
            {i: f"entrada {i}" for i in range(1, 21)},
            {"x": {1: "a", 10: "j"}, "y": [1, {2: "b"}]},
            {True: "v", False: "f", None: "n", 1.5: "f"},
            {"a": 1, "b": [1, 2, {"c": (3, 4)}]},
            [], {}, "", 0, -1, 3.5, None, True,
            [{"k": {7: [1, {8: "v"}]}}],
        ]
        for c in casos:
            escrita = canonico(c)
            releitura = canonico(_json.loads(escrita))
            self.assertEqual(escrita, releitura,
                             f"canonico instável sob round-trip para {c!r}")

    def test_canonico_ignora_a_ordem_de_insercao(self):
        self.assertEqual(canonico({1: "a", 2: "b", 3: "c"}),
                         canonico({3: "c", 1: "a", 2: "b"}))
        self.assertEqual(canonico({"z": 1, "a": 2}), canonico({"a": 2, "z": 1}))

    def test_canonico_recusa_ambiguidade(self):
        with self.assertRaises(ValueError):
            canonico({1: "a", "1": "b"})           # colisão na forma canônica
        with self.assertRaises(ValueError):
            canonico({float("nan"): 1})            # não-finito
        with self.assertRaises(ValueError):
            canonico({float("inf"): 1})
        with self.assertRaises(ValueError):
            canonico({"x": float("nan")})
        with self.assertRaises(TypeError):
            canonico({(1, 2): "x"})                # chave não serializável

    def test_registro_com_chaves_inteiras_verifica_depois_de_reaberto(self):
        """O caso que falhou na mesa: gravar, fechar, reabrir, verificar."""
        tabela = {i: f"evento {i}" for i in range(1, 21)}
        diario = DiarioDeAuditoria(self.caminho)
        diario.registrar("tabela_declarada",
                         {"entradas": tabela, "dado": "1d20"}, ator="mestre")
        diario.registrar("rolagem", {"resultado": 5, "tabela": tabela},
                         ator="mundo")
        rel = DiarioDeAuditoria(self.caminho, criar=False).verificar()
        self.assertTrue(rel.ok, rel.motivo)

    def test_remocao_de_registro_e_detectada(self):
        d = DiarioDeAuditoria(self.caminho)
        for i in range(8):
            d.registrar("rolagem", {"i": i})
        with open(self.caminho, "r", encoding="utf-8") as fh:
            linhas = fh.readlines()
        del linhas[2]
        with open(self.caminho, "w", encoding="utf-8") as fh:
            fh.writelines(linhas)
        rel = DiarioDeAuditoria(self.caminho, criar=False).verificar()
        self.assertFalse(rel.ok)
        self.assertTrue(
            "elo quebrado" in rel.motivo or "índice esperado" in rel.motivo,
            rel.motivo)

    def test_reamplaçar_cabeca_e_detectado(self):
        d = DiarioDeAuditoria(self.caminho)
        d.registrar("rolagem", {"total": 1})
        with open(self.caminho, "r", encoding="utf-8") as fh:
            linhas = fh.readlines()
        bruto = json.loads(linhas[0])
        bruto["prev"] = "f" * 64
        bruto["hash"] = hash_de(canonico({k: bruto[k] for k in
                                          ("i", "t", "tipo", "ator", "conteudo", "prev")}))
        linhas[0] = canonico(bruto) + "\n"
        with open(self.caminho, "w", encoding="utf-8") as fh:
            fh.writelines(linhas)
        rel = DiarioDeAuditoria(self.caminho, criar=False).verificar()
        self.assertFalse(rel.ok)

    def test_merkle_e_estavel_e_sensivel(self):
        d = DiarioDeAuditoria(self.caminho)
        for i in range(9):
            d.registrar("rolagem", {"i": i})
        raiz1 = d.raiz_merkle()
        self.assertEqual(raiz1, DiarioDeAuditoria(self.caminho, criar=False).raiz_merkle())
        d.registrar("rolagem", {"i": 9})
        self.assertNotEqual(raiz1, d.raiz_merkle())

    def test_selagem_publica(self):
        d = DiarioDeAuditoria(self.caminho)
        d.registrar("rolagem", {"total": 12})
        selo = os.path.join(self.tmp, "selos.txt")
        cabeca = d.selar(selo, nota="sessão de teste")
        with open(selo, encoding="utf-8") as fh:
            linha = json.loads(fh.read().strip())
        self.assertEqual(linha["cabeca"], cabeca)
        self.assertEqual(linha["nota"], "sessão de teste")

    def test_conteudo_invalido(self):
        d = DiarioDeAuditoria(self.caminho)
        with self.assertRaises(TypeError):
            d.registrar("x", ["não é dict"])  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            d.registrar("", {})

    def test_canonico_deterministico(self):
        self.assertEqual(canonico({"b": 1, "a": 2}), canonico({"a": 2, "b": 1}))
        self.assertEqual(canonico({"a": "ç"}), '{"a":"ç"}')


# ==========================================================================
# Camada 4 — compromisso
# ==========================================================================
class TesteCompromisso(unittest.TestCase):
    def setUp(self):
        self.aleat = Aleatoriedade(FonteSemeada("compromisso", "t"))
        self.tmp = tempfile.mkdtemp(prefix="xan-comp-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.diario = DiarioDeAuditoria(os.path.join(self.tmp, "d.jsonl"))

    def test_compromisso_verificavel(self):
        c = comprometer({"dd": 17, "regras": []}, self.aleat)
        self.assertTrue(verificar_compromisso(c))
        c2 = comprometer({"dd": 17, "regras": []}, self.aleat)
        self.assertNotEqual(c.token, c2.token, "o sal deve tornar o token único")

    def test_payload_vazio_recusado(self):
        with self.assertRaises(ValueError):
            comprometer({}, self.aleat)

    def test_payload_alterado_nao_confere(self):
        c = comprometer({"dd": 17}, self.aleat)
        from dataclasses import replace
        c_falso = replace(c, payload={"dd": 12})
        self.assertFalse(verificar_compromisso(c_falso))

    def test_fluxo_completo_ok(self):
        decl = Declaracao(
            acao="atacar", ator="Lin", atributo="con", valor_atributo=14,
            bonus_atributo=2, graduacao=3, dificuldade=17,
        )
        for _ in range(10):
            resolver(decl, self.aleat, self.diario)
        self.assertTrue(self.diario.verificar().ok)
        rel = conferir(self.diario)
        self.assertTrue(rel.ok, rel.texto())
        self.assertEqual(rel.compromissos, 10)
        self.assertEqual(rel.rolagens, 10)
        self.assertEqual(rel.revelacoes, 10)

    def test_rolagem_sem_compromisso_e_detectada(self):
        self.diario.registrar("rolagem", {"token": "inexistente", "total": 20})
        rel = conferir(self.diario)
        self.assertFalse(rel.ok)
        self.assertTrue(any("sem compromisso" in p for p in rel.problemas))

    def test_revelacao_adulterada_e_detectada(self):
        decl = Declaracao(acao="x", ator="A", atributo="int",
                          valor_atributo=12, bonus_atributo=1, dificuldade=10)
        resolver(decl, self.aleat, self.diario)
        # reescreve a revelação com outro payload, mantendo o token
        regs = list(self.diario.registros)
        rev = [r for r in regs if r.tipo == "revelacao"][0]
        novo = rev.como_dict()
        novo["conteudo"]["payload"]["dificuldade"] = 5
        linhas = []
        anterior = HASH_GENESIS
        for r in regs:
            d = r.como_dict()
            if r.indice == rev.indice:
                d = novo
            d["prev"] = anterior
            payload = {k: d[k] for k in ("i", "t", "tipo", "ator", "conteudo", "prev")}
            d["hash"] = hash_de(canonico(payload))
            anterior = d["hash"]
            linhas.append(canonico(d))
        with open(self.diario.caminho, "w", encoding="utf-8") as fh:
            fh.write("\n".join(linhas) + "\n")
        d2 = DiarioDeAuditoria(self.diario.caminho, criar=False)
        self.assertTrue(d2.verificar().ok, "a cadeia em si foi refeita de forma válida")
        rel = conferir(d2)
        self.assertFalse(rel.ok, "mas o protocolo commit-reveal tem que acusar")
        self.assertTrue(any("não bate com o token" in p for p in rel.problemas))


# ==========================================================================
# Camada 5 — regras
# ==========================================================================
class TesteRegistroDeRegras(unittest.TestCase):
    def test_codigos_bem_formados(self):
        for codigo, regra in REGISTRO.items():
            self.assertIn(":", codigo)
            self.assertEqual(codigo, regra.codigo)
            self.assertTrue(regra.capitulo)
            self.assertTrue(len(regra.descricao) > 10)
            self.assertLessEqual(regra.limite[0], regra.limite[1])

    def test_relacao_elemental_completa(self):
        casos = {
            ("metal", "madeira"): "supera",
            ("madeira", "metal"): "subjugado",
            ("madeira", "fogo"): "gerador",
            ("fogo", "madeira"): "gerado",
            ("fogo", "fogo"): "igual",
            ("nenhum", "fogo"): "neutro",
            ("vazio", "metal"): "neutro",
        }
        for (a, b), esperado in casos.items():
            self.assertEqual(relacao_elemental(a, b), esperado, f"{a}×{b}")

    def test_ciclo_wuxing_e_matematicamente_fechado(self):
        elementos = ("metal", "madeira", "agua", "fogo", "terra")
        for a in elementos:
            relacoes = Counter(relacao_elemental(a, b) for b in elementos)
            self.assertEqual(relacoes["supera"], 1)
            self.assertEqual(relacoes["subjugado"], 1)
            self.assertEqual(relacoes["gerador"], 1)
            self.assertEqual(relacoes["gerado"], 1)
            self.assertEqual(relacoes["igual"], 1)
            # e a relação é anti-simétrica em valor
            for b in elementos:
                self.assertEqual(
                    valor_de("ELEMENTO:RELACAO",
                             {"elemento_atacante": a, "elemento_alvo": b}),
                    -valor_de("ELEMENTO:RELACAO",
                              {"elemento_atacante": b, "elemento_alvo": a}),
                )

    def test_supressao_de_reino(self):
        f = {"reino_atacante": 7, "reino_alvo": 4}
        self.assertEqual(valor_de("REINO:SUPRESSAO", f), 6)
        self.assertEqual(valor_de("REINO:SUPRESSAO",
                                  {"reino_atacante": 0, "reino_alvo": 12}), -10)
        self.assertEqual(valor_de("REINO:SUPRESSAO",
                                  {"reino_atacante": 12, "reino_alvo": 0}), 10)

    def test_regra_desconhecida_e_recusada(self):
        with self.assertRaises(ModificadorIlegal):
            valor_de("NARRATIVA:PORQUE_SIM", {})
        with self.assertRaises(ModificadorIlegal):
            valor_de("MESTRE:EU_QUERO", {})

    def test_fato_ausente_e_recusado(self):
        with self.assertRaises(ModificadorIlegal):
            valor_de("ELEMENTO:RELACAO", {"elemento_atacante": "fogo"})

    def test_fato_de_tipo_errado_e_recusado(self):
        with self.assertRaises(ModificadorIlegal):
            valor_de("POSICAO:FLANCO", {"flanqueado": "sim"})
        with self.assertRaises(ModificadorIlegal):
            valor_de("ESTADO:EXAUSTAO", {"qi_atual": 1.5, "qi_maximo": 100})
        with self.assertRaises(ModificadorIlegal):
            valor_de("AMBIENTE:LUZ", {"luz": "mais ou menos escura"})
        with self.assertRaises(ModificadorIlegal):
            valor_de("REINO:SUPRESSAO", {"reino_atacante": 99, "reino_alvo": 0})

    def test_fato_contrario_nao_da_bonus(self):
        """Declarar a regra não dá bônus se o fato não a sustenta."""
        self.assertEqual(
            valor_de("POSICAO:FLANCO", {"flanqueado": True}), 2)
        self.assertEqual(
            valor_de("POSICAO:FLANCO", {"flanqueado": False}), 0)
        self.assertEqual(
            valor_de("POSICAO:TERRENO", {"terreno": "baixo"}), -1)
        self.assertEqual(
            valor_de("POSICAO:EMBOSCADA", {"oculto": True, "percebido": True}), 0)
        self.assertEqual(
            valor_de("POSICAO:EMBOSCADA", {"oculto": True, "percebido": False}), 2)

    def test_exclusividade(self):
        self.assertTrue(conflitos(("COMBATE:GUARDA_TOTAL", "COMBATE:DEFESA_DECLARADA")))
        self.assertFalse(conflitos(("COMBATE:GUARDA_TOTAL", "POSICAO:FLANCO")))

    def test_toda_regra_tem_valor_dentro_do_limite(self):
        """Exercita cada regra com fatos plausíveis e confere o limite."""
        exemplos = {
            "ELEMENTO:RELACAO": {"elemento_atacante": "fogo", "elemento_alvo": "metal"},
            "REINO:SUPRESSAO": {"reino_atacante": 9, "reino_alvo": 3},
            "POSICAO:TERRENO": {"terreno": "alto"},
            "POSICAO:FLANCO": {"flanqueado": True},
            "POSICAO:EMBOSCADA": {"oculto": True, "percebido": False},
            "ALVO:COBERTURA": {"cobertura": "total"},
            "ALVO:PASSOS_LEVES": {"passos_leves": True},
            "ALCANCE:FAIXA": {"alcance": "extremo"},
            "ESTADO:FERIMENTO": {"ferimento": "agonizando"},
            "ESTADO:VISAO": {"visao": "cego"},
            "ESTADO:EXAUSTAO": {"qi_atual": 10, "qi_maximo": 100},
            "ESTADO:DESVIO_DE_QI": {"desvio_de_qi": True},
            "ESTADO:DEMONIO_INTERIOR": {"demonio_interior": True},
            "ESTADO:IMOBILIZADO": {"imobilizado": True},
            "AMBIENTE:LUZ": {"luz": "trevas"},
            "AMBIENTE:CLIMA": {"clima": "nevasca"},
            "AMBIENTE:FENGSHUI": {"fengshui": "muito_auspicioso"},
            "AMBIENTE:DENSIDADE_QI": {"densidade_qi": "terra_imortal"},
            "AMBIENTE:FORMACAO": {"formacao": "hostil"},
            "RECURSO:ELIXIR": {"elixir": "celestial"},
            "RECURSO:TALISMA": {"talisma": "maior"},
            "RECURSO:ARTEFATO": {"artefato": "primordial"},
            "PREPARO:MEDITACAO": {"meditou": True},
            "PREPARO:ESTUDO_PREVIO": {"estudou": True},
            "PREPARO:QUEIMA_LONGEVIDADE": {"anos_queimados": 40},
            "SOCIAL:FACE": {"face": "desonrada"},
            "SOCIAL:DISPOSICAO": {"disposicao": "inimigo_jurado"},
            "SOCIAL:HIERARQUIA": {"hierarquia": "superior"},
            "SOCIAL:DIVIDA_DE_HONRA": {"divida_de_honra": "grande"},
            "SOCIAL:SEGREDO_EXPOSTO": {"segredo_exposto": True},
            "DESEJO:PRIORIDADE": {"camada": "dever"},
            "FACCAO:RELACAO": {"relacao_de_faccoes": "guerra"},
            "COMBATE:SURPRESA": {"alvo_surpreso": True},
            "COMBATE:GUARDA_TOTAL": {"guarda_total": True},
            "COMBATE:ACOES_MULTIPLOS": {"acoes_no_turno": 3},
            "COMBATE:DEFESA_DECLARADA": {"acao_de_defesa": True},
        }
        self.assertEqual(set(exemplos), set(REGISTRO),
                         "toda regra registrada precisa ter exemplo de teste")
        for codigo, fatos in exemplos.items():
            v = valor_de(codigo, fatos)
            lo, hi = REGISTRO[codigo].limite
            self.assertTrue(lo <= v <= hi, f"{codigo} → {v} fora de [{lo},{hi}]")


# ==========================================================================
# Camada 6 — resolução
# ==========================================================================
class TesteResolucao(unittest.TestCase):
    def setUp(self):
        self.aleat = Aleatoriedade(FonteSemeada("resolucao", "t"))
        self.tmp = tempfile.mkdtemp(prefix="xan-res-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.diario = DiarioDeAuditoria(os.path.join(self.tmp, "d.jsonl"))

    def _decl(self, **kw):
        base = dict(
            acao="golpe de espada", ator="Lin Yue", atributo="con",
            valor_atributo=14, bonus_atributo=2, pericia="espada",
            graduacao=3, dificuldade=17,
            regras=("ELEMENTO:RELACAO", "REINO:SUPRESSAO"),
            fatos={"elemento_atacante": "metal", "elemento_alvo": "madeira",
                   "reino_atacante": 4, "reino_alvo": 4},
            contexto={"reino": 4},
        )
        base.update(kw)
        return Declaracao(**base)

    def test_bonus_de_atributo(self):
        esperados = {1: -5, 8: -1, 9: -1, 10: 0, 11: 0, 12: 1, 14: 2,
                     20: 5, 30: 10}
        for valor, b in esperados.items():
            self.assertEqual(bonus_de_atributo(valor), b, f"attr {valor}")
        with self.assertRaises(DeclaracaoInvalida):
            bonus_de_atributo(0)
        with self.assertRaises(DeclaracaoInvalida):
            bonus_de_atributo(31)

    def test_atributos_sao_seis_e_com_elemento(self):
        self.assertEqual(set(ATRIBUTOS), {"per", "con", "cha", "int", "luk", "pot"})
        for a in ATRIBUTOS.values():
            self.assertTrue(a.chines and a.pinyin and a.virtude)

    def test_bonus_negociado_e_recusado(self):
        """O motor não aceita bônus que não decorra do valor do atributo."""
        with self.assertRaises(DeclaracaoInvalida) as ctx:
            Declaracao(acao="x", ator="A", atributo="con", valor_atributo=14,
                       bonus_atributo=8, dificuldade=15)
        self.assertIn("não confere", str(ctx.exception))

    def test_validacoes_da_declaracao(self):
        casos = [
            dict(atributo="sorte"),
            dict(valor_atributo=0, bonus_atributo=bonus_de_atributo(1)),
            dict(valor_atributo=31),
            dict(graduacao=6),
            dict(graduacao=-1),
            dict(dificuldade=0),
            dict(dificuldade=61),
            dict(dificuldade=15.5),
            dict(regras=("NARRATIVA:PORQUE_SIM",)),
            dict(fatos={"elemento_atacante": "ouro"}),
            dict(acao=""),
            dict(ator=""),
        ]
        for extra in casos:
            with self.assertRaises((DeclaracaoInvalida, ModificadorIlegal), msg=str(extra)):
                kw = dict(regras=("ELEMENTO:RELACAO",),
                          fatos={"elemento_atacante": "fogo",
                                 "elemento_alvo": "metal"})
                kw.update(extra)
                self._decl(**kw)

    def test_regra_duplicada_e_exclusiva(self):
        with self.assertRaises(DeclaracaoInvalida):
            self._decl(regras=("POSICAO:FLANCO", "POSICAO:FLANCO"),
                       fatos={"flanqueado": True})
        with self.assertRaises(DeclaracaoInvalida):
            self._decl(regras=("COMBATE:GUARDA_TOTAL", "COMBATE:DEFESA_DECLARADA"),
                       fatos={"guarda_total": True, "acao_de_defesa": True})

    def test_fato_missing_falha_antes_de_gastar_dado(self):
        antes = self.aleat.consumo()
        with self.assertRaises(ModificadorIlegal):
            self._decl(regras=("ELEMENTO:RELACAO",), fatos={"elemento_alvo": "fogo"})
        self.assertEqual(self.aleat.consumo(), antes,
                         "não se gasta entropia em declaração inválida")

    def test_float_proibido_no_caminho_critico(self):
        with self.assertRaises(DeclaracaoInvalida):
            self._decl(fatos={"elemento_atacante": "fogo",
                              "elemento_alvo": "metal", "peso": 1.5})

    def test_aritmetica_do_resultado(self):
        r = resolver(self._decl(), self.aleat)
        esperado = (r.rolagem.total + 2 + 3
                    + sum(m.valor for m in r.modificadores))
        self.assertEqual(r.total, esperado)
        self.assertEqual(r.margem, r.total - 17)
        self.assertEqual(r.sucesso, r.margem >= 0 or r.critico == "toque_do_dao")
        self.assertTrue(r.verificar())

    def test_modificadores_recalculados_dos_fatos(self):
        r = resolver(self._decl(), self.aleat)
        codigos = {m.codigo: m.valor for m in r.modificadores}
        self.assertEqual(codigos.get("ELEMENTO:RELACAO"), 2)   # metal supera madeira
        self.assertNotIn("REINO:SUPRESSAO", codigos)           # 4 vs 4 → 0, omitido

    def test_resultado_imutavel(self):
        r = resolver(self._decl(), self.aleat)
        with self.assertRaises(Exception):
            r.total = 30  # type: ignore[misc]
        with self.assertRaises(Exception):
            r.grau = "triunfo"  # type: ignore[misc]

    def test_resultado_adulterado_e_bloqueado(self):
        r = resolver(self._decl(), self.aleat)
        from dataclasses import replace
        with self.assertRaises(AssertionError):
            replace(r, total=r.total + 1)
        with self.assertRaises(AssertionError):
            replace(r, margem=r.margem + 1)
        with self.assertRaises(AssertionError):
            replace(r, grau="triunfo")
        with self.assertRaises(AssertionError):
            replace(r, sucesso=not r.sucesso)

    def test_criticos_por_face(self):
        achou1 = achou20 = False
        for _ in range(6000):
            r = resolver(self._decl(), self.aleat)
            if r.face_d20 == 1:
                achou1 = True
                self.assertEqual(r.critico, "desvio")
                self.assertEqual(r.grau, "fracasso_critico")
                self.assertFalse(r.sucesso)
            if r.face_d20 == 20:
                achou20 = True
                self.assertEqual(r.critico, "toque_do_dao")
                self.assertEqual(r.grau, "sucesso_critico")
                self.assertTrue(r.sucesso)
        self.assertTrue(achou1 and achou20)

    def test_escalas_de_margem(self):
        from xan.resolucao import grau_por_margem
        self.assertEqual(grau_por_margem(-1), "fracasso")
        self.assertEqual(grau_por_margem(-50), "fracasso")
        self.assertEqual(grau_por_margem(0), "sucesso")
        self.assertEqual(grau_por_margem(4), "sucesso")
        self.assertEqual(grau_por_margem(5), "sucesso_maior")
        self.assertEqual(grau_por_margem(9), "sucesso_maior")
        self.assertEqual(grau_por_margem(10), "triunfo")

    def test_diario_completo_e_auditavel(self):
        for _ in range(25):
            resolver(self._decl(), self.aleat, self.diario)
        self.assertTrue(self.diario.verificar().ok)
        rel = conferir(self.diario)
        self.assertTrue(rel.ok, rel.texto())
        self.assertEqual(rel.rolagens, 25)

    def test_indice_do_diario_vinculado(self):
        r = resolver(self._decl(), self.aleat, self.diario)
        self.assertIsNotNone(r.indice_no_diario)
        regs = self.diario.por_tipo("rolagem")
        self.assertEqual(regs[-1].indice, r.indice_no_diario)
        self.assertEqual(regs[-1].conteudo["selo"], r.hash_resultado)
        self.assertEqual(regs[-1].conteudo["total"], r.total)

    def test_mesma_semente_mesmos_resultados(self):
        d1 = Declaracao(acao="a", ator="A", atributo="per", valor_atributo=15,
                        bonus_atributo=2, dificuldade=12)
        a1 = Aleatoriedade(FonteSemeada("sessao-1", "mesa"))
        a2 = Aleatoriedade(FonteSemeada("sessao-1", "mesa"))
        seq1 = [resolver(d1, a1).total for _ in range(50)]
        seq2 = [resolver(d1, a2).total for _ in range(50)]
        self.assertEqual(seq1, seq2)

    def test_teste_oposto_e_desempates(self):
        da = Declaracao(acao="atacar", ator="A", atributo="con",
                        valor_atributo=16, bonus_atributo=3, graduacao=4,
                        dificuldade=10)
        dd = Declaracao(acao="defender", ator="D", atributo="con",
                        valor_atributo=14, bonus_atributo=2, graduacao=3,
                        dificuldade=10)
        for _ in range(200):
            r = teste_oposto(da, dd, self.aleat)
            self.assertIn(r.vencedor, ("atacante", "defensor", "empate"))
            if r.atacante.total != r.defensor.total:
                esperado = "atacante" if r.atacante.total > r.defensor.total else "defensor"
                self.assertEqual(r.vencedor, esperado)
            else:
                # totais iguais → desempate por graduação (4 > 3) → atacante
                self.assertEqual(r.vencedor, "atacante")
                self.assertIn("graduação", r.criterio)

    def test_invariantes_estruturais(self):
        rel = verificar_invariantes()
        self.assertTrue(rel.ok, rel.texto())
        self.assertGreater(rel.verificacoes, 100)


# ==========================================================================
# Justiça estatística (versão rápida; a bateria completa fica no CLI)
# ==========================================================================
class TesteJusticaRapida(unittest.TestCase):
    def setUp(self):
        self.aleat = Aleatoriedade(FonteSemeada("justica-rapida", "testes"))

    def test_distribuicao_de_1d20(self):
        t = teste_distribuicao(self.aleat, "1d20", 20_000)
        self.assertGreater(t.p_valor, 1e-6, t.nota)

    def test_distribuicao_de_2d6(self):
        t = teste_distribuicao(self.aleat, "2d6", 20_000)
        self.assertGreater(t.p_valor, 1e-6, t.nota)

    def test_distribuicao_de_4d6kh1(self):
        t = teste_distribuicao(self.aleat, "4d6kh1", 20_000)
        self.assertGreater(t.p_valor, 1e-6, t.nota)

    def test_kh_cl_imparcial(self):
        t = teste_manter_imparcial(self.aleat, "4d6kh1", 15_000)
        self.assertGreater(t.p_valor, 1e-6, t.nota)

    def test_determinismo(self):
        t = teste_determinismo()
        self.assertTrue(t.ok, t.nota)

    def test_imparcialidade_entre_atores(self):
        """O teste central do requisito 'sem vantagem narrativa'."""
        t = teste_imparcialidade_entre_atores(n=3_000)
        self.assertGreater(t.p_valor, 1e-6, t.nota)

    def test_funcoes_especiais_contra_valores_conhecidos(self):
        self.assertAlmostEqual(chi2_p_valor(3.841, 1), 0.05, delta=1e-3)
        self.assertAlmostEqual(chi2_p_valor(5.991, 2), 0.05, delta=1e-3)
        self.assertAlmostEqual(chi2_p_valor(18.307, 10), 0.05, delta=1e-3)
        self.assertAlmostEqual(chi2_p_valor(0.0, 5), 1.0, delta=1e-9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
