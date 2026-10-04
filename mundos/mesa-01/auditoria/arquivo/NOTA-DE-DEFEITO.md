# Diário v1 — ARQUIVADO POR DEFEITO DO MOTOR (não por adulteração)

**Status:** `verificar()` → `ok = False`
**Motivo reportado:** `conteúdo adulterado: hash não bate com o payload`
**Linha afetada:** 41 de 50 (`tabela_declarada`)
**Causa real:** bug em `auditoria.canonico()`, não adulteração.

## O que aconteceu

A linha 41 gravou uma tabela de 20 encontros com **chaves inteiras** (`{1: "...", 2: "...", ..., 20: "..."}`).

`json.dumps(..., sort_keys=True)` ordena chaves inteiras **numericamente**
(`1, 2, 10, 20`). Depois do round-trip pelo arquivo, as chaves viram strings e
`sort_keys` ordena **lexicograficamente** (`"1", "10", "2", "20"`). O hash
gravado na escrita não bate com o recalculado na leitura.

As outras 49 linhas verificam. Nenhuma delas tem chave inteira.

## Por que este arquivo foi guardado em vez de apagado

Porque ele é a evidência de que o sistema funcionou como projetado: **detectou
uma inconsistência que ninguém viu acontecer**, incluindo o mestre. O falso
positivo é um defeito; a detecção é a garantia.

Apagar seria perder a única amostra real do bug.

## O que foi feito

1. `canonico()` corrigido: normaliza recursivamente toda chave para a string que
   o próprio JSON produziria. Forma canônica idêntica na escrita e na leitura.
2. Casos ambíguos agora são **recusados**: colisão de chaves (`{1:"a","1":"b"}`),
   float não-finito, chave não serializável.
3. Quatro testes de regressão, incluindo o cenário exato que falhou.
4. **O diário da sessão foi recomeçado do zero** (`../mesa-01.jsonl`, v2).

## O que NÃO foi feito

Os números do personagem gerados sob o diário v1 **não foram preservados**.

As rolagens individuais (índices 3–22) verificam corretamente — o defeito está
só na linha 41. Seria possível argumentar que a ficha continua válida. Mas o
personagem foi re-rolado mesmo assim, e o motivo importa:

> Extrair valores de um diário que `verificar()` condena, e decidir quais
> conservar, é o mestre escolhendo a ficha. É precisamente o que a Cláusula 1 do
> Contrato de Imparcialidade proíbe.

O custo foi uma ficha. A alternativa era abrir a primeira exceção — e uma
exceção ao contrato vale mais que qualquer personagem.

O que o v1 continha, para registro: `Tan Zhong 譚忠`, masculino, 17 anos,
PER 12 / CON 6 / CHA 15 / INT 11 / LUK 18 / POT 16, raiz amarela de quatro
elementos com 9% de pureza. Esses números estão mortos. O v2 decidiu outros.
