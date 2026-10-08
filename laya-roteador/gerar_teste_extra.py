"""Gera um conjunto de teste ampliado e escrito à mão (dados/teste_extra.jsonl).

Cada pedido traz uma etiqueta de categoria, para ver onde o roteador erra:
- comum: casos típicos de cada classe
- curto: pedidos curtos (o maior ponto fraco do piloto em opus)
- longo: pedidos longos e com contexto
- enganoso: pedidos que parecem de outra classe (haiku com termos técnicos, opus sem jargão)
- informal: gírias, erros de digitação, sem pontuação

Nenhum pedido vem dos modelos de frase de gerar_dados.py.
Uso: python gerar_teste_extra.py
"""
import json
import os

from perguntas import QUESTIONS

# (rótulo, categoria, texto)
CASOS = [
    # ============================================================== HAIKU
    # comum
    ("haiku", "comum", "Qual é a capital da Islândia?"),
    ("haiku", "comum", "How many ounces are in a pound?"),
    ("haiku", "comum", "Quem pintou o Abaporu?"),
    ("haiku", "comum", "What's the past tense of 'swim'?"),
    ("haiku", "comum", "Qual a fórmula química da água?"),
    ("haiku", "comum", "Translate 'I love you' into Japanese"),
    ("haiku", "comum", "Quantos lados tem um hexágono?"),
    ("haiku", "comum", "When is Brazil's Independence Day?"),
    ("haiku", "comum", "Qual é o antônimo de 'ascender'?"),
    ("haiku", "comum", "What is 7 squared?"),
    ("haiku", "comum", "Em que continente fica o Marrocos?"),
    ("haiku", "comum", "Who wrote Romeo and Juliet?"),
    ("haiku", "comum", "Coloque essas palavras em ordem alfabética: sol, lua, mar, céu"),
    ("haiku", "comum", "How do you say 'thank you' in Korean?"),
    ("haiku", "comum", "Qual a velocidade da luz aproximadamente?"),
    ("haiku", "comum", "What's the currency of Switzerland?"),
    ("haiku", "comum", "Quantos minutos tem uma hora e meia?"),
    ("haiku", "comum", "Name the three primary colors"),
    ("haiku", "comum", "Qual é o maior oceano do mundo?"),
    ("haiku", "comum", "What's 20% of 250?"),
    # curto
    ("haiku", "curto", "oi"),
    ("haiku", "curto", "valeu!"),
    ("haiku", "curto", "thanks"),
    ("haiku", "curto", "2+2?"),
    ("haiku", "curto", "capital do Peru?"),
    ("haiku", "curto", "plural de 'pão'"),
    ("haiku", "curto", "sinônimo de 'alegre'"),
    ("haiku", "curto", "hello!"),
    ("haiku", "curto", "pi com 3 casas"),
    ("haiku", "curto", "'gato' em inglês"),
    # longo
    ("haiku", "longo", "Oi, tudo bem? Estou escrevendo um cartão de aniversário para a minha avó e queria só confirmar uma coisa bem rápida: o certo é 'parabéns pelo seu aniversário' ou 'parabéns por seu aniversário'? Obrigado!"),
    ("haiku", "longo", "Hey! My kid asked me at dinner and I honestly blanked on it, so just to settle the argument at the table: how many planets are there in the solar system now that Pluto isn't counted anymore?"),
    ("haiku", "longo", "Estou preenchendo um formulário do banco e ele pede a data no formato AAAA-MM-DD. Minha data de nascimento é 3 de abril de 1990. Como fica?"),
    ("haiku", "longo", "I'm writing a quick note to my landlord and I just want to double check one word: is it 'principal' or 'principle' in 'the principal reason I'm moving out'?"),
    ("haiku", "longo", "Tenho uma receita americana que pede 350 graus Fahrenheit no forno, mas meu forno é em Celsius. Qual temperatura eu coloco, mais ou menos?"),
    ("haiku", "longo", "We're planning a trip and someone in the group chat said Lisbon is the capital of Spain. I'm pretty sure that's wrong. What is the capital of Spain?"),
    ("haiku", "longo", "Recebi um e-mail com a sigla 'FYI' no começo e fiquei sem entender. Alguém da equipe mandou um relatório com isso. O que significa?"),
    ("haiku", "longo", "Quick formatting question for my resume: should 'Bachelor of Science' be capitalized when it's written out in full in the education section?"),
    # enganoso (parece técnico mas é simples)
    ("haiku", "enganoso", "O que significa a sigla API?"),
    ("haiku", "enganoso", "What does SQL stand for?"),
    ("haiku", "enganoso", "Quem criou a linguagem Python?"),
    ("haiku", "enganoso", "In what year was JavaScript created?"),
    ("haiku", "enganoso", "Qual a extensão de arquivo de um script Python?"),
    ("haiku", "enganoso", "What's the default port for HTTPS?"),
    ("haiku", "enganoso", "Quantos bits tem um byte?"),
    ("haiku", "enganoso", "Is HTML a programming language or a markup language?"),
    ("haiku", "enganoso", "Qual a capital da Teoria da Relatividade? Brincadeira — quem formulou a teoria da relatividade?"),
    ("haiku", "enganoso", "What does 'git' stand for, if anything?"),
    ("haiku", "enganoso", "Qual é o atalho de teclado para copiar no Windows?"),
    ("haiku", "enganoso", "Who proved Fermat's Last Theorem?"),
    ("haiku", "enganoso", "Em que ano foi lançado o primeiro iPhone?"),
    ("haiku", "enganoso", "What's the binary representation of the number 5?"),
    ("haiku", "enganoso", "Quem é considerado o pai da computação?"),
    ("haiku", "enganoso", "What does RAM stand for?"),
    # informal
    ("haiku", "informal", "kkk qual a capital da russia msm"),
    ("haiku", "informal", "yo whats the capital of italy"),
    ("haiku", "informal", "mano quanto e 9x7"),
    ("haiku", "informal", "how u spell restaurant lol"),
    ("haiku", "informal", "qnts dias tem fevereiro esse ano"),
    ("haiku", "informal", "tradus 'cachorro' pra ingles pfv"),
    ("haiku", "informal", "whats 100 km in miles"),
    ("haiku", "informal", "blz, brigadão!"),
    ("haiku", "informal", "qm descobriu a penicilina"),
    ("haiku", "informal", "ok cool ty"),

    # ============================================================= SONNET
    # comum
    ("sonnet", "comum", "Escreve uma função em Python que verifica se uma string é palíndromo, com testes"),
    ("sonnet", "comum", "My React app shows a blank page after build, but works in dev. How do I debug it?"),
    ("sonnet", "comum", "Cria um script que baixa todas as imagens de uma página web"),
    ("sonnet", "comum", "Write a Node.js script that reads a JSON file and writes a CSV"),
    ("sonnet", "comum", "Como faço um left join no pandas mantendo todas as linhas da tabela da esquerda?"),
    ("sonnet", "comum", "Add dark mode support to this Tailwind layout"),
    ("sonnet", "comum", "Escreve um Dockerfile otimizado para uma aplicação Flask"),
    ("sonnet", "comum", "Write a Python CLI with argparse that compresses a folder"),
    ("sonnet", "comum", "Cria uma API REST simples em Express com CRUD de tarefas"),
    ("sonnet", "comum", "Fix this Python function so it handles None inputs"),
    ("sonnet", "comum", "Monta uma query no MongoDB que agrupa vendas por mês"),
    ("sonnet", "comum", "Write a GitHub Actions workflow to run pytest on pull requests"),
    ("sonnet", "comum", "Escreve um e-mail educado recusando uma proposta comercial"),
    ("sonnet", "comum", "Summarize this meeting transcript and list action items with owners"),
    ("sonnet", "comum", "Converte esse script Bash em Python"),
    ("sonnet", "comum", "Write a function to flatten a nested dictionary in JavaScript"),
    ("sonnet", "comum", "Cria um formulário HTML com validação de e-mail e telefone"),
    ("sonnet", "comum", "Add retry logic with exponential backoff to this API client"),
    ("sonnet", "comum", "Explica por que esse teste do pytest está falhando com AssertionError"),
    ("sonnet", "comum", "Write a Rust struct and impl for a simple bank account with deposit and withdraw"),
    # curto
    ("sonnet", "curto", "regex pra validar email"),
    ("sonnet", "curto", "fix my CORS error"),
    ("sonnet", "curto", "script python pra renomear arquivos"),
    ("sonnet", "curto", "write a debounce function in JS"),
    ("sonnet", "curto", "dockerfile pra node"),
    ("sonnet", "curto", "sql pra deletar duplicados"),
    ("sonnet", "curto", "react hook para fetch"),
    ("sonnet", "curto", "unit tests for this function"),
    ("sonnet", "curto", "corrige esse bug aqui"),
    ("sonnet", "curto", "bash loop over files"),
    # longo
    ("sonnet", "longo", "Tenho uma aplicação Django com um modelo Pedido que tem um campo status. Quando o pagamento é confirmado pelo webhook do gateway, eu atualizo o status, mas às vezes o webhook chega duas vezes e o pedido é processado em dobro, gerando duas notas fiscais. Como eu deixo esse processamento idempotente? Segue o código da view do webhook."),
    ("sonnet", "longo", "I have a Next.js app that fetches products from our API on the server. After we added authentication with cookies, the product page started returning 401 on the server side even though the user is logged in in the browser. I think the cookie isn't being forwarded. Here's the getServerSideProps code and the middleware, can you find the issue and fix it?"),
    ("sonnet", "longo", "Preciso de um script em Python que leia uma pasta cheia de planilhas Excel de vendas (uma por loja), junte tudo numa tabela só, calcule o total por produto e por mês, e gere um gráfico de barras em PNG. As planilhas têm as colunas data, produto, quantidade e valor, mas algumas lojas usam 'Data' com maiúscula."),
    ("sonnet", "longo", "Our Go service leaks goroutines: the count grows slowly over a day until the pod is OOM-killed. I suspect the HTTP client calls without context timeouts in the worker loop. Here's the worker code and the pprof goroutine dump. Can you point out the leak and patch it?"),
    ("sonnet", "longo", "Escreve um e-mail para os clientes avisando que o sistema vai ficar fora do ar no sábado das 2h às 6h para manutenção, explicando o que muda (novo login com dois fatores), o que eles precisam fazer antes, e um contato de suporte. Tom profissional mas próximo, uns três parágrafos."),
    ("sonnet", "longo", "I've got a Flask API and a React frontend in the same repo. I want a single docker-compose setup for local dev with hot reload on both, a Postgres database with a seed script, and environment variables loaded from a .env file. Can you write the compose file, both Dockerfiles, and explain how to run it?"),
    ("sonnet", "longo", "Meu componente React de lista tem 5 mil itens e está travando ao digitar no campo de busca que filtra a lista. Já tentei useMemo mas continua lento. Segue o código do componente. Como deixo isso fluido?"),
    ("sonnet", "longo", "Write a Python class that wraps the Stripe API for our subscription flow: create customer, attach payment method, create subscription with a trial, cancel at period end, and handle webhook signature verification. Include type hints and docstrings, and unit tests using mocks."),
    ("sonnet", "longo", "Recebi esse relatório de 15 páginas sobre a pesquisa de satisfação dos funcionários. Preciso de um resumo de uma página para a diretoria com os 5 principais achados, os números mais importantes e 3 recomendações práticas."),
    ("sonnet", "longo", "Our Postgres query for the dashboard takes 8 seconds. It joins orders, customers and products, filters by date range and region, and orders by total. Here's the EXPLAIN ANALYZE output and the table definitions. What indexes or rewrites would speed it up?"),
    # enganoso (parece simples ou parece complexo, mas é intermediário)
    ("sonnet", "enganoso", "Explica de forma simples o que esse código faz"),
    ("sonnet", "enganoso", "Can you make this function faster?"),
    ("sonnet", "enganoso", "Traduz esse arquivo de i18n do inglês para o português mantendo as chaves JSON"),
    ("sonnet", "enganoso", "Rewrite this paragraph to be clearer and more concise, keeping the technical terms"),
    ("sonnet", "enganoso", "Faz um resumo desse artigo científico em linguagem simples para um blog"),
    ("sonnet", "enganoso", "Design a simple database schema for a todo app with users and tags"),
    ("sonnet", "enganoso", "Projete o esquema de banco de dados de um blog com posts, autores e comentários"),
    ("sonnet", "enganoso", "Explain the difference between let, const and var with examples"),
    ("sonnet", "enganoso", "Me explica a diferença entre processo e thread com exemplos em código"),
    ("sonnet", "enganoso", "What's wrong with this code? It prints the wrong total"),
    ("sonnet", "enganoso", "Organize meu código em módulos, ele está todo num arquivo só"),
    ("sonnet", "enganoso", "Write a cover letter for a junior frontend developer position"),
    ("sonnet", "enganoso", "Monta um plano de estudos de 4 semanas para aprender SQL"),
    ("sonnet", "enganoso", "Explain how this sorting algorithm works and its time complexity"),
    ("sonnet", "enganoso", "Faz uma tabela comparando três frameworks web Python para um projeto pequeno"),
    ("sonnet", "enganoso", "Turn these notes into a well-structured README"),
    # informal
    ("sonnet", "informal", "mano meu codigo n roda da erro de indentaçao no python help"),
    ("sonnet", "informal", "pls fix this my app keeps crashing on startup"),
    ("sonnet", "informal", "faz um script q pega os emails de um csv e manda msg pra cada um"),
    ("sonnet", "informal", "why tf does npm install keep failing w/ ERESOLVE"),
    ("sonnet", "informal", "preciso de um bot de discord q responde comandos simples"),
    ("sonnet", "informal", "my css grid is all messed up on mobile can u fix"),
    ("sonnet", "informal", "da pra fazer um site simples de portfolio em html e css?"),
    ("sonnet", "informal", "git push dando rejected oq eu faço"),
    ("sonnet", "informal", "can u write me a python scraper for amazon prices"),
    ("sonnet", "informal", "faz uns testes pra essa função ai"),

    # =============================================================== OPUS
    # comum
    ("opus", "comum", "Projete a arquitetura de um sistema de reservas de passagens aéreas que evite overbooking com milhares de compras simultâneas"),
    ("opus", "comum", "Design a disaster recovery strategy for a multi-cloud Kubernetes platform with RPO under 5 minutes"),
    ("opus", "comum", "Demonstre que o conjunto dos números reais não é enumerável"),
    ("opus", "comum", "Prove that the halting problem is undecidable"),
    ("opus", "comum", "Analise os riscos e benefícios de adotar arquitetura orientada a eventos em um ERP legado"),
    ("opus", "comum", "Compare the CAP theorem trade-offs of Spanner, CockroachDB and DynamoDB for a global inventory system"),
    ("opus", "comum", "Elabore um plano de pesquisa para medir o impacto de IA generativa na produtividade de desenvolvedores"),
    ("opus", "comum", "Derive the closed-form solution for ordinary least squares and discuss when it fails"),
    ("opus", "comum", "Desenvolva uma estratégia de precificação dinâmica para uma rede de hotéis considerando sazonalidade e concorrência"),
    ("opus", "comum", "Investigate why our Raft cluster occasionally elects two leaders and propose a fix"),
    ("opus", "comum", "Projete um sistema de recomendação para um e-commerce com 50 milhões de produtos e cold start"),
    ("opus", "comum", "Develop a threat model for a healthcare data-sharing platform across hospitals"),
    ("opus", "comum", "Explique a prova do teorema da incompletude de Gödel em linhas gerais e suas implicações"),
    ("opus", "comum", "Design an algorithm to schedule exams for 20,000 students with no conflicts and minimal back-to-back exams"),
    ("opus", "comum", "Avalie criticamente o uso de microsserviços versus monólito para uma empresa com 8 desenvolvedores e crescimento acelerado"),
    ("opus", "comum", "Write a research proposal on interpretability methods for large language models"),
    ("opus", "comum", "Modele matematicamente a propagação de uma epidemia com vacinação e discuta os parâmetros críticos"),
    ("opus", "comum", "Analyze the second-order effects of moving our company to a four-day work week"),
    ("opus", "comum", "Projete um protocolo de sincronização offline para um app de prontuário médico com resolução de conflitos"),
    ("opus", "comum", "Propose and justify an architecture for real-time collaborative editing like Google Docs"),
    # curto
    ("opus", "curto", "prove P ≠ NP implica que não existe algoritmo polinomial para SAT"),
    ("opus", "curto", "Prove √3 é irracional"),
    ("opus", "curto", "prove the four color theorem's key lemma"),
    ("opus", "curto", "Arquitetura para 1 bilhão de usuários?"),
    ("opus", "curto", "design a global payment ledger"),
    ("opus", "curto", "Demonstre o teorema de Bayes a partir dos axiomas"),
    ("opus", "curto", "Is our crypto protocol secure? Formal analysis please"),
    ("opus", "curto", "Estratégia de IA da empresa para 5 anos"),
    ("opus", "curto", "prove quicksort's expected O(n log n)"),
    ("opus", "curto", "Resolva o problema de Monty Hall generalizado para n portas e prove"),
    ("opus", "curto", "design a consensus algorithm"),
    ("opus", "curto", "Por que o universo tem mais matéria que antimatéria? Analise as hipóteses"),
    ("opus", "curto", "formalize and verify this mutex"),
    ("opus", "curto", "prove Cantor's theorem"),
    ("opus", "curto", "Root cause: p99 latency spike, sem mudança de código"),
    ("opus", "curto", "Compare RLHF vs DPO teoricamente"),
    # longo
    ("opus", "longo", "Somos uma fintech com 2 milhões de clientes e nosso sistema de conciliação bancária roda em batch toda madrugada, demorando 6 horas. O negócio quer conciliação em tempo real. Temos um monólito Java, um Oracle e integrações com 14 bancos via arquivos CNAB. Desenhe a arquitetura alvo, o plano de migração em fases sem parar a operação, os riscos e como medir sucesso."),
    ("opus", "longo", "Our ML team trains a fraud model weekly. In production, precision dropped from 92% to 71% over three months while offline metrics stayed stable. Features come from a feature store with both batch and streaming pipelines. Walk through every plausible hypothesis (data drift, training-serving skew, label delay, feedback loops), how to test each one, and what monitoring we should build."),
    ("opus", "longo", "Preciso de uma análise completa sobre se devemos internalizar nosso call center (hoje terceirizado, 300 atendentes) ou automatizar parte dele com IA. Considere custos em 5 anos, impacto na satisfação do cliente, riscos trabalhistas e regulatórios, e proponha cenários com premissas explícitas."),
    ("opus", "longo", "We're designing a new programming language for data pipelines. We want static types, incremental computation, and the ability to run the same code locally and distributed. Propose the core semantics, the type system, how incremental recomputation works, and the trade-offs against existing tools like dbt and Spark."),
    ("opus", "longo", "Temos três serviços (pedidos, estoque e pagamento) que usam um saga orquestrado. Em casos raros, um pedido é cancelado mas o estoque não é devolvido, e não conseguimos reproduzir. Os logs mostram timeouts no serviço de estoque nesses horários. Levante as hipóteses, explique como cada uma geraria o sintoma, e proponha um desenho que garanta consistência."),
    ("opus", "longo", "I'm writing a paper on whether transformer language models can learn compositional generalization. Review the main theoretical arguments on both sides, summarize the key empirical results, identify the methodological weaknesses in existing benchmarks, and propose a new experiment that would be more decisive."),
    ("opus", "longo", "Uma prefeitura quer usar dados de celulares para planejar o transporte público. Avalie as abordagens técnicas possíveis, os riscos de privacidade à luz da LGPD, como anonimizar de forma robusta contra reidentificação, e proponha uma arquitetura e uma governança de dados."),
    ("opus", "longo", "Our startup has 18 months of runway. We can either double down on our SMB product, which has good retention but low ACV, or pivot to enterprise, which two pilots suggest could be 10x ACV but with long sales cycles. Lay out a decision framework, the key uncertainties, how to cheaply reduce them in the next 90 days, and your recommendation."),
    ("opus", "longo", "Estou projetando um sistema de controle para um braço robótico em uma linha de montagem. Ele precisa ser seguro perto de humanos, tolerar falhas de sensores e atingir precisão de 0,1 mm. Proponha a arquitetura de controle, a estratégia de redundância, como validar a segurança formalmente e os modos de falha críticos."),
    ("opus", "longo", "We run a marketplace where sellers set prices and we suspect some sellers are colluding. Design an approach to detect collusion from pricing and order data, discuss the statistical pitfalls (false positives, confounding by seasonality), and how we'd validate the method without ground truth labels."),
    # enganoso (parece simples, mas é complexo)
    ("opus", "enganoso", "Por que o céu é azul? Quero a explicação física completa, com a derivação do espalhamento Rayleigh"),
    ("opus", "enganoso", "Is this number prime: 2^61 - 1? Prove it rigorously"),
    ("opus", "enganoso", "Explique por que 0,999... é igual a 1 com uma prova rigorosa usando limites e uma usando cortes de Dedekind"),
    ("opus", "enganoso", "Tell me a story — but it must be a valid proof of the infinitude of primes told as a narrative, with every step correct"),
    ("opus", "enganoso", "Qual é a melhor linguagem de programação? Faça uma análise rigorosa considerando contextos, evidências empíricas e trade-offs"),
    ("opus", "enganoso", "Should we raise prices? Here are 3 years of sales, churn and competitor data — build the analysis and recommend"),
    ("opus", "enganoso", "Me ajuda a decidir entre aceitar uma oferta de emprego no exterior ou ficar, considerando carreira, finanças, família e impostos nos dois países"),
    ("opus", "enganoso", "Write a sorting function — but it must be provably optimal for nearly-sorted inputs; prove the bound"),
    ("opus", "enganoso", "Revisa esse contrato de fusão de 40 páginas e aponta riscos jurídicos, cláusulas assimétricas e o que negociar"),
    ("opus", "enganoso", "Fix this bug: our distributed lock sometimes lets two nodes in at once across regions"),
    ("opus", "enganoso", "Traduz esse poema do Drummond para o inglês preservando métrica, rima e ambiguidades, e justifica cada escolha"),
    ("opus", "enganoso", "Explain why this code is slow — it's a 3D physics engine and we need to hit 120 fps with 100k rigid bodies"),
    ("opus", "enganoso", "Resume a história da filosofia da mente e posicione criticamente o funcionalismo frente às objeções mais fortes"),
    ("opus", "enganoso", "Can you check my proof that every continuous function on [0,1] is uniformly continuous? Point out any gaps"),
    # informal
    ("opus", "informal", "mano preciso arquitetar um sistema de pagamento q aguente black friday sem cair, me ajuda a pensar tudo"),
    ("opus", "informal", "ok so our whole infra is on fire every monday morning and nobody knows why, help me think through root causes"),
    ("opus", "informal", "prova pra mim q raiz de 2 é irracional mas bem rigoroso tipo de livro"),
    ("opus", "informal", "need a full strategy to take our saas from 1M to 10M ARR, think it through"),
    ("opus", "informal", "qual a melhor forma de desenhar um banco distribuido q n perca dado nunca, pensa em tudo"),
    ("opus", "informal", "explain godel incompleteness like actually rigorously not the pop sci version"),
    ("opus", "informal", "me ajuda a modelar o risco de uma carteira de investimentos com correlação entre ativos, coisa séria"),
    ("opus", "informal", "design me a whole recsys from scratch w/ cold start, ranking, eval, the works"),
    ("opus", "informal", "a gente ta perdendo cliente e ngm sabe pq, monta uma investigação completa"),
    ("opus", "informal", "how would u build a chess engine that beats stockfish, deep dive pls"),
]


def main():
    os.makedirs("dados", exist_ok=True)
    with open("dados/teste_extra.jsonl", "w", encoding="utf-8") as f:
        for label, cat, text in CASOS:
            f.write(json.dumps({"state": text, "questions": QUESTIONS,
                                "expected": {"modelo": label}, "categoria": cat},
                               ensure_ascii=False) + "\n")
    counts = {}
    for label, cat, _ in CASOS:
        counts[(label, cat)] = counts.get((label, cat), 0) + 1
    print(len(CASOS), "exemplos")
    for k in sorted(counts):
        print(" ", k, counts[k])


if __name__ == "__main__":
    main()
