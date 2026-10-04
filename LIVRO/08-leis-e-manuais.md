# Capítulo 8 — Leis e Manuais

## 8.1 O que é uma Lei (功法)

A Lei é o método de cultivo: como o personagem converte Qi do mundo em Qi
próprio, que técnicas ele pode aprender e que preço paga. Escolher a Lei é a
segunda decisão mais importante da criação, depois da Raiz — e, diferente da
Raiz, ela é uma escolha.

`./xan tabelas leis` imprime as 30 publicadas.

## 8.2 Compatibilidade com a Lei (Law Match)

Cada Lei exige mínimos de atributo. A compatibilidade é um percentual inteiro:

```
por atributo exigido:  razão = min(valor, 2 × requisito) × 100 ÷ requisito
compatibilidade     =  média das razões, limitada a 0..150
```

Cumprir exatamente o requisito dá 100%. O dobro dá 200% (truncado em 150% na
média). Abaixo, cai proporcionalmente.

Efeito na DD de ruptura:

| Compatibilidade | Ajuste na DD |
|---|---|
| > 100 | −1 a cada 25 pontos acima |
| 60–100 | nenhum |
| < 60 | +1 a cada 15 pontos faltantes |

E efeito na velocidade de cultivo: pontos mensais × `compatibilidade ÷ 100`.

```bash
./xan ruptura --ator "Lin Yue" --nivel 5 --lei SETE_MASSACRES --int 16 --per 14 --con 15 --cha 12 --luk 14 --pot 13 --compreensao 4
```

## 8.3 As cinco Leis Supremas Taiyi (太乙)

As Taiyi são as Leis elementais básicas. Qualquer uma delas leva à Ascensão; o
que muda é o caminho.

| Código | Nome | 中文 | Elemento | Requisitos |
|---|---|---|---|---|
| `TAIYI_METAL` | Sabedoria do Grande Carro | 北斗洞心劫法 | Metal | PER 7, CON 4, INT 5 |
| `TAIYI_MADEIRA` | Seis Rotas de Reincarnação | 長生六道輪迴經 | Madeira | CON 6, INT 6, LUK 3, PER 4 |
| `TAIYI_AGUA` | Dezesseis Passos Supremos | 太和十六洞天 | Água | CON 7, CHA 5, INT 6 |
| `TAIYI_FOGO` | Refino do Sol Verdadeiro | 三陽三昧丙丁煉火訣 | Fogo | PER 5, CON 5, CHA 5, INT 5, LUK 5 |
| `TAIYI_TERRA` | Refino do Girassol | 葵花煉神大法 | Terra | PER 6, CHA 6, INT 6 |

**Refino do Sol Verdadeiro** é a Lei do equilíbrio: exige cinco atributos
parelhados, o que significa que só um generalista a aproveita. É a mais difícil
de começar e a mais flexível de terminar.

**Seis Rotas de Reincarnação** é a Lei que trata a morte como etapa. Ela concede
`SR_CORPO_QUE_RENASCE` no nível 10: uma vez por ano o personagem sobrevive a
dano letal, perdendo um nível e as memórias do último mês.

## 8.4 Leis avançadas não-Taiyi

| Código | Nome | Elemento | Requisitos | Ajuste de DD |
|---|---|---|---|---:|
| `CORTE_EMOCOES` | Corte das Emoções 太上忘情道 | Fogo | PER 5, CHA 9, INT 5 | +1 |
| `ALQUIMIA_PRIMORDIAL` | Alquimia Primordial 九轉金丹直指 | Fogo | PER 6, CON 5, INT 6 | 0 |
| `ROUBO_CELESTIAL` | Roubo Celestial 偷天決 | Terra | CON 9, LUK 3 | +2 |
| `SETE_MASSACRES` | Espada dos Sete Massacres 七殺劍訣 | Metal | PER 7, CON 7, LUK 4 | +1 |
| `MIL_ARTEFATOS` | Mil Artefatos 己寅九衝多寶真解 | Madeira | PER 8, INT 5, LUK 3 | 0 |
| `PUREZA_JADE` | Pureza de Jade 玉清仙法 | nenhum | PER 4, INT 7, LUK 6 | 0 |
| `SIMBOLOS_PRIMORDIAIS` | Símbolos Primordiais 太元五符元籙 | nenhum | PER 8, CHA 4, INT 8 | 0 |
| `CONQUISTA_NIMBO` | Conquista do Nimbo 雲霄征伐律 | nenhum | PER 6, CHA 6, LUK 6 | +1 |

Duas merecem aviso:

* **Corte das Emoções** exige Carisma 9 e concede `CE_CORACAO_SERENO`: imune a
  Demônio Interior comum, estado mental nunca abaixo de 40 — **e o personagem
  não pode mais formar laços novos.** É a Lei mais poderosa do jogo para quem
  aceita jogar alguém que está deixando de ser pessoa.
* **Roubo Celestial** é a mais rápida e a mais odiada. Cada ruptura exige
  sacrificar longevidade, um laço ou uma vítima — declarado antes da rolagem.

## 8.5 Leis Shendao

| Código | Nome | Requisitos |
|---|---|---|
| `TROVAO_CELESTIAL` | Salvação pelo Trovão Celestial 九天雷救經 | CHA 7, INT 5, CON 4 |
| `OITO_CEUS` | Sadhana dos Oito Céus 八天修行法 | CHA 6, PER 6, INT 6 |
| `SALVACAO_SUBMUNDO` | Salvação do Submundo 幽冥救苦經 | CHA 8, INT 4 |

## 8.6 Leis corporais

| Código | Nome | Elemento | Requisitos |
|---|---|---|---|
| `VAJRA_DOURADO` | Corpo do Vajra Dourado 金剛不壞體 | Metal | CON 8, POT 5 |
| `DRAGAO_AZUL` | Corpo Imortal do Dragão Azul 青龍不死身 | Madeira | CON 6, POT 7 |
| `TARTARUGA_NEGRA` | Carapaça da Tartaruga Negra 玄武甲功 | Água | CON 7, PER 4 |
| `FENIX_CARMESIM` | Corpo da Fênix Carmesim 朱雀焚身訣 | Fogo | CON 7, POT 6 |
| `MONTANHA_INABALAVEL` | Montanha Inabalável 不動山嶽體 | Terra | CON 9, POT 4 |

## 8.7 Leis marciais (Murim)

As nove ortodoxas e as não-ortodoxas, com as casas clássicas:

| Código | Nome | Casa | Elemento |
|---|---|---|---|
| `AMEIXEIRA` | Espada da Flor de Ameixeira 梅花劍法 | Monte Hua 華山 | Madeira |
| `PALMA_TAIJI` | Palma Taiji 太極掌 | Wudang 武当 | Água |
| `PUNHO_VAJRA` | Punho Arhat 羅漢拳 | Shaolin 少林 | Metal |
| `AGULHAS_TANG` | Agulhas Ocultas 唐門暗器術 | Clã Tang 唐門 | Metal |
| `FORMACOES_ZHUGE` | Formações 諸葛奇門陣 | Clã Zhuge 諸葛 | Terra |
| `CAJADO_MENDIGO` | Cajado do Mendigo 打狗棒法 | Seita dos Mendigos 丐幫 | Madeira |
| `PALMA_DRAGAO_PENG` | Palma do Dragão do Norte 彭家龍掌 | Família Peng 彭 | Fogo |
| `DEMONIO_CELESTIAL` | Demônio Celestial 天魔功 | Culto Demoníaco 天魔教 | Fogo (demoníaca) |
| `SANGUE_SETE_ESTRELAS` | Sangue das Sete Estrelas 七殺血功 | seita não-ortodoxa | Água (demoníaca) |

Leis demoníacas somam **+1 raio** em toda tribulação e **+2** na DD de ruptura.
O céu cobra mais caro o atalho, e cobra em número.

## 8.8 Manuais (典籍)

A Lei é o método; o **manual** é o objeto que o ensina. Manuais têm grau:

| Grau | Subgraus | O que contém | Preço típico |
|---|---|---|---|
| Mortal 凡 | baixo / médio / alto | técnicas de nível 0–3 | 50–500 pedras |
| Terra 地 | baixo / médio / alto | técnicas de nível 4–6 | 2 000–20 000 |
| Céu 天 | baixo / médio / alto | técnicas de nível 7–9 | 100 000–1 000 000 |
| Primordial 元 | baixo / médio / alto | técnicas de nível 10–13, uma Lei inteira | não tem preço; tem dono |

**Aprender de um manual** exige um teste de Compreensão contra DD
`12 + 2 × grau do manual`, e consome pontos de Compreensão iguais a
`grau × subgrau × 200`. Falhar não destrói o manual: apenas não ensina, e o
personagem pode tentar de novo depois de um mês de jogo.

**Inspiración (靈感):** pontos ganhos em estudo, ruínas e conversas com mestres.
Cada ponto de Inspiração reduz em 10 o custo em Compreensão do próximo manual.
A Inspiração não acumulada é perdida a cada ruptura — é a mecânica que impede
alguém de juntar dez anos de estudo para o dia seguinte.

## 8.9 Mestre e discípulo

* Um discípulo aprende as perícias do mestre pela **metade** do custo em
  Compreensão enquanto o mestre estiver vivo e disposto.
* O mestre pode transferir Qi diretamente (perda de 20% na transferência).
* Matar o próprio mestre é uma das poucas ações que **todas** as facções
  ortodoxas punem com caçada vitalícia: registre `matou_um_superior` no livro de
  relações de cada facção ortodoxa do continente.
* Um mestre só pode ter `nível ÷ 2` discípulos internos de uma vez.
