"""Mede a precisão de um checkpoint do Laya no conjunto de teste.

Uso: USE_TF=0 python avaliar.py <checkpoint> [dados/teste.jsonl]
"""
import json
import sys
from collections import Counter

import laya


def main():
    ckpt = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) > 2 else "dados/teste.jsonl"
    rows = [json.loads(line) for line in open(path, encoding="utf-8")]
    agent = laya.load(ckpt)
    hits, conf = 0, Counter()
    for r in rows:
        pred = agent.predict(r["state"], r["questions"])["answers"]["modelo"]["choice"]
        gold = r["expected"]["modelo"]
        hits += pred == gold
        conf[(gold, pred)] += 1
    print(f"{ckpt}: precisão {hits}/{len(rows)} = {hits / len(rows):.1%}")
    labels = ["haiku", "sonnet", "opus"]
    print("certo \\ previsto  " + "  ".join(f"{l:>6}" for l in labels))
    for g in labels:
        print(f"{g:>16}  " + "  ".join(f"{conf[(g, p)]:>6}" for p in labels))


if __name__ == "__main__":
    main()
