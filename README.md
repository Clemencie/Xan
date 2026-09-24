# XAN — Mesa solo de Wrath & Glory na Grande Cruzada (30K)

> *"I was there the day Horus slew the Emperor."* — esta mesa começa muito antes desse dia.

Este repositório é o **sistema da nossa campanha solo**: eu (o Mestre, agente Arena) narro, e você joga
com um **Legionário Astartes de Tier 2** no fim da **Grande Cruzada**, seguindo os acontecimentos
dos livros da **Heresia de Hórus** (começando por *Horus Rising*).

## Como funciona a mesa

- **Sistema:** Warhammer 40.000: Wrath & Glory (Cubicle 7, d6 dice pool), adaptado para o **31º milênio**.
- **Mestre:** eu narro cenas, interpreto NPCs, controlo inimigos e o recurso **Ruína**.
- **Jogador:** você — um Legionário Astartes. Você declara intenções; **eu rolo todos os dados
  de forma transparente** com o motor em `motor/` e mostro cada dado.
- **Ritmo:** jogamos aqui no chat, uma ação por vez, com cenas curtas e cliffhangers.

## Leia nesta ordem

1. `sistema/01-regras-wrath-glory.md` — o núcleo do Wrath & Glory (testes, Wrath, Glória, Ruína, combate).
2. `sistema/02-grande-cruzada-30k.md` — a adaptação para 30K: Verdade Imperial, Legiões, linha do tempo.
3. `sistema/03-criacao-personagem.md` — criação do seu Legionário (Tier 2).
4. `sistema/04-protocolo-mesa.md` — como jogamos no chat (formato de turno, comandos, recursos).
5. `fichas/ficha-jogador.md` — a sua ficha (preenchida após você escolher a Legião).
6. `campanha/campanha.md` — a bíblia da campanha: premissa, arcos, NPCs, bancos de Glória/Ruína.

## O motor de dados

`motor/wg.py` (Python 3, sem dependências) executa testes e dano exatamente pelas regras da mesa:

```bash
python3 -m motor.wg teste --pool 8 --dn 3        # teste com 1 dado de Wrath
python3 -m motor.wg dano --base 10 --ed 2 --res 8 --tough 4
python3 -m motor.wg derivados --tier 2 --tough 4 --init 4 --will 3 --armadura 3
python3 -m motor.wg selftest
```

Toda rolagem feita pelo Mestre no chat segue este motor — mesmos números, mesma lógica.

## Estado da campanha

- **Era:** ~000.M31 — Triunfo de Ullanor recente; Hórus é o novo Warmaster.
- **Livro atual:** *Horus Rising* (Livro 1) — a 63ª Expedição parte para a Conformidade de 63-19.
- **Personagem:** a definir — escolha sua Legião (recomendação do Mestre: **Luna Wolves**).

O Imperador protege. Ou, como se diz nesta era de razão: **a Verdade Imperial prevalecerá.**
