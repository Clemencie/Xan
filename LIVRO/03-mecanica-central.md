# Capítulo 3 — A Mecânica Central

## 3.1 A fórmula

```
d20 + bônus de atributo + graduação de perícia + modificadores de regras ≥ DD
```

Quatro parcelas, e cada uma tem uma origem diferente e verificável:

| Parcela | De onde vem | Faixa |
|---|---|---|
| `d20` | entropia auditada | 1–20 |
| bônus de atributo | `(atributo − 10) ÷ 2`, arredondado para baixo | −5 a +10 |
| graduação de perícia | ficha do personagem | 0 a +5 |
| modificadores | Registro de Regras, recalculado dos fatos | cada um tem limite próprio |

**A dificuldade (DD)** vem da tabela 3.3 ou de um valor passivo (Defesa em
combate, Cap. 10).

### Exemplo completo

Lin Yue (Percepção 14, Espada 4) ataca do alto de um telhado um cultivador de
Madeira usando uma técnica de Metal, sob chuva, à noite:

```
d20 = 13
bônus de Percepção = (14 − 10) ÷ 2 = +2
graduação em Espada = +4
ELEMENTO:RELACAO   metal supera madeira = +2
POSICAO:TERRENO    eu estou no alto     = +1
AMBIENTE:LUZ       penumbra             = −1
AMBIENTE:CLIMA     chuva                = −1
ALVO:COBERTURA     parcial              = −2
                                  total = 13 + 2 + 4 + 2 + 1 − 1 − 1 − 2 = 18
Defesa do alvo                          = 16
margem = 18 − 16 = +2 → SUCESSO
```

Todos os sete fatos foram declarados antes do dado. O motor grava isso.

## 3.2 Notação de dados

| Notação | Significado | Exemplo |
|---|---|---|
| `NdS` | N dados de S faces, soma | `3d6` |
| `NdS!` | explosivo: cada face máxima rola de novo e soma | `2d6!` |
| `NdS!T` | explode no limiar T (T ≥ 1) | `1d10!8` |
| `NdS kh M` | rola N, mantém os M **maiores** | `4d6kh3` (clássico) |
| `NdS kl M` | rola N, mantém os M **menores** | `4d6kl1` |
| `NdF` | dados Fudge/Fate (−1, 0, +1) | `3dF` |
| `d%` | percentile (1–100) | `d%` |
| `A ± B` | expressões com soma e subtração, incluindo termos negativos | `1d20 − 1d4 + 2` |

Limites de segurança: no máximo 1 000 dados por termo, 1 000 000 de faces, 256
explosões em cadeia. Expressões ambíguas (`1d20 5`) são recusadas em vez de
interpretadas.

`./xan rolar "4d6kh3" --teoria` imprime também o **valor esperado exato** em
fração e o mínimo/máximo — calculados por estatística de ordem, não por
simulação. `4d6kh3` = 15869/1296 ≈ 12,2446.

## 3.3 Tabela de dificuldades

| DD | Nome | Referência |
|---:|---|---|
| 5 | trivial | um mortal treinado consegue quase sempre |
| 10 | fácil | um profissional consegue |
| 15 | média | exige competência real |
| 20 | difícil | exige talento ou preparo |
| 25 | muito difícil | exige maestria |
| 30 | heroica | exige maestria **e** circunstância favorável |
| 35 | sobrenatural | só cultivadores de reino alto |
| 40 | imortal | o limite do que um ser pode fazer |
| 50 | proibida | existe para ser recusada |

Faixa legal de DD: 1 a 60. Fora disso o motor recusa a declaração.

## 3.4 Graus de sucesso

O grau vem da **margem** (total − DD), e só dela:

| Margem | Grau | O que significa na ficção |
|---:|---|---|
| < 0 | `fracasso` | não aconteceu, e o mundo respondeu |
| 0 a 4 | `sucesso` | aconteceu, pelo preço esperado |
| 5 a 9 | `sucesso_maior` | aconteceu melhor ou mais rápido |
| ≥ 10 | `triunfo` | aconteceu e ainda sobrou alguma coisa |

E duas exceções de face natural, que só valem quando a expressão é exatamente um
`1d20` sem modificadores de dado:

| Face | Grau | Nome |
|---:|---|---|
| 1 | `fracasso_critico` | **desvio** — algo quebrou: Qi, osso, plano ou reputação |
| 20 | `sucesso_critico` | **toque do Dao** — o mundo concedeu; vai além do pedido |

Face natural nunca anula a aritmética: um 20 com margem −12 continua sendo um
20 natural (toque do Dao) **e** um fracasso de margem. O motor registra os dois
e o mestre interpreta os dois: você falha, e algo extraordinário acontece
apesar disso.

## 3.5 Testes opostos

Quando dois lados agem, cada um rola e compara-se o total. A cascata de
desempate é fixa e está no código:

1. maior total;
2. maior graduação na perícia usada;
3. maior valor bruto do atributo;
4. maior reino de cultivo declarado no contexto;
5. persistindo o empate, **o defensor prevalece**.

O quinto item é deliberado: num empate verdadeiro, quem não precisava fazer
nada não perde nada. Isso evita que empate vire "o mestre decide".

## 3.6 Modificadores: o Registro de Regras

Existem 36 regras registradas, em 11 domínios. Cada uma:

* tem código `DOMINIO:NOME`;
* declara quais fatos exige — sem o fato, a regra não entra;
* recalcula o próprio valor a partir do fato, toda vez;
* tem um limite numérico; produzir algo fora dele é erro;
* cita o capítulo do livro onde está escrita.

`./xan tabelas regras` imprime todas. `EXCLUSIVAS` declara pares que não podem
coexistir (Guarda Total × Defesa Declarada; Emboscada × Surpresa; Meditação ×
Desvio de Qi) — tentar declarar os dois juntos aborta a rolagem.

Alguns domínios:

| Domínio | Exemplos |
|---|---|
| `ELEMENTO:` | relação Wuxing entre atacante e alvo (−2 a +2) |
| `REINO:` | supressão de cultivo: ±2 por nível de lacuna, limitado a ±10 |
| `POSICAO:` | terreno, flanco, emboscada |
| `ALVO:` | cobertura, passos leves |
| `AMBIENTE:` | luz, clima, feng shui, densidade de Qi, formação |
| `ESTADO:` | ferimento, exaustão, visão, imobilização, desvio de Qi, demônio interior |
| `RECURSO:` | artefato, talismã, elixir |
| `PREPARO:` | estudo prévio, meditação, queima de longevidade |
| `COMBATE:` | surpresa, ações múltiplas, guarda total, defesa declarada |
| `SOCIAL:` | disposição, face, hierarquia, dívida de honra, segredo exposto |
| `FACCAO:` | relação entre facções |
| `DESEJO:` | prioridade entre camadas de desejo de um NPC |

## 3.7 Falhar bem

Fracasso não é "nada acontece". Role 1d6 na tabela e aplique — ou declare a
consequência antes da rolagem, que é melhor ainda:

| d6 | Consequência do fracasso |
|---:|---|
| 1 | **Progresso com custo**: acontece, mas custa Qi, tempo, um item ou uma promessa |
| 2 | **Complicação**: um terceiro aparece, ou um fato da cena muda contra você |
| 3 | **Ruído**: alguém importante soube do que você tentou |
| 4 | **Dano**: 1d6 de Vitalidade por nível de risco da ação, ou Qi equivalente |
| 5 | **Perda de Face**: −1 de Face; registre no livro de relações de quem viu |
| 6 | **Desvio menor**: −5 de estado mental; se chegar a 0, role a tabela de Desvio de Qi (Cap. 11.6) |

## 3.8 Ações fora de combate

Cada personagem tem, por turno de cena (não de combate):

* **uma ação** (o que exige teste);
* **um movimento** (deslocar-se, sacar, falar uma frase);
* **uma reação** (responder a algo que aconteceu no turno de outro).

Ações extras no mesmo turno são possíveis e custam caro: a regra
`COMBATE:ACOES_MULTIPLOS` aplica penalidade cumulativa conforme o número de
ações declaradas.

## 3.9 Auxílio

Um aliado pode ajudar se tiver graduação ≥ 1 na mesma perícia e fizer sentido na
ficção. O auxílio é declarado **antes** do teste principal e concede +1 (só um
auxiliar conta; dois não somam +2). O auxiliar fica exposto às mesmas
consequências do fracasso.

## 3.10 O que o motor grava

Cada `resolver()` com diário produz três registros encadeados por SHA-256
(compromisso, rolagem, revelação). O diário é JSONL append-only, com `fsync` a
cada linha, raiz de Merkle calculável e um comando `selar` que grava o hash da
cabeça num arquivo separado — para guardar fora do repositório da mesa.

Verificação a qualquer momento:

```bash
./xan auditoria verificar --diario mundos/minha-mesa/auditoria/diario.jsonl
./xan auditoria selar     --diario mundos/minha-mesa/auditoria/diario.jsonl --saida selos/2026-10-03.txt
```
