# Capítulo 2 — A Regra de Ouro e o Contrato de Imparcialidade

> **A Regra de Ouro do XAN:**
> *Depois que os dados e os modificadores são declarados, nada mais pode mudar
> o resultado. Nem o mestre, nem o jogador, nem a história, nem o motor.*

Este capítulo é o documento mais importante do sistema. Se você ler só um, leia
este.

---

## 2.1 Por que um contrato, e não uma recomendação

"Não trapaceie no dado" é uma recomendação. Recomendações falham sob pressão: o
vilão está escapando, o jogador vai chorar, a sessão está acabando, foi só uma
rolagem.

Um contrato transforma isso em **procedimento**. Ele diz o que deve acontecer
*antes*, para que não exista nada a decidir *depois*.

O contrato tem três cláusulas. Assine-as na sessão zero, em voz alta, com todo
mundo presente.

### Cláusula 1 — Compromisso antes do dado

Toda rolagem que importe começa com uma **declaração completa e pública**:

* o que está sendo tentado;
* quem tenta e contra quem;
* qual atributo e qual perícia, com os valores da ficha;
* a dificuldade (DD), lida da tabela;
* **todos** os fatos objetivos da cena que geram modificadores.

Essa declaração é convertida em hash e gravada antes do dado. No motor:

```bash
./xan teste --atributo con --valor 16 --pericia espada --graduacao 4 \
            --dd 18 --regras "ELEMENTO:RELACAO,POSICAO:TERRENO" \
            --fatos '{"elemento_atacante":"metal","elemento_alvo":"madeira","terreno":"alto"}' \
            --diario mundos/minha-mesa/auditoria/diario.jsonl
```

O diário recebe três registros, nesta ordem, e a ordem é verificável:

1. `compromisso` — o token (hash da declaração + sal secreto);
2. `rolagem` — as faces, o total, os modificadores, o selo;
3. `revelacao` — o sal e o payload, para que qualquer um refaça o token.

Se alguém alterar a declaração depois de ver o dado, a revelação não bate com o
token. `./xan auditoria verificar --diario …` aponta o índice exato.

### Cláusula 2 — Modificadores vêm de fatos, não de intenções

Não existe "+2 porque é dramático". Existe um **Registro de Regras** fechado:
cada modificador tem um código (`DOMINIO:NOME`), um capítulo do livro, uma
descrição, um limite numérico e uma lista de fatos que exige. Se o fato não for
declarado, a regra não se aplica. Se o fato for declarado com tipo errado, o
motor recusa.

Exemplo — `POSICAO:TERRENO`:

| fato declarado | modificador |
|---|---:|
| `alto` | +1 |
| `neutro` | 0 |
| `baixo` | −1 |

Quem quer o +1 precisa dizer, antes do dado, "eu estou no alto". Se ninguém
disse, o bônus não existe. Se alguém disser depois de ver o resultado, o token
já foi gravado e não bate.

### Cláusula 3 — A mesma entropia para todos

Mestre e jogadores consomem **a mesma** `Aleatoriedade`. Não existe "dado do
mestre" e "dado do jogador". Não existe caminho de código que trate um ator de
forma diferente — e o motor testa isso
(`justica.teste_imparcialidade_entre_atores`, família O: seis atores com nomes
diferentes rolam a mesma distribuição, qui-quadrado com gl=5).

---

## 2.2 O que continua sendo do mestre

O contrato restringe o dado. **Não restringe a criação.** O mestre continua
sendo o autor de:

* o que existe no mundo e onde;
* quem os jogadores encontram e quando;
* o que os NPCs querem (embora o NPC tenha desejos próprios — Cap. 12);
* qual DD usar, **lida da tabela de dificuldades**;
* quais fatos objetivos são verdadeiros na cena;
* o que acontece **entre** as rolagens.

Um mestre que quer que os jogadores percam uma luta pode, legitimamente, colocá-
los contra um oponente três reinos acima. O que ele não pode é reduzir o dano
depois de vê-lo. **A dificuldade é uma escolha de autoria feita antes; o
resultado é um fato descoberto depois.** Essa é a diferença inteira.

## 2.3 O que continua sendo do jogador

* Declarar a própria intenção e os fatos que conhece.
* Escolher a tática: modo de defesa, técnica, gasto de Qi, queima de
  longevidade.
* Aceitar o resultado sem negociar.
* Exigir auditoria: qualquer jogador pode pedir `./xan auditoria verificar`
  sobre qualquer sessão, a qualquer momento, sem dar explicação.

## 2.4 As cinco proibições

Estas cinco coisas não existem no motor. Não é disciplina: é ausência de código.
`resolucao.verificar_invariantes()` inspeciona o motor inteiro e falha se
alguma aparecer.

1. **Re-rolar.** Não há função que aceite um resultado e produza outro.
2. **Ajustar total.** `Resultado` é imutável e recalcula a própria aritmética no
   construtor; se o total gravado não bater com a soma das faces mais os
   modificadores, a construção aborta.
3. **Modificador sem regra.** Nomes como `bonus_narrativo`, `ajuste`,
   `plot_armor`, `mercy`, `favor` estão na lista de nomes proibidos; o motor
   varre o próprio código à procura deles.
4. **Parâmetro de intenção.** Nenhuma função do motor aceita algo parecido com
   `desejado`, `esperado`, `alvo_do_mestre`. Também estão na lista proibida.
5. **Mutabilidade.** `Declaracao`, `Rolagem`, `Resultado`, `Compromisso` e
   `TermoDado` são `frozen`. O teste verifica `__dataclass_params__.frozen`.

## 2.5 Quando o resultado parece errado

Vai acontecer. Um 1 natural no momento pior, um triunfo que resolve um mistério
cedo demais, um NPC que morre na primeira rodada.

O procedimento é este, e ele é o mesmo sempre:

1. **Aceite o resultado.** Ele já existe. Anote-o.
2. **Interprete as consequências.** Um fracasso não é "nada acontece"; é "o
   mundo responde de outro jeito". O Cap. 3.7 tem a tabela de falhas.
3. **Se houver suspeita de erro mecânico, audite.** `./xan auditoria verificar`
   confere a cadeia de hash, a ordem compromisso→rolagem→revelação e a raiz de
   Merkle. Erro de conta é diferente de resultado indesejado: o primeiro se
   corrige, o segundo se joga.
4. **Mude a regra antes da próxima sessão, nunca durante.** Casa de regra é
   legítima; casa de regra aplicada retroativamente é trapaça com outro nome.

## 2.6 O certificado

`./xan justica --saida docs/CERTIFICADO_DE_JUSTICA` roda 40 testes estatísticos
sobre mais de 3,5 milhões de amostras e publica um certificado em Markdown e
JSON. O certificado está no repositório para que qualquer pessoa possa conferir
os números sem precisar confiar em ninguém.

As famílias de teste:

| Fam. | O que testa |
|---|---|
| A | Uniformidade de cada face de d4, d6, d8, d10, d12, d20 e d100 (qui-quadrado) |
| B | `abaixo(n)` — amostragem imparcial com rejeição, sem viés de módulo |
| C | Distribuição exata dos totais de 1d20, 2d6, 3d6, 4d6kh1, 2d20kh1, 1d20+5, 3dF contra a distribuição teórica calculada por frações exatas |
| D | Média e variância amostrais contra os valores teóricos exatos |
| E | Kolmogorov–Smirnov sobre uniformes em [0,1) |
| F | Autocorrelação serial lag-1 |
| G | Corridas acima/abaixo da mediana |
| H | Monobit, pôquer-4 e maior corrida de uns (NIST SP 800-22), com a distribuição da maior corrida calculada **exatamente** por programação dinâmica |
| I | Independência de pares consecutivos |
| J | Imparcialidade de `kh`/`kl`: as faces mantidas e as descartadas têm a mesma distribuição marginal |
| K | `escolher_ponderado` contra os pesos declarados |
| L | Fisher–Yates: todas as permutações igualmente prováveis e cada carta em cada posição com probabilidade 1/n |
| M | Eficiência da rejeição: bytes consumidos por resultado batem com a razão teórica |
| N | Determinismo: mesma semente → mesma sequência; sementes diferentes → sequências diferentes |
| O | Imparcialidade entre atores: o nome de quem rola não afeta nada |

Nível de significância α = 0,001 por teste. Falha dura em p < 10⁻⁶.

## 2.7 Honestidade sobre os limites

O motor **não** é certificado pelo NIST CAVP e não reivindica vetores de teste
oficiais — não há como obtê-los offline. O que ele faz:

* implementa o HMAC-DRBG conforme a construção do SP 800-90A §10.1.2 com
  SHA-256;
* testa regressão de valores-ouro e determinismo;
* publica a bateria estatística acima.

E, mais importante: em modo **fonte viva** a entropia vem de `os.urandom`
(ruído do sistema operacional). Em modo **semeado** ela é reproduzível *de
propósito*, e a semente fica gravada no diário — para que preparação de sessão
possa ser conferida depois, não para que alguém escolha o resultado.

Escolher a semente é escolher o mundo. **Não** é escolher o dado: a semente é
declarada antes, vale para todo mundo e fica registrada.
