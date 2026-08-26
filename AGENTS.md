# AGENTS.md

## Regra dura de escrita (vale para TODO agente e TODO humano editando este repo)

NUNCA use travessão nem meia-risca (os caracteres unicode U+2014 em-dash e U+2013 en-dash)
em NENHUM comentário de código e NENHUM documento. Isso inclui: READMEs, PLANs,
EXECUTION-PLANs, POST-PLANs, prompts, rascunhos de post, ADRs, comentários inline,
docstrings e mensagens de commit.

Substitua por vírgula, dois-pontos ou parênteses, o que ler melhor no contexto.

Verificação rápida antes de qualquer commit:

```bash
grep -rnP '\x{2014}|\x{2013}' --include='*.md' --include='*.py' --include='*.sh' .
```

O comando acima deve retornar ZERO resultados fora de `.venv/` e `.git/`.
