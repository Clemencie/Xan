# 01 — Núcleo de regras: Wrath & Glory (resumo da mesa)

Baseado no **Wrath & Glory da Cubicle 7** (sistema d6 dice pool), condensado para jogo solo fluido.
Regra de ouro: na dúvida entre fluidez e letra-fria do livro, **a fluidez vence** — o Mestre decide
e anota a decisão em `campanha/campanha.md`.

## O teste básico

Para qualquer ação incerta, monte uma **parada de d6s = Atributo + Perícia (+ bônus)** e role:

| Dado | Nome | Sucessos |
|------|------|----------|
| 1–3 | Falha | 0 |
| 4–5 | Ícone | 1 |
| 6 | Ícone Exaltado | 2 |

Some os sucessos (ícones). Se **≥ DN (Número de Dificuldade)**, sucesso. DN padrão: **3**.
Média: cada dado rende ~2/3 de sucesso — para DN 3 você quer ±5 dados na parada.

- **Margem:** sucessos além do DN podem alimentar *shifts* (abaixo).
- **Comprar sucessos:** fora de situação estressante, em vez de rolar, receba **metade da
  parada (arredondada p/ baixo)** em sucessos automáticos, limitado a **Tier × 2**.
- **Limites de Tier:** bônus máximos de **Tier + 3 dados**; penalidade máxima de **Tier + 3 no DN**.

## O Dado de Wrath (sempre 1 por teste)

Um dos dados da parada é especial (o Mestre o marca com ⚡):

- **⚡ = 1 → Complicação.** Algo dá errado *mesmo se o teste passar*: reforços chegam, a arma
  emperra, um inocente vê demais. O Mestre narra; o jogador pode sugerir.
- **⚡ = 6 → Ponto de Glória para o grupo** + em ataque bem-sucedido, **Crítico**.

Psicologia da mesa: o dado de Wrath existe para que todo teste importante tenha *drama*.

## Shifts (deslocar exaltados)

Cada **6 excedente** (que não faz falta para bater o DN) pode ser *shiftado* para um efeito:

- **Dano extra:** +1 dado de dano (ED) por shift em ataques (uso mais comum).
- **Rapidez:** concluir a tarefa mais rápido.
- **Qualidade:** mais informação, melhor resultado, impressionar testemunhas.
- **Glória:** converter 1 shift em +1 Glória (máx. 1 por teste).

Regra prática: você pode shiftar 6s enquanto os ícones restantes ainda batem o DN
(cada 6 shiftado "custa" 2 ícones da margem).

## Os três recursos

### Ira (Wrath) — individual, começa com 2
Ganha por: boa interpretação, cumprir objetivos, descanso entre operações, arbítrio do Mestre.
Gasta com (1 ponto cada, salvo indicação):
- **Rerolar** todas as falhas de um teste;
- **Recuperar** 1d3+3 Shock;
- **+1d** em teste de Desafio (defy death);
- **Declarar narrativa:** inserir um elemento na cena (sujeito a veto do Mestre).

### Glória (Glory) — pool do grupo
Ganha por: ⚡ = 6, e shifts convertidos. Gasta com:
- **+1d** na parada por ponto (respeita o teto Tier+3);
- **+1 dano** por ponto (sem teto de Tier);
- **Agravar crítico** (aumentar severidade);
- **Tomar a iniciativa** (agir fora da ordem).

### Ruína (Ruin) — recurso do Mestre
O Mestre começa com 0 e ganha com: falhas suas em testes de **Corrupção/Medo**, e ⚡ = 6
dos inimigos. Gasta como Ira+Glória dos NPCs: rerolar, absorver dano, recuperar Shock,
interromper a ordem de iniciativa e ativar **habilidades de Ruína** (poderes especiais de chefes).

> Os bancos de Ira/Glória/Ruína ficam registrados no fim de cada cena e em
> `campanha/campanha.md`. Transparência total, sempre.

## Atributos e perícias

**Atributos:** Strength (Força), Toughness (Vigor), Agility (Agilidade), Initiative (Iniciativa),
Willpower (Vontade), Intellect (Intelecto), Fellowship (Comunhão). **Speed** é deslocamento.

**Perícias da mesa:** Athletics, Awareness, Ballistic Skill, Cunning, Deception, Insight,
Intimidation, Investigation, Leadership, Medicae, Persuasion, Pilot, Scholar, Stealth,
Survival, Tech, Weapon Skill. (Maestria Psíquica só para Librarius — ver doc 30K.)

**Traços derivados** (calculados na ficha):
- **Defence** = Initiative − 1 (+ cobertura, talentos)
- **Resilience** = Toughness + blindagem
- **Wounds** = Toughness + Tier | **Shock** = Willpower + Tier
- **Determination** = parada de Toughness para *soak* (cada ícone converte 1 Wound em Shock)
- **Conviction** = resistência à Corrupção | **Resolve** = moral | **Influence** = Fellowship − 1

## Combate

**Turno:** 1 movimento (+ Speed em metros) + 1 ação de combate + 1 ação simples + 1 reflexiva.
Opções comuns: Mirar (+bônus), Investida, Chamar Tiro (Called Shot), Defesa Total (rola
Initiative e soma à Defence), Supressão (Ballistic Skill como ataque de interação).

**Ataque:** teste de Ballistic Skill (tiro) ou Weapon Skill (corpo a corpo) vs **Defence** do alvo.
**Dano:** valor base da arma + ED (cada ícone rolado nos ED = +1 dano) + shifts + Glória.
Compare ao **Resilience** do alvo (menos AP da arma):
- **Dano < Resilience:** sem efeito.
- **Dano = Resilience:** 1 Shock.
- **Dano > Resilience:** 1 Wound por ponto excedente — o alvo pode rolar **Determination**
  para converter Wounds em Shock (Mortal Wounds **não** podem ser convertidas).

**Crítico** (⚡ = 6 em ataque com sucesso): causa **no mínimo 1 Wound** + efeito da tabela
de críticos (membro dilacerado, sangramento, atordoado…). Críticos ignoram a lógica de
"resistiu tudo": mesmo um tiro de sorte pode derrubar um gigante — raramente, gloriosamente.

**Ataques de interação:** Intimidation, Persuasion, Deception, Tech etc. podem atacar em combate
para deixar o inimigo **Hindered** (+1 DN nos testes dele) ou **Vulnerable** (−1 Defence).

**Queda:** 0 Wounds = morrendo — testes de Desafio (1d6, 4+ estabiliza; 6+ volta com 1 Wound).
0 Shock = **Exausto** (só rastejar, recuar, soak e ações básicas; Shock excedente vira Wound).
**Ferido** (abaixo do máx. de Wounds): +1 DN em tudo — dói ser herói.

## Corrupção e Medo

Certas cenas pedem testes de Conviction/Resolve (DN 3 + nível de Corrupção). Falhar = +1
Corrupção (complicação = dobra), e o **Mestre ganha Ruína**. Nesta era, chamamos de
**Sussurros do Warp** (ver doc 30K) — a mecânica é a mesma, o nome é mais honesto para um
tempo em que "Caos" ainda não é palavra de vocabulário.

## Fontes da pesquisa

- Sistema de dados, dado de Wrath, Glória: Bell of Lost Souls sobre o W&G —
  https://www.belloflostsouls.net/2017/11/40k-rpg-wrath-and-glory-core-rules-spotted.html
- Revisão do núcleo e Tiers: Enworld/Cubicle 7 —
  https://www.enworld.org/threads/warhmamer-40k-wrath-glory-cubicle-7-re-release-review.672170/
- Mecânicas, Tier, Glória, shifts: 1d6chan wiki —
  https://1d6chan.miraheze.org/wiki/Wrath_&_Glory
- Criação de personagem e Tiers: análise do rulebook (2024) —
  https://illmetbymorrslieb.wordpress.com/2024/04/29/warhammer-40000-wrath-glory-rulebook-part-1-character-creation/
- Combate, Shock/Wounds, soak, Ruína: GamersPlane + Reddit 40krpg —
  https://staging.gamersplane.com/forums/thread/32253/ e
  https://www.reddit.com/r/40krpg/comments/17hpnue/wrath_and_glory_shock_and_wounds/
