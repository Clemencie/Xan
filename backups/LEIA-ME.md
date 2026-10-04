# Backups do XAN

Três camadas independentes, porque uma só nunca é suficiente.

| Arquivo | O que é | Como restaurar |
|---|---|---|
| `<data>-<rótulo>.bundle` | histórico git completo, todos os ramos, num arquivo só | `git clone X.bundle dir/` |
| `<data>-<rótulo>.tar.gz` | foto do diretório de trabalho, sem `.git` | `tar -xzf X.tar.gz -C dir/` |
| `<data>-<rótulo>.MANIFESTO.txt` | data, ramo, commit, contagens | leitura humana |
| `SHA256SUMS` | somas SHA-256 de tudo acima | `./verificar_backups.sh` |

## Criar

```bash
./backups/criar_backup.sh                    # rótulo "completo"
./backups/criar_backup.sh antes-da-sessao-07 # rótulo próprio
```

## Verificar

```bash
./backups/verificar_backups.sh
./backups/restaurar_backup.sh -l
./backups/restaurar_backup.sh -v backups/20261003T000000Z-completo.bundle
```

## Restaurar

```bash
# histórico completo (recomendado: traz o git de volta)
./backups/restaurar_backup.sh -c backups/<arquivo>.bundle ~/restaurado

# só os arquivos de trabalho
./backups/restaurar_backup.sh -x backups/<arquivo>.tar.gz ~/restaurado
```

Depois de restaurar, confira:

```bash
cd ~/restaurado/Xan            # ou ~/restaurado, conforme o modo
cd motor && python3 -m unittest discover -s testes -t .
./xan motor autoteste
./xan auditoria verificar --diario mundos/<mesa>/auditoria/diario.jsonl
```

## A regra que ninguém quer ouvir

**Copie `backups/` para fora desta máquina.** Um backup que mora no mesmo disco
do original não é backup: é uma cópia que morre junto.

Sugestão: um bundle num drive externo, um tar.gz num serviço de nuvem cifrado, e
o `SHA256SUMS` impresso ou colado num e-mail para você mesmo. O SHA256SUMS
separado é o que impede que alguém troque os dois arquivos de lugar e você não
perceba.

## Diários de auditoria das mesas

Os diários (`mundos/*/auditoria/*.jsonl`) são **append-only** e ficam fora do git
por padrão (`.gitignore`), porque crescem a cada rolagem. Ainda assim eles estão
incluídos no `tar.gz` — que é justamente o motivo de o tar.gz existir além do
bundle.

Se quiser preservar um diário de sessão importante:

```bash
./xan auditoria selar --diario mundos/minha-mesa/auditoria/2026-10-03.jsonl \
                      --saida mundos/minha-mesa/selos/2026-10-03.txt
```

Guarde o arquivo de selo junto com o backup externo. Ele prova que ninguém
reescreveu o diário depois daquela data — inclusive você.

## Nota sobre o que o bundle contém

O `git bundle` captura o histórico **até o commit em que ele foi criado**. Os
próprios arquivos de backup nunca estão dentro do bundle que os contém — isso é
uma regressão impossível de fechar, e é normal.

Na prática:

* o bundle deste diretório contém todo o código, o livro, o mundo de exemplo, os
  testes e o certificado;
* se você criar um novo backup depois, o novo bundle conterá também este;
* o `tar.gz` contém o diretório de trabalho inteiro **exceto** `.git`, outros
  bundles e outros tar.gz — ou seja, ele é a foto dos arquivos, e o bundle é a
  foto do histórico. Os dois juntos cobrem tudo.

Restauração verificada: clonar o bundle reproduz o repositório com os 260 testes
passando e `./xan motor autoteste` verde.
