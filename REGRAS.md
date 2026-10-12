# MARÉ ALTA — Mutantes & Malfeitores 3ª Edição

Sistema de RPG solo de **super-heróis** rodando sobre **Mutantes & Malfeitores 3e**
(Steve Kenson, edição brasileira Jambô). O motor de dados, a dosagem de PdMs e o
filtro de coerência são da ferramenta; as regras são do livro.

> **O que veio do PDF e o que veio do sistema publicado está marcado em
> `mm3/regras.py`, bloco por bloco.** Ver "Fontes" no fim deste arquivo.

---

## 1 · A mecânica básica

**Tudo é `d20 + modificadores vs Classe de Dificuldade`.** Igual ou maior = sucesso.

| CD | Nome | Exemplo do livro |
|---|---|---|
| 0 | Muito fácil | perceber algo à vista |
| 5 | Fácil | escalar uma corda com nós |
| 10 | Médio | ouvir um segurança se aproximando |
| 15 | Difícil | desarmar um explosivo |
| 20 | Desafiador | nadar contra uma correnteza forte |
| 25 | Formidável | escalar uma montanha molhada e escorregadia |
| 30 | Heroico | sobrepujar um sistema de segurança sofisticado |
| 35 | Super-heroico | convencer guardas a deixar você entrar sem credencial |
| 40 | Quase impossível | rastrear um comando na selva sem lua após 12 dias de chuva |

**Graus:** cada 5 pontos de margem acima (ou abaixo) da CD = 1 grau. Frações ignoradas.
**20 natural** = sucesso crítico: calcula o grau e **sobe um passo** (pode transformar falha em sucesso).
**Teste de rotina:** sem pressão, use 10 no dado em vez de rolar.
**Oposição de rotina:** a CD é o modificador de quem se opõe **+10**.
**Circunstância:** ±2 para vantagem pequena, ±5 para grande.

---

## 2 · Criação de herói

**Nível de Poder (NP) 10** é o padrão do livro. **Pontos de poder = 15 × NP.**

| O que | Custo |
|---|---|
| Habilidade | 2 pp por graduação |
| Defesa | 1 pp por graduação **acima** do que a habilidade já dá |
| Perícia | 1 pp por 2 graduações |
| Vantagem | 1 pp por vantagem ou graduação |
| Poder | (custo do efeito + extras − falhas) × graduações |

### As oito habilidades
Força · Vigor · Agilidade · Destreza · Luta · Intelecto · Prontidão · Presença
(faixa −5 a 20; 0 = mediano, 7 = ápice humano)

### As cinco defesas
| Defesa | Vem de | Contra |
|---|---|---|
| Esquiva | Agilidade | ataques à distância |
| Aparar | Luta | ataques corpo-a-corpo |
| Fortitude | Vigor | veneno, doença, físico |
| Vontade | Presença | efeitos mentais |
| Resistência | Vigor (+ Proteção) | dano |

### Os cinco limites de Nível de Poder — **inegociáveis**
1. **Perícia:** habilidade + graduações + vantagem ≤ **NP + 10**
2. **Ataque + Efeito** ≤ **2 × NP** (efeito com salvamento mas sem ataque ≤ NP)
3. **Esquiva + Resistência** ≤ **2 × NP**
4. **Aparar + Resistência** ≤ **2 × NP**
5. **Fortitude + Vontade** ≤ **2 × NP**

É por isso que dá para fazer um herói de muito dano e pouca mira, ou o contrário —
mas nunca os dois no máximo. `heroi.criar()` **recusa** a ficha e lista tudo que estourou.

### Complicações
**Mínimo 2, sendo uma a Motivação.** O livro não dá ponto por complicação: quando o
mestre usa uma contra você, você ganha **1 ponto heroico**. Por isso herói tem vida
complicada — ele precisa dos pontos.

Motivações do livro: Aceitação · Adrenalina · Cobiça · Fazer o Bem · Justiça ·
Patriotismo · Reconhecimento · Responsabilidade.

---

## 3 · Pontos heroicos e esforço extra

**Pontos heroicos** (começa a sessão com 1, não guarda para a próxima):
editar a cena · feito heroico (ganha uma vantagem por um turno) · **melhorar uma
rolagem** (re-rola e fica com o melhor; 1–10 vira 11–20) · inspiração ·
repelir instantaneamente · recuperar-se.

**Esforço extra** (ação livre, 1× por turno): ação padrão extra · bônus +2 ·
poder +1 graduação · façanha de poder · salvamento extra · velocidade +1 · força +1.
**Custo:** no turno seguinte fica **Fatigado**. Fatigado → **Exausto**. Exausto →
**Incapacitado**. Gastar um ponto heroico cancela a fadiga.

---

## 4 · Condições

16 básicas (Atordoado, Compelido, Controlado, Debilitado, Desabilitado, Desatento,
Enfraquecido, Fatigado, Imóvel, Impedido, Indefeso, Normal, Prejudicado, Tonto,
Transformado, Vulnerável) e 13 combinadas (Abatido, Adormecido, Amarrado, Caído,
Cego, Exausto, Incapacitado, Moribundo, Paralisado, Restrito, Surdo, Surpreso, Transe).

**Moribundo:** Fortitude CD 15 por rodada. 2 graus de sucesso = estabilizado.
**3 graus de falha acumulados = morte.**

---

## 5 · As três regras da ferramenta (não são do livro — são nossas)

### 5.1 Ninguém gasta pensamento em obstáculo
O `d10` de **Peso Narrativo** decide a profundidade, e o mundo impõe o teto:

| d10 | Tier | O que a ferramenta elabora |
|---|---|---|
| 1–2 | T0 Decoração | nada — sem nome, sem desejo, sem ficha |
| 3–4 | T1 Obstáculo | nome + 1 traço + 1 desejo trivial + 1 poder, sempre do mesmo jeito |
| 5–7 | T2 Coadjuvante | + 2 traços, poderes, equipamento |
| 8–9 | T3 Peça-chave | + desejo profundo, **segredo**, complicações, 2 ganchos |
| 10 | T4 Âncora | + como pensa, o que esconde de si, ponta de trama |

Capanga de assalto **não** tem segredo. Isso é assertiva de teste, não promessa.

### 5.2 A forma manda no que existe
- **Animal** → teto T1, sem nome próprio (o rótulo é a espécie), sem segredo; ganha **instinto**.
- **Objeto** → teto T0, sem nome, sem desejo; ganha *o que faz* e *o que guarda*.
- **Ambiente** → teto T0; só *o que acontece*.
- **Humano** → nome a partir de T1, segredo só em T3+.

### 5.3 Tudo pertence a esta história
Cada encontro tem uma **ÂNCORA** de trama e passa por filtro de terreno + hora.
Cada facção tem **repertório próprio** de poderes: agente da AEGIS não anda com
frasco de água do mar; gente do Coro não anda com colete balístico.
Se a âncora não tocar nada estabelecido, o encontro entra **mudo** — vira detalhe e
**semente**, nunca "pizza, abacaxi, hambúrguer".

---

## 6 · O mundo

**Baía de Santa Clara.** Há quinze anos o mar recuou três quilômetros e voltou como
parede de luz. 1.200 mortos, 11.000 pessoas diferentes.

O que as autoridades não falam: **a Maré volta de quinze em quinze anos.**
O que está no Farol: a luz apagou na noite da Maré e nunca mais acendeu.

| Facção | Quer | Segredo |
|---|---|---|
| AEGIS-BR | manter o registro e o público sem pânico | sabe há dois anos que a Maré volta |
| O Panteão | renovar o contrato de transmissão | Ápice não tem poderes há dois anos; a empresa injeta |
| A Ressaca | manter o Morro fora do cadastro | esconde uma criança que **apaga** poderes |
| O Coro | que todo mundo ouça a música | o regente não é mais humano da cintura para baixo |
| Linha Vermelha | o monopólio da "poeira" | a poeira é feita com gente |
| Delegacia de O.E. | achar quem vazou a lista | o vazamento veio de dentro |
| Instituto (UFSC) | provar a periodicidade da Maré | a amostra do subsolo ainda está morna |
| Gente comum | chegar em casa | alguém da família "acordou" diferente |

9 terrenos, 76 encontros, 13 lugares, 8 ganchos de campanha.

---

## 7 · Rodando

```bash
python3 testes.py                          # invariantes (~7.500 sorteios)
python3 dados.py peso                      # d10 que dosa o PdM
python3 dados.py oraculo 70                # oráculo sim/não (Caos 5)
python3 dados.py cena                      # teste de cena (d10 vs Caos)
python3 dados.py encontro porto madrugada  # encontro filtrado
python3 dados.py faísca                    # Foco + Ação + Assunto
python3 dados.py cd                        # tabela de dificuldades do livro
```

| Arquivo | O que é |
|---|---|
| `dados.py` | CLI do motor: oráculo, cena, peso narrativo, encontro, faísca |
| `mm3/regras.py` | Habilidades, defesas, perícias, vantagens, 35 efeitos, condições, medidas, NP |
| `mm3/mundo.py` | Lore, 8 facções, 13 lugares, 76 encontros com âncora |
| `mm3/heroi.py` | Ficha com validação dos 5 limites, testes, ataque, esforço extra, pontos heroicos |
| `mm3/heroi_npc.py` | Gerador com dosagem por tier e forma |
| `mm3/encontros.py` | Sorteio com filtro de terreno/hora/forma |
| `testes.py` | Invariantes |
| `.arquivo/` | o sistema murim anterior, guardado |

---

## 8 · Fontes — o que é do PDF e o que não é

**Lido diretamente no `mutantes-malfeitores-3a-edicao.pdf`** (extração cobriu da
página 1 até ~40 de 224): créditos e ficha catalográfica; mecânica básica;
Tabela de Medidas completa; tabela de Classe de Dificuldade; graus de sucesso;
testes de rotina, opostos, comparativos, graduados e de equipe; modificadores de
circunstância; teste de ataque e de salvamento; rodada de ação; as 16 condições
básicas e as 13 combinadas; esforço extra e sua fadiga; pontos heroicos e seus
seis usos; pontos de poder iniciais; custo de características; os cinco limites de
Nível de Poder; NP efetivo de PdM; motivações e a lista de complicações.

**Não extraído** — o parser do PDF terminou no capítulo 2 (o restante do arquivo é
imagem pesada). Os capítulos de **Perícias, Vantagens, Poderes, Apetrechos,
Ação & Aventura e Mestrando** foram implementados a partir do sistema publicado,
e cada bloco em `mm3/regras.py` carrega a marcação `ADENDO (pág. N não extraída)`.
A **tabela de Resistência a Dano** (pág. 217) está implementada na forma
consagrada: CD 15 + graduações de dano; 1 grau de falha = abatido, 2 = atordoado,
3+ = incapacitado.

**Autoral (não é do livro):** o cenário Maré Alta, suas oito facções, os 76
encontros, a dosagem de PdMs por tier e o filtro de coerência.
