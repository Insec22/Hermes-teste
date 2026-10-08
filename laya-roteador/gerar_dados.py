"""Gera o conjunto de treino sintético para o roteador de modelos.

Cada exemplo é um pedido (em português ou inglês) rotulado com o modelo que deveria
atendê-lo: haiku (tarefas simples), sonnet (código e tarefas intermediárias) ou opus
(raciocínio complexo). Os pedidos são montados a partir de modelos de frase com partes
intercambiáveis; o conjunto de teste (teste.jsonl) é escrito à mão e não usa estes modelos,
para medir se o roteador generaliza.

Uso: python gerar_dados.py  -> escreve dados/treino.jsonl
"""
import json
import os
import random

from perguntas import QUESTIONS

random.seed(7)

# Cada entrada: (rótulo, idioma, modelo de frase, {campo: opções})
TEMPLATES = [
    # ---------------------------------------------------------------- haiku
    ("haiku", "pt", "Qual é a capital {pais}?", {"pais": ["da Alemanha", "do Japão", "da Argentina", "do Canadá", "da Austrália", "do Egito", "da Noruega", "do Chile"]}),
    ("haiku", "en", "What's the capital of {pais}?", {"pais": ["Germany", "Japan", "Argentina", "Canada", "Australia", "Egypt", "Norway", "Chile"]}),
    ("haiku", "pt", "Traduza para o {lingua}: \"{frase}\"", {"lingua": ["inglês", "espanhol", "francês", "italiano"], "frase": ["bom dia, tudo bem?", "onde fica a estação?", "obrigado pela ajuda", "a reunião foi adiada", "preciso de um café"]}),
    ("haiku", "en", "Translate to {lingua}: \"{frase}\"", {"lingua": ["Portuguese", "Spanish", "French", "German"], "frase": ["good morning", "where is the train station?", "thanks for your help", "the meeting was moved", "I need a coffee"]}),
    ("haiku", "pt", "Quanto é {a} vezes {b}?", {"a": ["12", "7", "25", "13", "48"], "b": ["8", "9", "4", "11", "3"]}),
    ("haiku", "en", "Convert {valor} to {unidade}.", {"valor": ["5 miles", "100 Fahrenheit", "3 pounds", "2 gallons", "10 inches"], "unidade": ["the metric system", "metric units"]}),
    ("haiku", "pt", "Converta {valor} para {unidade}.", {"valor": ["5 milhas", "100 graus Fahrenheit", "3 libras", "10 polegadas"], "unidade": ["o sistema métrico", "unidades métricas"]}),
    ("haiku", "pt", "{saud}", {"saud": ["Oi, tudo bem?", "Bom dia!", "Olá, como você está?", "Valeu, obrigado!", "Boa noite", "E aí?"]}),
    ("haiku", "en", "{saud}", {"saud": ["Hi there!", "Good morning!", "Thanks a lot!", "Hey, how are you?", "Hello", "Good night"]}),
    ("haiku", "pt", "Corrija a ortografia desta frase: \"{frase}\"", {"frase": ["eu nao sabia que ele hia vir", "agente vai viajar amanha", "faltou muitas pessoas na reuniao", "porisso eu sai mais sedo"]}),
    ("haiku", "en", "Fix the spelling: \"{frase}\"", {"frase": ["I recieved you're mesage", "their going to the libary", "definately tommorow", "we should of went earlier"]}),
    ("haiku", "pt", "Qual é um sinônimo de \"{p}\"?", {"p": ["feliz", "rápido", "difícil", "bonito", "importante", "grande"]}),
    ("haiku", "en", "Give me a synonym for \"{p}\".", {"p": ["happy", "fast", "difficult", "beautiful", "important", "big"]}),
    ("haiku", "pt", "Formate esta lista em ordem alfabética: {lista}", {"lista": ["banana, maçã, uva, abacaxi", "Pedro, Ana, Carlos, Bia", "zebra, gato, cão, arara"]}),
    ("haiku", "en", "Sort alphabetically: {lista}", {"lista": ["banana, apple, grape, kiwi", "Peter, Anna, Carl, Beth", "zebra, cat, dog, owl"]}),
    ("haiku", "pt", "Em que ano {evento}?", {"evento": ["o homem pisou na Lua", "começou a Segunda Guerra Mundial", "o Brasil ganhou a primeira Copa", "caiu o Muro de Berlim"]}),
    ("haiku", "en", "What year did {evento}?", {"evento": ["humans land on the Moon", "World War II start", "the Berlin Wall fall", "the Titanic sink"]}),
    ("haiku", "pt", "Quantos {x} tem {y}?", {"x": ["dias", "horas", "minutos"], "y": ["uma semana", "um ano bissexto", "um dia"]}),
    ("haiku", "en", "What does the acronym {s} stand for?", {"s": ["NASA", "HTML", "CPU", "UNESCO", "PDF"]}),
    ("haiku", "pt", "O que significa a sigla {s}?", {"s": ["CPF", "SUS", "HTML", "ONU", "PIB"]}),
    ("haiku", "pt", "Deixe esta frase mais formal: \"{frase}\"", {"frase": ["manda o arquivo aí", "não vou poder ir não", "valeu pela força", "bora marcar outro dia"]}),
    ("haiku", "en", "Make this more polite: \"{frase}\"", {"frase": ["send me the file", "I can't come", "fix this now", "you're late again"]}),
    # --------------------------------------------------------------- sonnet
    ("sonnet", "pt", "Corrija o erro {erro} no meu código {lang}: {ctx}", {"erro": ["TypeError", "NullPointerException", "IndexError", "KeyError", "segmentation fault"], "lang": ["Python", "Java", "JavaScript", "C"], "ctx": ["acontece quando a lista vem vazia", "segue o stack trace abaixo", "só ocorre em produção", "aparece depois do último deploy"]}),
    ("sonnet", "en", "Fix the {erro} in my {lang} code, {ctx}", {"erro": ["TypeError", "NullPointerException", "IndexError", "KeyError", "race condition"], "lang": ["Python", "Java", "TypeScript", "Go"], "ctx": ["it happens when the list is empty", "stack trace below", "only in production", "since the last deploy"]}),
    ("sonnet", "pt", "Escreva uma função em {lang} que {tarefa}.", {"lang": ["Python", "JavaScript", "Go", "Rust", "Java"], "tarefa": ["valide um CPF", "leia um CSV e some uma coluna", "remova duplicatas de uma lista mantendo a ordem", "faça paginação de resultados de uma API", "converta datas entre fusos horários"]}),
    ("sonnet", "en", "Write a {lang} function that {tarefa}.", {"lang": ["Python", "JavaScript", "Go", "Rust", "C#"], "tarefa": ["validates an email address", "parses a CSV and sums a column", "deduplicates a list preserving order", "retries an HTTP call with backoff", "converts timestamps between time zones"]}),
    ("sonnet", "pt", "Refatore esta classe {lang} para {obj}.", {"lang": ["Python", "Java", "TypeScript"], "obj": ["ficar mais legível", "usar injeção de dependência", "remover código duplicado", "separar as responsabilidades"]}),
    ("sonnet", "en", "Refactor this {lang} module to {obj}.", {"lang": ["Python", "Java", "TypeScript"], "obj": ["be more readable", "use dependency injection", "remove duplication", "split responsibilities"]}),
    ("sonnet", "pt", "Escreva testes unitários para {alvo}.", {"alvo": ["esta função de cálculo de frete", "o endpoint de login", "o serviço de pagamentos", "este parser de JSON"]}),
    ("sonnet", "en", "Write unit tests for {alvo}.", {"alvo": ["this shipping cost function", "the login endpoint", "the payment service", "this JSON parser"]}),
    ("sonnet", "pt", "Crie uma consulta SQL que {q}.", {"q": ["traga os 10 clientes que mais compraram no mês", "calcule a média de vendas por região", "encontre pedidos sem pagamento", "junte as tabelas de usuários e pedidos"]}),
    ("sonnet", "en", "Write a SQL query that {q}.", {"q": ["returns the top 10 customers by revenue this month", "computes average sales per region", "finds orders without a payment", "joins users and orders"]}),
    ("sonnet", "pt", "Resuma este {doc} em {n} tópicos.", {"doc": ["relatório trimestral", "artigo técnico", "contrato de prestação de serviços", "ata de reunião"], "n": ["5", "três", "dez"]}),
    ("sonnet", "en", "Summarize this {doc} in {n} bullet points.", {"doc": ["quarterly report", "technical article", "service contract", "meeting transcript"], "n": ["5", "three", "ten"]}),
    ("sonnet", "pt", "Escreva um e-mail para {dest} explicando {assunto}.", {"dest": ["o cliente", "minha equipe", "o fornecedor", "o diretor"], "assunto": ["o atraso na entrega", "a mudança de escopo do projeto", "o novo processo de reembolso", "o resultado do trimestre"]}),
    ("sonnet", "en", "Draft an email to {dest} explaining {assunto}.", {"dest": ["the client", "my team", "the vendor", "our director"], "assunto": ["the delivery delay", "the scope change", "the new reimbursement process", "last quarter's results"]}),
    ("sonnet", "pt", "Configure um {ci} que {faz}.", {"ci": ["workflow do GitHub Actions", "pipeline do GitLab CI", "Dockerfile"], "faz": ["rode os testes a cada push", "faça build e publique a imagem", "rode o lint antes do merge"]}),
    ("sonnet", "en", "Set up a {ci} that {faz}.", {"ci": ["GitHub Actions workflow", "GitLab CI pipeline", "Dockerfile"], "faz": ["runs tests on every push", "builds and pushes the image", "lints before merge"]}),
    ("sonnet", "pt", "Explique o que este trecho de código {lang} faz, linha por linha.", {"lang": ["Python", "JavaScript", "Bash", "SQL"]}),
    ("sonnet", "en", "Explain what this {lang} snippet does, line by line.", {"lang": ["Python", "JavaScript", "Bash", "SQL"]}),
    ("sonnet", "pt", "Crie um componente React que {c}.", {"c": ["mostre uma tabela com filtro", "seja um formulário de cadastro com validação", "exiba um gráfico de vendas"]}),
    ("sonnet", "en", "Build a React component that {c}.", {"c": ["shows a filterable table", "is a signup form with validation", "renders a sales chart"]}),
    # ----------------------------------------------------------------- opus
    ("opus", "pt", "Projete a arquitetura de {sis}, considerando {req}.", {"sis": ["um sistema de pagamentos para milhões de usuários", "uma plataforma de streaming de vídeo", "um marketplace multi-tenant", "um sistema bancário distribuído"], "req": ["alta disponibilidade e failover entre regiões", "consistência forte e auditoria", "escalabilidade horizontal e custos", "segurança e conformidade com a LGPD"]}),
    ("opus", "en", "Design the architecture for {sis}, accounting for {req}.", {"sis": ["a payments system for millions of users", "a video streaming platform", "a multi-tenant marketplace", "a distributed banking ledger"], "req": ["multi-region failover", "strong consistency and auditability", "horizontal scalability and cost", "security and GDPR compliance"]}),
    ("opus", "pt", "Prove {teo}.", {"teo": ["que existem infinitos números primos", "que a raiz de 2 é irracional", "o teorema do valor médio a partir do teorema de Rolle", "que todo grafo planar é 5-colorível", "a corretude do algoritmo de Dijkstra"]}),
    ("opus", "en", "Prove {teo}.", {"teo": ["that there are infinitely many primes", "that sqrt(2) is irrational", "the mean value theorem from Rolle's theorem", "that every planar graph is 5-colorable", "the correctness of Dijkstra's algorithm"]}),
    ("opus", "pt", "Compare criticamente {a} e {b} para {uso}, com prós, contras e uma recomendação fundamentada.", {"a": ["microsserviços", "Kafka", "PostgreSQL", "Kubernetes"], "b": ["um monólito modular", "RabbitMQ", "Cassandra", "serverless"], "uso": ["uma fintech em crescimento", "um sistema de IoT com milhões de eventos", "uma startup com equipe pequena"]}),
    ("opus", "en", "Critically compare {a} and {b} for {uso}, with trade-offs and a justified recommendation.", {"a": ["microservices", "Kafka", "PostgreSQL", "Kubernetes"], "b": ["a modular monolith", "RabbitMQ", "Cassandra", "serverless"], "uso": ["a growing fintech", "an IoT system with millions of events", "a startup with a small team"]}),
    ("opus", "pt", "Investigue por que {prob} e proponha uma solução, considerando todas as hipóteses.", {"prob": ["nosso sistema distribuído perde mensagens sob carga alta", "a latência p99 triplicou sem mudança de código", "há um deadlock intermitente entre três serviços", "o modelo de ML piorou em produção mas não no teste"]}),
    ("opus", "en", "Investigate why {prob} and propose a fix, considering every hypothesis.", {"prob": ["our distributed system drops messages under load", "p99 latency tripled with no code change", "there's an intermittent deadlock across three services", "our ML model degrades in production but not in testing"]}),
    ("opus", "pt", "Escreva uma revisão de literatura sobre {tema}, comparando as principais abordagens e lacunas em aberto.", {"tema": ["aprendizado por reforço com feedback humano", "computação quântica tolerante a falhas", "modelos de linguagem para descoberta de fármacos", "consenso em sistemas distribuídos"]}),
    ("opus", "en", "Write a literature review on {tema}, comparing major approaches and open gaps.", {"tema": ["reinforcement learning from human feedback", "fault-tolerant quantum computing", "language models for drug discovery", "consensus in distributed systems"]}),
    ("opus", "pt", "Elabore uma estratégia de {estr} para os próximos {n} anos, com riscos, cenários e métricas.", {"estr": ["expansão internacional", "migração da infraestrutura para a nuvem", "adoção de IA na empresa", "entrada em um novo mercado"], "n": ["3", "5"]}),
    ("opus", "en", "Develop a {n}-year {estr} strategy with risks, scenarios and metrics.", {"estr": ["international expansion", "cloud migration", "company-wide AI adoption", "new market entry"], "n": ["3", "5"]}),
    ("opus", "pt", "Desenvolva um algoritmo {alg} e analise sua complexidade e casos-limite.", {"alg": ["de escalonamento ótimo para tarefas com dependências e prazos", "para detectar fraude em grafos de transações em tempo real", "de roteamento de veículos com janelas de tempo"]}),
    ("opus", "en", "Devise an algorithm {alg} and analyze its complexity and edge cases.", {"alg": ["for optimal scheduling of tasks with dependencies and deadlines", "to detect fraud rings in transaction graphs in real time", "for vehicle routing with time windows"]}),
    ("opus", "pt", "Faça uma análise de segurança completa de {alvo}, modelando ameaças e priorizando mitigações.", {"alvo": ["nossa arquitetura de autenticação com OAuth e SSO", "um protocolo de votação eletrônica", "nossa cadeia de suprimentos de software"]}),
    ("opus", "en", "Do a full security analysis of {alvo}, with threat modeling and prioritized mitigations.", {"alvo": ["our OAuth and SSO architecture", "an electronic voting protocol", "our software supply chain"]}),
]


def expand(tpl, slots, n):
    out = set()
    keys = list(slots)
    tries = 0
    while len(out) < n and tries < n * 20:
        tries += 1
        out.add(tpl.format(**{k: random.choice(slots[k]) for k in keys}))
    return list(out)


def main():
    rows = []
    for label, _, tpl, slots in TEMPLATES:
        for text in expand(tpl, slots, 20):
            rows.append({"state": text, "questions": QUESTIONS, "expected": {"modelo": label}})
    random.shuffle(rows)
    os.makedirs("dados", exist_ok=True)
    with open("dados/treino.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    counts = {}
    for r in rows:
        counts[r["expected"]["modelo"]] = counts.get(r["expected"]["modelo"], 0) + 1
    print(len(rows), "exemplos", counts)


if __name__ == "__main__":
    main()
