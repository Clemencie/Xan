# Capítulo 18 — O Mestre e a Imparcialidade

Este capítulo existe para responder à objeção óbvia: *"se o mestre não pode
ajustar nada, como é que se mestrar?"*

## 18.1 A distinção inteira

Há duas coisas que parecem iguais e não são:

| | Autoria | Interferência |
|---|---|---|
| Quando | **antes** do dado | **depois** do dado |
| O que muda | o mundo, as circunstâncias, a dificuldade | o resultado |
| Quem vê | todo mundo | só quem operou |
| É verificável | sim, está na declaração gravada | sim, e aparece como divergência |
| É legítima | **sim** | **não** |

Colocar os jogadores contra um oponente três reinos acima é autoria. Reduzir o
dano desse oponente depois de vê-lo é interferência. A primeira é o seu trabalho;
a segunda quebra o jogo.

## 18.2 As dez alavancas legítimas do mestre

Todas são declaradas antes, todas ficam no diário, todas valem igual para todo
mundo.

1. **Escolher a DD** — lida da tabela do Cap. 3.3, não inventada.
2. **Escolher os fatos da cena** — luz, clima, terreno, cobertura, formação,
   feng shui, densidade de Qi. Uma cena escura é uma escolha; `AMBIENTE:LUZ` faz
   o resto.
3. **Escolher o oponente** — nível, Lei, técnicas, preparação, modo de defesa.
4. **Escolher o que existe no mundo** — a semente gera; você escolhe onde os
   jogadores estão quando ela é gerada.
5. **Escolher quem aparece e quando** — as agendas dos NPCs (Cap. 12.9) dizem o
   que eles querem; você escolhe quando isso cruza o caminho do grupo.
6. **Escolher as consequências do fracasso** — antes do dado, de preferência.
7. **Escolher a magnitude do pedido** — a tabela do Cap. 12.6 tem dez níveis.
8. **Escolher o custo de oportunidade** — o tempo passa, as agendas avançam, os
   rivais também cultivam.
9. **Escolher a informação** — o que os NPCs sabem, o que escondem, o que
   entendem errado.
10. **Escolher o tom** — descrição, ritmo, música, silêncio. Nada disso é número.

Repare: **nenhuma das dez toca no resultado.** E ainda assim elas são quase todo
o trabalho de mestrar.

## 18.3 Ferramentas do mestre

### Preparar a sessão

```bash
# 1. o mundo (faça isso uma vez por campanha)
./xan mundo gerar --semente minha-campanha --saida mundos/minha-campanha --npcs 12

# 2. o diário da sessão
mkdir -p mundos/minha-campanha/auditoria

# 3. os NPCs da sessão (semente própria = reproduzível)
./xan npc --semente minha-campanha-anciao-01 --nivel 9 --ocupacao "Ancião de seita" \
          --faccao "Seita do Monte Hua" --agendas 2 > sessao-07-anciao.md

# 4. o encontro (opcional: role antes e veja o que o mundo reserva)
./xan combate --semente sessao-07-duelo --nivel 7 --defensivo
```

### Durante a sessão

```bash
# qualquer rolagem, auditada
./xan rolar "1d20" --ator "Lin Yue" --diario mundos/minha-campanha/auditoria/07.jsonl

# um teste com fatos declarados
./xan teste --ator "Lin Yue" --atributo per --valor 14 --pericia rastreamento \
            --graduacao 3 --dd 15 --regras "AMBIENTE:LUZ,AMBIENTE:CLIMA" \
            --fatos '{"luz":"penumbra","clima":"chuva"}' \
            --diario mundos/minha-campanha/auditoria/07.jsonl

# consulta rápida
./xan tabelas leis ; ./xan tabelas tecnicas ; ./xan tabelas reinos
```

### Depois da sessão

```bash
./xan auditoria verificar --diario mundos/minha-campanha/auditoria/07.jsonl
./xan auditoria selar     --diario mundos/minha-campanha/auditoria/07.jsonl \
                          --saida mundos/minha-campanha/selos/2026-10-03.txt
```

Guarde o arquivo de selo **fora** do repositório da mesa (num e-mail, num drive,
impresso). Ele é a prova de que o diário não foi reescrito depois.

## 18.4 O que fazer quando você quer "salvar" alguém

Você vai querer. É normal, e quase sempre é sinal de que algo na cena está mal
calibrado. As saídas legítimas:

| Vontade | Saída legítima |
|---|---|
| "não quero que ele morra" | Ele não morre: Vitalidade ≤ 0 é *caído*, e o 1d6 do Cap. 6.7 decide o resto. Anuncie isso **antes** da luta |
| "o vilão não podia morrer agora" | Dê ao vilão `LAMPADA_ALMA` (Cap. 15.3) antes da cena, ou um `TAL_CORACAO_CELESTE`. É um item, comprado, declarado, público |
| "a luta está longa demais" | O inimigo foge: teste de Passos Leves oposto (Cap. 10.9). Fuga é resultado, não trapaça |
| "os jogadores não estavam prontos" | Eles podem queimar longevidade, usar elixires, ativar o Manto de Qi. Custos declarados, disponíveis a qualquer um |
| "saiu um 1 no pior momento" | Aplique o 1. É um desvio. O Cap. 11.6 diz o que acontece, e o mundo fica mais interessante |
| "eu quero que eles ganhem" | Então não deveria ter rolado. Declare o resultado sem dado e diga que não houve dado — isso é honesto; rolar e ignorar não é |

A última linha é a mais importante do capítulo. **Se você decidir o resultado,
decida sem rolar.** Uma rolagem ignorada é pior que nenhuma rolagem: ela ensina
a mesa a não acreditar em nada.

## 18.5 Quando os jogadores pedem para você trapacear

Vai acontecer também: "deixa eu rolar de novo", "dá um +2, eu me preparei".

* **Preparo é legítimo** — se foi declarado antes. "Eu estudei o alvo na sessão
  passada" é `PREPARO:ESTUDO_PREVIO` (+1), e deveria ter sido anotado na época.
  Anote agora, com data, e aplique daqui em diante.
* **Re-rolagem não é.** Explique o Cap. 2 uma vez. Se insistirem, rode
  `./xan auditoria verificar` e mostre que o token já estava gravado antes do
  dado: não é o mestre recusando, é o diário.

## 18.6 Mestre rotativo

O sistema foi feito para funcionar com mestre rotativo, e há duas razões
estruturais:

1. o mundo é gerado por semente, então quem chega não precisa saber nada;
2. o diário é encadeado e selável, então o mestre anterior não pode ter
   favorecido ninguém — e o próximo não pode apagar.

Regra sugerida: quem mestra assina o diário da sessão no começo (`selar`) e o
próximo mestre verifica antes de assumir.

## 18.7 Imparcialidade não é neutralidade

Ser imparcial no dado **não** é ser neutro na ficção. Você pode — e deve — fazer
um mundo cruel, injusto, cheio de vilões que trapaceiam, seitas corruptas e
deuses que mentem. O XAN tem NPCs com Segredo, Preço e linha vermelha cruzável
por outros.

A diferença é esta: **os personagens do mundo podem ser desonestos. O dado não.**

Isso é o que torna a desonestidade deles jogável. Se o dado também mente, nada
mais significa nada.
