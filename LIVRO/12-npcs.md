# Capítulo 12 — NPCs: Personalidade e Desejos

> Requisito deste sistema: **NPCs têm personalidades e desejos.**
> Aqui isso não é uma sugestão de interpretação. É um modelo com números,
> tabelas e um procedimento de resolução no dado.

## 12.1 As três camadas

```
PERSONALIDADE  →  o que ele é           (Cinco Virtudes + Temperamento + Traços)
DESEJOS        →  o que ele quer        (oito camadas, frequentemente em conflito)
RELAÇÕES       →  o que ele sente por você  (livro-razão de fatos com peso inteiro)
```

A personalidade **causa** os desejos: cada camada de desejo é sorteada com peso
derivado das virtudes do NPC. Um NPC de Retidão alta não sorteia "vende
informações para uma facção inimiga" como segredo com a mesma probabilidade que
um de Sabedoria alta e Benevolência baixa. Isso é o que faz o NPC parecer uma
pessoa em vez de uma lista.

## 12.2 As Cinco Virtudes (五常)

Cada uma de 1 a 10. Média mortal = 5.

| Virtude | 字 | Elemento | Atributo equivalente | Alta significa | Baixa significa |
|---|---|---|---|---|---|
| Benevolência | 仁 | Madeira | Inteligência | protege, ensina, perdoa | cruel, indiferente |
| Retidão | 義 | Metal | Constituição | cumpre juramentos, pune traição | oportunista |
| Propriedade | 禮 | Fogo | Carisma | valoriza hierarquia e Face | selvagem, direto |
| Sabedoria | 智 | Água | Percepção | planeja, desconfia, prevê | ingênuo, impulsivo |
| Integridade | 信 | Terra | Potencial | previsível, leal, constante | volúvel, mentiroso |

Bônus derivado: `(virtude − 5) ÷ 2`, de −2 a +2. A virtude **dominante** e a
**falha** são calculadas e aparecem na ficha.

## 12.3 Os Oito Temperamentos (八卦)

Cada NPC tem exatamente um. Ele dá bônus social, bônus de iniciativa e um
**gatilho** — a coisa que o faz perder o controle.

| Código | Nome | 卦 | Natureza | Social | Iniciativa | Gatilho |
|---|---|---|---|---:|---:|---|
| `qian` | O Céu | 乾 ☰ | imperativo | +2 | +1 | ser desobedecido por um inferior |
| `kun` | A Terra | 坤 ☷ | receptivo | +1 | −1 | ser forçado a escolher sozinho |
| `zhen` | O Trovão | 震 ☳ | impulsivo | −1 | +3 | ser interrompido ou humilhado |
| `xun` | O Vento | 巽 ☴ | instável | +2 | +2 | ficar preso a um compromisso |
| `kan` | A Água | 坎 ☵ | astuto | 0 | +1 | ser exposto ou lido por alguém |
| `li` | O Fogo | 離 ☲ | apaixonado | +3 | 0 | ser ignorado ou deixado de fora |
| `gen` | A Montanha | 艮 ☶ | obstinado | −2 | 0 | ser apressado |
| `dui` | O Lago | 兌 ☱ | comunicativo | +3 | −1 | silêncio prolongado ou solidão |

**Como usar o gatilho:** quando alguém dispara o gatilho em cena, o NPC faz um
teste de `d20 + bônus de Potencial + Vontade de Ferro + prioridade da camada
"obsessão"` contra DD 12. Falhar significa que ele age pelo temperamento, não
pelo plano — e isso é registrado no diário.

## 12.4 Traços

Cada NPC tem de 2 a 4 traços, sorteados com peso derivado das virtudes, e
traços incompatíveis nunca coexistem (Guarda rancor × Perdoa fácil demais; Sangue
quente × Prudência extrema; Coração frágil × Coração de pedra; Paranoico ×
Confiança cega; Despreza os fracos × Protege os fracos; Boca solta × Guarda
segredo até a morte; Jovem mestre arrogante × Servo humilde).

Cada traço tem um **efeito numérico escrito**, não uma sugestão vaga. Alguns
exemplos dos 44 publicados:

| Traço | Efeito |
|---|---|
| Leva juramentos a sangue | +3 para resistir a qualquer proposta que exija quebrar um juramento |
| A face acima de tudo | −4 em testes que envolvam humilhação pública; +2 quando há plateia |
| Matador frio | imune a Demônio Interior por mortes cometidas; +1 de dano contra alvo ferido |
| Duelista vaidoso | +2 de dano no golpe anunciado, mas o alvo ganha +1 de Defesa |
| Coração do Dao frágil | −10 de estado mental após qualquer fracasso crítico; risco de Desvio de Qi dobrado |
| Mentor paciente | discípulos aprendem manuais pela metade do custo de Compreensão |
| Jovem mestre arrogante | +3 em hierarquia contra inferiores, −3 contra superiores; provoca duelos |
| Colecionador de armas | +1 em `RECURSO:ARTEFATO` com armas; paga 50% acima do preço por armas de grau Céu |
| Retornado do abismo | +2 em Vontade de Ferro contra medo; −2 social com quem não sabe |

`./xan npc` gera tudo isso de uma vez.

## 12.5 As oito camadas de desejo

| Camada | O que é | Prioridade |
|---|---|---:|
| **Linha vermelha** | o que ele jamais fará | 6 — **veto absoluto** |
| **Medo** | o gatilho de fuga | 5 |
| **Dever** | a lealdade que o prende | 4 |
| **Obsessão** | a compulsão que ele não controla | 3 |
| **Segredo** | o fato que ele protege | 3 |
| **Ambição** | o objetivo de vida | 2 |
| **Desejo imediato** | o que ele quer nesta cena | 1 |
| **Preço** | pelo que ele se vende | 0 |

Exemplos reais gerados pelo sistema:

* *Linha vermelha:* nunca mata crianças — nem demônios crianças.
* *Medo:* um homem específico que ele já viu uma vez.
* *Dever:* para com uma promessa feita a um moribundo.
* *Obsessão:* não consegue mentir. Fisicamente.
* *Segredo:* nunca formou o Núcleo — finge com truques e talismãs.
* *Ambição:* acabar com uma facção demoníaca inteira.
* *Desejo imediato:* entregar uma carta sem saber o que ela contém.
* *Preço:* que alguém o chame de mestre, com sinceridade.

### A linha vermelha não vai ao dado

Quando um conflito envolve a linha vermelha, ela vence **sem rolagem**. O motivo
é registrado no diário como `veto`. Dar ao acaso a chance de fazer um NPC cruzar
a única linha que ele jurou não cruzar seria quebrar a promessa do sistema de
que NPCs são pessoas — e pessoas com linha vermelha não a atravessam por causa
de um 20.

### Conflito entre as outras camadas

Quando duas camadas mandam condutas incompatíveis (o Dever diz "fique", o Medo
diz "fuja"), resolve-se no dado:

```
cada lado:  d20 + bônus do atributo da virtude governante + Vontade de Ferro
            + DESEJO:PRIORIDADE (o número da tabela acima)
            contra DD 10
vence: maior soma de total + prioridade
desempate: prioridade maior; persistindo, ordem alfabética (determinístico)
```

A virtude governante de cada camada: Medo→Sabedoria, Linha vermelha→Retidão,
Dever→Integridade, Obsessão/Desejo imediato→Benevolência, Ambição→Propriedade,
Preço/Segredo→Sabedoria.

```bash
# no motor: resolver_conflito_de_desejos(npc, "dever", "ambicao", aleat)
```

## 12.6 Conduta: o que o NPC faz quando não é óbvio

A pergunta mais comum da mesa é "ele aceitaria?". No XAN ela não é respondida
pelo mestre. É rolada.

```
d20 + bônus de Carisma + Persuasão + bônus de Propriedade
    + SOCIAL:DISPOSICAO + SOCIAL:FACE (+ SOCIAL:HIERARQUIA, FACCAO:RELACAO,
      SOCIAL:DIVIDA_DE_HONRA, SOCIAL:SEGREDO_EXPOSTO quando declarados)
    ≥ DD da magnitude do pedido + Integridade×2 − bônus social do temperamento
```

### Magnitude do pedido

| Magnitude | DD | Exemplo |
|---|---:|---|
| `informacao_comum` | 10 | onde fica a pousada |
| `direcao_ou_abrigo` | 12 | abrigo por uma noite |
| `favor_sem_risco` | 14 | apresentar alguém |
| `emprestimo_de_bem` | 17 | emprestar um manual |
| `informacao_sensivel` | 18 | quem matou o Ancião |
| `escolta_ou_viagem` | 20 | escoltar até a montanha |
| `risco_de_vida_menor` | 23 | mentir por ele diante de um Ancião |
| `traicao_de_faccao` | 28 | abrir o portão à noite |
| `segredo_mortal` | 32 | revelar onde fica a ruína proibida |
| `sacrificio_de_vida` | 40 | morrer no lugar dele |

### Tabela de conduta (por margem)

| Margem | Conduta |
|---:|---|
| ≤ −16 | **ataca** — considera o pedido uma ameaça |
| −15 a −11 | **hostil** — recusa com hostilidade aberta e avisa quem manda |
| −10 a −6 | **expulsa** — manda recado de que não quer vê-lo de novo |
| −5 a −1 | **recusa** — recusa seca e encerra o assunto |
| 0 a +4 | **negocia** — exige um preço condizente com o Preço dele |
| +5 a +9 | **ajuda_condicional** — cobra um favor registrado (`trocou_favores`) |
| +10 a +14 | **ajuda_generosa** — ajuda e ainda oferece informação sobre o Desejo imediato |
| +15 a +19 | **revela_segredo** — deixa escapar parte do Segredo |
| ≥ +20 | **jura_lealdade** — oferece um juramento (`dever_de_honra`) |

### Qual desejo se manifesta

Entre as camadas capazes de produzir a conduta sorteada, vence a de maior
`prioridade × 10 + bônus da virtude governante` **para aquele NPC**. É conta
fechada sobre a personalidade dele — não sorteio extra, não preferência do
mestre. Por isso dois NPCs diferentes podem recusar o mesmo pedido por motivos
diferentes, e a mesa fica sabendo qual.

## 12.7 Disposição: um livro-razão, não uma impressão

A Disposição (−10 a +10 na prática, sem teto no ledger) é a **soma dos pesos**
dos eventos registrados entre o NPC e aquele alvo específico. Cada evento tem um
peso fixo de catálogo — declarar um peso diferente do catálogo é erro.

| Evento | Peso | Evento | Peso |
|---|---:|---|---:|
| salvou a vida | +6 | mentiu para ele | −3 |
| salvou um ente querido | +8 | roubou dele | −5 |
| curou uma ferida | +3 | humilhou em público | −6 |
| ensinou uma técnica | +4 | matou um aliado | −10 |
| deu presente de grau superior | +3 | matou um familiar | **−20** |
| cumpriu uma promessa | +3 | quebrou um juramento | −7 |
| defendeu em público | +4 | revelou o segredo dele | −12 |
| venceu duelo honrado | +2 | recusou ajuda em crise | −4 |
| perdeu duelo honrado | −1 | trocou favores | +2 |
| compartilhou refeição | +1 | serviram na mesma seita | +2 |
| facções aliadas | +3 | facções em guerra | −4 |
| hierarquia superior dele | +2 | hierarquia inferior dele | −1 |
| dever de honra | +5 | | |

### Categorias derivadas

| Soma | Categoria | Fato para `SOCIAL:DISPOSICAO` |
|---:|---|---|
| ≥ 10 | devoto | +3 |
| 6 a 9 | amigável | +2 |
| 3 a 5 | cordial | +1 |
| −2 a 2 | neutro | 0 |
| −5 a −3 | desconfiado | −1 |
| −9 a −6 | hostil | −2 |
| ≤ −10 | inimigo jurado | −4 |

A categoria é **derivada** da soma. Ninguém declara "ele está amigável"; declara-
se o que aconteceu, e a categoria sai da conta.

## 12.8 Face (面子)

Face vai de −50 a +50 e traduz reputação no fato `SOCIAL:FACE`:

| Face | Fato | Modificador |
|---:|---|---:|
| ≤ −8 | desonrada | −3 |
| −7 a −1 | arranhada | −1 |
| 0 a 5 | neutra | 0 |
| 6 a 11 | respeitada | +1 |
| ≥ 12 | gloriosa | +2 |

Ganhar e perder Face é consequência pública: sempre que alguém é humilhado,
elogiado diante de testemunhas, vence um duelo ou é desmentido, registre.

## 12.9 Agendas (relógios de 6 segmentos)

Todo NPC importante tem de 0 a 2 **agendas**: planos que avançam fora de cena.

```
[ ][ ][ ][ ][ ][ ]   0/6 — "reunir recursos para a próxima ruptura"
[■][■][■][ ][ ][ ]   3/6 — avançou por uma rolagem de missão
[■][■][■][■][■][■]   6/6 — ACONTECE, queira o grupo ou não
```

* tamanho 4 (curto), 6 (padrão) ou 8 (longo);
* avança **por rolagem**, não por vontade do mestre: quando os NPCs agem fora de
  cena, role `d20 + prioridade da agenda` contra a DD dela; sucesso = +1 segmento,
  sucesso maior = +2, fracasso = 0, fracasso crítico = a agenda **regressa** 1;
* também avança 1 segmento por mês de jogo automaticamente (o mundo não espera);
* quando enche, acontece. O mestre não pode cancelar uma agenda completa — pode
  apenas mostrar as consequências.

É a mecânica que responde à pergunta "por que o vilão não ficou parado esperando
os jogadores?". Ele não ficou.

## 12.10 Gerando NPCs

```bash
./xan npc --semente minha-mesa-npc-01 --nivel 7 --ocupacao "Ancião de seita" \
          --faccao "Seita do Monte Hua" --local Qingyun --agendas 2
```

Sem `--semente` usa a fonte viva (imprevisível, ideal para figurantes na hora).
Com `--semente` é reproduzível — bom para preparar a sessão e conferir depois.

O gerador produz: nome chinês completo (romanizado + caracteres), sexo, idade,
raça, ocupação, posto, caminho, Lei, nível, seis atributos, 3–6 perícias, Raiz
Espiritual, temperamento, Cinco Virtudes, 2–4 traços compatíveis entre si, as
oito camadas de desejo, Face, estado mental, pedras espirituais, técnicas
conhecidas e agendas.

### Ocupações e o que elas implicam

A ocupação desloca as virtudes antes do sorteio — coerência em vez de acaso cego.
Um "Médico andarilho" tende a Benevolência alta; um "Assassino de aluguel", a
Benevolência baixa e Sabedoria alta. São 34 ocupações publicadas.

## 12.11 Interpretando sem trair o modelo

O modelo dá os números; a mesa dá a voz. Três regras de interpretação:

1. **Fale pela camada ativa.** Se a conduta sorteada foi `recusa` e a camada
   ativa foi `linha_vermelha`, o NPC recusa *por causa daquilo que ele não faz* —
   não por medo nem por preço. Isso torna a recusa informativa.
2. **Cite o ledger.** "Ele ainda lembra que você mentiu para ele em Wǔ" é muito
   melhor que "ele não gosta de você". E é conferível.
3. **Não suavize o resultado.** Se a mesa rolou `ataca`, o NPC ataca. Você pode
   escolher *como* — com aviso, com uma frase, com relutância — mas não *se*.
