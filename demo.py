"""
demo.py — prova de que o motor gira de ponta a ponta sobre Mutantes & Malfeitores 3e.
Rode:  python3 demo.py
"""
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "mm3"))
sys.path.insert(0, RAIZ)

import dados
import heroi
import encontros
import heroi_npc
from mundo import FACCOES
from regras import TABELA_CD, medida


def titulo(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


titulo("1 · MOTOR DE DADOS")
print("d100:", dados.d(100), "| 3d6:", dados.rol(6, 3), "| d20+3:", dados.d20(3))
o = dados.oraculo(70, caos=5)
print(f"oráculo (provável, caos 5): limiar {o['limiar']}, rolou {o['rolagem']} -> {o['resposta']}")
c = dados.cena(5)
print(f"teste de cena (caos 5): d10 {c['dado']} -> {c['resultado']}")
p = dados.peso_narrativo()
print(f"peso narrativo: d10 {p['d10']} -> T{p['tier']} {p['tier_nome']}")
print(f"Tabela de Medidas: graduação 9 = {medida(9, 'massa')} / {medida(9, 'tempo')} / {medida(9, 'distancia')}")


titulo("2 · FICHA — NP 10, 150 pontos de poder, os cinco limites conferidos")
h = heroi.criar(
    nome="Rafael Duarte", codinome="Cardume", np=10,
        origem="sobrevivente da Maré", motivacao="Responsabilidade",
        complicacoes=["Responsabilidade", "Identidade", "Relacionamento"],
        # 42 pp em habilidades (21 graduações x 2 pp)
        habilidades={"Força": 4, "Vigor": 4, "Agilidade": 3, "Destreza": 2,
                     "Luta": 3, "Intelecto": 1, "Prontidão": 3, "Presença": 1},
        # 28 pp em defesas. O bônus comprado de Resistência é ZERO: quem dá é o
        # poder Proteção 6. Resistência = Vigor 4 + Proteção 6 = 10, e Esq+Res = 20, no teto.
        defesas={"Esquiva": 6, "Aparar": 5, "Fortitude": 2, "Vontade": 5},
        # 20 pp em perícias (40 graduações, nenhuma passando de NP+10)
        pericias={"Acrobacia": 8, "Percepção": 10, "Furtividade": 6,
                  "Combate Corpo-a-Corpo": 12, "Intimidação": 8,
                  "Especialidade (História da Maré)": 6},
        # 9 pp em vantagens
        vantagens={"Esquiva Fabulosa": True, "De Pé": True, "Duro de Matar": True,
                   "Destemido": True, "Iniciativa Aprimorada": 3, "Equipamento": 2},
        # 63 pp em poderes
        poderes={
            "Maré Cheia": {"efeito": "Dano", "grad": 10, "ataque": 10, "extras": 1,
                           "rotulo": "água prensada em área"},
            "Pele de Sal": {"efeito": "Proteção", "grad": 6},
            "Correnteza": {"efeito": "Movimento", "grad": 4},
            "Fôlego de Fundo": {"efeito": "Imunidade", "grad": 3},
            "Ressaca": {"efeito": "Aflição", "grad": 7, "ataque": 7,
                        "rotulo": "corrente que derruba"},
            "Sentido da Maré": {"efeito": "Sentidos", "grad": 10},
            "Maré Alta": {"efeito": "Aumentar Característica", "grad": 6,
                          "alvo": "Força", "rotulo": "força da ressaca"},
        },
)
est = heroi.Estado().carregar()
est.d["heroi"] = h
est.d["local"] = "Porto Velho, Baía de Santa Clara"
est.d["hora"] = "madrugada"
_trama = "A lista de registrados vazou; nove nomes já morreram 'de acidente'"
if _trama not in est.d["tramas"]:
    est.d["tramas"].append(_trama)
print(est.ficha())
print("\nGastos detalhados:", {k: int(v) for k, v in h["gastos_detalhados"].items()})
print(f"Limites de NP 10: {h['limites_np']}")


titulo("3 · FICHA ILEGAL — o validador barra e diz o porquê")
for rotulo, kwargs in [
    ("perícia acima de NP+10", dict(pericias={"Acrobacia": 15}, habilidades={"Agilidade": 8})),
    ("ataque + efeito acima de 2xNP", dict(poderes={"Tiro": {"efeito": "Dano", "grad": 15, "ataque": 12}})),
    ("Esquiva + Resistência acima de 2xNP", dict(habilidades={"Agilidade": 10, "Vigor": 10},
                                                 defesas={"Esquiva": 10, "Resistência": 10})),
]:
    try:
        heroi.criar(nome="Teste", np=10, origem="t", motivacao="Justiça",
                    complicacoes=["Identidade", "Segredo"], **kwargs)
        print(f"  ✗ {rotulo}: PASSOU (não devia)")
    except ValueError as e:
        print(f"  ✓ {rotulo}: recusada — {str(e)[17:120]}")


titulo("4 · DOSAGEM DE PdM — o mesmo mundo, cinco profundidades")
for tier in range(5):
    n = heroi_npc.gerar("linha_vermelha", tier, np=8 if tier < 3 else 12)
    print(dados._fmt_pdm(n))
    print()

print("--- e três formas diferentes ---")
for forma, rot in [("humano", None), ("animal", "gaivota de asa cinzenta"),
                   ("objeto", "freezer do subsolo"), ("ambiente", None)]:
    n = heroi_npc.gerar("coro", 3, np=9, forma=forma, rotulo=rot)
    print(dados._fmt_pdm(n))
    print()


titulo("5 · ENCONTROS — filtrados por terreno e hora")
for terreno, hora in [("porto", "madrugada"), ("zona_quarentena", "noite"), ("hospital", "tarde")]:
    e = encontros.encontrar(terreno, hora)
    print(f"[{terreno}/{hora}] {e['o_que']}  x{e['quantidade']}  "
          f"NP {e['np_faixa']}  T{e['tier']}  âncora: {e['ancora']}")
    for n in e["npcs"]:
        print(dados._fmt_pdm(n, "    "))
    print()


titulo("6 · COMBATE — Cardume contra o líder do bando")
lider = heroi_npc.gerar("linha_vermelha", 3, np=12, papel="líder")
print("OPONENTE:")
print(dados._fmt_pdm(lider, "  "))
def_alvo = lider["defesas"]["Aparar"] if "defesas" in lider else 22

print(f"\nDefesa do alvo: {def_alvo}")
print("Regra do livro: 20 natural é sempre acerto e sobe um grau; 1 natural é sempre falha.\n")
for turno in range(1, 6):
    a = heroi.ataque(h, "Maré Cheia", defesa_alvo=def_alvo)
    txt = (f"turno {turno}: Maré Cheia — d20 {a['d20']}, total {a['total']} vs {def_alvo} -> "
           f"{'ACERTA' if a['acertou'] else 'ERRA'}")
    if a["critico"]:
        txt += " [CRÍTICO]"
    if a["falha_critica"]:
        txt += " [FALHA CRÍTICA]"
    print(txt)
    if a["acertou"]:
        r = heroi.resistencia_alvo(lider["defesas"]["Resistência"] - 15 if "defesas" in lider else 5,
                                   a["dano_grad"])
        print(f"    salvamento de Resistência do alvo: d20 {r['d20']} + "
              f"{(lider['defesas']['Resistência'] - 15) if 'defesas' in lider else 5} "
              f"vs CD {r['cd']} -> {r['resultado']} ({r['graus']:+d} grau)")

titulo("7 · ESFORÇO EXTRA E PONTOS HEROICOS (regras do livro)")
print("esforço extra 1:", heroi.esforco_extra(h, "bonus"))
print("esforço extra 2:", heroi.esforco_extra(h, "bonus"))
print("pontos heroicos:", h["pontos_heroicos"])
print("recuperar:", heroi.gastar_ponto_heroico(h, "recuperar"))
print("condições agora:", h["condicoes"] or ["normal"])
print("complicação aparece ->", heroi.ganhar_ponto_heroico(h, "Identidade: alguém o reconheceu sem máscara"))
print("pontos heroicos:", h["pontos_heroicos"])

titulo("8 · ESTADO PERSISTENTE")
arq = est.salvar()
print("salvo em:", arq)
print(heroi.Estado().carregar().ficha())
