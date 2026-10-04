# Capítulo 1 — O que é o XAN

## 1.1 A promessa

O XAN é um sistema de RPG de mesa sobre **cultivo imortal**: personagens que
começam como mortais comuns e, se tiverem talento, sorte, disciplina e uma
quantidade desconfortável de obsessão, sobem uma escada de treze degraus que
termina fora do mundo.

Ele é jogado com um d20, dados menores, papel e um computador opcional. O
computador não substitui ninguém: ele só garante uma coisa que nenhum humano
consegue garantir sozinho.

## 1.2 O problema que o XAN resolve

Todo mundo que joga RPG há tempo já viveu isto:

* O mestre rola atrás do escudo e anuncia um resultado que ninguém pode conferir.
* O vilão sobrevive porque "a história precisava".
* O personagem do jogador favorito escapa por um triz três sessões seguidas.
* Uma rolagem é refeita "porque saiu estranha".
* Um bônus de +2 aparece do nada porque a cena era importante.

Nenhum desses atos é necessariamente má-fé. A maioria é só o mestre fazendo o
trabalho dele. Mas o efeito cumulativo é o mesmo: **a mesa deixa de saber se o
resultado foi sorte ou decisão.** E quando a sorte deixa de ser distinguível da
decisão, ela para de valer alguma coisa.

O XAN resolve isso por arquitetura, não por boa vontade:

| O que poderia ser trapaceado | Como o XAN impede |
|---|---|
| Trocar o resultado do dado | O total é recalculado a partir das faces gravadas; divergência aborta a operação |
| Rolar de novo porque saiu ruim | Não existe nenhuma função de re-rolagem ou ajuste no motor (verificado estruturalmente) |
| Somar um bônus que não estava lá | Modificadores só nascem de um registro fechado de regras, recalculado dos fatos |
| Declarar os fatos *depois* de ver o dado | A declaração inteira vira hash e é gravada **antes** do dado |
| Editar o histórico depois | Diário append-only encadeado por SHA-256, com raiz de Merkle e selo externo |
| Dar dado melhor para um jogador | Mestre e jogadores consomem **a mesma** fonte de entropia |
| "O dado foi justo, confia" | 40 testes estatísticos, 3,5 milhões de amostras, certificado publicado |

## 1.3 O que o XAN não é

**Não é um sistema sem mestre.** O mestre continua decidindo o que existe no
mundo, quem aparece, o que os jogadores encontram e o que significa cada coisa.
A imparcialidade se aplica a **uma coisa só: o resultado do dado e os números
que entram nele.**

**Não é um simulador de planilha.** Os números existem para que a mesa pare de
discutir, não para que ela faça contabilidade. Toda conta do sistema cabe numa
linha.

**Não é fiel a um jogo só.** Ele mistura três tradições:

* De **Amazing Cultivation Simulator**: os níveis 1–12, os três caminhos
  (Xiandao, Shendao, Corpo), o Núcleo Dourado com grau decidido por fatores de
  preparo, o Qi como mana *e* escudo, a queima de longevidade, o sistema
  mestre/discípulo, o Torneio de Kunlun e a gestão de seita.
* Do **murim/wuxia coreano-chinês**: o Jianghu 江湖 como mundo paralelo ao
  Império, as nove grandes seitas ortodoxas, os cinco clãs nobres, o culto
  demoníaco, e a escada Terceira Classe → Pico → Transcendente → Absoluto.
* Do **xianxia clássico**: Raiz Espiritual 靈根, dantian, meridianos, os Três
  Tesouros (精氣神), Desvio de Qi 走火入魔, Demônios Interiores 心魔,
  tribulações celestiais e a Ascensão.

## 1.4 O tom

O XAN assume o gênero a sério, inclusive as partes desconfortáveis:

* A maioria das pessoas nasce com uma Raiz Espiritual inútil. Isso é uma
  tragédia e é o ponto de partida de quase todo protagonista.
* Seitas são instituições políticas com orçamentos, celeiros e vaidades.
* Um cultivador três reinos acima de você não pode ser atingido. Isso não é
  injustiça narrativa: é uma regra com número na tabela.
* Ninguém ascende sem perder alguma coisa no caminho.
* O mundo continua sem você. As agendas dos NPCs avançam todo mês, queiram os
  jogadores ou não.

## 1.5 O que você precisa para jogar

* 2–6 jogadores e um mestre.
* Um d20. Opcionalmente d4, d6, d8, d10, d12 e d%.
* O motor (`./xan`) para rolagens auditadas — recomendado, não obrigatório.
* Uma semente de mundo (qualquer palavra serve: `"minha-mesa-2026"`).
* As fichas em `LIVRO/fichas/`.

Sessão zero recomendada: gerar o mundo juntos, escolher a **tabela de raízes**
(Cap. 5.4) e assinar o Contrato de Imparcialidade (Cap. 2).

## 1.6 Estrutura do resto do livro

Capítulos 3 e 4 são a mecânica. 5 a 9 são o personagem e o cosmos. 10 e 11 são
conflito e transcendência. 12 a 17 são o mundo vivo. 18 e 19 são para o mestre.
20 e 21 são consulta.
