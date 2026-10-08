"""A pergunta que o roteador faz ao Laya, compartilhada entre treino, teste e uso."""

QUESTIONS = {
    "modelo": {
        "type": "choice",
        "instructions": "Which model tier should handle this request?",
        "criteria": {
            "haiku": "simple question, greeting, short factual lookup, translation, formatting",
            "sonnet": "writing or editing code, debugging, moderate multi-step tasks",
            "opus": "complex reasoning, architecture design, research, hard math or proofs",
        },
    },
}
