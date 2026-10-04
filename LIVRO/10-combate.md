# Capítulo 10 — Combate

## 10.1 Sequência de um encontro

1. **Declarar o cenário.** Terreno, luz, clima, feng shui, densidade de Qi e
   formação. Isso acontece **antes** de qualquer dado e fica gravado no diário
   como `encontro_aberto`. Depois disso o cenário só muda se um fato mudar de
   verdade (alguém apagou as tochas, começou a chover, a formação foi rompida).
2. **Declarar o modo de defesa** de cada combatente: esquiva, resistência ou
   aparar. Trocar de modo consome a ação do turno.
3. **Rolar iniciativa.** Uma vez por encontro, `d20 + bônus de Percepção +
   Duelo`. Desempate: total → graduação em Duelo → ordem alfabética (para o
   desempate nunca depender de preferência).
4. **Turnos.** Cada turno: uma ação, um movimento, uma reação.
5. **Encerrar** quando um lado cai, foge, se rende ou é expulso. O encerramento
   também é gravado.

## 10.2 Atacar

```
d20 + bônus do atributo da arma + graduação da arma + regras  ≥  Defesa do alvo
```

Atributo por tipo de arma:

| Perícia | Atributo |
|---|---|
| `espada`, `sabre`, `punho`, `palma`, `cajado` | Constituição |
| `arco`, `arma_oculta`, `lanca` | Percepção |
| `arma_exotica`, `duelo` | Percepção |
| técnicas de Qi | depende da técnica (campo `pericia` dela) |

## 10.3 Defesa

Três modos, declarados antes do primeiro ataque:

| Modo | Base | Atributo | Perícia | Quando usar |
|---|---:|---|---|---|
| **esquiva** 閃 | 10 | Percepção | Passos Leves | contra muitos atacantes ou golpes lentos |
| **resistência** 硬 | 11 | Constituição | Corpo de Ferro | contra dano alto e único |
| **aparar** 格 | 10 | Constituição | a própria arma | quando você também pretende atacar |

`Defesa = base + bônus de atributo + graduação (+2 com Manto de Qi)`
`(+3 se dedicar o turno a defender, +2 com Guarda Total — estas duas últimas
são exclusivas entre si)`

**Manto de Qi:** opção declarada que dá +2 de Defesa e custa 10 de Qi por
rodada. Se o Qi acabar, o Manto cai sozinho. É a única forma de comprar Defesa
com recurso — e o motivo de uma luta longa sempre acabar mal para quem tem menos
Qi.

## 10.4 Supressão de Reino em combate

Além do modificador `REINO:SUPRESSAO` (±2 por nível de lacuna, teto ±10), vale a
cláusula dura:

> **Três ou mais níveis abaixo do alvo, o ataque não rola dado. O motor recusa e
> explica o motivo.**

Só uma técnica marcada `ignora_supressao` atravessa. São sete no jogo, todas de
nível 7 para cima:

| Técnica | Lei | Nível |
|---|---|---:|
| `SM_ALMA_ESPADA` 劍魂 | Espada dos Sete Massacres | 11 |
| `PJ_LUZ_DE_YUQING` 玉清光 | Pureza de Jade | 9 |
| `CE_GOLPE_SEM_APEGO` 無情斬 | Corte das Emoções | 7 |
| `RC_MAO_ROUBA_CEU` 偷天手 | Roubo Celestial | 8 |
| `SR_SELO_SEIS_ROTAS` 六道印 | Seis Rotas de Reincarnação | 7 |
| `SMP_SELO_DIVINO` 神居籙 | Símbolos Primordiais | 10 |
| `SD_JULGAMENTO` 審判 | Trovão Celestial | 8 |

## 10.5 Cobertura, posição, luz, clima

| Fato | Valores → modificador |
|---|---|
| `ALVO:COBERTURA` | nenhuma 0 · parcial −2 · três-quartos −4 · total −5 |
| `POSICAO:TERRENO` | alto +1 · neutro 0 · baixo −1 |
| `POSICAO:FLANCO` | flanqueado +2 |
| `POSICAO:EMBOSCADA` | oculto e não percebido +2 |
| `COMBATE:SURPRESA` | alvo surpreso +4 |
| `ALVO:PASSOS_LEVES` | alvo com Passos Leves ativo −2 |
| `AMBIENTE:LUZ` | plena 0 · penumbra −1 · escuridão −2 · trevas −4 |
| `AMBIENTE:CLIMA` | limpo/nublado 0 · chuva/nevoeiro −1 · nevasca/tempestade/miasma −2 |
| `AMBIENTE:FORMACAO` | aliada +2 · nenhuma 0 · hostil −2 |
| `COMBATE:ACOES_MULTIPLOS` | −2 por ação além da primeira no turno |
| `COMBATE:GUARDA_TOTAL` | +2 (exige não atacar) |
| `COMBATE:DEFESA_DECLARADA` | +3 (dedica o turno inteiro) |

Emboscada e Surpresa **não podem** ser declaradas juntas. Se você preparou a
emboscada, o alvo não foi pego de surpresa por outro motivo — e o motor recusa a
declaração que tentar as duas.

## 10.6 Dano

```
Dano = dados da técnica
     + bônus do atributo de ataque
     + margem do acerto ÷ 2   (arredondado para baixo)
     + nível × 4
```

Sem técnica, o dado base é `1d(6 + 2 × (nível ÷ 2))`: 1d6 nos níveis 0–1, 1d8
nos 2–3, 1d10 nos 4–5, 1d12 nos 6–7 e assim por diante.

**Ordem de absorção:** o Qi absorve primeiro, 1 por 1. O que sobrar cai na
Vitalidade.

| Exemplo (nível 6, técnica 3d8, CON 16, margem +6) | |
|---|---:|
| 3d8 = 14 | |
| + bônus de Constituição | +3 |
| + margem ÷ 2 | +3 |
| + nível × 4 | +24 |
| **dano** | **44** |
| Qi do alvo | 178 → 134 |
| Vitalidade | intacta |

## 10.7 Escala de dano por nível

Média de dano de um golpe típico (atributo 14, margem +4):

| Nível | Dano médio | Qi + Vitalidade típicos | Golpes para derrubar |
|---:|---:|---:|---:|
| 1 | 12 | 108 | 9 |
| 3 | 24 | 141 | 6 |
| 6 | 44 | 308 | 7 |
| 9 | 68 | 557 | 8 |
| 12 | 92 | 1146 | 12 |

Encontros de mesmo nível duram entre 6 e 12 rodadas. Se estiver durando 30,
alguém está defendendo demais — e isso é uma escolha tática legítima, não um
problema de regra.

## 10.8 Estados em combate

| Estado | Fato | Efeito |
|---|---|---|
| Ferido (≥ 40% da Vitalidade) | `ferimento: ileso` | — |
| Ferido (< 75%) | `ferimento: ferido` | −1 |
| Grave (< 40%) | `ferimento: grave` | −2 |
| Agonizando (< 15%) | `ferimento: agonizando` | −3 |
| Exausto (Qi < ¼ do máximo) | `ESTADO:EXAUSTAO` | −1 |
| Imobilizado | `ESTADO:IMOBILIZADO` | −4 |
| Cego | `visao: cego` | −4 |
| Visão parcial | `visao: parcial` | −2 |
| Desvio de Qi | `ESTADO:DESVIO_DE_QI` | −3 e não pode meditar |
| Demônio Interior ativo | `ESTADO:DEMONIO_INTERIOR` | −2 |

O estado de ferimento é **derivado da aritmética** (`vitalidade_atual ÷ máxima`),
não declarado. Ninguém escolhe estar "mais ou menos ferido".

## 10.9 Fugir, render-se, perseguir

* **Fugir** é um teste oposto de Passos Leves contra a Percepção do perseguidor.
  Vencer sai do encontro; perder concede ao perseguidor um ataque gratuito com
  `COMBATE:SURPRESA`.
* **Render-se** encerra o combate e registra `venceu_um_duelo_honrado` (+2) para
  o vencedor e `perdeu_um_duelo_honrado` (−1) para o perdedor no livro de
  relações. Matar quem se rendeu registra `matou_um_aliado` (−10) com **todas**
  as facções que ficaram sabendo.
* **Perseguir** além do alcance de Passos Leves do fugitivo encerra a perseguição
  por falta de condição, não por decisão do mestre.

## 10.10 Combate em massa

Para batalhas entre seitas, não role por soldado. Use **unidades**:

* cada unidade tem nível, tamanho (10 / 100 / 1 000 soldados) e moral;
* uma unidade age como um único combatente com Vitalidade = tamanho × nível;
* formações aplicam `AMBIENTE:FORMACAO` a todas as unidades do mesmo lado;
* um personagem pode agir sozinho contra uma unidade: o dano dele é multiplicado
  por 10 se ele for 2+ níveis acima do nível da unidade, e por 0 se for 3+
  níveis abaixo (supressão de reino aplicada a exércitos).

Role 1d6 a cada rodada de batalha para eventos: `1` reforços de um lado, `2`
traição, `3` duelo de comandantes, `4` terreno colapsa, `5` clima vira, `6` nada.
O dado decide, e o evento é público.

```bash
./xan combate --semente duelo-teste --nivel 6 --defensivo --diario mundos/minha-mesa/auditoria/diario.jsonl
```
