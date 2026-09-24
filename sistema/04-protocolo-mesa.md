# 04 — Protocolo da mesa (como jogamos no chat)

## Papéis

- **Mestre (eu):** narra o mundo, interpreta NPCs e inimigos, define DNs, **rola todos os dados**
  com o motor (`motor/wg.py`), mostra cada resultado e atualiza ficha, bancos e diário.
- **Jogador (você):** declara o que seu Legionário **tenta fazer e como**. Uma ação principal por
  mensagem; reações curtas são livres.

## Formato de turno

1. **Mestre — Cena:** descreve situação, perigo e o que está em jogo; lista saídas visíveis.
2. **Jogador — Ação:** intenção + abordagem. Ex.: *"Vou cruzar a praça sob fogo para alcançar o
   Rhino — correndo baixo, usando os destroços como cobertura."*
3. **Mestre — Resolução:** declara o teste (Perícia + Atributo + DN + modificadores), rola no motor,
   mostra os dados e narra o resultado **com as consequências** (inclui complicações do ⚡=1).
4. **Jogador — Reação:** pode gastar recursos **antes** da narração final? Não — declare gastos
   reativos (rerolar com Ira, soak com Determination) **logo após ver os dados**, e eu ajusto a cena.

## Bloco de rolagem (padrão do Mestre)

Toda rolagem aparece assim, transparente:

```
🎲 Teste: Ballistic Skill (4) + Agility (4) = 8d6 vs DN 3
   Dados: [⚡6!] [6] [5] [4] [3] [2] [2] [1]
   Ícones: 2+2+1+1 = 6 vs DN 3 → SUCESSO (margem 4)
   ⚡6! → +1 Glória ao grupo; ataque = CRÍTICO
   Shifts: 2 exaltados disponíveis → +2 ED de dano
```

Sem dado escondido, sem "confia em mim". O motor é determinístico e auditável.

## Suas declarações especiais (diga em texto livre)

| Intenção | Como declarar |
|---|---|
| Rerolar falhas (1 Ira) | *"Gasto 1 Ira e rerolo as falhas."* |
| Bônus de Glória | *"Gasto 2 Glória: +2d neste teste."* / *"+2 de dano."* |
| Shift de exaltados | *"Shifto 2 para dano, 1 para Glória."* (ou deixe o Mestre sugerir o melhor uso) |
| Comprar sucessos | *"Sem estresse aqui — compro sucessos."* |
| Defesa Total | *"Entro em Defesa Total."* (ação reflexiva/completa conforme o caso) |
| Ataque de interação | *"Tento intimidar o líder deles antes de atirar."* |
| Narrar detalhe (1 Ira) | *"Gasto 1 Ira: digo que há um duto de manutenção atrás do altar."* (sujeito a veto) |
| Recuar / render-se / negociar | Sempre permitido — sobreviver também é glória. |

## Bancos e ficha

- Ao fim de **cada cena**, o Mestre exibe: `Ira: X | Glória: Y | Ruína: Z | Wounds/Shock atuais`.
- A ficha viva está em `fichas/ficha-jogador.md`; o diário em `campanha/sessoes/`.
- **Descanso entre operações:** recupera Shock total, metade das Wounds (arredondar p/ cima),
  +1 Ira (máx. 3 guardados) — e o Mestre pode avançar o relógio da Heresia…

## Tom e segurança

Warhammer é grimdark: guerra, fanatismo, horror corporal e cósmico. Vale tudo na ficção,
**menos**: violência sexual explícita e crueldade gratuita contra crianças — esses temas ficam
fora de cena ou nem aparecem. Se algo incomodar, diga *"véu"* e pulamos a descrição sem
julgamento. Divertir-se > sofrer.

## Ritmo

- Cenas curtas, decisões frequentes, cliffhanger sempre que possível.
- Fim de sessão = **Dossiê**: resumo, XP ganho, bancos, ganchos e "na próxima…".
- Canon é ponto de partida: seus atos podem ecoar (ou quebrar) os livros — e o Mestre adapta.
