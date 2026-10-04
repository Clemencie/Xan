# Mundo de exemplo

Gerado com:

```bash
./xan mundo gerar --semente "xan-mundo-exemplo" --saida mundos/exemplo --npcs 10
```

| Arquivo | Conteúdo |
|---|---|
| `mundo.json` | o mundo completo, máquina-legível (inclui a semente e a versão do gerador) |
| `mundo.md` | o mundo completo para ler na mesa: províncias, facções, matriz de relações, sítios com segredos, linha do tempo com consequências, tesouros |
| `mundo.svg` | mapa do continente em grade hexagonal; passe o mouse num marcador para ver o segredo do sítio |
| `npcs.json` / `npcs.md` | dez NPCs notáveis completos, com personalidade e desejos |
| `provincias/*.svg` | mapa de detalhe de cada província |

**Reproduzir:** rode o comando acima de novo. O resultado é idêntico byte a byte —
é disso que se trata.

**Aviso para o mestre:** os tooltips dos marcadores no `mundo.svg` revelam os
segredos de cada sítio. Se quiser que os jogadores descubram jogando, não projete
esse arquivo com o mouse passando por cima.
