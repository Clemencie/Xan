# Capítulo 14 — Seitas e Gestão

O *Amazing Cultivation Simulator* é, no fundo, um jogo de gestão com cultivo por
cima. O XAN assume isso: uma seita é uma instituição com orçamento, celeiro,
hierarquia e inimigos, e administrá-la é um modo de jogo completo.

## 14.1 Postos

Dez postos, e **cada um exige um nível de cultivo mínimo**. Não existe promoção
por merecimento narrativo — o motor recusa.

| Posto | 中文 | Nível mínimo |
|---|---|---:|
| Servo | 僕 | 0 |
| Discípulo Externo | 外門弟子 | 0 (nível 1 se cultivador) |
| Discípulo Interno | 內門弟子 | 3 |
| Discípulo Núcleo | 核心弟子 | 5 |
| Chefe de Ramo | 分支主 | 6 |
| Mestre de Pavilhão | 堂主 | 7 |
| Ancião | 長老 | 7 |
| Grande Ancião | 大長老 | 9 |
| Ancestral | 老祖 | 10 |
| Mestre da Seita | 掌門 | 8 |

**Discípulos externos** são mortais e nível 0–2: trabalham nos campos, na
cozinha e na forja. **Internos** cultivam. A diferença entre os dois é o motor
dramático de metade dos romances do gênero: o externo que é humilhado, descobre
um manual proibido e volta três anos depois.

## 14.2 Prédios

| Código | Nome | 中文 | Custo | Nv. mín. da seita | Produção/mês |
|---|---|---|---:|---:|---|
| `CELEIRO` | Celeiro | 糧倉 | 1 500 | 0 | 300 de comida |
| `TORRE_DE_VIGIA` | Torre de Vigia | 望樓 | 2 500 | 0 | alerta: +2 contra surpresa |
| `CAMPOS_ESPIRITUAIS` | Campos Espirituais | 靈田 | 3 000 | 0 | 8 ervas |
| `ARENA` | Arena de Duelos | 演武場 | 4 000 | 1 | +1 graduação marcial por temporada |
| `PAVILHAO_MANUAIS` | Pavilhão de Manuais | 藏經閣 | 5 000 | 1 | +1 Compreensão para internos |
| `ENFERMARIA` | Enfermaria | 醫館 | 5 000 | 2 | cura 6 Vitalidade/dia por paciente |
| `SALA_DE_MEDITACAO` | Sala de Meditação | 靜室 | 6 000 | 2 | +6 estado mental/mês |
| `OFICINA_DE_TALISMAS` | Oficina de Talismãs | 符籙坊 | 7 000 | 3 | 4 talismãs de grau Terra |
| `COFRE` | Cofre de Pedras | 庫房 | 8 000 | 3 | 2% ao mês sobre as pedras |
| `SALA_DE_FORMACOES` | Sala de Formações | 陣法堂 | 9 000 | 4 | 1 formação |
| `PRISAO` | Prisão de Selos | 封印牢 | 10 000 | 5 | mantém 2 prisioneiros selados |
| `SALA_DE_ALQUIMIA` | Sala de Alquimia | 丹房 | 12 000 | 4 | 2 elixires |
| `FORJA` | Forja de Artefatos | 煉器房 | 15 000 | 5 | 1 artefato de grau Terra |
| `ALTAR_SHENDAO` | Altar de Fé | 神壇 | 20 000 | 6 | 20 de Fé |

Produção é **aritmética**, não dado. Só o que exige julgamento rola: refinar um
elixir específico, forjar um artefato específico, montar uma formação sob
ataque.

A densidade de Qi da província soma à produção: `veia_espiritual` +1 em tudo e +2
nos Campos; `terra_imortal` +2 e +4. É a razão pela qual duas seitas brigam por
uma montanha: a mesma montanha rende o dobro.

**Consumo:** cada membro come 1 de comida por mês. Se faltar, `fome > 0` e a
seita perde 5 de prestígio por mês de fome, e 10% dos discípulos externos vão
embora.

## 14.3 Missões

Doze missões publicadas. Cada uma tem DD base, risco (1–5), prestígio, faixa de
pedras, XP e a perícia usada.

| Código | Missão | DD | Risco | Prestígio | Pedras |
|---|---|---:|---:|---:|---|
| `ENTREGAR_CARTA` | Entregar uma carta selada | 11 | 2 | +4 | 80–400 |
| `COLHER_ERVAS` | Colher ervas na encosta | 12 | 1 | +2 | 50–300 |
| `PROTEGER_VILA` | Proteger uma vila de saqueadores | 14 | 2 | +7 | 100–600 |
| `ESCOLTA_CARAVANA` | Escoltar uma caravana | 15 | 2 | +5 | 200–900 |
| `COBRAR_DIVIDA` | Cobrar uma dívida de um clã | 16 | 2 | +6 | 300–2 000 |
| `CACAR_BESTA` | Caçar uma besta espiritual | 17 | 3 | +8 | 300–2 500 |
| `EXPLORAR_RUINA` | Explorar uma ruína | 18 | 3 | +9 | 400–3 000 |
| `PARTICIPAR_TORNEIO` | Representar a seita em Kunlun | 20 | 3 | +20 | 500–5 000 |
| `RESGATAR_REFEM` | Resgatar um refém | 20 | 4 | +12 | 600–4 000 |
| `INFILTRAR_SEITA` | Infiltrar-se em seita rival | 22 | 4 | +14 | 800–5 000 |
| `ASSASSINAR_TRAIDOR` | Executar um traidor da seita | 24 | 4 | +18 | 1 000–8 000 |
| `SELAR_REINO_SECRETO` | Fechar um reino secreto que vazou | 26 | 5 | +25 | 2 000–20 000 |

A DD efetiva é `DD base + (risco − 1) − min(3, prestígio da seita ÷ 25)`.
Seitas prestigiadas recebem missões mais fáceis — é o único lugar do sistema em
que a reputação compra vantagem, e ela foi comprada com missões anteriores.

### Baixas

Falhar não é "não conseguiu". O risco define o que se perdeu:

| Risco | Baixas possíveis |
|---:|---|
| 1 | voltou de mãos vazias · perdeu o equipamento · −5 de estado mental |
| 2 | voltou ferido (2d6) · perdeu um companheiro externo · foi capturado e resgatado |
| 3 | voltou gravemente ferido (4d6) · um discípulo interno morreu · trouxe uma maldição |
| 4 | metade da equipe não voltou · o executor perdeu 1 nível · humilhação pública (−10 extra) |
| 5 | nenhum sobrevivente · o executor morreu · a missão despertou algo pior |

Em fracasso crítico, é sempre a última linha.

## 14.4 Prestígio

De −200 a +300. Efeitos:

| Prestígio | Efeito |
|---:|---|
| ≥ 200 | as nove grandes reconhecem; convites automáticos a Kunlun |
| 100–199 | respeitada; recrutar discípulos custa metade |
| 25–99 | estabelecida |
| 0–24 | desconhecida |
| −1 a −49 | malvista; mercadores cobram 25% a mais |
| −50 a −99 | caçada por outras seitas |
| ≤ −100 | marcada para extermínio |

## 14.5 O Torneio de Kunlun (崑崙大賽)

Uma vez por ano. As grandes seitas enviam discípulos. A seita campeã **ganha uma
Lei suprema** — é assim que as Taiyi circulam pelo mundo e é o motivo pelo qual
nenhuma seita domina para sempre.

Mecânica: chaveamento suíço sorteado pela mesma entropia auditada, sem repetição
de confronto enquanto houver adversário disponível. Cada luta é um teste oposto
de Duelo; vitória 3 pontos, derrota 1 (comparecer já vale alguma coisa).

```python
torneio_de_kunlun(ano, participantes, aleat, lei_em_disputa="TAIYI_METAL", diario=d)
```

Cada participante é um dicionário com `nome`, `seita`, `nivel`, `atributo`
(valor de Constituição) e `graduacao` (em Duelo). O resultado traz os
confrontos com os dois totais, o campeão, a seita campeã, a Lei conquistada e a
classificação final — tudo gravado no diário.

Consequências do torneio que a mesa deve aplicar:

* o campeão ganha a Lei em disputa e +20 de prestígio;
* quem mata um adversário "por acidente" registra `matou_um_aliado` com a seita
  da vítima **e** perde 15 de prestígio com todas as ortodoxas que presenciaram;
* os três primeiros viram NPCs notáveis do mundo (gere-os e guarde as fichas);
* a seita perdedora de um duelo público perde 2 de Face por membro presente.

## 14.6 Invasões do Templo Daemonia

Uma vez por década (ou quando a mesa decidir, antes da campanha), o Templo
Daemonia 天魔殿 abre e marcha. É o único evento de mundo que não é sorteado: é
anunciado.

Procedimento:

1. todas as facções demoníacas ganham +30 de prestígio e +1 nível de líder;
2. a relação `demoniaca × ortodoxa` cai 40 pontos;
3. cada seita ortodoxa recebe a missão `SELAR_REINO_SECRETO` obrigatória;
4. role 1d6 por província: 1–2 sofre invasão, 3–4 recebe refugiados, 5–6 nada;
5. as agendas dos NPCs demoníacos avançam 2 segmentos de uma vez.

## 14.7 Mestre e discípulo

* Um mestre pode ter `nível ÷ 2` discípulos internos.
* Discípulos aprendem as perícias e técnicas do mestre pela metade do custo.
* O mestre pode transferir Qi (perda de 20% na transferência) — é assim que um
  Ancião moribundo entrega cinquenta anos de cultivo a um discípulo.
* Trair o mestre registra `quebrou_um_juramento` (−7) **e** `matou_um_aliado`
  (−10) se houver violência, em todas as facções ortodoxas que souberem.

## 14.8 Ramificações

Uma seita com prestígio ≥ 100 pode fundar um ramo em outra província:

* custo: 20 000 pedras e um Chefe de Ramo (nível 6+);
* o ramo produz metade do que produziria a sede;
* o ramo tem relação automática +60 com a sede e herda os inimigos dela;
* se o ramo cair abaixo de −50 de prestígio, ele se declara independente — e
  vira uma facção nova na matriz, com relação −30 com a antiga sede.

```bash
./xan seita --nome "Seita do Monte Hua" --chines "華山派" --provincia Qingyun \
            --nivel-mestre 9 --pedras 80000 --comida 900 \
            --predios "PAVILHAO_MANUAIS,CAMPOS_ESPIRITUAIS,ARENA,CELEIRO,SALA_DE_ALQUIMIA" \
            --membros "Wang Mei:7,Li Fan:5,Zhang Wei:3" \
            --mes --densidade veia_espiritual \
            --missao EXPLORAR_RUINA --executor "Wang Mei" --valor 15 --graduacao 4
```
