# 03 — SISTEMA (Warhammer RPG) + PENDÊNCIAS

> **Arquivo 03.** Recomendação da casa: **Deathwatch (FFG)** — o RPG
> clássico de viver um Astartes, d100 percentil. Alternativa: **Wrath &
> Glory** (Cubicle 7, d6). A confirmar com o jogador.

## Deathwatch (FFG) — como funciona

- **Teste:** role **d100 ≤ alvo** (característica + treino + modificadores).
  **Graus de sucesso:** cada 10 completos abaixo do alvo = +1 grau (o
  primeiro sucesso vem do "≤ alvo"). **100 natural falha sempre.**
- **Características (em dezenas):** Armas Corpo a Corpo (WS), Armas de
  Fogo (BS), Força (S), Resistência (T), Agilidade (AG), Inteligência
  (Int), Percepção (Per), Vontade (WP), Carisma (Fel).
- **Astartes completo:** Força/Resistência ~45 **com Unnatural ×2** (o
  bônus derivado dobra — dá dano e absorção de transumano), ~30 Wounds,
  armadura de poder (AP ~12, sistemas integrados: vida, autosenses,
  +Força), bolter 2d10+10 Tearing Pen 6.
- **Testes opostos:** ambos rolam; vence o melhor grau de sucesso (com
  penalidade/bônus de situação).
- **Adaptação de casa para NEÓFITO (fiel ao momento da campanha):** ficha
  intermediária — Força/Resistência já acima de mortal (~35–40) sem os
  Unnaturais completos; sem armadura de poder (sem Carapaça); **cada fase
  de implante recuperada é um marco**: concede os bônus do órgão como
  talento/traço (ex.: Occulobe → visão no escuro real; Progenoides →
  status de irmão pleno; Carapaça Negra → armadura de poder + template
  cheio Deathwatch). Montagem numérica final na primeira sessão.

## Wrath & Glory (alternativa)

- Pool de **d6** = atributo + perícia; **4–5 = 1 Ícone, 6 = 2 Ícones**;
  atingir a **DN** (padrão 3) = sucesso. **Dado de Fúria** (1 por rolagem):
  6 = **Glória**, 1 = **Complicação**. Sistema de Tier e "comprar
  sucesso". Astartes jogáveis como arquétipo Battle-Brother.

## Os dados oficiais da mesa

```bash
python3 imperium/rolar.py 1d100 55      # teste d100 contra 55 (graus a cada 10)
python3 imperium/rolar.py 1d100 55 40   # teste oposto 55 × 40
python3 imperium/rolar.py 8d6 --wng     # pool W&G (ícones + Dado de Fúria)
python3 imperium/rolar.py 2d10+10       # dano de bolter, expressão livre
python3 imperium/rolar.py 3d10 --n 4    # repetições
```

## Mortalidade

- **Padrão Warhammer (assumida): ALTA.** Astartes é transumano, não
  imortal; a galáxia mata gente melhor que você todo dia. Deseja menos?
  Diga, e calibro.

## Pendências (resolver com o jogador)

- [ ] **Sistema:** Deathwatch (recomendado) ou Wrath & Glory.
- [ ] **Legião** (gene-seed define a ficha, o temperamento herdado e a
  campanha). As 18:
  I Dark Angels (Leão El'Jonson) · III Filhos do Imperador (Fulgrim) ·
  IV Guerreiros de Ferro (Perturabo) · V Cicatrices Brancas (Jaghatai
  Khan) · VI Lobos Espaciais (Leman Russ) · VII Punhos Imperiais (Rogal
  Dorn) · VIII Senhores da Noite (Konrad Curze) · IX Anjos Sanguinários
  (Sanguinius) · X Mãos de Ferro (Ferrus Manus) · XII Devoradores de
  Mundos (Angron) · XIII Ultramarines (Roboute Guilliman) · XIV Guarda da
  Morte (Mortarion) · XV Mil Filhos (Magnus, o Vermelho) · XVI Luna
  Wolves (Horus) · XVII Word Bearers (Lorgar) · XVIII Salamandras
  (Vulkan) · XIX Raven Guard (Corax) · XX Alpha Legion (Alpharius).
  *(II e XI estão expurgados dos registros.)*
- [ ] **Data de início:** 998.M30 (padrão recomendado), antes (~950.M30)
  ou véspera de Ullanor (999.M30).
- [ ] **Matiz das memórias:** só sonhos / sonhos + 1 eco mecânico por
  sessão / instinto puro sem mecânica.
- [ ] **Nome do neófito** (e mundo de recrutamento — pode ser da Legião
  escolhida ou um mundo conquistado na Cruzada).
- [ ] **Mortalidade:** Warhammer ALTA (assumida) — confirmar.

## Registro de decisões da mesa

| Data real | Decisão |
|---|---|
| 17–18/09/2026 | Turnos 0–2: mundos "Ondaval" e "Vespera" (ver `05-cronica.md`). |
| 18/09/2026 | **Turno 3: recriação total** — Warhammer 40K pré-Heresia, PJ neófito Astartes pós-cirurgia com memórias do mundo real (fundo), sistema Warhammer a confirmar, lore-fidelidade como lei. Pasta `imperium/`. |
