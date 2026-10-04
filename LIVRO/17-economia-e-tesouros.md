# Capítulo 17 — Economia e Tesouros

## 17.1 Pedras espirituais (靈石)

Moeda e bateria. Uma pedra espiritual é Qi cristalizado: pode ser gasta em
compra **ou** absorvida em cultivo, e essa dupla função é o que faz a economia
do Murim ser diferente de qualquer economia medieval.

| Grau | 中文 | Conversão | Absorve |
|---|---|---|---:|
| Baixa | 下品靈石 | 1 | 100 Qi |
| Média | 中品靈石 | 100 baixas | 10 000 Qi |
| Alta | 上品靈石 | 100 médias | 1 000 000 Qi |
| Suprema | 極品靈石 | 100 altas | não se absorve: é material de grau Primordial |

Todos os preços do livro estão em **pedras baixas**.

**Absorver pedra** é uma ação de 1 hora que restaura Qi na taxa da tabela, sem
teste. Mas há limite: absorver mais que `nível × 10` pedras baixas por dia causa
`ESTADO:EXAUSTAO` até o próximo amanhecer. Ricos não são invencíveis; são apenas
mais difíceis de cansar.

## 17.2 Preços de referência

| Item | Preço |
|---|---:|
| refeição em vila | 1 |
| noite em estalagem | 2–10 |
| cavalo comum | 50 |
| espada de aço comum | 30–80 |
| cavalo espiritual (nível 2) | 800 |
| manual de grau Mortal | 50–500 |
| Anel de Espírito inferior | 3 000–8 000 |
| manual de grau Terra | 2 000–20 000 |
| elixir de grau Terra | 1 500–6 000 |
| manual de grau Céu | 100 000–1 000 000 |
| artefato de grau Céu | 200 000–2 000 000 |
| prédio de seita | 1 500–20 000 |
| uma montanha com veia espiritual | não se compra: se toma |

## 17.3 Renda

| Origem | Renda mensal |
|---|---:|
| discípulo externo | 5–20 |
| discípulo interno | 30–100 |
| guarda de caravana | 100–400 por viagem |
| missão de risco 1–2 | 50–900 |
| missão de risco 3–4 | 300–8 000 |
| missão de risco 5 | 2 000–20 000 |
| Ancião de seita | 1 000–5 000 |
| Mestre de seita | 5 000–50 000 |
| comerciante de tesouros | varia de −tudo a 10× tudo |

## 17.4 Saque

`sortear_tesouro(aleat, nivel_do_local, sorte=LUK)` devolve categoria, objeto e
quantidade de pedras. O grau é sorteado com pesos inteiros por nível:

| Nível do local | Mortal | Terra | Céu | Primordial |
|---:|---:|---:|---:|---:|
| 1 | 60 | 35 | 4 | 0 |
| 4 | 18 | 55 | 24 | 1 |
| 7 | 10 | 45 | 38 | 2 |
| 10 | 0 | 12 | 55 | 25 |
| 13 | 0 | 0 | 5 | 80 |

Sorte desloca os pesos dos graus superiores: cada ponto acima de 10 aumenta em 4%
o peso de Céu e Primordial.

Distribuição medida (3 000 sorteios por nível, Sorte 12):

| Nível | Mortal | Terra | Céu | Primordial | Pedras (mediana) |
|---:|---:|---:|---:|---:|---:|
| 1 | 45% | 46% | 9% | 0% | 31 |
| 4 | 11% | 46% | 42% | 2% | 525 |
| 7 | 1% | 12% | 71% | 16% | 8 400 |
| 10 | 0% | 1% | 30% | 68% | 126 000 |
| 13 | 0% | 0% | 2% | 98% | 2 100 000 |

Dentro do grau sorteado: 35% de chance de virar talismã, 25% de virar elixir, o
resto artefato. O **subgrau** (baixo/médio/alto) afeta apenas o valor em pedras
(×1, ×3, ×8 ÷ 3), nunca o objeto — para que ninguém "melhore" o subgrau de uma
espada depois de vê-la.

## 17.5 Face como moeda

Face (面子) não compra coisas, mas muda preços:

| Face de quem compra | Efeito no preço |
|---:|---|
| ≥ 12 (gloriosa) | −25%, e o vendedor agradece |
| 6–11 (respeitada) | −10% |
| 0–5 (neutra) | preço cheio |
| −7 a −1 (arranhada) | +25% |
| ≤ −8 (desonrada) | +100%, ou recusa de venda |

## 17.6 Dívida de honra

Um favor grande cria `SOCIAL:DIVIDA_DE_HONRA`: menor +1, grande +2 a +3 em
testes sociais contra o devedor, e o devedor **não pode** atacar o credor sem
registrar `quebrou_um_juramento` (−7) no livro de relações de todas as facções
que souberem.

Dívida de honra não prescreve. É herdada. Um clã inteiro pode dever a um
errante morto há sessenta anos, e isso é um gancho de campanha pronto.

## 17.7 O que o dinheiro não compra

Quatro coisas, deliberadamente:

1. **Grau de Núcleo Dourado.** Só preparo conta (Cap. 11.3). Um bilionário com
   uma sala ruim forma um núcleo grau 8.
2. **Compatibilidade com a Lei.** É atributo, e atributo tem teto.
3. **Sobreviver à tribulação.** Elixires e artefatos ajudam; nenhum substitui.
4. **Disposição de um NPC.** O Preço dele pode ser dinheiro, mas o ledger
   registra o que aconteceu entre vocês, e isso não se compra.
