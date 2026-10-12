# XAN — motor de RPG solo

**Você joga um personagem. Eu sou a ferramenta: metade motor de dados, metade mundo.**
Eu controlo PdMs, clima, inimigos e consequências. Nunca controlo você.

**Sistema:** Mutantes & Malfeitores 3ª Edição (Steve Kenson, ed. brasileira Jambô).
**Cenário:** *Maré Alta* — Baía de Santa Clara, quinze anos depois de o mar ter recuado
três quilômetros e voltado como uma parede de luz.

> O sistema anterior (murim) está arquivado em `.arquivo/`, intacto, como referência
> de design. Não é mais jogável.

---

## O que este repositório faz

1. **Rola com aleatoriedade real** (`secrets`, não `random`). Nada de resultado inventado.
2. **Dosa a profundidade de cada PdM** por sorteio de peso narrativo. Um capanga de
   assalto **não** ganha passado, motivação profunda e segredo. Isso é assertiva de
   teste, não promessa de estilo.
3. **Faz a forma mandar.** Um bicho não tem nome próprio nem segredo. Um objeto não tem
   desejo. Um ambiente não tem ficha.
4. **Exige que tudo pertença a esta história.** Cada encontro tem uma âncora de trama e
   passa por filtro de terreno e hora. Cada facção tem repertório próprio de poderes.
5. **Valida a ficha contra os cinco limites de Nível de Poder** do livro e recusa com a
   lista completa do que estourou.

---

## Rodando

```bash
python3 testes.py        # ~7.600 sorteios sob invariante — tem que terminar em EXIT=0
python3 demo.py          # passeio de ponta a ponta: ficha, PdMs, encontros, combate
```

CLI do motor:

```bash
python3 dados.py peso                       # d10 -> tier de profundidade
python3 dados.py oraculo 70 [caos]          # oráculo sim/não
python3 dados.py cena [caos]                # teste de cena (d10 vs Caos)
python3 dados.py encontro porto madrugada   # encontro filtrado por terreno e hora
python3 dados.py faísca                     # Foco + Ação + Assunto
python3 dados.py cd                         # tabela de dificuldades do livro
```

---

## Mapa dos arquivos

| Arquivo | O que é |
|---|---|
| `dados.py` | CLI do motor: oráculo, cena, peso narrativo, encontro, faísca, tabela de CD |
| `mm3/regras.py` | 8 habilidades, 5 defesas, 16 perícias, ~40 vantagens, 40 efeitos, condições, Tabela de Medidas, tabela de CD, custos e limites de NP |
| `mm3/mundo.py` | Lore, 8 facções, 13 lugares, 76 encontros com âncora, listas de evento |
| `mm3/heroi.py` | Ficha com validação, testes d20, ataque, esforço extra, pontos heroicos, moribundo, estado persistente |
| `mm3/heroi_npc.py` | Gerador de PdM com dosagem T0–T4 e teto por forma |
| `mm3/encontros.py` | Sorteio de encontro com filtro de terreno/hora/forma |
| `testes.py` | Invariantes |
| `demo.py` | Demonstração executável |
| `REGRAS.md` | Referência de regras, com a marcação do que veio do PDF |
| `.arquivo/` | o sistema murim anterior |

---

## Como jogar

Eu rolo por baixo do capô. Você vê só a história. Se perguntar *"que rolagem foi
essa?"*, eu respondo seco.

Eu **não** termino uma narração sugerindo o que você deve fazer. A cena fica aberta e
eu espero.

Rolagem só entra quando há dúvida real com consequência real, quando uma cena abre,
quando você pede o oráculo, ou quando cai duplo — no máximo 3 a 5 perguntas cirúrgicas
por cena, nunca quinze para "montar" uma resposta.

**Leia `REGRAS.md` para as regras.** Este arquivo é só o índice.
