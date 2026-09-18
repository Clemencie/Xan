# Mesa da Grande Cruzada — Warhammer 40K, pré-Heresia

Campanha de RPG de mesa (**Warhammer 40.000, século 30 — antes da Heresia
do Horus**), mestrada por um agente para um jogador humano. Fidelidade à
lore é lei da mesa; datas canônicas conferidas (Lexicanum/wiki, set/2026).

## Mapa da memória (`imperium/`)

| Arquivo | O que é |
|---|---|
| `imperium/00-MEMORIA.md` | Protocolo do mestre — **leia primeiro** |
| `imperium/01-universo-40k.md` | O Imperium, a Grande Cruzada, datas canônicas |
| `imperium/02-astartes.md` | A criação do Astartes: 19 órgãos, estado do PJ, regras das memórias |
| `imperium/03-sistema.md` | Deathwatch (recomendado) / Wrath & Glory + pendências |
| `imperium/04-npcs.md` | NPCs (a preencher após a escolha da Legião) |
| `imperium/05-cronica.md` | Crônica viva — histórico completo da mesa |
| `imperium/06-segredos-mestre.md` | **Somente mestre** |
| `imperium/rolar.py` | Dados oficiais (entropia criptográfica) |

## Rolar dados

```bash
python3 imperium/rolar.py 1d100 55      # teste d100 contra 55 (graus a cada 10)
python3 imperium/rolar.py 1d100 55 40   # teste oposto 55 × 40
python3 imperium/rolar.py 8d6 --wng     # pool Wrath & Glory (Dado de Fúria)
python3 imperium/rolar.py 2d10+10       # dano de bolter (expressão livre)
```

## Estado atual

Sistema **Deathwatch** ✅ · início **~950.M30** ✅ · memórias **só
instinto** ✅. PJ em criação: **Astartes neófito** (lote 6–9 implantado).
Faltam: **Legião** (cardápio completo em `imperium/07-legioes.md`) e
**nome**. Primeira cena planejada: o despertar no Apotecarion.
