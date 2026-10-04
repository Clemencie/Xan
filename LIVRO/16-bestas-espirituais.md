# Capítulo 16 — Bestas Espirituais

## 16.1 O que é uma besta espiritual

Bestas espirituais (妖獸) cultivam. Elas seguem a **mesma escada 0–13** dos
humanos, o que significa que uma besta de nível 7 é um Núcleo Dourado com
garras, e que a supressão de reino se aplica a ela exatamente como se aplica a
qualquer um.

| Classe | O que é |
|---|---|
| `fera` | animal comum com um pé no Qi |
| `besta_espiritual` | cultiva de verdade; pode virar aliada |
| `demonio` | corrompida; quase sempre hostil |
| `morto_vivo` | cadáver animado (殭屍, 血傀) |
| `espirito_de_objeto` | um objeto que despertou |
| `fera_ancestral` | os quatro símbolos e equivalentes |
| `divindade_menor` | Qilin, Baize: funções do mundo, não animais |

## 16.2 Tamanhos

| Tamanho | Defesa | Vitalidade |
|---|---:|---:|
| minúsculo | +4 | 40% |
| pequeno | +2 | 70% |
| médio | 0 | 100% |
| grande | −2 | 160% |
| enorme | −4 | 260% |
| colossal | −6 | 500% |

Grande é fácil de acertir e difícil de matar. É a troca inteira.

## 16.3 O cânone

Vinte e duas bestas publicadas, incluindo os quatro símbolos celestiais, os
quatro flagelos e as criaturas de romances.

| Nv. | Nome | 中文 | Classe | Elemento |
|---:|---|---|---|---|
| 1 | Carpa que Salta o Portão do Dragão | 跳龍門鯉 | besta espiritual | Água |
| 2 | Gafanhoto de Praga | 蝗魔 | besta espiritual | Madeira |
| 2 | Tartaruga Espiritual Comum | 靈龜 | besta espiritual | Água |
| 3 | Lobo da Montanha Fria | 寒山狼 | fera | Água |
| 3 | Águia do Vento Cortante | 割風鷹 | fera | Metal |
| 4 | Macaco de Seis Braços | 六臂猿 | besta espiritual | Madeira |
| 4 | Aranha de Seda Espiritual | 靈蠶蛛 | besta espiritual | Madeira |
| 4 | Gato de Nove Vidas | 九命貓 | besta espiritual | Metal |
| 5 | Jiao | 蛟 | besta espiritual | Água |
| 5 | Urso de Ferro das Colinas | 鐵背熊 | fera | Terra |
| 5 | Cão-Cadáver | 殭屍 | morto-vivo | Terra |
| 6 | Puppet de Sangue | 血傀 | morto-vivo | Fogo |
| 6 | Cão Infernal de Duas Cabeças | 雙頭獄犬 | demônio | Fogo |
| 7 | Serpente de Sete Cabeças | 七頭蛇 | demônio | Água |
| 8 | Corvo de Três Pernas | 三足烏 | besta espiritual | Fogo |
| 9 | Raposa de Nove Caudas | 九尾狐 | demônio | Fogo |
| 9 | Qiongqi | 窮奇 | demônio | Metal |
| 9 | Baize | 白澤 | divindade menor | nenhum |
| 10 | Peng | 鵬 | besta espiritual | Madeira |
| 10 | Taotie | 饕餮 | demônio | Terra |
| 11 | Tigre Branco do Oeste | 白虎 | fera ancestral | Metal |
| 11 | Pássaro Vermelho do Sul | 朱雀 | fera ancestral | Fogo |
| 11 | Tartaruga Negra do Norte | 玄武 | fera ancestral | Água |
| 12 | Dragão Azul do Leste | 青龍 | fera ancestral | Madeira |

Alguns merecem nota:

* **Baize** (白澤) sabe o nome e a fraqueza de todas as criaturas do mundo. Ele
  não pode mentir, nunca. Converse com ele e o grupo inteiro ganha +2 de dano
  contra qualquer besta específica que ele nomear.
* **Qilin** (麒麟) não pode ser atacado por quem nunca matou um inocente. Não é
  imunidade: é a regra `IMUNE_A_INOCENTES`. Se alguém do grupo tem essa marca, o
  Qilin vai embora — e a mesa descobre quem é.
* **Raposa de Nove Caudas** (九尾狐) devora a Vitalidade máxima de quem dorme com
  ela: 1d4 por noite. Ela é `domavel: False` e inteligente; negociar é possível,
  domesticar não.
* **Taotie** (饕餮) tem cabeça e boca e nada mais. O resto ele comeu de si mesmo.
* **Carpa que Salta o Portão do Dragão**: uma vez na vida, teste de Sorte DD 30.
  Sucesso = salta para o nível 7. É a única mecânica do jogo em que um peixe pode
  virar dragão, e ela é uma rolagem.

## 16.4 Núcleo de besta (妖丹)

Bestas de nível 7+ condensam núcleo. É o ingrediente mais valioso da alquimia.

| Nível da besta | Grau do núcleo |
|---:|---|
| 7–9 | Terra |
| 10–11 | Céu |
| 12–13 | Primordial |

Retirar o núcleo intacto é um teste de Ervas ou Medicina DD `15 + nível da
besta`. Falhar destrói o núcleo.

## 16.5 Domar

Bestas marcadas como domáveis podem ser contratadas com `SR_SELO_SEIS_ROTAS`
(nível 7, Lei das Seis Rotas) ou por vínculo comum:

* vínculo comum: teste oposto de `bestas_espirituais` contra a Vontade da besta
  (`d20 + bônus de Potencial + nível`), DD 12. Sucesso = a besta acompanha, mas
  pode ir embora se for maltratada.
* selo das Seis Rotas: a besta fica presa a uma das seis rotas e obedece. Custo:
  70 de Qi, uma vez por besta, e o selo é visível para qualquer Percepção de Qi
  DD 18 — o que torna quem o usa um caçador de escravos aos olhos do Murim.

## 16.6 Gerador procedural

```bash
./xan besta --semente caverna-07 --nivel 8 --terreno montanhas
./xan besta --catalogo          # lista as 24 canônicas completas
```

O gerador produz nome (romanizado + caracteres), classe, elemento coerente com o
terreno, tamanho, habitat específico, Vitalidade e Qi na mesma escala dos
cultivadores (usa `qi_maximo`), Defesa, iniciativa, seis atributos, 1–3 ataques
com dado escalado por nível, habilidades por faixa de nível, temperamento,
fraqueza, tesouro e se é domável ou inteligente.

Habilidades por nível: 4+ ganha uma habilidade passiva (de um par fixo
nome/descrição/mecânica, para não sair incoerente), 7+ ganha Núcleo de Besta,
10+ ganha Fala Humana — e aí ela pode negociar, mentir e fazer juramentos.

## 16.7 Encontros aleatórios

Role 1d20 por dia de viagem, com modificador = perigo da província:

| 1d20 + perigo | Encontro |
|---:|---|
| ≤ 8 | nada |
| 9–12 | sinal de besta (rastro, carcaça, som) |
| 13–15 | besta de nível `1d6 + perigo ÷ 3` |
| 16–18 | cultivador errante (gere NPC) |
| 19–20 | patrulha de seita |
| ≥ 21 | evento do mundo: uma agenda de NPC completou |

O último item é o mais importante: ele é o mecanismo pelo qual o mundo avança
enquanto os jogadores estão na estrada.
