# Xan — a mesa de Ondaval

Este repositório guarda uma campanha de RPG de mesa (**GURPS 4ª edição**),
mestrada por um agente para um jogador humano. Tudo que importa vive em
[`ondaval/`](ondaval/).

## Mapa da memória

| Arquivo | O que é |
|---|---|
| `ondaval/00-MEMORIA.md` | Protocolo do mestre — **leia primeiro** |
| `ondaval/01-mundo-ondaval.md` | Cânone do mundo: cosmogonia, fé, Fina, geografia |
| `ondaval/02-marzagao-lomba.md` | A cidade onde a campanha começa |
| `ondaval/03-npcs.md` | Quem vive na Lomba — desejos, medos, rotinas |
| `ondaval/04-regras-da-mesa.md` | Combinados, regras da casa, pendências |
| `ondaval/05-ficha-pj.md` | Ficha do personagem do jogador |
| `ondaval/06-cronica.md` | Crônica viva — tudo que aconteceu na mesa |
| `ondaval/07-segredos-mestre.md` | **Somente mestre.** Segredos e relógio da campanha |
| `ondaval/rolar.py` | Dados oficiais da mesa (aleatoriedade criptográfica) |

## Rolar dados

```bash
python3 ondaval/rolar.py                # 3d6 solto
python3 ondaval/rolar.py 3d6 12         # teste contra Habilidade 12
python3 ondaval/rolar.py 3d6 12 14      # confronto rápido 12 × 14
python3 ondaval/rolar.py 2d6+1          # expressão livre NdN±M
python3 ondaval/rolar.py 3d6 14 --n 4   # quatro testes
```

## Estado atual

Campanha criada (Turno 0). Aguardando: ficha do PJ, gancho inicial e nome.
Detalhes em `ondaval/04-regras-da-mesa.md § Pendências`.
