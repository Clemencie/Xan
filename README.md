# XAN — 仙道 · Rios e Lagos

**Um sistema completo de RPG de mesa sobre cultivo imortal, seitas rivais e o
Murim — com um motor de dados que não pode ser trapaceado.**

Inspirado em [*Amazing Cultivation Simulator*](https://store.steampowered.com/app/1928690/)
(GSQ Games) e na tradição wuxia / xianxia / murim.

> **A Regra de Ouro:** depois que os dados e os modificadores são declarados,
> nada mais pode mudar o resultado. Nem o mestre, nem o jogador, nem a história,
> nem o motor.

---

## Começar em três comandos

```bash
./xan motor autoteste                                   # o motor confere a si mesmo
./xan mundo gerar --semente minha-mesa --saida mundos/minha-mesa --npcs 12
./xan personagem --nome "Lin Yue" --semente minha-mesa-pj1
```

Não há instalação. Só **Python 3.9+** e a biblioteca padrão — nenhuma
dependência externa.

---

## O que tem aqui

```
Xan/
├── xan                      # ponto de entrada executável (CLI)
├── motor/
│   ├── xan/                 # o motor
│   │   ├── entropia.py      #   HMAC-DRBG (SP 800-90A), fonte viva e semeada
│   │   ├── dados.py         #   notação NdS, !, kh/kl, Fudge, d% + matemática exata
│   │   ├── auditoria.py     #   diário JSONL encadeado por SHA-256 + Merkle + selo
│   │   ├── compromisso.py   #   commit-reveal: hash da declaração ANTES do dado
│   │   ├── regras.py        #   Registro fechado de 36 modificadores
│   │   ├── resolucao.py     #   Mecânica Central, invariantes, testes opostos
│   │   ├── justica.py       #   40 testes estatísticos de imparcialidade
│   │   ├── calendario.py    #   estações, shichen, Yin/Yang, clima, harmonia
│   │   ├── reinos.py        #   14 níveis, 30 Leis, Núcleo Dourado, tribulação
│   │   ├── personagens.py   #   Raiz Espiritual, 44 perícias, estado auditável
│   │   ├── artes.py         #   75 técnicas, artefatos, talismãs, formações, elixires
│   │   ├── npcs.py          #   personalidade, 8 camadas de desejo, conduta no dado
│   │   ├── mundo.py         #   gerador procedural (províncias, facções, história)
│   │   ├── seitas.py        #   prédios, missões, prestígio, Torneio de Kunlun
│   │   ├── bestiario.py     #   24 bestas canônicas + gerador procedural
│   │   ├── combate.py       #   iniciativa, defesa declarada, Qi-escudo, supressão
│   │   ├── mapas.py         #   mapas SVG sem dependências
│   │   └── cli.py           #   todos os verbos
│   ├── testes/              # 260 testes (unittest, biblioteca padrão)
│   └── servidor/            #   interface web (biblioteca padrão)
├── LIVRO/                   # o livro de regras em PT-BR (22 capítulos + fichas)
├── mundos/exemplo/          # um mundo gerado, com mapas SVG
├── docs/                    # certificado de justiça, arquitetura, auditoria
├── ferramentas/             # scripts auxiliares
└── backups/                 # git bundle + tar.gz + SHA256SUMS + restauração
```

---

## A espinha dorsal imparcial

O pedido central deste projeto foi um sistema de rolagens **completamente
aleatório e justo, sem vantagem narrativa**. Isso foi implementado como
arquitetura, não como política:

| Tentativa de interferência | O que impede |
|---|---|
| Trocar o resultado depois de vê-lo | `Resultado` é imutável e **recalcula** a própria aritmética no construtor; divergência aborta |
| Rolar de novo | Não existe nenhuma função de re-rolagem ou ajuste — verificado estruturalmente por `verificar_invariantes()` |
| Somar um bônus que não estava lá | Modificadores só nascem do **Registro de Regras** fechado, recalculado a partir de fatos objetivos |
| Declarar os fatos depois do dado | A declaração inteira vira hash e é gravada **antes** do dado (commit-reveal) |
| Editar o histórico | Diário append-only encadeado por SHA-256, raiz de Merkle, `fsync` por linha e **selo externo** |
| Dar dado melhor a um jogador | Mestre e jogadores consomem a **mesma** `Aleatoriedade`; testado (família O) |
| Viés de módulo | Amostragem por rejeição; eficiência verificada contra a razão teórica (família M) |
| "confia em mim" | 40 testes estatísticos sobre 3,5 milhões de amostras, publicados em `docs/CERTIFICADO_DE_JUSTICA.md` |

**Viés de módulo zero:** `abaixo(n)` descarta bytes fora do maior múltiplo de
`n` que cabe em um byte. Para `abaixo(7)` o consumo medido é 8/7 bytes por
resultado; para `abaixo(100)`, 128/100. Os dois batem com a teoria.

**`kh`/`kl` imparciais:** as faces *mantidas* e as *descartadas* têm a mesma
distribuição marginal — testado contra a distribuição exata calculada por
frações, não por simulação.

### Certificado

```bash
./xan justica --saida docs/CERTIFICADO_DE_JUSTICA --amostras 40000 --leves 15000
```

| Métrica | Valor |
|---|---:|
| testes | 40 |
| amostras | 3 527 846 |
| α por teste | 0,001 |
| falha dura | p < 10⁻⁶ |
| reprovados | 0 |
| **veredito** | **APROVADO** |

Honestidade sobre limites: o motor implementa a construção HMAC-DRBG do
**SP 800-90A §10.1.2** com SHA-256 e é validado por regressão de valores-ouro,
determinismo e pela bateria estatística acima. Ele **não** reivindica
certificação NIST CAVP — não há vetores oficiais disponíveis offline.

---

## O sistema em uma página

```
d20 + bônus de atributo + graduação de perícia + modificadores de regras ≥ DD
```

* **Seis atributos** (1–30): Percepção 感知, Constituição 體質, Carisma 魅力,
  Inteligência 悟性, Sorte 氣運, Potencial 根骨 — cada um ligado a uma das Cinco
  Virtudes (五常) e a um elemento do Wuxing.
* **Bônus** = `(valor − 10) ÷ 2`, de −5 a +10. **Perícias** 0–5 somam direto.
* **Graus**: margem <0 fracasso · 0–4 sucesso · 5–9 sucesso maior · ≥10 triunfo.
  Natural 1 = **desvio**. Natural 20 = **toque do Dao**.
* **36 modificadores** registrados, cada um recalculado de fatos declarados.
  Exemplo: `ELEMENTO:RELACAO` (Metal supera Madeira ⇒ +2), `REINO:SUPRESSAO`
  (±2 por nível de lacuna), `AMBIENTE:LUZ`, `ESTADO:FERIMENTO`.
* **13 níveis de cultivo** compartilhados por quatro caminhos (Xiandao 仙道,
  Shendao 神道, Corpo 體修, Marcial 武林), com nomes do Murim na mesma escada.
* **Núcleo Dourado** com grau 9→1 decidido por **pontuação de preparo**, não por
  dado — e só se tenta uma vez na vida.
* **Tribulação Celestial**: 3, 4 ou 9 raios. Medido: sobreviver à Ascensão com o
  melhor preparo possível tem **18,4%** de chance.
* **NPCs** com Cinco Virtudes, temperamento do Bagua, 2–4 traços com efeito
  numérico e **oito camadas de desejo**. Quando não é óbvio o que ele faria,
  **o dado decide** — pela Tabela de Conduta, filtrada pela personalidade dele.
* **Mundo procedural**: uma semente gera 9 províncias, sítios, facções, matriz de
  relações, 40 eventos históricos **com consequências materiais no presente**,
  tesouros lendários, clima dos 360 dias do ano e mapas SVG.

---

## CLI

```bash
./xan motor info | motor autoteste
./xan justica [--amostras N] [--saida PREFIXO]
./xan rolar "4d6kh3" [--teoria] [--diario CAMINHO] [--ator NOME]
./xan teste --atributo con --valor 16 --pericia espada --graduacao 4 --dd 18 \
            --regras "ELEMENTO:RELACAO,POSICAO:TERRENO" \
            --fatos '{"elemento_atacante":"metal","elemento_alvo":"madeira","terreno":"alto"}'
./xan oposto --ator-a X --valor-a 16 --ator-b Y --valor-b 14 --atributo con --pericia duelo
./xan mundo gerar --semente S --saida DIR [--provincias 9] [--eventos 40] [--npcs 12]
./xan npc [--semente S] [--nivel N] [--ocupacao "Ancião de seita"] [--agendas 2]
./xan personagem --nome N [--metodo sorteio|pontos] [--lei CODIGO] [--raiz heroica]
./xan besta [--nivel N] [--terreno T] [--catalogo]
./xan ruptura --ator N --nivel 5 --lei SETE_MASSACRES --int 16 --compreensao 4 ...
./xan nucleo --qi 420 --elemento metal --estacao inverno --dia 25 --polaridade yin ...
./xan tribulacao --ator N --nivel 9 --con 20 --vitalidade 220 --qi 370 ...
./xan combate [--nivel 6] [--defensivo] [--diario CAMINHO]
./xan seita --nome N --predios "..." --membros "Nome:nível,..." --mes --missao EXPLORAR_RUINA
./xan tabelas leis|regras|tecnicas|pericias|reinos|bestiario|predios|missoes
./xan auditoria verificar|selar|resumo --diario CAMINHO
./xan exemplo            # regenera mundos/exemplo/
```

Sem `--semente` o motor usa a **fonte viva** (`os.urandom`). Com `--semente` fica
reproduzível — a semente é declarada antes, vale para todos e fica gravada.

---

## Interface web

```bash
python3 motor/servidor/app.py            # ou: ./ferramentas/servir.sh
```

Abre em `http://localhost:8000`: livro de regras navegável, rolagem auditada com
o diário aparecendo na tela, gerador de NPCs e de personagens, gerador de mundo
com mapa SVG, simulador de combate e o certificado de justiça.

---

## Testes

```bash
cd motor && python3 -m unittest discover -s testes -t . -v
```

**260 testes**, biblioteca padrão, sem `pytest` nem `numpy`. Cobrem:

* o DRBG (determinismo, separação por semente, valores-ouro, ressemeadura);
* amostragem imparcial (rejeição, `escolher_ponderado`, Fisher–Yates);
* o parser de dados (incluindo regressões de bugs reais encontrados no caminho);
* matemática exata conferida contra **enumeração exaustiva**;
* auditoria (cadeia, Merkle, adulteração, remoção de linha, reordenação);
* compromisso/revelação (ordem obrigatória, token adulterado);
* o Registro de Regras (todas as 36 regras exercitadas, limites, exclusividades);
* a Mecânica Central (invariantes, bônus negociado recusado, validações);
* as camadas de jogo: reinos, Leis, Núcleo Dourado, tribulação, personagens,
  raízes, NPCs, ledger de relações, conduta, mundo, artes, bestiário, combate,
  seitas, torneio, mapas;
* **coerência entre módulos**: fatos produzidos pelo gerador de mundo são
  aceitos pelo Registro de Regras, disposições de NPC viram fatos válidos,
  estados de jogo viram fatos válidos.

---

## Backup

```bash
./backups/criar_backup.sh              # gera git bundle + tar.gz + SHA256SUMS
./backups/restaurar_backup.sh -l       # lista o que existe
./backups/verificar_backups.sh         # confere as somas SHA-256
```

Três camadas independentes:

1. **git bundle** — o histórico completo num único arquivo, clonável;
2. **tar.gz** — uma foto do diretório de trabalho, inclusive o que não está no git;
3. **SHA256SUMS** — verificação de integridade das duas.

Copie `backups/` para fora da máquina. Um backup que mora no mesmo disco que o
original não é backup.

---

## O livro

`LIVRO/` contém o sistema completo em português: 22 capítulos e 4 fichas.

Comece por `LIVRO/00-indice.md`. Se quiser entender por que o sistema é assim,
leia `LIVRO/02-regra-de-ouro-e-contrato-de-imparcialidade.md` e
`LIVRO/18-mestre-e-imparcialidade.md` — são o coração do projeto.

---

## Licença

Sistema original, escrito para esta mesa. *Amazing Cultivation Simulator* é da
GSQ Games e é citado apenas como referência de design. Os termos chineses são de
domínio cultural.
