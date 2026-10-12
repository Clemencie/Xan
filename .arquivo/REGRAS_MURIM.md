# CÉU LACRADO — Livro de Regras Rígidas

Sistema solo murim/wuxia. As regras aqui são **a física do mundo**: as Nove Tábuas de
Jade deixadas pelo Último Ascendido não são filosofia, são lei mecânica. Quando uma
regra parece arbitrária, é porque uma Tábua manda assim.

> Tudo que está neste arquivo está implementado em código e coberto por `testes.py`.
> Se o texto e o código discordarem, o código venceu — e o texto é bug.

---

## 1 · Os Nove Degraus

| # | Degrau | Qi máx | PV máx | Teto de técnicas | O que muda no corpo |
|---|---|---|---|---|---|
| 1 | Forjamento Corporal | 10 | 10 | 3 | Ossos densos, ferida fecha rápido |
| 2 | Abertura de Meridianos | 22 | 16 | 5 | Qi corre de verdade; sente intenção a 3 passos |
| 3 | Condensação de Qi | 40 | 24 | 8 | **Qi sai do corpo**: lâmina de vento, palma à distância |
| 4 | Núcleo Interno | 70 | 34 | 12 | Núcleo no dantian; luta três dias sem dormir |
| 5 | Alma Nascente | 110 | 48 | 16 | Alma sai do corpo por instantes; mata cem soldados |
| 6 | Transformação Divina | 170 | 66 | 20 | Corpo obedece à vontade |
| 7 | Retorno ao Vazio | 250 | 88 | 24 | Presença desmaia mortal a 10 passos |
| 8 | Tribulação | 360 | 116 | 28 | O Céu tenta matá-lo ativamente |
| 9 | Ascensão | 500 | 150 | 32 | Nenhum vivo confirmado. Só lenda e ossos |

**Regra dura do degrau:** cada técnica tem um rank. Usar técnica acima do seu degrau dá
**Desvantagem** no acerto e **+2 de estresse de meridianos** (Tábua II). Não é proibido —
é caro.

**Regra dura do abismo:** contra oponente **4+ degraus acima**, você não consegue mirar
ponto fraco: **Dano −6** e Defesa dele recebe **+2 por degrau de diferença** no seu acerto
(como bônus negativo). Um rank 1 não mata um rank 6 na trocação. Ele mata com veneno,
emboscada, terreno, Dívida do Céu — ou não mata.

---

## 2 · Criação de personagem

### 2.1 Atributos (4)
| Atributo | Serve para |
|---|---|
| **Corpo** | força, resistência, acerto de golpe, PV, Defesa de Aparar |
| **Passo** | esquiva, furtividade, iniciativa, Defesa de Esquiva |
| **Mente** | percepção, tática, ler Qi alheio, resistir a ilusão |
| **Vontade** | Qi máximo, resistir a intenção assassina, meditação |

**Orçamento: 6 pontos.** Cada modificador custa:

| mod | −1 | 0 | +1 | +2 | +3 | +4 |
|---|---|---|---|---|---|---|
| custo | −1 | 0 | 2 | 4 | 7 | 12 |

(−1 devolve 1 ponto.) É impossível ter três atributos em +2. Isso é de propósito.

### 2.2 Estilo (7)
| Estilo | Dado de arma | Alcance | Passiva |
|---|---|---|---|
| Espada | d8 | 1 | +1 Aparar com lâmina |
| Sabre | d10 | 1 | Dano +2 contra mais de um alvo |
| Punho | d6 | 0 | Combo +1 dano por acerto seguido (máx +4); 1ª técnica custa 1 Qi a menos |
| Palma | d6 | 1 | Ignora metade da armadura; técnicas internas custam −2 Qi |
| Lança | d8 | 2 | +2 Aparar contra alcance 1; Desvantagem se colarem em você |
| Chicote | d6 | 2 | Pode desarmar; alvo fica −1 Defesa por 1 turno |
| Arco | d8 | 12 | Recarga é ação livre 1×/turno; Desvantagem corpo a corpo |

### 2.3 Origem (12)
Cada uma dá bônus de atributo, Qi/PV extras e **um gancho de campanha pronto**:

Bastardo de casa nobre · Discípulo expulso · Soldado de guarnição · Guarda de caravana ·
Herborista · Mendigo de rede · Caçador de serra · Ferreiro de lâminas · Médico itinerante ·
Ator de trupes · Condenado fugido · Órfão de clã caído.

### 2.4 Fórmulas
```
Qi máx = Qi do degrau + Qi da origem + 2 × max(0, mod Vontade)
PV máx = PV do degrau + PV da origem + max(0, mod Corpo)
Defesa de Aparar  = 10 + (degrau // 2) + mod Corpo  (+1 com Espada)
Defesa de Esquiva = 10 + (degrau // 2) + mod Passo
Pego de surpresa  = 5 + mod Passo   (as duas defesas caem para isso)
```

---

## 3 · Combate

### 3.1 Acerto
```
Acerto = d20 + mod Corpo + bônus de proficiência + 2 × (seu degrau − degrau do alvo)
Acerta se Acerto ≥ Defesa escolhida pelo alvo (Aparar ou Esquiva)
20 natural = acerto garantido, dano ×1,5 +2
1 natural  = falha garantida
```

### 3.2 Dano
```
Dano = (dado da técnica OU dado da arma) + (mod Corpo ÷ 2) + Qi investido no golpe
       × multiplicador de proficiência
       − 6 se o alvo estiver 4+ degraus acima
```
Cada ponto de **Qi investido** no golpe vira **+1 de dano**. É assim que se gasta Qi em luta.

### 3.3 Turno
1 **Ataque** (golpe simples ou técnica) + 1 **Movimento** + 1 **Ação livre** (respiração,
grito, sacar). Gastar Qi extra no golpe é parte do Ataque, não ação à parte.

**Iniciativa:** ambos rolam `d10 + mod Passo`; empate = quem declarou intenção primeiro.

### 3.4 Dano em PV
- PV ≤ 0 → **À Beira da Morte**: Vontade (CD 12) ou apaga. Cada turno apagado, −1 PV.
- Ferida que passe de metade do PV máx de uma vez = **ferida grave**: −1 em tudo até tratar.

---

## 4 · Qi, Fadiga, Estresse, Dívida

| Recurso | Sobe com | Desce com | Estoura em |
|---|---|---|---|
| **Qi** | meditação, sono, chá | técnicas, investir em dano | **Tábua I**: abaixo de 0 → **Contragolpe 1d6 de PV** e o golpe **não acontece** |
| **Fadiga** | cada uso de técnica (valor da técnica) | sono | **Tábua III**: a 10, a técnica some até você dormir |
| **Estresse de meridianos** | usar técnica acima do degrau (+2), abuso de Proibida | descanso longo | A 10: **Lesão de Meridiano** — −1 degrau efetivo por uma cena inteira |
| **Dívida do Céu** | técnica Proibida (+1 a +3) | nada. Nunca. | A cada 3 de Dívida: −1 PV máximo **permanente** |

**Regeneração**
- Em combate: `1d4 + max(0, Vontade)` de Qi (Respiração de Quatro Contas)
- Meditação (1 hora): `1d8 + 2 + max(0, Vontade)` de Qi
- Sono: Qi cheio, metade do PV, Fadiga e Estresse zerados

**Duelo declarado (Tábua V):** se os dois estão conscientes, sem pressa e se encaram,
**Mente substitui Corpo na Defesa**. Intenção vence força bruta — é por isso que duelo de
honra é perigoso até para o mais forte.

---

## 5 · Técnicas e proficiência

Toda técnica tem: **casa**, **rank**, **custo de Qi**, **dano**, **fadiga**, **tipo**,
**raridade**. 31 técnicas no livro, do `Corte Sujo` (rank 1, 2 Qi) à
`Palma da Tábua Rachada` (rank 8, Proibida, custa um ano de vida).

**Casa de origem é regra dura.** Só 7 técnicas são **genéricas** — o resto pertence a uma
facção. Um guarda da Corte Cinzenta não aparece usando `Passo sobre Juncos`, que é da
Garça Branca; quando ele não tem arte da casa no próprio degrau, improvisa o básico e a
ferramenta diz isso na ficha. A única exceção é o **Errante**, que por definição não tem
casa: cada técnica dele veio de um lugar diferente — e ele nunca aprende Proibida de graça.

**Proficiência — sobe com uso, não com nível:**

| Nível | Dano | Acerto | Custo | Como se sente |
|---|---|---|---|---|
| Entrada | ×1,0 | +0 | ×1,0 | funciona, mas você pensa antes |
| Pequena Realização | ×1,0 | +1 | ×1,0 | sai sem pensar |
| Grande Realização | ×1,5 | +2 | ×0,75 | o corpo faz sozinho |
| Perfeição | ×2,0 | +4 | ×0,5 | a técnica escolhe por você |

Sobe de nível: **3 usos sob pressão real** (combate ou risco), ou **10 treinos** com um mestre.

**Técnicas Proibidas (Tábua IV):** custam **0 Qi** e pagam em **PV próprio**, e cada uso
dá **Dívida do Céu**. Elas existem porque funcionam. É esse o ponto.

---

## 6 · As Nove Tábuas (regras do mundo)

| Tábua | Lei | Efeito mecânico |
|---|---|---|
| I | Canal vazio não carrega técnica | Qi abaixo de 0 → Contragolpe 1d6 e efeito nenhum |
| II | Corpo não temperado estoura | Técnica acima do degrau → Desvantagem e +2 estresse |
| III | O Nome cobra | Fadiga por uso; a 10 a técnica some até dormir |
| IV | Qi de sangue paga com vida | Proibida: 0 Qi, dano em PV próprio, +1 a +3 Dívida |
| V | Intenção vence força | Duelo declarado: Mente substitui Corpo na Defesa |
| VI | Ninguém vê acima de três degraus | 4+ degraus abaixo → Dano −6 |
| VII | A terra lembra | Em Ruína/Templo: Percepção +2, Qi regenera pela metade |
| VIII | Juramento pesa | Promessa com testemunha vira obrigação; quebrar = −1 em tudo por 1 cena |
| IX | Há um degrau acima do Último | Ninguém voltou para contar o custo |

---

## 7 · Motor de dados

### 7.1 Oráculo (d100)
`limiar = base + (Caos − 5) × 3`, preso entre 1 e 99.

| d100 | Leitura |
|---|---|
| ≤ limiar ÷ 5 | **SIM, E COM FORÇA** |
| ≤ limiar | **SIM** (com **SIM, MAS…** quando couber complicação) |
| até 5 acima | **NÃO, MAS…** |
| 6–10 acima | **NÃO** |
| 11+ acima | **NÃO, E PIROU** |

**Caos (1–9, começa em 5):** −1 quando você controla a cena, +1 quando está sob pressão.

**Duplas (11, 22 … 99):** se o algarismo da dupla for ≤ Caos, dispara **Evento Aleatório**
(Foco + Ação + Assunto) — e a interpretação é obrigação da ferramenta.

### 7.2 Teste de cena (d10 vs Caos)
- Acima do Caos → **ESPERADA**
- Ímpar ≤ Caos → **ALTERADA** (vira a próxima versão lógica da intenção)
- Par ≤ Caos → **INTERROMPIDA** (evento aleatório toma a cena)

### 7.3 CD de mundo
| Trivial | Fácil | Moderado | Difícil | Heroico | Lendário | Acima do Céu |
|---|---|---|---|---|---|---|
| 8 | 12 | 15 | 18 | 22 | 26 | 30 |

---

## 8 · Dosagem de NPCs — a regra que impede desperdício

O **d10 de Peso Narrativo** decide a profundidade. O mundo impõe o teto.

| d10 | Tier | O que a ferramenta gasta de pensamento |
|---|---|---|
| 1–2 | **T0 Decoração** | Nada. Sem nome, sem desejo, sem ficha. "O terceiro homem." |
| 3–4 | **T1 Obstáculo** | Nome + 1 traço + 1 desejo trivial + no máx. 1 técnica gasta |
| 5–7 | **T2 Coadjuvante** | Nome + 2 traços + desejo + 1–2 técnicas + proficiência |
| 8–9 | **T3 Peça-chave** | + desejo profundo + **segredo** + 2–4 técnicas + 2 ganchos |
| 10 | **T4 Âncora** | + como pensa + o que esconde de si + ponta de trama |

**Limites duros (testados em `testes.py`):**
- T0–T2 **nunca** recebem segredo nem interioridade. Obstáculo não consome sua atenção.
- T1 tem **exatamente 1 traço** e **no máximo 1 técnica**.
- **Fera**: teto T1, sem nome, sem segredo — ganha **instinto**, não desejo.
- **Sem forma** (névoa, Qi residual, silêncio): teto T0 — sem nome, sem desejo, sem
  técnica. Recebe apenas **o que faz**.
- **Mortal** (degrau 0): sem Qi, PV 5–8, dano 1d6, **nenhuma técnica de cultivo**.
- Ninguém do mesmo bando tem **nome ou traço repetido**. Quando o repertório da facção
  acaba (10 traços), o extra vira *"rosto comum — nada nele gruda na memória"*.
- O repertório de técnicas vem **da facção**, filtrado pelo degrau. Discípulo da Garça
  Branca não usa `Corte Sujo` de bandido.

---

## 9 · Encontros — filtro de coerência

Um encontro só sai se passar por três filtros: **terreno** (9 tabelas, 74 entradas),
**hora/clima** (noite dobra cão selvagem e gás de pântano; chuva forte cancela névoa),
e **forma** (rank 0 = ambiente, nunca vira ficha).

Cada entrada tem uma **ÂNCORA** — o gancho de trama ao qual pertence. Se a âncora não
tocar nada já estabelecido, o encontro entra **mudo**: vira detalhe de cenário e
**semente**, não fato. Nada de "pizza, abacaxi, hambúrguer".

---

## 10 · Progressão

Sobe de degrau quando: fecha uma trama inteira, sobrevive a um combate 2+ degraus acima,
ou treina com alguém 2+ degraus acima por uma cena inteira. Ao subir: Qi/PV no máximo,
teto de técnicas sobe, e o mundo repara — **NPCs de facção passam a tratá-lo diferente**.

---

## 11 · Arquivos

| Arquivo | O que é |
|---|---|
| `dados.py` | CLI do motor: oráculo, cena, peso narrativo, encontro |
| `ceu_lacrado/mundo.py` | Lore, 8 facções, 9 terrenos, 74 encontros, listas de evento |
| `ceu_lacrado/regras.py` | 28 técnicas, estilos, origens, Tábuas, tabelas |
| `ceu_lacrado/npc.py` | Gerador com dosagem por tier e forma |
| `ceu_lacrado/encontros.py` | Sorteio com filtro de terreno/hora/clima/forma |
| `ceu_lacrado/personagem.py` | Ficha, combate, Qi, estado persistente |
| `testes.py` | Invariantes: ~7.300 sorteios exigindo coerência |
