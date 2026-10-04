# Capítulo 13 — Mundo Procedural

## 13.1 O princípio

> **A semente decide, ninguém mais.**

Duas mesas com a mesma semente encontram a mesma montanha, o mesmo rancor de
trezentos anos e o mesmo poço envenenado. Mudar a semente muda o mundo inteiro —
não apenas o detalhe que incomoda o mestre.

Isso tem uma consequência prática importante: **ninguém pode editar o mundo para
salvar uma cena.** Se a vila que os jogadores precisam visitar não existe, ou
eles viajam até a que existe, ou a mesa troca de semente e recomeça o mundo
inteiro. Não existe a opção de acrescentar uma vila conveniente depois.

```bash
./xan mundo gerar --semente rios-e-lagos-01 --saida mundos/rios-e-lagos --npcs 12
```

Gera, em menos de um segundo:

```
mundos/rios-e-lagos/
├── mundo.json          # o mundo completo, máquina-legível
├── mundo.md            # o mundo completo, legível na mesa
├── mundo.svg           # mapa do continente em grade hexagonal
├── npcs.json           # NPCs notáveis
├── npcs.md             # fichas dos NPCs notáveis
└── provincias/
    ├── FengHu.svg      # mapa de detalhe de cada província
    ├── ShanDu.svg
    └── …
```

## 13.2 O que é gerado

### As Nove Províncias (九州)

Posicionadas numa grade hexagonal (centro + anéis), cada uma com:

| Campo | Faixa | Efeito |
|---|---|---|
| nome e caracteres | gerador | — |
| elemento dominante | Wuxing ou neutro | afeta clima, harmonia e `ELEMENTO:RELACAO` local |
| terreno | 12 opções | afeta Qi, movimento e `POSICAO:TERRENO` |
| densidade de Qi | 0–10 | vira o fato `AMBIENTE:DENSIDADE_QI` |
| clima base | 8 opções | pesos da tabela de clima |
| perigo | 1–10 | DD de encontros aleatórios |
| veias espirituais | 0–3 | bônus de produção para quem as controla |

A densidade de Qi não é sorteada no vácuo: terrenos montanhosos e vulcânicos
recebem +2, planaltos e litorais +1, desertos −2, tundras −1. Lógica geográfica,
não acaso cego.

### Sítios

22 tipos, distribuídos por coerência:

| Família | Tipos |
|---|---|
| Civilização | cidade, vila, porto, mercado negro, passo de montanha |
| Facções | seita ortodoxa, seita não-ortodoxa, culto demoníaco, clã nobre, mosteiro, templo, fortaleza |
| Natureza | pico de cultivo, lago espiritual, floresta proibida, caverna de bestas, veia espiritual |
| História | ruína, campo de batalha, tumba antiga, reino secreto, torre de observação |

Cada sítio tem nível (0–13), dono, população, densidade de Qi própria (a da
província ± 2, com +3 em veias e picos, 10 fixo em reinos secretos, −3 em ruínas
e campos de batalha), terreno, recurso explorável, perigo, ano de fundação, uma
linha de história e **um segredo**.

### Segredos

Cada sítio tem exatamente um segredo, sorteado de uma lista de 18. Alguns:

* Um Ancião morto ainda dá ordens: alguém falsifica a caligrafia dele.
* O poço da vila envenena devagar quem bebe por mais de um ano.
* Metade das pedras espirituais do cofre são falsas.
* Uma criança da vila nasceu com raiz de um único elemento e ninguém sabe.
* O mapa local está errado: uma montanha inteira foi omitida.
* Nada. O lugar é exatamente o que parece — e isso é o mais raro de tudo.

O segredo está no `title` do SVG: passar o mouse sobre o marcador revela. Isso é
intencional e é uma armadilha para mestres desprevenidos — **não mostre o mapa
com os tooltips ativos para os jogadores** se quiser que eles descubram jogando.

## 13.3 Facções e a matriz de relações

Cada sítio de facção vira uma facção com nome, caracteres, alinhamento
(ortodoxa / não-ortodoxa / demoníaca / imperial / neutra), nível do líder,
número de membros, prestígio (−100 a +100), elemento, Lei principal, sede, renda
anual, reputação e 1–3 objetivos.

A relação entre duas facções é um inteiro de −100 a +100, derivado de:

```
base por par de alinhamentos   (ortodoxa×ortodoxa +10, ortodoxa×demoníaca −70, …)
+ 8  se mesma província
+ 6  se mesmo elemento
− 8  se o elemento de uma supera o da outra
+ ruído inteiro de −30 a +30
+ efeito histórico acumulado (máximo ±20 por par de alinhamentos)
```

Distribuição medida sobre 2 878 pares em seis mundos diferentes:

| Faixa | Categoria | Ocorrência |
|---|---|---:|
| ≥ 60 | aliadas | 16,5% |
| 20 a 59 | amigáveis | ~28% |
| −19 a 19 | neutras | 20,4% |
| −59 a −20 | rivais | ~26% |
| ≤ −60 | em guerra | 9,3% |

O efeito histórico tem teto de ±20 **de propósito**: quarenta eventos de "aliança
do Murim" não podem apagar um ódio concreto entre duas facções específicas. A
história influencia; não sobrescreve.

`mundo.relacao_como_fato(a, b)` devolve exatamente a string que a regra
`FACCAO:RELACAO` espera, e só ela:

| Valor | Fato | Modificador |
|---:|---|---:|
| a == b | `mesma` | +2 |
| ≥ 60 | `aliada` | +1 |
| 20 a 59 | `amigavel` | +1 |
| −19 a 19 | `neutra` | 0 |
| −59 a −20 | `rival` | −1 |
| ≤ −60 | `guerra` | −2 |

Um teste automatizado percorre todas as facções de um mundo gerado e confere que
cada fato produzido é aceito pela regra — o gerador de mundo não pode inventar
vocabulário que o Registro de Regras não conheça.

## 13.4 A linha do tempo: o passado causa o presente

São sorteados 40 eventos (configurável) espalhados pelos últimos 900 anos, e
**cada evento gera consequências materiais no estado atual do mundo**. O mundo é
lido de trás para frente.

| Tipo de evento | Peso | Consequências materiais |
|---|---:|---|
| fundação de seita | 14 | cria facção + sede |
| guerra entre facções | 12 | relação −60 entre as duas + campo de batalha |
| queda de seita | 7 | ruína + tesouro lendário perdido |
| tribulação de imortal | 5 | pico de cultivo; às vezes floresta proibida |
| praga demoníaca | 6 | cria culto demoníaco + caverna de bestas |
| manual supremo perdido | 6 | tesouro lendário |
| queda de dinastia | 4 | relação imperial −20 com todos |
| grande torneio | 9 | prestígio redistribuído |
| cometa e presságio | 8 | densidade de Qi alterada |
| descoberta de veia | 7 | sítio de veia + densidade permanente +2 |
| invasão do Templo Daemonia | 5 | floresta proibida nível 11 + relação demoníaca −20 |
| aliança do Murim | 6 | relação ortodoxa +15 |
| seca ou inundação | 8 | população da província reduzida a 60% |
| nascimento de um gênio | 6 | registro único + NPC notável |
| besta ancestral desperta | 5 | floresta proibida nível 12 |
| reino secreto aparece | 6 | reino secreto nível 9 |

Cada evento traz título, descrição em prosa e a lista explícita de consequências
— o `mundo.md` imprime as três coisas juntas, para que a mesa possa ler a
história e ver de onde veio cada fato do mapa.

## 13.5 Clima do ano corrente

Para cada província e cada um dos 360 dias do ano atual, o clima é sorteado
**uma vez** na geração e gravado no JSON. Os pesos são inteiros e dependem da
estação, do elemento da região (peso ×3 no clima correspondente) e da altitude.

Isso significa que:

* o clima de hoje em FengHu é um fato, não uma escolha;
* se os jogadores voltarem no tempo (e no nível 12 isso é concebível), o clima
  que encontram é o que estava gravado;
* a harmonia elemental de uma ruptura (Cap. 9.7) usa o clima real do dia real.

## 13.6 Tesouros lendários

Entre 6 e 11 por mundo, cada um com nome, caracteres, grau, tipo, onde se
perdeu, guardião e maldição. Exemplos gerados:

> **Espada das Sete Estrelas de QingYun** (七星劍湖) — grau Céu, arma de Metal.
> Perdida em algum lugar de RiYe desde o ano 1180.
> Guardião: o fantasma do último dono.
> Maldição: sussurra o nome de quem a portou antes — todos mortos.

## 13.7 NPCs notáveis

`--npcs N` gera os NPCs importantes do mundo: os líderes das facções de maior
prestígio (com nível igual ao do líder da facção e ocupação coerente) mais
errantes espalhados pelas províncias. Todos completos, com desejos e agendas.

## 13.8 Escalas

| Parâmetro | Padrão | Faixa |
|---|---:|---|
| `--provincias` | 9 | 3–20 |
| `--eventos` | 40 | 1–400 |
| `--anos-de-historia` | 900 | ≥ eventos |
| sítios por província | 4–9 | — |
| facções-alvo | 14 | +6 pelo histórico |

Um mundo de 20 províncias com 400 eventos leva cerca de três segundos e produz
um `mundo.md` de uns 400 KB. Para uma campanha de anos, é o tamanho certo.

## 13.9 Reproduzibilidade

`mundo.json` contém a semente e a versão do gerador. Qualquer pessoa pode:

1. baixar o JSON;
2. rodar `./xan mundo gerar --semente <a mesma>`;
3. comparar os dois byte a byte.

Se divergir, é bug — e o bug está no gerador, não na mesa. O campo
`versao_do_gerador` existe exatamente para que uma mudança futura no gerador não
seja confundida com adulteração.
