# XAN — 仙道 · Rios e Lagos

**Um sistema completo de RPG de mesa sobre cultivo imortal, seitas rivais e o Murim.**

Inspirado em *Amazing Cultivation Simulator* (GSQ Games) e na tradição
wuxia/xianxia/murim — mas construído do zero, com uma exigência que quase
nenhum sistema de mesa tem: **o dado não pode ser manipulado, nem pelo mestre,
nem pelo sistema, nem por você.**

---

## Como ler este livro

Se você só quer jogar hoje, leia os capítulos **1, 3, 5 e 12**. O resto é
consulta.

Se você quer entender *por que* o sistema é assim, leia o capítulo **2**
(Contrato de Imparcialidade) e o **18** (O Mestre e a Imparcialidade). Eles são
o coração do projeto.

Se você quer auditar o motor, vá direto para `motor/` e rode:

```bash
./xan motor autoteste        # invariantes estruturais
./xan justica --saida docs/CERTIFICADO_DE_JUSTICA   # bateria estatística
```

---

## Índice

| Cap. | Arquivo | Conteúdo |
|---|---|---|
| 0 | `00-indice.md` | Este arquivo |
| 1 | `01-o-que-e-xan.md` | O que é o XAN, o que ele promete, o que ele recusa |
| 2 | `02-regra-de-ouro-e-contrato-de-imparcialidade.md` | **A Regra de Ouro e o contrato que a mesa assina** |
| 3 | `03-mecanica-central.md` | d20 + atributo + perícia + regras ≥ DD. Graus de sucesso |
| 4 | `04-atributos-e-pericias.md` | Os seis atributos, as Cinco Virtudes, as 44 perícias |
| 5 | `05-raizes-espirituais-e-criacao.md` | Raiz Espiritual (靈根), criação de personagem |
| 6 | `06-reinos-de-cultivo.md` | A escada 0–13, os quatro caminhos, longevidade |
| 7 | `07-caminhos.md` | Xiandao, Shendao, Corpo e Marcial em detalhe |
| 8 | `08-leis-e-manuais.md` | As 30 Leis (功法), Compatibilidade, manuais e Inspiração |
| 9 | `09-qi-elementos-e-fengshui.md` | Wuxing, Qi, Feng Shui, densidade, clima, horas Yin/Yang |
| 10 | `10-combate.md` | Iniciativa, defesa declarada, dano, Qi-escudo, supressão de reino |
| 11 | `11-tribulacoes-e-rupturas.md` | Rupturas, Núcleo Dourado (grau 9→1), Desvio de Qi, Tribulação |
| 12 | `12-npcs.md` | **Personalidade, desejos, livro de relações e conduta no dado** |
| 13 | `13-mundo-procedural.md` | Geração de mundo por semente: províncias, sítios, história |
| 14 | `14-seitas-e-gestao.md` | Prédios, postos, missões, prestígio, Torneio de Kunlun |
| 15 | `15-alquimia-artefatos-talismas-formacoes.md` | Os quatro ofícios |
| 16 | `16-bestas-espirituais.md` | Bestiário canônico e gerador procedural |
| 17 | `17-economia-e-tesouros.md` | Pedras espirituais, graus de tesouro, tabelas de saque |
| 18 | `18-mestre-e-imparcialidade.md` | Ferramentas do mestre que **não** violam o contrato |
| 19 | `19-campanhas-e-ganchos.md` | Estruturas de campanha e 40 ganchos |
| 20 | `20-glossario.md` | Glossário chinês ↔ português |
| 21 | `21-tabelas.md` | Todas as tabelas numéricas em um só lugar |
| — | `fichas/` | Ficha de personagem, de NPC, de seita e de facção |

---

## O sistema em uma página

1. **Atributos** (1–30): Percepção 感知, Constituição 體質, Carisma 魅力,
   Inteligência 悟性, Sorte 氣運, Potencial 根骨. Bônus = `(valor − 10) ÷ 2`,
   arredondado para baixo.
2. **Perícias** (0–5): somam direto no teste.
3. **Teste**: `d20 + bônus de atributo + graduação + modificadores de regras ≥ DD`.
4. **Modificadores** só existem se estiverem no **Registro de Regras** e só são
   calculados a partir de **fatos objetivos declarados antes da rolagem**.
5. **Compromisso**: a declaração inteira vira um hash gravado num diário
   encadeado **antes** do dado cair. Depois, o dado. Depois, a revelação do sal.
6. **Graus**: margem < 0 fracasso · 0–4 sucesso · 5–9 sucesso maior · ≥ 10 triunfo.
   Natural 1 = desvio. Natural 20 = toque do Dao.
7. **Cultivo**: níveis 0–13 compartilhados por quatro caminhos, com rupturas
   roladas, um Núcleo Dourado pontuado e tribulações que matam quem não se prepara.
8. **NPCs**: Cinco Virtudes, um temperamento do Bagua, 2–4 traços com efeito
   numérico e oito camadas de desejo. Quando não é óbvio o que ele faria,
   **o dado decide** — não o mestre.
9. **Mundo**: uma semente gera continente, províncias, facções, história e clima
   do ano inteiro. Mesma semente, mesmo mundo, sempre.

---

## Licença e autoria

Sistema original. O nome *Amazing Cultivation Simulator* pertence à GSQ Games e
é citado apenas como referência de design. Os termos chineses são de domínio
cultural.
