# Certificado de Justiça — Motor de Aleatoriedade XAN

- **Motor:** 1.0.0
- **Fonte de acaso:** `FonteViva(os.urandom + HMAC-DRBG SHA-256, reseed a cada 1024)`
- **Amostras totais:** 3.527.846
- **α por teste:** 0.001
- **VEREDITO:** **APROVADO**

40 testes. 3.527.846 amostras. 40 aprovados. 0 abaixo de α=0.001. 0 falhas duras (p<1e-06).

| Família | Teste | Amostras | Estatística | p-valor | Veredito |
|---|---|---:|---:|---:|:--:|
| A | d4 uniforme | 15.000 | 2.2992 | 0.5127 | ✅ |
| A | d6 uniforme | 15.000 | 7.9928 | 0.1566 | ✅ |
| A | d8 uniforme | 15.000 | 7.9904 | 0.3334 | ✅ |
| A | d10 uniforme | 15.000 | 14.9453 | 0.09245 | ✅ |
| A | d12 uniforme | 15.000 | 4.7920 | 0.9408 | ✅ |
| A | d20 uniforme | 15.000 | 19.9813 | 0.3957 | ✅ |
| A | d100 uniforme | 15.000 | 133.3867 | 0.01212 | ✅ |
| B | abaixo(3) | 15.000 | 1.7452 | 0.4179 | ✅ |
| B | abaixo(5) | 15.000 | 4.6900 | 0.3206 | ✅ |
| B | abaixo(6) | 15.000 | 7.8544 | 0.1644 | ✅ |
| B | abaixo(7) | 15.000 | 6.5095 | 0.3686 | ✅ |
| B | abaixo(13) | 15.000 | 5.4597 | 0.9408 | ✅ |
| B | abaixo(20) | 15.000 | 15.8293 | 0.6686 | ✅ |
| B | abaixo(100) | 15.000 | 97.1600 | 0.5335 | ✅ |
| C | total de 1d20 | 15.000 | 21.6080 | 0.3042 | ✅ |
| C | total de 2d6 | 15.000 | 19.9393 | 0.02983 | ✅ |
| C | total de 3d6 | 15.000 | 14.1483 | 0.5143 | ✅ |
| C | total de 4d6kh1 | 15.000 | 9.0227 | 0.1082 | ✅ |
| C | total de 2d20kh1 | 15.000 | 15.1912 | 0.7104 | ✅ |
| C | total de 1d20+5 | 15.000 | 21.5093 | 0.3094 | ✅ |
| C | total de 3dF | 15.000 | 4.2506 | 0.6428 | ✅ |
| D | média/variância de 1d20 | 40.000 | -1.5929 | 0.1112 | ✅ |
| D | média/variância de 2d6 | 40.000 | -0.2588 | 0.7958 | ✅ |
| D | média/variância de 4d6kh1 | 40.000 | 1.4416 | 0.1494 | ✅ |
| D | média/variância de 2d20kh1 | 40.000 | -0.1284 | 0.8978 | ✅ |
| E | KS uniforme [0.1) | 15.000 | 0.0065 | 0.555 | ✅ |
| F | autocorrelação lag-1 | 15.000 | 0.0095 | 0.2453 | ✅ |
| G | corridas acima/abaixo da mediana | 15.000 | -1.7310 | 0.08345 | ✅ |
| H | monobit | 960.000 | 0.6757 | 0.4993 | ✅ |
| H | pôquer-4 | 960.000 | 22.0845 | 0.1056 | ✅ |
| H | maior corrida de uns (M=128) | 960.000 | 12.4583 | 0.4905 | ✅ |
| I | pares consecutivos d6 | 15.000 | 33.6336 | 0.534 | ✅ |
| J | kh/kl imparcial em 4d6kh1 | 15.000 | 4.8725 | 0.4316 | ✅ |
| K | ponderado [1. 2. 3. 4. 5] | 15.000 | 11.1678 | 0.02474 | ✅ |
| K | ponderado [7. 1] | 15.000 | 0.1560 | 0.6928 | ✅ |
| L | Fisher-Yates 4 cartas | 3.750 | 20.4576 | 0.2233 | ✅ |
| M | rejeição ativa para abaixo(7) | 15.000 | -0.2396 | 0.8106 | ✅ |
| M | rejeição ativa para abaixo(100) | 15.000 | 1.1047 | 0.2693 | ✅ |
| N | determinismo e separação por semente | 4.096 | 1.0000 | 1 | ✅ |
| O | atores distintos. mesma taxa | 30.000 | 3.8252 | 0.5748 | ✅ |

## O que cada família garante

- **A/B** — nenhuma face é favorecida; amostragem sem viés de módulo.
- **C/D** — o total da expressão segue EXATAMENTE a distribuição teórica.
- **E/F/G** — a sequência não tem padrão, tendência ou memória.
- **H** — os bits brutos passam nos testes clássicos do NIST SP 800-22.
- **I** — chamadas consecutivas são independentes entre si.
- **J** — `kh`/`kl` não espiam nem filtram: mantidas e descartadas são ambas uniformes.
- **K/L** — sorteio ponderado e embaralhamento são exatos.
- **M** — a rejeição está realmente ativa (prova construtiva contra `% n`).
- **N** — semente reproduz o mundo bit a bit (auditabilidade).
- **O** — **nenhum ator tem vantagem**: rótulos diferentes produzem a mesma taxa de sucesso.
