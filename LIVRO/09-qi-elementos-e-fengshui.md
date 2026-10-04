# Capítulo 9 — Qi, Elementos e Feng Shui

## 9.1 Wuxing (五行)

Dois ciclos, cinco elementos, e nenhum deles é decorativo: ambos viram número.

**Ciclo de Geração (生)** — cada elemento alimenta o próximo:

```
Madeira → Fogo → Terra → Metal → Água → Madeira
```

**Ciclo de Superação (剋)** — cada elemento domina o próximo:

```
Madeira → Terra → Água → Fogo → Metal → Madeira
```

## 9.2 A regra ELEMENTO:RELACAO

Com `elemento_atacante` e `elemento_alvo` declarados:

| Relação | Modificador | Exemplo |
|---|---:|---|
| atacante **supera** o alvo | **+2** | Metal corta Madeira |
| atacante é **gerado** pelo alvo | +1 | Água alimenta Madeira |
| **iguais** ou algum é neutro | 0 | Fogo contra Fogo |
| atacante **gera** o alvo | −1 | Madeira alimenta Fogo (você o nutre) |
| atacante é **superado** pelo alvo | **−2** | Madeira contra Metal |

Tabela completa em `TABELA_RELACAO`; `./xan tabelas regras` mostra o limite.

Elementos fora do ciclo (`nenhum`, `vazio`) não geram nem superam: valem 0
contra tudo, e são por isso valiosos — uma Lei sem elemento não pode ser
contrariada por elemento nenhum.

## 9.3 Elementos e o resto do sistema

| Elemento | Atributo | Virtude | Estação | Direção | Cor | Órgão |
|---|---|---|---|---|---|---|
| Madeira 木 | Inteligência | Benevolência 仁 | primavera | leste | verde | fígado |
| Fogo 火 | Carisma | Propriedade 禮 | verão | sul | vermelho | coração |
| Terra 土 | Potencial | Integridade 信 | fim de verão | centro | amarelo | baço |
| Metal 金 | Constituição | Retidão 義 | outono | oeste | branco | pulmão |
| Água 水 | Percepção | Sabedoria 智 | inverno | norte | preto | rim |

## 9.4 Qi (氣)

O Qi é uma substância, não uma metáfora. No jogo ele tem quatro funções:

1. **Mana** — paga o custo das técnicas.
2. **Escudo** — absorve dano antes da Vitalidade (Cap. 10.6).
3. **Combustível de cultivo** — circulado em meditação, vira pontos de cultivo.
4. **Fato ambiental** — a densidade de Qi do local modifica testes
   (`AMBIENTE:DENSIDADE_QI`, −2 a +3).

### Densidade de Qi

| Valor 0–10 | Fato | Modificador | Onde aparece |
|---:|---|---:|---|
| 0–1 | `esteril` | −2 | desertos, terras devastadas, campos de batalha antigos |
| 2–3 | `pobre` | −1 | interior afastado de veias |
| 4–5 | `comum` | 0 | a maior parte do mundo |
| 6–7 | `rica` | +1 | proximidade de veia espiritual |
| 8–9 | `veia_espiritual` | +2 | sobre uma veia; sede das grandes seitas |
| 10 | `terra_imortal` | +3 | reinos secretos, picos de Ascensão |

**Exaustão:** quando `qi_atual < qi_maximo ÷ 4`, `ESTADO:EXAUSTAO` aplica −1.
Quando o Qi chega a zero, o escudo some e cada técnica custa Vitalidade na
proporção 1:2.

## 9.5 Feng Shui (風水)

O Feng Shui de um lugar é um fato declarado (e pode ser medido com a perícia
`leitura_de_fengshui`, DD 15 para avaliar um cômodo, 20 para um terreno, 25 para
uma montanha inteira).

| Fato | Modificador | Pontos no Núcleo Dourado |
|---|---:|---:|
| `muito_auspicioso` | +2 | +8 |
| `auspicioso` | +1 | +4 |
| `neutro` | 0 | 0 |
| `sinistro` | −1 | −4 |
| `muito_sinistro` | −2 | −8 |

Para um cultivador corporal, o Feng Shui do quarto gera Essência por mês (Cap.
7.3). Para um Xiandao, ele entra no cálculo do Núcleo Dourado — e aí os oito
pontos de diferença entre uma sala muito auspiciosa e uma muito sinistra podem
ser exatamente a distância entre o grau 3 e o grau 4. **Por isso os cultivadores
brigar por uma sala é canônico, não é frescura.**

## 9.6 O calendário

* Ano de **12 meses** lunares, mês de **30 dias**, 4 estações de 3 meses.
* Dia dividido em **12 shichen** (時辰) de duas horas, cada um com polaridade
  Yin ou Yang.

| Shichen | 字 | Horas | Polaridade |
|---|---|---|---|
| Zǐ | 子 | 23–01 | yang (o yang nasce no yin pleno) |
| Chǒu | 丑 | 01–03 | yin |
| Yín | 寅 | 03–05 | yang |
| Mǎo | 卯 | 05–07 | yin |
| Chén | 辰 | 07–09 | yang |
| Sì | 巳 | 09–11 | yin |
| Wǔ | 午 | 11–13 | yang |
| Wèi | 未 | 13–15 | yin |
| Shēn | 申 | 15–17 | yang |
| Yǒu | 酉 | 17–19 | yin |
| Xū | 戌 | 19–21 | yang |
| Hài | 亥 | 21–23 | yin |

Horas Yang (06–18) favorecem Fogo e Madeira. Horas Yin (21–04) favorecem Água e
Metal. Terra é neutra e recebe +1 em qualquer polaridade.

## 9.7 Janelas auspiciosas e harmonia elemental

Cada elemento tem melhor estação e melhor quinzena. A **harmonia elemental** do
momento vale de 0 a 12 pontos e entra no cálculo do Núcleo Dourado:

| Componente | Pontos |
|---|---:|
| estação dentro da janela auspiciosa | +4 |
| dia dentro da quinzena auspiciosa | +2 |
| polaridade da hora coincide com o elemento | +2 (Terra: sempre +1) |
| polaridade contrária | −2 |
| clima manifesta o elemento | +4 |
| clima neutro | +1 |
| clima de elemento que **supera** o seu | −3 |
| clima de outro elemento | −1 |

| Elemento | Melhores estações | Quinzena | Clima que manifesta |
|---|---|---|---|
| Fogo | primavera, verão | dias 1–15 | miasma, calor extremo |
| Madeira | inverno, primavera | dias 1–15 | chuva, nevoeiro |
| Metal | outono, inverno | dias 16–30 | tempestade |
| Água | outono, inverno | dias 16–30 | chuva, nevasca, frio extremo |
| Terra | verão, outono | todos | — |

```bash
./xan nucleo --qi 420 --elemento metal --estacao inverno --dia 25 --polaridade yin \
             --clima tempestade --fengshui muito_auspicioso --densidade terra_imortal \
             --mental 150 --elixir maior --compat 141 --compreensao 2400 --mestre --artefato ceu
```

O comando imprime cada parcela com a justificativa. Nenhum ponto aparece sem
motivo escrito.

## 9.8 Clima

O clima de cada província, para cada um dos 360 dias do ano corrente, é sorteado
**uma vez** na geração do mundo e gravado no JSON. O mesmo dia nunca muda de
clima no meio da sessão — porque mudar seria interferência.

Os pesos por estação são inteiros e estão em `calendario._PESOS_CLIMA`. A região
com elemento forte puxa o clima correspondente (peso ×3), e altitude ≥ 2 dobra
nevasca e frio extremo e corta chuva pela metade.
