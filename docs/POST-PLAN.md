# PLANO DE POST, `llm-redteam-lab`

> O repo está construído e publicado, falta só o post LinkedIn. Este plano define ângulo,
> matéria-prima auditável, esqueleto, prompt de execução e análise adversarial do POST.
> **Estilo OBRIGATÓRIO:** anatomia de 7 blocos de [POST-STYLE.md](../../POST-STYLE.md), 
> o esqueleto da seção 4 já é uma instância dela (link só no primeiro comentário).

---

## 1. Objetivo & público

| | |
|---|---|
| Objetivo | Converter atenção em visita ao repo; posicionar Alan como quem pratica (não só lê sobre) AI security |
| Público primário | Engenheiros/security folks que constroem com LLMs e sabem que prompt injection é real |
| Público secundário | Hiring managers técnicos; comunidade AppSec curiosa sobre OWASP LLM Top 10 |
| Ação desejada | Clonar o lab / salvar o post / seguir para os próximos posts da série |

## 2. Matéria-prima auditável (só cite isso, nada fora daqui)

| Claim possível | Fonte no repo |
|---|---|
| Mesma bateria de 7 ataques: **6/7** com defesas off → **1/7** com guardrails mínimos | `results/insecure/report.md`, `results/secure/report.md` |
| A categoria que sobrevive: many-shot (deixada visível DE PROPÓSITO) | `results/secure/report.md` |
| Root cause em 1 linha: dados não confiáveis concatenados com instruções | README §What I learned |
| Mapeamento das técnicas ao OWASP LLM Top 10 (2025), com lacunas declaradas (LLM03/09/10 NÃO falsificados) | `taxonomy/owasp-llm-top10.md` |
| Alvo vulnerável próprio: chat com system prompt secreto + RAG que ingere documento do atacante + tool agent | `target/app/` |
| Oracle baseado em canary: achado = "canary plantado vazou", nunca roubo de dado real | `target/app/canaries.py`, DISCLAIMER |
| Um harness, 3 ferramentas da indústria: runner próprio + garak + promptfoo + PyRIT | `attacks/` |
| Dois backends honestos: mock determinístico (roda em qualquer lugar/CI) e ollama real opcional | README §backends |
| Sandbox de tools segura path traversal nos DOIS modos; o que quebra inseguro é a regra "please don't" no prompt | README §learned |

## 3. Ângulo & hooks (escolher 1, gerar variantes na execução)

- **A (ofensivo direto, recomendado):** *"Ataquei minha própria IA 7 vezes. Sem defesas, 6 dos 7 funcionaram. Com guardrails mínimos, caiu pra 1."*
- **B (vazio de mercado):** *WebGoat ensinou uma geração a atacar aplicações web. Cadê o equivalente para prompt injection? Eu construí um.*
- **C (insight):** *Toda falha de prompt injection que eu já vi cabe numa linha: dados não confiáveis viram instrução. Se você nomeia a causa, a defesa fica óbvia.*

Regra: o hook promete exatamente o que a tabela entrega. Zero exagero, a honestidade É o diferencial.

## 4. Esqueleto do post, instância dos 7 blocos ([POST-STYLE.md](../../POST-STYLE.md))

| # | Bloco | Conteúdo deste repo |
|---|---|---|
| 1 | Origem conversacional + tese não-dita | rodando ataques contra meu próprio lab de LLM, caiu a ficha: atacar IA dos outros é problema jurídico; atacar a sua é o único jeito honesto de saber se ela aguenta |
| 2 | Concessão ("Beleza.") | colocar guardrail é rápido: um filtrozinho aqui, um "não faça isso" no prompt ali |
| 3 | Pergunta-pivô | mas e aí, o SEU system prompt vaza ou não vaza? Você TESTOU? |
| 4 | Exagero | se bastasse escrever "ignore instruções maliciosas" no prompt, já tinham resolvido a segurança da internet |
| 5 | Bullets-pergunta (3-5) | seu system prompt sobrevive a contexto adversarial longo? · seu RAG ingere documento do usuário, e se o documento MANDAR algo? · agent com tool de arquivo: quem valida o caminho? · dos 10 riscos da OWASP LLM, quantos você já EXPLOROU de verdade no seu sistema? (o "6/7 → 1/7" entra aqui dentro, como dado, não como tabela solta) |
| 6 | Aforismo espelhado | falar de prompt injection é fácil; ter um alvo que você PODE quebrar é que é raro |
| 7 | Pergunta aberta final | quantos dos seus controles de IA resistem a um ataque real, ou você só acredita que sim? |

How-to-run (`make lab` / `make attack`), teaser do post blue-team e o link vão no PRIMEIRO COMENTÁRIO. + convite a clonar

## 5. Checklist de conversão LinkedIn

- [ ] Primeira linha funciona SOZINHA antes do "ver mais"
- [ ] ≤1300 chars; parágrafos de 1-2 linhas (respiração mobile)
- [ ] Bloco 2 existe: o texto CONCEDE antes de virar a mesa ("Beleza.")
- [ ] Termina em interrogação (bloco 7)
- [ ] Zero link no corpo; primeiro comentário preparado (link + how-to-run)
- [ ] Números batem 100% com `results/*/report.md`
- [ ] Zero buzzword vazio ("revolucionário", "game changer", "IA generativa vai mudar tudo")
- [ ] Framing defensivo claro (lab próprio, canaries, disclaimer), sem cheiro de "olha meu exploit"
- [ ] Sem hashtags-genéricas em excesso (máx 2 no fim)

## 6. Prompt de execução (colar em sessão nova do opencode)

```
CONTEXTO: quero criar o post LinkedIn do repo llm-redteam-lab (já publicado).
Leia README.md, results/insecure/report.md, results/secure/report.md,
taxonomy/owasp-llm-top10.md e docs/POST-PLAN.md (a especificação deste post).

TAREFAS:
1. Gere 3 variantes do post em pt-BR seguindo a ANATOMIA DE 7 BLOCOS de ../../POST-STYLE.md
   (a seção 4 deste plano é a instância concreta), variando o bloco 1 entre os hooks A/B/C
   da seção 3. Tom informal real, parágrafos curtos, SEM link no corpo, terminando em pergunta.
   Gere também o texto do PRIMEIRO COMENTÁRIO (link + make lab/make attack + teaser).
2. Para cada variante, audite: TODOS os números citados existem nos reports? Algum claim além
   da matéria-prima §2? Marque OK/NOK por claim.
3. Recomende 1 variante vencedora com justificativa (conversão, clareza, honestidade).
4. Salve a vencedora em docs/post-draft.md junto das outras duas, com o checklist §5 marcado.
5. Sugira 2 melhorias concretas na vencedora (hook mais afiado, corte de linha fraca).

REGRAS: nada que não esteja na matéria-prima §2 do POST-PLAN; zero buzzword vazio;
framing defensivo sempre (alvo próprio, canaries); link SOMENTE no primeiro comentário;
nunca inventar pessoa/diálogo real no bloco 1. NÃO publique nada, só gerar arquivos locais.
```

## 7. 🔴 Análise adversarial do POST

Rodar numa sessão nova depois do rascunho pronto. Não edita nada, só julga.

```
CONTEXTO: análise ADVERSARIAL do rascunho de post LinkedIn em docs/post-draft.md do repo
llm-redteam-lab. Leia o rascunho, README.md, results/*/*.md e docs/POST-PLAN.md.
Você é um revisor hostil triplo: usuário cético de LinkedIn (scroll rápido, zero paciência),
security researcher que DETESTA hype, e hiring manager técnico de 45 segundos. NÃO edite nada.

EIXOS DE ATAQUE:
1. HONESTIDADE: algum claim exagerado ou número que não bate com os reports? O post vende o
   many-shot residual como vitória quando é gap declarado?
2. GANCHO: a primeira linha faria VOCÊ parar o scroll? Ou é genérica ("trabalhei num projeto
   legal de segurança")? Teste: cubra o resto do post, a linha 1 entrega curiosidade sozinha?
3. CLAREZA EM 45s: um dev que nunca viu prompt injection entende o valor? Jargão sem contexto?
4. TOM: soa como praticante mostrando trabalho ou como vendedor? Buzzwords? Cringe?
5. FRAMING DE SEGURANÇA: o post deixa óbvio que é lab próprio/educacional, ou alguém poderia
   ler como tutorial de ataque a terceiros?
6. CONVERSÃO: o CTA é único e específico? O leitor sabe EXATAMENTE o que fazer depois?
7. FORMATO: cabe no feed? Parágrafos respiram? A tabela renderiza bem em texto simples?

SAÍDA OBRIGATÓRIA: relatório markdown, achados com P1 (não publica) / P2 (corrigir antes) /
P3 (polimento), evidência (linha do rascunho), correção concreta de 1 linha. Veredito:
"pronto para publicar: SIM/NÃO" + top 3 fixes. Eixos limpos: declare "sem achados".
```

## 8. Fluxo pós-análise & publicação

1. P1 → corrigir rascunho → rodar análise de novo nos eixos afetados.
2. Veredito SIM → aplicar P2 rápidos → postar (terça/quarta, 8h-10h horário de SP costuma performar melhor).
3. Primeiro comentário próprio: link do repo + 1 linha "how to run" (mantém o corpo do post limpo).
4. Responder TODO comentário técnico nas primeiras 2h (janela de distribuição).
5. Depois de publicado: marcar checkbox aqui e no roadmap geral do portfólio.

### Sequência da trilogia (onde este post entra)

**1º este** (gancho ofensivo, maior alcance) → **2º llm-security-evals** ("tranquei o que ataquei") → **3º llm-conductor** (amplitude de engenharia). Os três juntos contam: *eu ataco, travo, e sei construir a infraestrutura*.
