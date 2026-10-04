# Capítulo 5 — Raiz Espiritual e Criação de Personagem

## 5.1 A Raiz Espiritual (靈根)

A Raiz Espiritual é o que separa quem pode cultivar de quem não pode. Ela é
descoberta num teste de pedra espiritual entre os 6 e os 14 anos, e **não muda
nunca**. Todo o resto do sistema pode ser trabalhado; a raiz é destino.

Ela tem três componentes:

1. **Quantos elementos** você conduz. Quanto menos, mais puro.
2. **Pureza** (1–100%), o quanto o Qi passa sem se contaminar.
3. **Mutação** (rara): Gelo 冰, Trovão 雷, Vento 風, Trevas 暗, Vazio 虛,
   Caos 混沌, Espaço 空, Tempo 時.

### Graus

| Nº de elementos | Grau | Pureza máxima | Multiplicador de cultivo |
|---:|---|---:|---:|
| 1 | **Céu** 天 | 100% | 400% (+ ajuste) |
| 2 | **Terra** 地 | 85% | 220% |
| 3 | **Preto** 玄 | 65% | 140% |
| 4 | **Amarelo** 黃 | 45% | 90% |
| 5 | **Desperdício** 廢 | 30% | 40% |

O multiplicador é `base + (pureza − 50) ÷ 5`, e **+25** se houver mutação. Ele
multiplica os pontos de cultivo ganhos por mês de prática (Cap. 6.5).

### Mutações

| Código | Nome | Comporta-se como |
|---|---|---|
| `gelo` | Raiz de Gelo 冰靈根 | Água, mas congela em vez de fluir |
| `trovao` | Raiz do Trovão 雷靈根 | Metal; dano que ignora armadura |
| `vento` | Raiz do Vento 風靈根 | Madeira; velocidade e corte |
| `trevas` | Raiz das Trevas 暗靈根 | Água; invisibilidade e corrosão |
| `vazio` | Raiz do Vazio 虛靈根 | fora do ciclo; atravessa barreiras |
| `caos` | Raiz do Caos 混沌靈根 | todos e nenhum; imprevisível |
| `espaco` | Raiz do Espaço 空靈根 | Terra; teletransporte |
| `tempo` | Raiz do Tempo 時靈根 | Fogo; antecipa e atrasa |

Raiz mutante **não aparece em teste comum de pedra espiritual**: a pedra lê
"Desperdício" ou "Amarelo". Descobrir a própria mutação é um arco inteiro de
campanha — e o momento em que o personagem deixa de ser figurante.

## 5.2 As quatro tabelas de raiz

A raridade é uma **regra de mesa escolhida antes da criação** e aplicada a todos
igualmente. Isso é diferente de vantagem narrativa (que é decidida depois de ver
o resultado), e por isso é legítima.

| Tabela | Céu | Terra | Preto | Amarelo | Desperdício | Uso |
|---|---:|---:|---:|---:|---:|---|
| `realista` | 0,01% | 0,20% | 1,95% | 12,05% | 85,79% | população do mundo, NPCs |
| `heroica` | 0,38% | 3,60% | 16,13% | 29,92% | 49,97% | **padrão para personagens de jogadores** |
| `lendária` | 2,98% | 13,92% | 27,98% | 31,98% | 23,13% | era de ouro, campanhas épicas |
| `mortal` | 0,01% | 0,02% | 0,30% | 4,04% | 95,63% | wuxia puro: esforço decide tudo |

Medido sobre 200 000 sorteios por tabela. Com Sorte 10 (o neutro), as frequências
reproduzem os pesos publicados da tabela exatamente — propriedade coberta por
teste automatizado.

Sorte (LUK) desloca os pesos: cada ponto acima de 10 aumenta em 3% o peso das
raízes puras. É um atributo de ficha declarado antes, igual para todos.

```bash
./xan personagem --nome "Lin Yue" --semente minha-mesa --raiz heroica
```

## 5.3 Atributos

Três métodos, declarados antes da criação:

* **Sorteio** (padrão): `4d6kh3` por atributo, mínimo 3, máximo 18. Média 12,24.
* **Pontos**: todos começam em 8 e você distribui 78 pontos com custo crescente
  (1 ponto até 14, 2 até 17, 3 acima).
* **Manual**: para conversão de fichas antigas ou NPCs importantes.

## 5.4 Passo a passo da criação

1. **Escolha a tabela de raiz da mesa** e anote na ficha de campanha.
2. **Role ou compre os seis atributos.**
3. **Sorteie a Raiz Espiritual** (`sortear_raiz` usa a Sorte do passo anterior).
4. **Escolha o caminho** (Cap. 7): Xiandao, Shendao, Corpo ou Marcial.
   Personagens novos começam no **nível 0 ou 1**.
5. **Escolha a Lei** (Cap. 8). Ela exige atributos mínimos; se você não os tem,
   a Compatibilidade cai e a Lei rende menos. Nada impede de tentar — o gênero
   inteiro é sobre gente inadequada insistindo.
6. **Distribua 12 pontos de perícia** (máx. 5 por perícia, máx. 3 perícias
   distintas por grupo).
7. **Calcule os derivados**: Qi máximo, Vitalidade máxima, Defesa nos três modos,
   longevidade.
8. **Escreva três coisas que não são números**: de onde você veio, o que você
   quer, e o que você não faz. Se quiser, use o gerador de desejos de NPC do
   Cap. 12 — personagens com as oito camadas são muito mais jogáveis.
9. **Escolha uma facção** ou declare-se errante (Jianghu 江湖 sem seita é mais
   livre e muito mais perigoso).
10. **Assine o Contrato de Imparcialidade** (Cap. 2).

## 5.5 Nível inicial recomendado

| Estilo de campanha | Nível inicial |
|---|---:|
| Mortais que descobriram o cultivo ontem | 0 |
| Clássica (discípulos novos) | 1–2 |
| Já estabelecidos no Murim | 4–5 |
| Veteranos com Núcleo | 7–8 |
| Épica (Anima Nascente) | 10 |

Acima de 10 a campanha muda de natureza: os personagens deixam de participar do
mundo e passam a ser um fenômeno meteorológico dele.

## 5.6 Equipamento inicial

Um personagem de nível 0–2 começa com:

* uma arma de grau Mortal;
* vestes comuns;
* 10–40 pedras espirituais baixas (Cap. 17);
* um manual da própria Lei, grau Mortal;
* um item de origem escolhido pelo jogador, sem efeito mecânico — ainda.

## 5.7 Ficha

`LIVRO/fichas/ficha-personagem.md` tem a ficha completa em Markdown, pronta para
copiar. Os campos numéricos batem exatamente com o que o motor calcula; se a sua
ficha e o motor discordarem, o motor está certo e a ficha é que foi mal copiada.
