"""Gera o conjunto de treino v2 (dados/treino_v2.jsonl): treino.jsonl + exemplos de reforço.

Os exemplos de reforço são escritos à mão e miram os pontos fracos do teste ampliado:
opus curto, informal e "enganoso" (parece simples mas exige rigor), e a fronteira
sonnet x opus (pares parecidos em que só a profundidade muda).

Nenhum deles aparece em teste.jsonl ou teste_extra.jsonl; o script confere isso.
Uso: python gerar_reforco.py
"""
import json
import random

from perguntas import QUESTIONS

OPUS = [
    # curto
    "prove que existem infinitos primos da forma 4k+3",
    "Prove the Cauchy-Schwarz inequality",
    "demonstre que e é irracional",
    "prove Hall's marriage theorem",
    "Design a distributed message queue",
    "projete um banco de dados distribuído",
    "design a CDN from scratch",
    "Arquitetura de um sistema bancário",
    "Estratégia de entrada no mercado chinês",
    "design a search engine",
    "prove the master theorem",
    "Demonstre o teorema de Pitágoras de três formas",
    "Analyze the Byzantine generals problem",
    "Formal proof: bubble sort is correct",
    "Verifique formalmente esse algoritmo de consenso",
    "Plano de 3 anos pra nossa área de dados",
    "Teoria dos jogos aplicada ao nosso leilão de anúncios",
    "Why do LLMs hallucinate? Deep analysis",
    "Por que a inflação persiste? Análise rigorosa",
    "Root cause our data loss incident",
    "Prove min-cut max-flow",
    "Projete um compilador JIT",
    "design an OS scheduler for real-time tasks",
    "Avalie a tese do nosso fundo de investimento",
    # informal
    "mano me ajuda a montar toda a arquitetura do app de delivery, do zero, pensando em escala",
    "yo we need a full plan to migrate 200 services off our datacenter, think it all through",
    "preciso entender pq nosso modelo de churn piorou do nada, investiga tudo comigo",
    "bro prove that the harmonic series diverges but like properly",
    "faz uma analise seria se vale abrir filial em portugal, custos riscos tudo",
    "how do i design a multiplayer game server for 1M concurrent players, go deep",
    "me explica a demonstração do teorema central do limite direitinho",
    "our k8s cluster randomly loses pods at night, walk me thru every possible cause",
    "quero uma estrategia completa pra reduzir 30% do custo de cloud sem perder performance",
    "need u to poke holes in my startup's business model and stress test it",
    "pensa comigo num algoritmo pra otimizar rota de 500 entregadores em tempo real",
    "can u analyze if our pricing model is actually optimal, theres a lot of data",
    "qual seria a arquitetura ideal pra um sistema de votação online seguro? pensa em tudo",
    "lol our db replication is broken in weird ways, need a real investigation",
    "faz um threat model completo do nosso app, com tudo q pode dar errado",
    "explain why quantum computers break RSA, with the actual math",
    # enganoso
    "Quanto é 1+1? Quero a prova formal a partir dos axiomas de Peano",
    "Why is the sky dark at night? Explain Olbers' paradox and its resolution rigorously",
    "Is 91 prime? Then generalize: prove a fast primality test is correct",
    "Me conta uma curiosidade sobre buracos negros — com a derivação do raio de Schwarzschild",
    "Escreve um haicai — e depois analise formalmente a métrica e a tradição do gênero em três línguas",
    "Quick question: is our encryption scheme IND-CCA2 secure? Here's the construction",
    "Resume esse livro de 600 páginas de economia e critique os argumentos centrais",
    "What's the best database? Give a rigorous, evidence-based analysis across workloads",
    "Como faço um bolo? Brincadeira — modele a transferência de calor no forno e otimize o tempo",
    "Fix this race condition: it only happens across 3 data centers under partition",
    "Check my proof that sqrt(2) is irrational and find every gap",
    "Which is faster, quicksort or mergesort? Prove under which input distributions each wins",
    "Me ajuda a escolher entre dois imóveis considerando financiamento, valorização, impostos e risco",
    "Revisa esse acordo de acionistas e aponta todos os riscos para o minoritário",
    "Explain this one line of code — it's the core of a lock-free hash map, prove it's linearizable",
    "Traduza esse soneto de Camões para o inglês mantendo decassílabos e rimas, justificando as escolhas",
    "Should I learn Rust? Analyze rigorously for a team building safety-critical firmware",
    "Qual o melhor time de futebol? Construa um modelo estatístico rigoroso e defenda as premissas",
]

SONNET = [
    # pares de contraste com opus: mesma área, profundidade menor
    "Escreve a prova de que a soma de dois números pares é par, simples, pra uma aula",
    "Explain the halting problem in simple terms with an example",
    "Faz um diagrama em texto da arquitetura atual que eu te descrevi",
    "Write a Python implementation of Dijkstra's algorithm",
    "Implementa uma fila de mensagens simples em Redis",
    "Write a simple CDN config for Cloudflare caching static assets",
    "Monta o schema SQL de um sistema bancário simples com contas e transações",
    "Escreve um script que calcula a inflação acumulada a partir de uma planilha",
    "Write a basic multiplayer chat server with websockets",
    "Implementa o algoritmo de Kruskal em Java",
    "Configure Kubernetes liveness and readiness probes for this service",
    "Escreve uma função que testa se um número é primo",
    "Write a script to check replication lag on our Postgres replicas",
    "Implementa criptografia AES em Python com a biblioteca cryptography",
    "Explica o teorema central do limite com um exemplo em Python",
    "Monta uma planilha comparando os custos de dois imóveis",
    # enganoso/curto/informal de sonnet
    "faz um crud em fastapi",
    "query pra top 5 produtos",
    "write a makefile for this project",
    "arruma esse yaml do github actions",
    "why is my python venv not activating on windows",
    "faz um scraper de noticias q salva em csv",
    "converte esse componente pra typescript",
    "add logging to this script pls",
    "como eu faço deploy desse app flask no render?",
    "my jest test times out, here's the code",
    "deixa esse código mais pythonico",
    "write a regex to extract dates from text",
    "escreve uma descrição de vaga para dev backend pleno",
    "Turn this long Slack thread into a short status update",
    "Faz um resumo executivo desse relatório de vendas",
    "Write a short blog post introducing our new API feature",
]

HAIKU = [
    "qual o nome do maior rio do mundo?",
    "What's the capital of Kenya?",
    "how many weeks in a year",
    "tradução de 'janela' em francês",
    "Who discovered gravity?",
    "qnto é 15% de 200",
    "Spell 'rhythm'",
    "o que significa CPU",
    "What does URL stand for?",
    "qual o simbolo quimico do ferro",
    "Who invented the telephone?",
    "bom diaaa",
    "is python case sensitive?",
    "quantos ms tem 1 segundo",
    "What's the opposite of 'ancient'?",
    "em q ano acabou a 2a guerra",
]


def main():
    test_states = set()
    for path in ("dados/teste.jsonl", "dados/teste_extra.jsonl"):
        test_states |= {json.loads(l)["state"] for l in open(path, encoding="utf-8")}
    novos = [(t, "opus") for t in OPUS] + [(t, "sonnet") for t in SONNET] + [(t, "haiku") for t in HAIKU]
    vazados = [t for t, _ in novos if t in test_states]
    assert not vazados, "exemplos de reforço vazaram para o teste: %r" % vazados

    base = [json.loads(l) for l in open("dados/treino.jsonl", encoding="utf-8")]
    reforco = [{"state": t, "questions": QUESTIONS, "expected": {"modelo": lab}} for t, lab in novos]
    # Repete o reforço 2x para pesar mais que os modelos de frase.
    rows = base + reforco * 2
    random.Random(11).shuffle(rows)
    with open("dados/treino_v2.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(reforco), "exemplos de reforço;", len(rows), "linhas em treino_v2.jsonl")


if __name__ == "__main__":
    main()
