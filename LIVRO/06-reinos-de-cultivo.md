# Capítulo 6 — Reinos de Cultivo

## 6.1 A escada

Treze níveis compartilhados por todos os caminhos. O mesmo número significa
coisas diferentes para um Xiandao, um Shendao, um cultivador corporal e um
artista marcial do Murim — mas a **mecânica é a mesma**, e é isso que permite
um monge de Shaolin lutar contra um imortal sem que a mesa precise inventar uma
tabela de conversão.

| Nv. | Trilha (universal) | Xiandao 仙道 | Shendao 神道 | Corpo 體修 | Marcial (Murim) | Longevidade | Saída do nível |
|---:|---|---|---|---|---|---:|---|
| 0 | Mortal | Mortal | Mortal | Mortal | Terceira Classe | 70 | rolagem DD 12 |
| 1 | Temperado | Moldagem de Qi I | Ascético | Remoldagem | Terceira Classe | 90 | DD 13 |
| 2 | Concentrado | Moldagem de Qi II | Ascético | Remoldagem | Segunda Classe | 100 | DD 14 |
| 3 | Moldador | Moldagem de Qi III | Ascético | Remoldagem | Primeira Classe | 120 | DD 16 |
| 4 | Portão da Mente | Moldagem de Núcleo I | Peregrino | Limpeza de Medula | Reino do Pico | 150 | DD 18 |
| 5 | Caldeirão | Moldagem de Núcleo II | Peregrino | Limpeza de Medula | Pico Supremo | 180 | DD 20 |
| 6 | Moldador de Essência | Moldagem de Núcleo III | Peregrino | Limpeza de Medula | Transcendente | 220 | **pontuação** (Núcleo Dourado) |
| 7 | Núcleo Dourado | Núcleo Dourado I | Divino | Incubação | Irrestrito | 300 | DD 24 |
| 8 | Alquimia | Núcleo Dourado II | Divino | Incubação | Absoluto — Alma Marcial | 400 | DD 26 |
| 9 | Embrionário | Núcleo Dourado III | Divino | Incubação | Absoluto — Sem Limite | 500 | **tribulação** (3 raios) |
| 10 | Incubação da Origem | Espírito Primordial I | Realização | Caos | Natureza — Despertar | 800 | DD 30 |
| 11 | Espírito Ascendente | Espírito Primordial II | Realização | Caos | Natureza — Eterno | 1200 | **tribulação** (4 raios) |
| 12 | Espírito Primordial | Espírito Primordial III | Realização | Caos | Natureza — Divino | 2000 | **tribulação** (9 raios) |
| 13 | Ascensão | Imortal 仙 | Divindade 神 | Caos Unificado | Trono Constelar 星座 | ∞ | — |

Três métodos de saída de nível, e **nenhum é intercambiável**:

* `rolagem` — teste de Compreensão contra a DD da tabela;
* `pontuação` — o Núcleo Dourado não se rola: se **conta** (Cap. 11.3);
* `tribulacao` — o céu ataca (Cap. 11.5).

Tentar usar `./xan ruptura --nivel 6` produz um erro explicando que o nível 6 sai
por pontuação. O motor não deixa você escolher o método mais fácil.

## 6.2 Recursos derivados

```
Qi máximo   = base do reino + Constituição + Percepção÷2 + Inteligência÷2 + bônus do Núcleo
Vitalidade  = base do reino + 2 × Constituição + Potencial + 3 × nível
```

| Nv. | Qi base | Vitalidade base |
|---:|---:|---:|
| 0 | 0 | 20 |
| 1 | 20 | 25 |
| 2 | 35 | 30 |
| 3 | 55 | 36 |
| 4 | 80 | 45 |
| 5 | 110 | 55 |
| 6 | 150 | 70 |
| 7 | 200 | 90 |
| 8 | 260 | 115 |
| 9 | 340 | 150 |
| 10 | 440 | 200 |
| 11 | 560 | 260 |
| 12 | 700 | 340 |
| 13 | 900 | 600 |

Bônus do Núcleo Dourado (nível ≥ 7): `(10 − grau) × 25 + nível × 5`. Um Núcleo
grau 1 vale +345 de Qi no nível 12; um grau 9 vale +105. **É a decisão mais
consequente da vida do personagem e ela é irreversível.**

O Qi é mana **e** escudo: enquanto houver Qi, o dano é absorvido por ele. Quando
acaba, a Vitalidade começa a cair. (Cap. 10.6.)

## 6.3 Supressão de Reino

A regra mais importante do gênero, e ela é aritmética:

```
REINO:SUPRESSAO = 2 × (reino de quem rola − reino do oponente), limitado a ±10
```

E a cláusula de imbatibilidade: **três ou mais níveis abaixo do alvo, o ataque
não rola dado.** O motor recusa e explica. Só uma técnica marcada como
`ignora_supressao` atravessa — e há pouquíssimas, todas de nível 7 para cima.

| Lacuna | Efeito |
|---:|---|
| −3 ou pior | ataque impossível sem técnica suprema |
| −2 | −4 |
| −1 | −2 |
| 0 | 0 |
| +1 | +2 |
| +2 | +4 |
| +3 ou mais | +6 a +10 (teto) |

Isso significa que um cultivador de nível 7 perde para um de nível 10 quase
sempre — e que vencer acima do próprio reino é o feito que dá nome a um
personagem.

## 6.4 Pontos de cultivo (悟)

Para tentar uma ruptura é preciso acumular os pontos do nível atual:

| Nv. | pontos | Nv. | pontos |
|---:|---:|---:|---:|
| 0 | 100 | 7 | 28 000 |
| 1 | 250 | 8 | 55 000 |
| 2 | 600 | 9 | 110 000 |
| 3 | 1 400 | 10 | 220 000 |
| 4 | 3 000 | 11 | 440 000 |
| 5 | 6 500 | 12 | — (só tribulação) |
| 6 | 14 000 | | |

Ganho mensal de pontos = `100 × multiplicador da Raiz ÷ 100 × (1 + bônus de
preparo)`, dobrado em local com `densidade_qi ≥ rica`, dobrado de novo dentro de
uma Formação de Reunião de Qi. O ACS chama isso de velocidade de cultivo; aqui é
uma linha de conta.

## 6.5 O gargalo (瓶頸)

Nos níveis 3, 6, 9 e 12 existe um gargalo: antes de rolar a ruptura, é preciso
vencer um teste de **Compreensão** contra DD `10 + nível`. Falhar não causa
Desvio de Qi; apenas consome os pontos acumulados pela metade e adia a tentativa
por um mês de jogo. É a mecânica que impede alguém de tentar romper toda semana.

## 6.6 O que cada reino permite

| Nv. | Capacidade nova |
|---:|---|
| 1 | sentir Qi; circular pelos meridianos |
| 2 | imbuir a arma; quebrar pedra com a palma |
| 3 | saltar telhados (qinggong básico) |
| 4 | abrir o Portão da Mente; Qi visível como névoa |
| 5 | Qi de Espada 劍氣 à distância |
| 6 | voo curto; telecinese leve |
| 7 | Núcleo Dourado; Força de Espada 劍罡; voo sustentado |
| 8 | domínio do próprio elemento |
| 9 | enxergar o Dao; intenção move a arma antes do braço |
| 10 | Alma Nascente projetável; sobrevive à destruição do corpo |
| 11 | Espada da Mente 心劍; altera o clima local |
| 12 | um com o Céu e a Terra |
| 13 | deixa o plano mortal |

## 6.7 Morte

Vitalidade ≤ 0 é **caído**, não morto. Role 1d6:

| d6 | Estado |
|---:|---|
| 1–2 | inconsciente; estabiliza com Medicina DD 12 ou em 1d4 horas |
| 3–4 | ferimento permanente: −1 em um atributo físico até cura de grau Céu |
| 5 | meridiano rompido: perde 10% do Qi máximo até ser tratado por um Ancião |
| 6 | morte. Sem ressalva. Um cultivador de nível 10+ pode ter a Alma Nascente escapado (Cap. 7.1) |

Nível 10 ou acima, o 6 vira "o corpo morre, a Alma Nascente escapa": o
personagem perde tudo que é material e precisa de um novo corpo ou de um
discípulo disposto a abrigá-lo. Isso é canônico e é horrível, e é exatamente por
isso que cultivadores de alto nível raramente matam uns aos outros em público.
