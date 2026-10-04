# Capítulo 21 — Tabelas

Todas as tabelas numéricas do sistema num lugar só. Os valores aqui são os
valores do código: se divergirem, o código venceu e este arquivo está desatualizado.

## 21.1 Dificuldades

| 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 50 |
|---|---|---|---|---|---|---|---|---|
| trivial | fácil | média | difícil | muito difícil | heroica | sobrenatural | imortal | proibida |

Faixa legal: 1–60.

## 21.2 Bônus de atributo

`bônus = (valor − 10) ÷ 2`, arredondado para baixo. Faixa: −5 a +10.

| 1 | 2–3 | 4–5 | 6–7 | 8–9 | 10–11 | 12–13 | 14–15 | 16–17 | 18–19 | 20–21 | 24–25 | 30 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| −5 | −4 | −3 | −2 | −1 | 0 | +1 | +2 | +3 | +4 | +5 | +7 | +10 |

## 21.3 Graus de sucesso

| Margem | Grau | Nome ficcional |
|---:|---|---|
| ≤ −1 | `fracasso` | — |
| 0 a 4 | `sucesso` | — |
| 5 a 9 | `sucesso_maior` | — |
| ≥ 10 | `triunfo` | — |
| face 1 | `fracasso_critico` | **desvio** |
| face 20 | `sucesso_critico` | **toque do Dao** |

## 21.4 Reinos

| Nv. | Trilha | Qi base | Vit. base | Longevidade | Saída | DD | XP |
|---:|---|---:|---:|---:|---|---:|---:|
| 0 | Mortal | 0 | 20 | 70 | rolagem | 12 | 100 |
| 1 | Temperado | 20 | 25 | 90 | rolagem | 13 | 250 |
| 2 | Concentrado | 35 | 30 | 100 | rolagem | 14 | 600 |
| 3 | Moldador | 55 | 36 | 120 | rolagem | 16 | 1 400 |
| 4 | Portão da Mente | 80 | 45 | 150 | rolagem | 18 | 3 000 |
| 5 | Caldeirão | 110 | 55 | 180 | rolagem | 20 | 6 500 |
| 6 | Moldador de Essência | 150 | 70 | 220 | **pontuação** | — | 14 000 |
| 7 | Núcleo Dourado | 200 | 90 | 300 | rolagem | 24 | 28 000 |
| 8 | Alquimia | 260 | 115 | 400 | rolagem | 26 | 55 000 |
| 9 | Embrionário | 340 | 150 | 500 | **tribulação ×3** | — | 110 000 |
| 10 | Incubação da Origem | 440 | 200 | 800 | rolagem | 30 | 220 000 |
| 11 | Espírito Ascendente | 560 | 260 | 1 200 | **tribulação ×4** | — | 440 000 |
| 12 | Espírito Primordial | 700 | 340 | 2 000 | **tribulação ×9** | — | — |
| 13 | Ascensão | 900 | 600 | ∞ | — | — | — |

```
Qi máximo  = Qi base + Constituição + Percepção÷2 + Inteligência÷2 + bônus do Núcleo
Vitalidade = Vit. base + 2×Constituição + Potencial + 3×nível
bônus do Núcleo (nível ≥ 7) = (10 − grau) × 25 + nível × 5
```

## 21.5 Defesa

```
esquiva      = 10 + bônus de Percepção   + Passos Leves
resistência  = 11 + bônus de Constituição + Corpo de Ferro
aparar       = 10 + bônus de Constituição + perícia da arma
+2 com Manto de Qi (custa 10 Qi/rodada)
+3 dedicando o turno a defender   ┐ exclusivos
+2 com Guarda Total               ┘
```

O nível **não** entra na Defesa — a lacuna de reinos já é `REINO:SUPRESSAO`.

## 21.6 Dano

```
Dano = dados da técnica + bônus do atributo + margem÷2 + nível × 4
```

Sem técnica: dado base `1d(6 + 2×(nível÷2))`.

## 21.7 Registro de Regras (36)

`./xan tabelas regras` imprime tudo com descrição, capítulo, fatos exigidos e
limite. Resumo dos limites:

| Domínio | Regras | Faixas |
|---|---|---|
| ELEMENTO | RELACAO | −2 a +2 |
| REINO | SUPRESSAO | −10 a +10 |
| ALCANCE | FAIXA | −4 a 0 |
| POSICAO | TERRENO, FLANCO, EMBOSCADA | −1 a +2 |
| ALVO | COBERTURA, PASSOS_LEVES | −5 a 0 |
| AMBIENTE | LUZ, CLIMA, FENGSHUI, DENSIDADE_QI, FORMACAO | −4 a +3 |
| ESTADO | FERIMENTO, EXAUSTAO, VISAO, IMOBILIZADO, DESVIO_DE_QI, DEMONIO_INTERIOR | −4 a 0 |
| RECURSO | ARTEFATO, TALISMA, ELIXIR | 0 a +4 |
| PREPARO | ESTUDO_PREVIO, MEDITACAO, QUEIMA_LONGEVIDADE | 0 a +5 |
| COMBATE | SURPRESA, ACOES_MULTIPLOS, GUARDA_TOTAL, DEFESA_DECLARADA | −10 a +4 |
| SOCIAL | DISPOSICAO, FACE, HIERARQUIA, DIVIDA_DE_HONRA, SEGREDO_EXPOSTO | −4 a +3 |
| FACCAO | RELACAO | −2 a +2 |
| DESEJO | PRIORIDADE | 0 a +6 |

**Exclusivas:** Guarda Total × Defesa Declarada · Emboscada × Surpresa ·
Meditação × Desvio de Qi.

## 21.8 Núcleo Dourado

| Parcela | Fórmula | Máx. |
|---|---|---:|
| Qi máximo | `qi ÷ 100` | ~4 |
| Feng Shui | muito_auspicioso +8 · auspicioso +4 · neutro 0 · sinistro −4 · muito_sinistro −8 | +8 |
| Densidade de Qi | esteril −8 · pobre −4 · comum 0 · rica +4 · veia +8 · terra_imortal +12 | +12 |
| Harmonia elemental | Cap. 9.7 | +12 |
| Estado mental | `estado ÷ 10` | +20 |
| Elixir | nenhum 0 · menor 2 · médio 5 · maior 9 · celestial 14 | +14 |
| Compatibilidade | `match ÷ 10` | +15 |
| Compreensão | `pontos ÷ 200` | — |
| Artefato | mortal 0 · terra 2 · céu 5 · primordial 9 | +9 |
| Mestre presente | sim +4 | +4 |

| ≥95 → 1 | 85–94 → 2 | 72–84 → 3 | 60–71 → 4 | 48–59 → 5 | 36–47 → 6 | 25–35 → 7 | 15–24 → 8 | <15 → 9 |
|---|---|---|---|---|---|---|---|---|

## 21.9 Tribulação

```
raios (saída do nível):  6 demoníaca → 1 · 9 → 3 · 11 → 4 · 12 → 9   (+1 se Lei demoníaca)
DD do raio k      = 14 + nível + 2×(k−1)
poder do raio k   = 30 + 43×nível + 20×(k−1)
dano se falhar    = max(1, poder − total)     → Qi absorve primeiro
```

## 21.10 Desvio de Qi

| 1d6 (+deslocamento por gravidade) | Efeito |
|---:|---|
| 1 | perde 25% dos pontos de cultivo e 1d6 de Vitalidade |
| 2 | −1 permanente em Constituição até cura por Ancião |
| 3 | instala um Demônio Interior (gere o NPC) |
| 4 | regressão: −1 nível e perde a técnica mais recente |
| 5 | coma de 1d4 meses; −2 em Percepção por um ano |
| 6 | **morte definitiva** |

Gravidade: comum +0 · grave +1 · catastrófica +2.

## 21.11 Raiz Espiritual

| Elementos | Grau | Pureza máx. | Multiplicador base |
|---:|---|---:|---:|
| 1 | Céu 天 | 100 | 400 |
| 2 | Terra 地 | 85 | 220 |
| 3 | Preto 玄 | 65 | 140 |
| 4 | Amarelo 黃 | 45 | 90 |
| 5 | Desperdício 廢 | 30 | 40 |

`multiplicador = base + (pureza − 50)÷5 + 25 se mutação`.

**Tabelas de raridade (pesos por nº de elementos):**

| Tabela | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|
| `realista` | 1 | 20 | 200 | 1 200 | 8 579 |
| `heroica` | 40 | 360 | 1 600 | 3 000 | 5 000 |
| `lendária` | 300 | 1 400 | 2 800 | 3 200 | 2 300 |
| `mortal` | 0 | 2 | 30 | 400 | 9 568 |

**Mutação (pesos em 10 000 por grau):** Céu 2 500 · Terra 400 · Preto 80 ·
Amarelo 25 · Desperdício 30.

## 21.12 NPC — prioridades de desejo

| Camada | Prioridade |
|---|---:|
| linha vermelha | 6 (**veto, não rola**) |
| medo | 5 |
| dever | 4 |
| obsessão / segredo | 3 |
| ambição | 2 |
| desejo imediato | 1 |
| preço | 0 |

## 21.13 NPC — conduta por margem

| ≤−16 | −15…−11 | −10…−6 | −5…−1 | 0…+4 | +5…+9 | +10…+14 | +15…+19 | ≥+20 |
|---|---|---|---|---|---|---|---|---|
| ataca | hostil | expulsa | recusa | negocia | ajuda condicional | ajuda generosa | revela segredo | jura lealdade |

## 21.14 Livro de relações

`salvou_a_vida +6 · salvou_um_ente_querido +8 · curou_uma_ferida +3 ·
ensinou_uma_tecnica +4 · deu_um_presente_de_grau_superior +3 ·
cumpriu_uma_promessa +3 · defendeu_em_publico +4 · venceu_um_duelo_honrado +2 ·
perdeu_um_duelo_honrado −1 · mentiu_para_ele −3 · roubou_dele −5 ·
humilhou_em_publico −6 · matou_um_aliado −10 · matou_um_familiar −20 ·
quebrou_um_juramento −7 · revelou_o_segredo_dele −12 · recusou_ajuda_em_crise −4 ·
trocou_favores +2 · compartilhou_uma_refeicao +1 · serviu_juntos_na_mesma_seita +2 ·
faccoes_em_guerra −4 · faccoes_aliadas +3 · hierarquia_superior_dele +2 ·
hierarquia_inferior_dele −1 · dever_de_honra +5`

| ≥10 | 6–9 | 3–5 | −2–2 | −5…−3 | −9…−6 | ≤−10 |
|---|---|---|---|---|---|---|
| devoto | amigável | cordial | neutro | desconfiado | hostil | inimigo jurado |
| +3 | +2 | +1 | 0 | −1 | −2 | −4 |

## 21.15 Magnitude de pedidos

| 10 | 12 | 14 | 17 | 18 | 20 | 23 | 28 | 32 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| informação comum | direção/abrigo | favor sem risco | empréstimo de bem | informação sensível | escolta | risco de vida menor | traição de facção | segredo mortal | sacrifício de vida |

## 21.16 Valores esperados exatos (conferência)

Frações exatas calculadas por estatística de ordem — não por simulação:

| Expressão | Valor esperado | Variância |
|---|---|---|
| `1d20` | 21/2 = 10,5 | 133/4 = 33,25 |
| `2d6` | 7 | 35/6 ≈ 5,833 |
| `3d6` | 21/2 = 10,5 | 105/12 |
| `4d6kh1` | 6797/1296 ≈ 5,2446 | ≈ 0,9101 |
| `4d6kh3` | ≈ 12,2446 | — |
| `4d6kl1` | 2275/1296 ≈ 1,7554 | — |
| `2d20kh1` | 13,825 | — |
| `3d6kh2` | ≈ 8,4583 | — |
| `5d6kl2` | ≈ 4,0698 | — |
| `2d6kh1` | ≈ 4,4722 | — |
| `6d6kh4` | ≈ 17,3445 | — |
| `3d8kl2` | 7,03125 | — |
| `2d6!` | 42/5 = 8,4 | — |
| `1d10!8` | 55/7 ≈ 7,8571 | — |
| `3dF` | 0 | — |
| `1d20+5` | 31/2 = 15,5 | — |

Sanidade: `E[min de 2d20] + E[máx de 2d20] = 7,175 + 13,825 = 21 = 2 × 10,5`.

## 21.17 Estatísticas de criação

Média medida sobre **200 000 sorteios por tabela**. Com Sorte 10 (neutro) as
frequências reproduzem os pesos publicados — propriedade coberta por teste:

| Tabela | Céu | Terra | Preto | Amarelo | Desperdício |
|---|---:|---:|---:|---:|---:|
| realista | 0,01% | 0,20% | 1,95% | 12,05% | 85,79% |
| heroica | 0,38% | 3,60% | 16,13% | 29,92% | 49,97% |
| lendária | 2,98% | 13,92% | 27,98% | 31,98% | 23,13% |
| mortal | 0,01% | 0,02% | 0,30% | 4,04% | 95,63% |

Atributos por `4d6kh3`: média medida **12,2753** sobre 9 000 amostras
(teórico 12,2446 = 15869/1296).

## 21.18 Mundo gerado

Medido sobre 6 mundos, 2 878 pares de facções:

| Aliadas (≥60) | Neutras (−19…19) | Em guerra (≤−60) |
|---:|---:|---:|
| 16,5% | 20,4% | 9,3% |

## 21.19 Combate

Simulação de 60 duelos de nível 6 em cenário neutro:

| Métrica | Valor |
|---|---:|
| taxa de acerto | 57,7% |
| turnos por duelo | 17,8 (mín. 9, máx. 29) |
| rodadas por duelo | 9,6 (máx. 15) |
| duelos sem resolução em 400 turnos | 0 |

## 21.20 Certificação de justiça

| Métrica | Valor |
|---|---:|
| testes | 40 |
| amostras | 3 521 846 |
| α por teste | 0,001 |
| falha dura | p < 10⁻⁶ |
| aprovados | 40 |
| **veredito** | **APROVADO** |
