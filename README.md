# Vespera — a mesa

Este repositório guarda uma campanha de RPG de mesa (**GURPS 4ª edição**,
cenário futurista), mestrada por um agente para um jogador humano. Tudo que
importa vive em [`vespera/`](vespera/).

## Mapa da memória

| Arquivo | O que é |
|---|---|
| `vespera/00-MEMORIA.md` | Protocolo do mestre — **leia primeiro** |
| `vespera/01-universo.md` | Cânone: da Centelha (Ano 1) ao presente (Ano 6.047) |
| `vespera/02-alvora-baixada.md` | A cidade onde a campanha começa |
| `vespera/03-povos-e-racas.md` | Raças (estilo Pathfinder), custos GURPS, vida média |
| `vespera/04-npcs.md` | Quem vive na Baixada — desejos, medos, rotinas |
| `vespera/05-regras-da-mesa.md` | Combinados, mecânica, **ano de nascimento** |
| `vespera/06-ficha-pj.md` | Ficha do personagem do jogador |
| `vespera/07-cronica.md` | Crônica viva — tudo que aconteceu na mesa |
| `vespera/08-segredos-mestre.md` | **Somente mestre.** Segredos e relógio da campanha |
| `vespera/rolar.py` | Dados oficiais da mesa (aleatoriedade criptográfica) |

## Rolar dados

```bash
python3 vespera/rolar.py                # 3d6 solto
python3 vespera/rolar.py 3d6 12         # teste contra Habilidade 12
python3 vespera/rolar.py 3d6 12 14      # confronto rápido 12 × 14
python3 vespera/rolar.py 2d6+1          # expressão livre NdN±M
python3 vespera/rolar.py 3d6 14 --n 4   # quatro testes
```

## Estado atual

Presente da campanha: **14 de abril de Ano 6.047 da Alvorada**, Baixada de
Alvora, planeta Cindra. PJ em criação — faltam: **raça, ano de nascimento,
molde/conceito, nome e mortalidade** (detalhes em `vespera/05-regras-da-mesa.md
§ Pendências`).
