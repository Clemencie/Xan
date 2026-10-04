# Capítulo 4 — Atributos e Perícias

## 4.1 Os seis atributos

O XAN usa os cinco atributos do *Amazing Cultivation Simulator* mais o
**Potencial** (根骨), que os romances tratam como uma coisa à parte: o teto do
que o corpo pode virar.

| Código | Nome | 中文 | Virtude (五常) | Elemento | O que mede |
|---|---|---|---|---|---|
| `per` | Percepção | 感知 | Sabedoria 智 | Água | notar, mirar, sentir Qi, reagir |
| `con` | Constituição | 體質 | Retidão 義 | Metal | aguentar dano, sustentar Qi, resistir a veneno |
| `cha` | Carisma | 魅力 | Propriedade 禮 | Fogo | presença, liderança, Face, negociação |
| `int` | Inteligência | 悟性 | Benevolência 仁 | Madeira | compreender manuais, romper gargalos, estratégia |
| `luk` | Sorte | 氣運 | — (Fio do Destino) | fora do ciclo | o que o céu reserva; afeta sorteios, não testes |
| `pot` | Potencial | 根骨 | Integridade 信 | Terra | velocidade e teto do cultivo, força bruta interna |

Faixa legal: **1 a 30**. Bônus = `(valor − 10) ÷ 2` arredondado para baixo,
portanto de **−5 a +10**:

| valor | 1 | 8 | 9 | 10 | 11 | 12 | 14 | 16 | 20 | 24 | 30 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bônus | −5 | −1 | −1 | 0 | 0 | +1 | +2 | +3 | +5 | +7 | +10 |

**Sorte é diferente dos outros cinco.** Ela quase nunca entra num teste direto:
ela desloca os pesos dos sorteios (Raiz Espiritual, tesouros, missões). Isso é
deliberado — um atributo que dá +5 em tudo torna os outros cinco irrelevantes.

## 4.2 Virtudes e atributos

As Cinco Virtudes confucianas governam o comportamento dos NPCs (Cap. 12) e
correspondem aos atributos **pelo elemento**:

| Virtude | Elemento | Atributo do mesmo elemento |
|---|---|---|
| 仁 Benevolência | Madeira | Inteligência |
| 義 Retidão | Metal | Constituição |
| 禮 Propriedade | Fogo | Carisma |
| 智 Sabedoria | Água | Percepção |
| 信 Integridade | Terra | Potencial |

Personagens de jogador não têm virtudes explícitas; elas aparecem quando o
personagem vira NPC de alguém (um discípulo, um rival, um inimigo jurado).

## 4.3 Perícias

Graduação de **0 a 5**, soma direto no teste. Perícias marcadas como
*treinadas* não podem ser usadas com graduação 0 — quem não sabe, não tenta.

`./xan tabelas pericias` lista todas. Resumo por grupo:

### Marciais (武)
`espada` 劍 · `sabre` 刀 · `lanca` 槍 · `punho` 拳 · `palma` 掌 ·
`arma_oculta` 暗器 *(treinada)* · `arco` 弓 · `cajado` 棍 ·
`arma_exotica` 奇門 *(treinada)* · `duelo` 對決 *(treinada)*

### Corporais (體)
`corpo_de_ferro` 鐵布衫 · `passos_leves` 輕功 · `resistencia_a_veneno` 抗毒 ·
`folego_interno` 內息 · `acupuntura_propria` 穴道 *(treinada)*

### Mentais (心)
`compreensao` 悟 · `meditacao` 入定 · `estrategia` 兵法 ·
`percepcao_de_qi` 氣感 *(treinada)* · `vontade_de_ferro` 道心

### Sociais (世)
`persuasao` · `intimidacao` · `etiqueta` 禮節 · `negociacao` 交易 ·
`mentira` 欺騙 *(treinada)* · `leitura_de_pessoas` 察言 *(treinada)* · `lideranca` 統領

### Saberes (學) — todos treinados, exceto onde indicado
`alquimia` 丹道 · `forja_de_artefatos` 煉器 · `talismas` 符籙 · `formacoes` 陣法 ·
`medicina` 醫術 · `ervas` 草藥 (livre) · `historia_das_seitas` 宗門史 (livre) ·
`leitura_de_fengshui` 風水 · `astrologia` 星象 · `bestas_espirituais` 妖獸 (livre) ·
`linguas_antigas` 古文

### Mundanas (凡)
`sobrevivencia` 求生 · `rastreamento` 追蹤 · `furtividade` 潛行 ·
`prestidigitacao` 手法 *(treinada)* · `cavalgar` 騎術 · `oficio` 工藝 ·
`comercio` 商道 · `navegacao` 航海 · `jogos` 賭 · `cozinha` 靈廚

## 4.4 Perícias em combate

Armas usam a perícia da arma. A distância decide se a arma serve:

| Distância | Armas que alcançam |
|---|---|
| toque | todas |
| curto | todas, exceto as de haste longa em corredor (a critério do terreno declarado) |
| médio | `arco`, `arma_oculta`, `lanca`, técnicas de Qi |
| longo | `arco` de guerra, técnicas de Qi de alcance longo |
| extremo | só técnicas com `alcance="extremo"` |

Atacar além do alcance declarado **não rola dado**: o motor recusa antes, e
informa o motivo. Atacar dentro do alcance aplica `ALCANCE:FAIXA`
(curto/médio 0, longo −2, extremo −4).

## 4.5 Valores passivos

Alguns números não são rolados; são calculados. Em valores passivos a graduação
conta **dobro** — é a diferença entre "eu tento" e "eu já sou assim".

| Valor passivo | Fórmula |
|---|---|
| Defesa (esquiva) | `10 + bônus de Percepção + Passos Leves + 2 se Manto de Qi` |
| Defesa (resistência) | `11 + bônus de Constituição + Corpo de Ferro + 2 se Manto de Qi` |
| Defesa (aparar) | `10 + bônus de Constituição + perícia da arma + 2 se Manto de Qi` |
| Percepção passiva | `10 + bônus de Percepção + 2 × graduação em Percepção de Qi` |
| Vontade passiva | `10 + bônus de Potencial + 2 × graduação em Vontade de Ferro` |
| Iniciativa | rolada: `d20 + bônus de Percepção + Duelo` |

**O nível de cultivo não entra na Defesa.** A diferença de reinos já é tratada
por `REINO:SUPRESSAO`; contá-la duas vezes tornaria mestres intocáveis e
destruiria a tensão.

## 4.6 Aprimoramento de atributos

Atributos sobem por três caminhos, todos custosos e todos registráveis:

1. **Cultivo**: a cada ruptura bem-sucedida, +1 em um atributo ligado à Lei
   (escolhido **antes** da ruptura e anotado na ficha).
2. **Elixir**: `ELI_ETERNIDADE` e `ELI_FLAGELO` dão +10% permanente com
   contrapartida. Usar dois mata.
3. **Remoldagem corporal** (caminho Corpo): partes do corpo substituídas por
   materiais espirituais, cada uma com bônus e custo próprios.

O teto absoluto é 30. Nenhuma combinação de efeitos o ultrapassa — o motor
recusa.

## 4.7 Graduações de perícia

Graduações sobem com **pontos de Compreensão** (悟), ganhos em estudo, missões e
rupturas:

| graduação | custo cumulativo |
|---:|---:|
| 1 | 50 |
| 2 | 150 |
| 3 | 400 |
| 4 | 900 |
| 5 | 2 000 |

Um discípulo aprende as perícias do mestre pela **metade** do custo enquanto o
mestre estiver vivo e disposto — é a regra mestre/discípulo do ACS e é a melhor
razão do jogo para não matar o próprio mestre.
