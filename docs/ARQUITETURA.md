# Arquitetura do Motor do Destino Imparcial (MDI)

Documento técnico. O livro de regras está em `LIVRO/`; aqui está **como** o motor
garante o que o livro promete.

---

## 1. Ameaças e defesas

O requisito era: *rolagens completamente aleatórias e justas, sem vantagem
narrativa*. Isso significa enumerar as formas de trapacear e fechar cada uma por
arquitetura.

| # | Ameaça | Defesa | Onde |
|---|---|---|---|
| 1 | Previsibilidade do gerador | HMAC-DRBG (SP 800-90A §10.1.2, SHA-256) alimentado por `os.urandom` | `entropia.py` |
| 2 | Viés de módulo | Amostragem por rejeição sobre o maior múltiplo de `n` que cabe no byte | `entropia.Aleatoriedade.abaixo` |
| 3 | Dois RNGs (um para o mestre, outro para os jogadores) | Uma única `Aleatoriedade` compartilhada; nenhum caminho de código diferencia o ator | todo o motor |
| 4 | Declarar modificadores depois de ver o dado | Commit-reveal: hash da declaração gravado **antes** | `compromisso.py`, `resolucao.resolver` |
| 5 | Modificador inventado na hora | Registro fechado de regras; o valor é **recalculado** dos fatos | `regras.py` |
| 6 | Fato declarado com tipo errado para forçar um bônus | Tipagem estrita: `bool` exige `bool`, categoria exige valor da tabela, inteiro exige inteiro na faixa | `regras._bool/_categoria/_inteiro` |
| 7 | Alterar o total depois | `Resultado` é `frozen` e **recomputa** a aritmética no `__post_init__`; divergência aborta | `resolucao.py` |
| 8 | Re-rolar | Não existe API de re-rolagem; `verificar_invariantes()` varre o motor atrás de nomes proibidos | `resolucao.py` |
| 9 | Editar o histórico | JSONL append-only, encadeado por SHA-256, `fsync` por linha | `auditoria.py` |
| 10 | Reescrever o arquivo inteiro | Raiz de Merkle + `selar()` gravando a cabeça num arquivo externo | `auditoria.py` |
| 11 | "o dado é justo, confia" | 40 testes estatísticos com p-valores calculados de funções especiais escritas à mão | `justica.py` |
| 12 | Regra de casa aplicada retroativamente | Regras novas passam por `registrar()`; o histórico já selado não muda | `regras.py` |

---

## 2. Entropia

```
FonteDeBytes (abstrata)
├── FonteViva      → os.urandom, re-semeadura periódica do DRBG
└── FonteSemeada   → HKDF-like a partir de (semente, derivação) — reproduzível
        ↓
   HMACDRBG (SP 800-90A §10.1.2, SHA-256, com contador de ressemeadura)
        ↓
   Aleatoriedade  ← a ÚNICA porta de entrada usada pelo resto do sistema
        ├── bytes(n)
        ├── abaixo(n)            → rejeição, zero viés de módulo
        ├── entre(lo, hi)
        ├── moeda()
        ├── escolher(itens)
        ├── escolher_ponderado(itens, pesos)   → pesos inteiros, sem float
        ├── amostrar(itens, k)
        ├── baralhar(itens)      → Fisher–Yates Durstenfeld
        ├── unico()              → 16 bytes hex, para identificadores
        └── consumo()            → chamadas e bytes, para auditoria
```

**Por que não `random.Random`.** O Mersenne Twister é recuperável a partir de
624 saídas consecutivas. Numa mesa onde alguém pode anotar rolagens, isso é
inaceitável. O HMAC-DRBG não é invertível sem a semente.

**Rejeição.** `abaixo(n)` descarta bytes ≥ `256 − (256 mod n)`. Para `n = 7` o
consumo esperado é 8/7 bytes por resultado; para `n = 100`, 128/100. O teste da
família M confere o consumo medido contra essa razão teórica — é uma prova
observável de que a rejeição está realmente acontecendo.

**Reprodutibilidade não é trapaça.** `FonteSemeada` existe para preparação de
sessão e para testes. A semente é declarada antes, vale para todos e fica
gravada. Trocar de semente troca o mundo inteiro, não o dado que incomodou.

---

## 3. Notação de dados e matemática exata

`dados.py` implementa `NdS`, `NdS!`, `NdS!T`, `NdS kh M`, `NdS kl M`, `NdF`,
`d%` e expressões com `+`/`−` (inclusive termos negativos). Limites de segurança:
1 000 dados por termo, 1 000 000 de faces, 256 explosões em cadeia. Expressões
ambíguas são recusadas (`"1d20 5"` não vira `1d205`).

O que importa aqui não é o parser, é que **`valor_esperado()` devolve uma
`Fraction` exata**, calculada por estatística de ordem:

```
P(k-ésimo maior de n dados de s faces ≥ v) = Σ_{j=k}^{n} C(n,j) · p^j · (1−p)^(n−j)
com p = (s − v + 1)/s
E[k-ésimo maior] = Σ_v P(k-ésimo maior ≥ v)
```

Isso foi validado contra **enumeração exaustiva** por `itertools.product` para
dez expressões, incluindo `4d6kh1`, `4d6kh3`, `2d20kh1`, `4d6kl1`, `3d6kh2`,
`5d6kl2`, `2d6kh1`, `6d6kh4`, `3d8kl2`.

> **Bug real encontrado assim.** A primeira implementação usava
> `preciso = n − k + 1` na condição "pelo menos `preciso` dados ≥ v", o que
> calcula o k-ésimo **menor**. `4d6kh1` devolvia 1,7554 — exatamente `E[min]`.
> A condição correta é "o k-ésimo maior ≥ v ⟺ pelo menos **k** dados ≥ v".
> A força bruta pegou; a sanidade `E[min] + E[máx] = 2·E[dado]`
> (7,175 + 13,825 = 21 para 2d20) confirmou a correção.

`distribuicao_exata()` devolve a PMF completa em frações para espaços ≤ 2 M;
acima disso, ou com dados explosivos, levanta `Indeterminado` em vez de
aproximar em silêncio.

---

## 4. Auditoria

### 4.1 Registro canônico

```python
canonico(obj) = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False).encode("utf-8")
hash_registro = sha256(canonical(registro_sem_o_campo_hash))
```

Campos: `i` (índice), `t` (nanossegundos UTC), `tipo`, `ator`, `conteudo`,
`prev` (hash do anterior), `hash`. O genesis tem `prev = "0" × 64`.

Canonicalização determinística é o que permite que **terceiros** refaçam o hash:
sem `sort_keys` e sem espaços opcionais, dois `json.dumps` do mesmo objeto podem
diferir e a verificação daria falso-positivo de adulteração.

### 4.2 Propriedades verificadas

`verificar()` confere, em uma passada:

1. índices contíguos a partir de 0;
2. `prev` de cada linha == `hash` da anterior;
3. `hash` de cada linha == SHA-256 do seu próprio conteúdo canônico;
4. o genesis aponta para `"0" × 64`.

Remover uma linha, editar um campo, reordenar ou truncar o arquivo quebra pelo
menos uma das quatro. Os testes exercitam **cada** uma delas separadamente.

### 4.3 Raiz de Merkle e selo

`raiz_merkle()` reduz o diário inteiro a um único hash. `selar(destino)` anexa
`{cabeca, raiz_merkle, registros, t, nota}` a um arquivo externo.

O desenho é deliberado: o selo deve viver **fora** do repositório da mesa. Quem
tem o selo de ontem prova que o diário de hoje não foi reescrito desde então —
inclusive por quem administra o repositório.

### 4.4 Compromisso e revelação

```
compromisso  {token = sha256(sal ‖ canonico(payload)), hash_declaracao}
rolagem      {token, expressao, faces, total, modificadores, margem, grau, selo}
revelacao    {token, sal, payload}
```

`conferir()` exige, para todo o diário:

* nenhuma `rolagem` antes do seu `compromisso`;
* nenhuma `revelacao` antes da sua `rolagem`;
* `sha256(sal ‖ canonico(payload)) == token` em cada revelação;
* nenhum token duplicado.

O sal vem da **mesma** `Aleatoriedade`, então o compromisso consome entropia
auditável e não pode ser forjado retroativamente.

---

## 5. Registro de Regras

```python
RegraModificadora(codigo, capitulo, descricao, requer, calcular, limite)
```

36 regras em 13 domínios. Invariantes:

* **`codigo` tem a forma `DOMINIO:NOME`.** Sem exceção.
* **`requer` lista os fatos.** Se um fato falta, a regra não é aplicável e a
  declaração é recusada — não é tratada como zero.
* **`calcular` recebe só os fatos.** Não recebe o resultado, o ator, a hora, nem
  nada que permita decisão contextual.
* **`limite` é verificado na saída.** Uma regra que produza algo fora da faixa
  levanta `ModificadorIlegal`.
* **`EXCLUSIVAS` declara pares incompatíveis.** Declarar os dois juntos aborta.

O histórico de design importa: a primeira versão usava valores fixos com
`requer` verificando apenas **presença** de fato. Isso permitia declarar
`POSICAO:TERRENO` e informar `terreno="alto"` quando o terreno era baixo — o
bônus vinha do rótulo, não do mundo. A versão final **recalcula** o valor a
partir do fato e recusa tipos errados.

`DESEJO:PRIORIDADE` é o exemplo mais interessante: a prioridade entre camadas de
desejo de um NPC é uma **regra registrada**, não uma constante escondida no
código de NPCs. Isso a torna visível, auditável e citável no livro.

---

## 6. Resolução

```python
Declaracao(acao, ator, alvo, atributo, valor_atributo, bonus_atributo,
           pericia, graduacao, dificuldade, regras, fatos, contexto)
```

Validações no construtor (todas antes de qualquer dado):

* atributo pertence aos seis;
* `1 ≤ valor_atributo ≤ 30`, inteiro e não `bool`;
* `bonus_atributo == (valor_atributo − 10) // 2` — **o motor não aceita bônus
  negociado**;
* `0 ≤ graduacao ≤ 5`;
* `1 ≤ dificuldade ≤ 60`;
* cada código de `regras` existe no Registro;
* cada regra consegue calcular o seu valor a partir dos fatos (chamada de
  validação seca);
* nenhum par exclusivo declarado junto;
* `acao` e `ator` não vazios;
* `fatos` e `contexto` serializáveis em JSON canônico.

`Resultado` recalcula `total`, `margem`, `grau`, `critico` e `sucesso` no
construtor e aborta se o que recebeu divergir. Quatro invariantes explícitos.

`verificar_invariantes()` faz introspecção do próprio pacote:

* varre o código-fonte atrás de **nomes proibidos**
  (`rerolar`, `ajustar_total`, `bonus_narrativo`, `plot_armor`, `mercy`,
  `fudge`, `desejado`, `esperado_pelo_mestre`, …);
* confere que `Declaracao`, `Resultado`, `Rolagem`, `Compromisso` e `TermoDado`
  continuam `frozen`;
* confere que nenhuma função pública aceita parâmetro de intenção;
* exercita cada regra do Registro com fatos plausíveis e confere o limite.

Rodar `./xan motor autoteste` imprime o resultado — hoje, **656 verificações
estruturais**.

---

## 7. Certificação estatística

`justica.py` não usa `scipy` nem `numpy`. As funções especiais são escritas à
mão:

| Função | Método |
|---|---|
| `gamma_q(a, x)` | série `_gser` para `x < a+1`, fração continuada de Lentz `_gcf` acima |
| `chi2_p_valor(x, gl)` | `gamma_q(gl/2, x/2)` |
| `ks_p_valor(d, n)` | série de Kolmogorov com 100 termos |
| `normal_p_valor_bicaudal(z)` | `erfc(|z|/√2)` |
| `distribuicao_exata(expr)` | convolução em `Fraction` |
| `momentos_exatos(expr)` | estatística de ordem em `Fraction` |
| `distribuicao_maior_corrida(M)` | **programação dinâmica exata em inteiros** |

> **Bug real encontrado aqui.** A primeira versão do teste de "maior corrida de
> uns" usava uma tabela de π do NIST SP 800-22 lembrada de cabeça. A distribuição
> estava deslocada em uma categoria: `P(L ≤ 1)` para M = 128 não é 0,1174, é
> ≈ 1,9 × 10⁻¹². A versão final **calcula** a distribuição por PD
> (`_contagens_sem_corrida(M, k)` conta sequências de comprimento M sem corrida
> de 1s maior que k) e foi validada contra força bruta para M = 8, casando
> fração por fração.

> **Segundo bug real.** No teste de imparcialidade de `kh`/`kl`, as distribuições
> marginais das faces mantidas e descartadas somam `k` e `n − k`, não 1. Passá-las
> como probabilidades para o qui-quadrado produzia `p = 0` e uma "falha"
> inexistente. A correção normaliza as duas marginais.

As 15 famílias:

| Fam. | Teste | Estatística |
|---|---|---|
| A | uniformidade de d4, d6, d8, d10, d12, d20, d100 | qui-quadrado |
| B | `abaixo(n)` para n = 3, 5, 6, 7, 13, 20, 100 | qui-quadrado |
| C | distribuição exata de 1d20, 2d6, 3d6, 4d6kh1, 2d20kh1, 1d20+5, 3dF | qui-quadrado contra PMF exata |
| D | média e variância de 1d20, 2d6, 4d6kh1, 2d20kh1 | χ² com 2 gl |
| E | uniformes em [0,1) | Kolmogorov–Smirnov |
| F | autocorrelação lag-1 | z-normal |
| G | corridas acima/abaixo da mediana | z-normal |
| H | monobit, pôquer-4, maior corrida (M = 128) | NIST SP 800-22, com PD exata |
| I | pares consecutivos de d6 | qui-quadrado (36 células) |
| J | marginais de mantidas e descartadas em `4d6kh1` | dois qui-quadrados |
| K | `escolher_ponderado` | qui-quadrado contra os pesos |
| L | Fisher–Yates: permutações e posição de cada carta | dois qui-quadrados |
| M | eficiência da rejeição | z contra a razão teórica de bytes |
| N | determinismo e separação por semente | comparação exata |
| O | seis atores diferentes, mesma distribuição | qui-quadrado gl = 5 |

α = 0,001 por teste. Falha dura em p < 10⁻⁶. Vereditos: `APROVADO`,
`APROVADO COM RESSALVA`, `REPROVADO`.

**Resultado publicado** (`docs/CERTIFICADO_DE_JUSTICA.md`): 40 testes,
3 527 846 amostras, 0 abaixo de α, 0 falhas duras — **APROVADO**.

---

## 8. Camadas de jogo

Toda camada de jogo obedece à mesma disciplina: **nada de decisivo fica sem
número na tabela**, e nada de numérico é decidido por opinião.

```
entropia ─┐
dados     ├── resolucao ──┬── reinos ──── personagens ──┐
auditoria ┤               │                             │
compromisso┘               ├── npcs ────────────────────┤
regras ────────────────────┘                             ├── combate
        calendario ── mundo ── seitas ── artes ── bestiario┘
                     └── mapas (SVG)
        justica (certificação)         cli (verbos)      servidor/app.py (web)
```

Decisões de projeto que valem registro:

* **A Defesa não inclui o nível.** A lacuna de reinos já é `REINO:SUPRESSAO`;
  contar as duas coisas tornaria mestres intocáveis.
* **O Qi não infla a Defesa.** Ele é escudo no sentido do ACS: absorve **dano**.
  Quem quer Defesa maior sustenta um Manto de Qi (+2, 10 Qi por rodada) — uma
  escolha tática com custo, não um número derivado da riqueza.
* **O Núcleo Dourado não rola dado.** É pontuação sobre fatos declarados. É a
  única ruptura sem sorte e por isso é a mais consequente.
* **A tribulação é calibrada por simulação.** 1,6% de sobrevivência sem preparo no
  nível 9; 75% com preparo bom; 18,4% na Ascensão com o melhor preparo possível.
  Números medidos com o motor real, não estimados.
* **A linha vermelha de um NPC não vai ao dado.** Dar ao acaso a chance de fazer
  alguém cruzar a única linha que jurou não cruzar quebraria a promessa de que
  NPCs são pessoas.
* **A conduta do NPC é rolada, e a camada de desejo que a explica é derivada** de
  `prioridade × 10 + bônus da virtude governante` para aquele NPC. Conta fechada
  sobre a personalidade dele — sem sorteio extra e sem preferência do mestre.
* **O gerador de mundo só emite vocabulário que o Registro de Regras aceita.**
  Existe teste que percorre todas as províncias e facções de um mundo gerado e
  passa cada fato pela regra correspondente.
* **A tabela de raridade de raízes é escolhida antes da criação** e vale para
  todos. É regra de mesa, não vantagem narrativa — a diferença entre as duas é o
  momento em que se decide.

---

## 9. Testes

```bash
cd motor && python3 -m unittest discover -s testes -t . -v
```

**260 testes**, `unittest` da biblioteca padrão.

`test_espinha_dorsal.py` — DRBG, fontes, amostragem, parser, matemática exata
(conferida contra enumeração), auditoria (cada forma de adulteração),
compromisso, Registro de Regras, Mecânica Central, invariantes, e uma versão
rápida da bateria de justiça.

`test_dominio.py` — calendário, reinos, Leis, compatibilidade, Núcleo Dourado,
rupturas, tribulação (incluindo conservação da aritmética do dano), personagens,
raízes (distribuição conferida contra os pesos publicados), NPCs (ledger,
conduta, veto, agendas), mundo (determinismo, unicidade de nomes, simetria da
matriz, coerência geográfica, clima), artes, bestiário, combate (supressão,
alcance, Qi-escudo, estatística de duelos), seitas, torneio, mapas (XML válido,
escape de caracteres) e **coerência entre módulos**.

Três bugs reais foram encontrados pelos testes durante o desenvolvimento e estão
documentados acima, nos blocos de citação.

---

## 10. O que este motor não faz

* **Não é certificado pelo NIST CAVP.** Não há vetores oficiais disponíveis
  offline; reivindicar isso seria mentira. O que se afirma é: a construção é a do
  SP 800-90A §10.1.2, há regressão de valores-ouro, determinismo testado e uma
  bateria estatística publicada.
* **Não impede um mestre de decidir sem rolar.** E nem deveria: o Cap. 18 do
  livro trata disso. O que o motor impede é rolar **e** ignorar.
* **Não é à prova de adulteração física.** Quem tem acesso de escrita ao arquivo
  e ao selo pode reescrever os dois. A defesa é separar o selo do diário — e o
  `LEIA-ME.md` de `backups/` diz isso explicitamente.
* **Não gera aleatoriedade verdadeira em modo semeado.** `FonteSemeada` é
  determinística de propósito. Para a mesa, use a fonte viva (padrão quando não
  se passa `--semente`).
