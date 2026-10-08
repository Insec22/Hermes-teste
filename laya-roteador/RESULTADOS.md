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

## Treino v2: com exemplos de reforço

`gerar_reforco.py` acrescenta 106 pedidos escritos à mão (opus curto, informal e enganoso; pares
sonnet x opus da mesma área), repetidos 2x, ao treino original → `dados/treino_v2.jsonl` (713 linhas).
Mesmo comando de treino, trocando `--data dados/treino_v2.jsonl`.

| checkpoint | teste (150) | teste ampliado (200) |
|---|---|---|
| `laya-multilingual` sem ajuste | 70,0% | 62,0% |
| ajustado v1 | 90,7% | 85,5% |
| **ajustado v2** | **94,7%** | **95,0%** |

Acerto do v2 por categoria no teste ampliado:

| | comum | curto | longo | enganoso | informal |
|---|---|---|---|---|---|
| haiku | 100% | 100% | 100% | 100% | 90% |
| sonnet | 100% | 80% | 100% | **62%** | 100% |
| opus | 100% | 100% | 100% | 93% | 100% |

- `opus` foi de 71% para 99% (69/70) no teste ampliado.
- **Efeito colateral**: parte do erro migrou para `sonnet enganoso`. Pedidos de nível intermediário
  com palavras de "complexidade" ("Projete o esquema de banco de um blog", "explique a complexidade
  desse algoritmo") agora vão para `opus`; pedidos curtos de código ("regex pra validar email")
  vão para `haiku`.
- **Ressalva**: os exemplos de reforço foram escritos depois de ver os erros no teste ampliado,
  mirando as mesmas categorias. Mesmo sem nenhuma frase repetida, isso deixa o teste ampliado
  menos independente; a melhora no teste original (90,7% → 94,7%) é a evidência mais limpa.
  Para medir de verdade, falta um terceiro conjunto, nunca usado para decidir nada.

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
