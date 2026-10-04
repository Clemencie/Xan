# Capítulo 11 — Rupturas, Núcleo Dourado, Desvio de Qi e Tribulação

Este capítulo é onde o XAN mais se distancia de outros sistemas: **o avanço de
reino não é uma recompensa.** É um evento com risco, custo e procedimento.

## 11.1 Ruptura por rolagem

```
d20 + bônus de Inteligência + Compreensão + regras de preparo ≥ DD do nível
```

Regras que normalmente se aplicam: `AMBIENTE:FENGSHUI`, `AMBIENTE:DENSIDADE_QI`,
`RECURSO:ELIXIR`, `PREPARO:MEDITACAO`. A DD da tabela do Cap. 6.1 é ajustada pela
Compatibilidade com a Lei (Cap. 8.2) e pelo `dd_extra` da Lei.

```bash
./xan ruptura --ator "Lin Yue" --nivel 5 --lei SETE_MASSACRES \
              --int 16 --per 14 --con 15 --cha 12 --luk 14 --pot 13 \
              --compreensao 4 --fengshui auspicioso --densidade rica \
              --elixir medio --meditou --diario mundos/minha-mesa/auditoria/diario.jsonl
```

## 11.2 Falhar uma ruptura

Falha não é "tente de novo na semana que vem". A margem negativa define a
gravidade e a gravidade define a tabela de Desvio de Qi:

| Margem | Gravidade | Deslocamento na tabela |
|---:|---|---|
| −1 a −4 | comum | nenhum |
| −5 a −9 | grave | +1 |
| ≤ −10 ou 1 natural | catastrófica | +2 |

E os pontos de cultivo acumulados caem pela metade. É caro de propósito: quem
tenta romper sem preparo perde meses de jogo.

## 11.3 O Núcleo Dourado (金丹)

A ruptura do nível 6 para o 7 é a única que **não se rola**. Como no *Amazing
Cultivation Simulator*, o Núcleo sempre se forma — o que varia é a qualidade, e
a qualidade é uma conta fechada sobre fatos declarados.

**Só se tenta uma vez na vida.** Depois de formado, o grau é permanente.

| Fator | Como conta | Máximo |
|---|---|---:|
| Qi máximo acumulado | `qi_maximo ÷ 100` | ~4 no nível 6 |
| Feng Shui do local | tabela Cap. 9.5 | +8 |
| Densidade de Qi do local | tabela Cap. 9.4 | +12 |
| Harmonia de estação/hora/clima | Cap. 9.7 | +12 |
| Estado mental (Coração do Dao) | `estado ÷ 10` | +20 |
| Elixir de ruptura | nenhum 0 · menor 2 · médio 5 · maior 9 · celestial 14 | +14 |
| Compatibilidade com a Lei | `match ÷ 10` | +15 |
| Compreensão acumulada | `pontos ÷ 200` | sem teto prático |
| Artefato de cultivo | mortal 0 · terra 2 · céu 5 · primordial 9 | +9 |
| Mestre guiando a ruptura | sim +4, não 0 | +4 |

| Pontuação | Grau | Título |
|---:|---:|---|
| ≥ 95 | **1** | Núcleo de Taiyi — uma vez por era |
| 85–94 | 2 | Núcleo Imaculado |
| 72–84 | 3 | Núcleo Radiante |
| 60–71 | 4 | Núcleo Sólido |
| 48–59 | 5 | Núcleo Comum |
| 36–47 | 6 | Núcleo Turvo |
| 25–35 | 7 | Núcleo Rachado |
| 15–24 | 8 | Núcleo Impuro |
| < 15 | 9 | Núcleo de Escória |

Efeito: `(10 − grau) × 25 + nível × 5` de Qi máximo adicional. No nível 12, um
grau 1 dá +345 de Qi e um grau 9 dá +105.

**Referência de pontuações típicas:**

| Perfil | Pontos | Grau |
|---|---:|---:|
| Improvisado, sem mestre, sala comum | ~24 | 8 |
| Preparo decente | ~54 | 5 |
| Preparo cuidadoso | ~80 | 3 |
| Tudo maximizado | 108 | 1 |

O grau 1 exige praticamente o teto de cada fator. É para ser lenda — e é
verificável: `./xan nucleo` imprime cada parcela com a justificativa.

## 11.4 Demônios Interiores (心魔)

Um Demônio Interior **é um NPC**: tem virtudes, temperamento, traços e desejos
próprios, e mora na cabeça do cultivador. Gere-o com `./xan npc` e anote-o na
ficha.

Gatilhos objetivos (não "quando for dramático"):

* estado mental abaixo de 30;
* falha crítica (1 natural) em qualquer ruptura;
* quebrar a própria linha vermelha;
* ver morrer alguém a quem se devia dever;
* usar uma técnica demoníaca acima do próprio nível.

Quando dispara, é um **teste oposto**: o personagem contra o demônio, ambos com
`d20 + bônus de Potencial + Vontade de Ferro` contra DD `10 + (100 − estado
mental) ÷ 5`. Quem perde:

* demônio perde → o personagem ganha +5 de estado mental e o demônio dorme;
* personagem perde → o demônio age por ele **uma** ação, escolhida pela
  `resolver_conduta` do Cap. 12.6, usando os desejos do demônio.

O demônio nunca some. Ele pode ser selado (`SALVACAO_SUBMUNDO`), negociado (ele
tem Preço) ou aceito (o personagem ganha a técnica do demônio e perde 10 de
estado mental máximo permanentemente).

## 11.5 A Tribulação Celestial (天劫)

O céu ataca quem desafia a ordem natural. Acontece ao sair dos níveis 9, 11 e
12, e no nível 6 **apenas** para Leis demoníacas.

| Saída do nível | Raios | Nome |
|---:|---:|---|
| 6 (só demoníaca) | 1 | Primeiro Aviso |
| 9 | 3 | Três Trovões da Conversão |
| 11 | 4 | Quatro Selos do Julgamento |
| 12 | 9 | **Os Nove Trovões da Ascensão** |

Leis demoníacas somam +1 raio sempre.

Cada raio é uma declaração comprometida:

```
DD    do raio k = 14 + nível + 2 × (k − 1)
poder do raio k = 30 + 43 × nível + 20 × (k − 1)
```

Cada raio se resiste com `d20 + bônus de Constituição + Corpo de Ferro + regras
de preparo`. Falhar causa `max(1, poder − total)` de dano, absorvido primeiro
pelo Qi.

Regras de preparo que valem aqui: `RECURSO:ARTEFATO`, `AMBIENTE:FORMACAO`,
`RECURSO:ELIXIR`, `PREPARO:QUEIMA_LONGEVIDADE` (cada 10 anos queimados = +1, até
+5) e `REINO:SUPRESSAO` (o céu conta como um nível acima).

### Sobrevivência medida

Simulação de 500 tribulações por perfil, com o motor real:

| Perfil | Escudo (Qi+Vit) | Raios | Sobrevive |
|---|---:|---:|---:|
| nível 9, sem preparo nenhum | 813 | 3 | **1,6%** |
| nível 9, preparo bom | 823 | 3 | 75,4% |
| nível 11, preparo bom | 1179 | 4 | 80,8% |
| nível 11, preparo supremo | 1189 | 4 | 97,8% |
| Ascensão, preparo bom | 1417 | 9 | **0,6%** |
| Ascensão, preparo supremo | 1437 | 9 | **18,4%** |

Leia os números com calma. Eles dizem três coisas sobre o gênero:

1. **Ninguém enfrenta o céu sem preparo.** Dois raios falhados matam.
2. **Preparo é o jogo.** Artefato, formação, elixir e longevidade queimada valem
   mais que atributo.
3. **Ascensão é quase impossível de propósito.** 18% para o cultivador mais bem
   preparado do mundo. Numa campanha longa, isso significa que a Ascensão é um
   evento — não um nível.

```bash
./xan tribulacao --ator "Lin Yue" --nivel 9 --con 20 --defesa 4 \
                 --vitalidade 210 --qi 380 --artefato ceu --formacao aliada \
                 --elixir maior --anos-queimados 20 \
                 --diario mundos/minha-mesa/auditoria/diario.jsonl
```

## 11.6 Desvio de Qi (走火入魔)

Role 1d6 e some o deslocamento de gravidade:

| 1d6 | Consequência |
|---:|---|
| 1 | O dantian racha: perde 25% dos pontos de cultivo acumulados e 1d6 de Vitalidade |
| 2 | Um meridiano se rompe: −1 permanente em Constituição até ser curado por um Ancião |
| 3 | Um Demônio Interior se instala (gere o NPC, Cap. 11.4) |
| 4 | Regressão: cai 1 nível e perde a técnica mais recente |
| 5 | Coma de 1d4 meses; ao despertar, −2 em Percepção por um ano |
| 6 | O Qi inverte e o corpo explode. **Morte definitiva — sem ressurreição** |

## 11.7 Queima de Longevidade

Um cultivador pode queimar anos de vida por poder imediato:

* **em teste**: cada 10 anos queimados = +1 (máx. +5, ou seja, 50 anos);
* **em dano**: queimar 5 anos dobra o dano do próximo golpe;
* **em velocidade**: queimar 20 anos concede uma ação extra neste turno sem
  penalidade de `COMBATE:ACOES_MULTIPLOS`.

A queima é declarada **antes** do dado, entra no diário e é irreversível.
Longevidade queimada não volta — nem com `ELI_LONGEVIDADE`, que soma ao total
*atual*.

## 11.8 Vazio (破碎虛空)

No nível 12, antes da Ascensão, existe a opção de romper o Vazio: são
**500 pontos de Compreensão** gastos de uma vez, com ganho proporcional à
Compatibilidade com a Lei (`3% × compatibilidade ÷ 100` por hora de meditação).
Sucesso concede uma técnica de grau Primordial sem manual. Falha causa Desvio de
Qi de gravidade catastrófica.
