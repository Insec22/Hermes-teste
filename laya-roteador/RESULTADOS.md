# Piloto: ajuste fino do Laya como roteador de modelos

Objetivo: o Laya escolher qual modelo atende um pedido (`haiku`, `sonnet` ou `opus`).

## Dados

- `dados/treino.jsonl`: 501 pedidos gerados por `gerar_dados.py` a partir de modelos de frase
  (português e inglês). 451 usados no treino e 50 na calibração.
- `dados/teste.jsonl`: 150 pedidos escritos à mão por `gerar_teste.py` (50 por classe), com
  redação e assuntos diferentes dos de treino, para medir generalização.

Os rótulos foram definidos pelo Claude, não por uso real; revisar uma amostra antes de confiar neles.

## Treino

```bash
USE_TF=0 laya-train --data dados/treino.jsonl --eval dados/teste.jsonl \
  --base convaiinnovations/laya-multilingual --out ./ckpt-multi \
  --loss soft-ce --epochs 4 --micro-batch 8 --grad-accum 2 --shuffle-options --device cpu
```

Rodou só em CPU (4 núcleos), dentro do container.

## Resultado no conjunto de teste (150 pedidos)

| checkpoint | precisão |
|---|---|
| `laya-multilingual` sem ajuste | 70,0% |
| `laya` (inglês) sem ajuste | 84,7% |
| **`laya-multilingual` ajustado** | **90,7%** |

Matriz de confusão do ajustado (linha = certo, coluna = previsto):

| | haiku | sonnet | opus |
|---|---|---|---|
| haiku | 48 | 2 | 0 |
| sonnet | 2 | 48 | 0 |
| opus | 3 | 7 | 40 |

## Teste ampliado (200 pedidos, `dados/teste_extra.jsonl`)

Gerado por `gerar_teste_extra.py`, escrito à mão e etiquetado por categoria: `comum`, `curto`,
`longo`, `enganoso` (parece de outra classe) e `informal` (gíria, erros de digitação).

| checkpoint | precisão |
|---|---|
| `laya-multilingual` sem ajuste | 62,0% |
| `laya` (inglês) sem ajuste | 76,5% |
| **`laya-multilingual` ajustado** | **85,5%** |

Acerto do ajustado por categoria:

| | comum | curto | longo | enganoso | informal |
|---|---|---|---|---|---|
| haiku | 100% | 100% | 100% | 94% | 90% |
| sonnet | 95% | 90% | 100% | 69% | 100% |
| opus | 85% | 69% | 100% | **43%** | 60% |

O ponto fraco continua sendo `opus` que não "parece" complexo: pedidos curtos, informais ou que
soam simples mas exigem rigor ("Por que o céu é azul? Quero a derivação completa"). 15 dos 20
erros em `opus` foram para `sonnet`.

## Limitações observadas

- **Erros concentrados em `opus`**: pedidos complexos com redação diferente dos modelos de frase
  (ex.: "Projete do zero um compilador...") foram para `sonnet`; alguns ("prove que o problema da
  parada é indecidível") foram para `haiku`, provavelmente por serem curtos.
- **Confiança não calibrada**: o modelo acertou 100% dos itens de calibração (vindos do mesmo
  gerador), então a temperatura ficou em 1,0. Vários erros saíram com confiança 0,95–1,0, de modo
  que um limiar de confiança ainda não serve para detectar quando escalar para o `opus`.
- O treino zerou a perda já na 3ª época: sinal de que os dados sintéticos são fáceis demais.

## Próximos passos sugeridos

1. Dados mais variados e realistas, com mais pedidos difíceis de `opus` curtos e de `sonnet` longos.
2. Calibrar com dados separados e reais (não vindos do gerador).
3. Testar o ajuste fino também no `laya` em inglês, que já parte de 84,7%.
4. Coletar rótulos reais do uso (qual modelo de fato resolveu o pedido).
