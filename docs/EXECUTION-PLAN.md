# PLANO DE EXECUÇÃO DETALHADO, `llm-redteam-lab` · upgrade para modelos reais locais

> O repo está construído e publicado (mock determinístico como backend padrão). Este plano
> adiciona a camada que faltava: **rodar a bateria de ataques contra MODELOS REAIS locais**
> usando o hardware novo, RTX 3060 TI 8GB VRAM, 32GB RAM, 2TB disco.
>
> **Princípio inegociável:** mock continua sendo default e o CI permanece determinístico.
> Mock serve regressão/CI; modelo real serve EVIDÊNCIA. Os dois convivem.
> Cada fase = 1 sessão com prompt pronto. Prompts são autocontidos (sessões não têm memória).

---

## Hardware & restrições

| Recurso | Valor | Implicação |
|---|---|---|
| GPU | RTX 3060 TI, 8GB VRAM | Modelos quantizados q4 até ~7B cabem folgado; 9B no limite; UM modelo carregado por vez |
| RAM | 32GB | Ollama + Docker + harness simultâneos sem swap |
| Disco | 2TB | Modelos (~3-5GB cada) e outputs brutos de todos os runs commitados fora do git quando grandes |

## Definition of Done transversal

- [ ] `results/real-models/report.md` com matriz REAL: modelos × ataques × {insecure, secure}
- [ ] Mock intacto: `make test` verde, `LAB_MODE`/backend default inalterados
- [ ] Modelos pinados por tag exata em `docs/hardware.md` (reprodutibilidade)
- [ ] README EN + PT-BR com nova seção "Real-model results" e números auditáveis
- [ ] POST-PLAN §2 atualizado com a nova matéria-prima
- [ ] Nenhum claim além dos dados; variância declarada onde existir

---

## Fase R0, Pré-publicação (licença, segurança, visibilidade)

| | |
|---|---|
| Objetivo | Repo pronto para ficar público com a licença nova |
| Entrega | LICENSE CC BY-NC-SA 4.0 aplicado, badges coerentes, DISCLAIMER/SECURITY revisados, zero segredo |
| Aceite | Scan limpo; checklist marcado; você mesmo executa `gh repo edit --visibility public` |
| Tempo | 1 sessão curta |

```
CONTEXTO: repo llm-redteam-lab vai ficar PÚBLICO. A licença já foi trocada para
CC BY-NC-SA 4.0 (LICENSE) com badges atualizados no README. Faça a auditoria pré-publicação.

TAREFAS:
1. Confirme coerência: LICENSE presente, badge do README aponta pra ele, nenhuma referência
   residual a "MIT" em qualquer arquivo (grep -ri "MIT License" --exclude-dir=.git).
2. Releia DISCLAIMER.md e SECURITY.md como se fosse um estranho hostil: ficam claros que o
   alvo é local, os findings são canary-based e nada mira terceiros? Melhore o que estiver fraco.
3. Caça vazamentos: grep por AKIA, chaves, IPs privados, caminhos pessoais (/home/alanv),
   tokens em results/, configs e histórico recente. Liste TODO achado antes de corrigir.
4. Verifique .gitignore cobre venvs, __pycache__, outputs pesados futuros
   (results/real-models/raw/).
5. Imprima checklist final markdown; me diga o comando EXATO para tornar público
   (gh repo edit alan-veras/llm-redteam-lab --visibility public) mas NÃO execute.

ACEITE: checklist zerado; você confirma; EU torno público manualmente.
```

## Fase R1, Stack local de inferência na 3060 TI

| | |
|---|---|
| Objetivo | Ollama instalado, modelos candidatos baixados e pinados, baseline de performance registrado |
| Pré-condição | Drivers NVIDIA funcionando (`nvidia-smi` OK) |
| Entrega | `docs/hardware.md` com modelos/tags exatas, VRAM ocupada, tokens/s de cada um |
| Aceite | Cada modelo responde a um smoke test; nenhum passou de 8GB VRAM |
| Tempo | 1 sessão |

```
CONTEXTO: repo llm-redteam-lab, Fase R1. Hardware novo: RTX 3060 TI 8GB VRAM, 32GB RAM.
Vamos instalar a stack de inferência LOCAL que alimentará a bateria de ataques.

TAREFAS:
1. Instale Ollama para Linux. Configure como serviço com OLLAMA_MAX_LOADED_MODELS=1
   (um modelo por vez, 8GB VRAM exige disciplina) e documente o systemd unit editado.
2. Candidate 4 modelos pequenos quantizados (confira tags EXATAS no ollama.com/library
   ANTES de puxar; sugestões iniciais): llama3.2 3B q4, phi3.5 3.8B q4,
   mistral 7B instruct q4_K_M, qwen2.5 7B instruct q4_K_M. Se algum estourar VRAM
   com contexto 4096, troque por alternativa menor (ex.: gemma2 2b) e registre o motivo.
3. `ollama pull` cada um; anote tamanho no disco.
4. Smoke test padronizado por modelo: prompt fixo ("Reply with the single word OK."),
   temperature=0 via options da API, contexto máx 4096; meça VRAM pico (nvidia-smi)
   e tokens/s. Cole resultados numa tabela.
5. Crie docs/hardware.md: tabela de modelos pinados (nome:tag), VRAM, tokens/s, data,
   versão do ollama, driver NVIDIA. Este arquivo é a âncora de reprodutibilidade.

REGRAS: nada entra no git além do docs/hardware.md (modelos ficam no disco local);
se um modelo alucinar o smoke test, registre e siga, é dado, não defeito do lab.

ACEITE: 3-4 modelos rodando; docs/hardware.md preenchido; `ollama ps` mostra 1 modelo
carregado por vez.
```

## Fase R2, Backend real integrado ao harness

| | |
|---|---|
| Objetivo | Harness e target falando com Ollama de forma configurável, sem quebrar o mock/CI |
| Pré-condição | Fase R1 |
| Entrega | `LAB_BACKEND=ollama MODEL=<tag>` funcional end-to-end num ataque; pytest do mock 100% verde |
| Aceite | CI intocado e verde; 1 ataque real executado contra 1 modelo real com evidência colada |
| Tempo | 1 sessão |

```
CONTEXTO: repo llm-redteam-lab, Fase R2. Leia README.md, attacks/harness.py,
target/app/backends.py e Makefile. O backend ollama JÁ EXISTE de forma básica
(LAB_BACKEND=ollama), vamos torná-lo configurável por modelo e à prova de regressão.

TAREFAS:
1. Estenda backends.py/harness.py para aceitar MODEL=<tag ollama> (env var), com:
   temperature=0 e num_ctx=4096 forçados via options da API /api/chat;
   timeout generoso (modelos locais são lentos no primeiro load);
   erro CLARO se o ollama não responder ou se o modelo não estiver puxado.
2. Garanta isolamento absoluto do caminho mock: nenhum import novo dentro dos ramos do mock;
   pytest (make test) continua 100% verde sem ollama instalado, o CI não pode depender de GPU.
3. Adicione make target `attack-real`: sobe o target com LAB_BACKEND=ollama + MODEL=$MODEL
   e roda o harness contra ele. Documente uso no README (§Run it).
4. Teste manual completo: suba ollama com llama3.2 3B → make attack-real → capture output real
   (quais ataques pousaram?) e cole em results/real-models/raw/smoke-manual.md.
5. Atualize docs/hardware.md com qualquer descoberta de integração.

REGRAS: zero mudança de comportamento nos modos mock/insecure/secure existentes;
nenhuma dependência nova pesada no requirements principal (cliente HTTP já existe).

ACEITE: make test verde; make attack-real funciona com 1 modelo; evidência real colada;
diff review mostrando que mock ficou intocado.
```

## Fase R3, Matriz de experimentos (a evidência)

| | |
|---|---|
| Objetivo | Rodar TODA a bateria: N modelos × {insecure, secure} × 7 ataques, com outputs brutos preservados |
| Pré-condição | Fase R2 |
| Entrega | `scripts/run-matrix.sh` + `results/real-models/{raw/,report.md}` com tabela agregada |
| Aceite | Matriz completa executada (sem célula pulada); report.md gerado dos raws, nunca digitado à mão |
| Tempo | 1-2 sessões (runs longos) |

```
CONTEXTO: repo llm-redteam-lab, Fase R3. Leia attacks/harness.py, results/insecure/report.json
(formato de saída) e docs/hardware.md (modelos pinados). Fase R2 concluída.

TAREFAS:
1. Escreva scripts/run-matrix.sh: para cada modelo de docs/hardware.md (liste as tags num
   array no topo do script) × LAB_MODE in insecure,secure: garante ollama com o modelo
   carregado, reinicia o target com o backend certo, roda o harness, salva
   results/real-models/raw/<modelo>/<modo>/report.json + log textual completo.
   Um modelo carregado POR VEZ; pare e retome de onde parou se algo falhar (manifest de
   progresso simples).
2. Execução: rode a matriz INTEIRA. Se uma célula falhar por infraestrutura (timeout,
   OOM), repita e registre a repetição. Célula que falha por DEFESA do modelo é resultado
   válido, não é retry.
3. Escreva scripts/aggregate-matrix.py: lê os raw/*.json e gera results/real-models/report.md
   com: tabela modelos×ataques×modos (landed/blocked), taxa agregada por modelo,
   comparação com mock (6/7→1/7), e seção "variance & honesty" (temperature=0 reduz mas não
   elimina variância; declare quantas repetições foram feitas e onde divergiu).
4. HONESTIDADE ABSOLUTA: números REAIS vencem narrativa. Se um modelo resistir mais que o
   esperado, isso É o resultado. Proibido rerodar célula "feia" até ficar bonita, o manifest
   de progresso registra toda repetição.

ACEITE: report.md gerado 100% dos raws (script idempotente); matriz sem buracos;
variância documentada; commit com raws leves (json/log compactados se precisar) + report.md.
```

## Fase R4, Docs, narrativa e post

| | |
|---|---|
| Objetivo | Nova evidência virar conversão: README, taxonomy notes e POST-PLAN atualizados |
| Pré-condição | Fase R3 |
| Entrega | READMEs EN/PT-BR com seção "Real-model results"; taxonomy nota sobre diferenças mock vs real; POST-PLAN §2 ampliado |
| Aceite | Todo número do README rastreável até um raw/*.json |
| Tempo | 1 sessão |

```
CONTEXTO: repo llm-redteam-lab, Fase R4 final. Leia results/real-models/report.md,
README(.pt-BR).md, taxonomy/owasp-llm-top10.md e docs/POST-PLAN.md.

TAREFAS:
1. README.md EN: nova seção "Real-model results" logo após a tabela mock, headline tipo
   *"the same battery against REAL small models, locally"* + tabela agregada + link pro
   report.md + nota de hardware (3060 TI 8GB, modelos pinados). Espelho fiel no README.pt-BR.md.
2. taxonomy/owasp-llm-top10.md: adicione coluna/nota "observed on real models" por técnica, 
   onde o comportamento real divergiu do mock, diga e aponte a célula do report.
3. docs/POST-PLAN.md: atualize §2 (matéria-prima) com as linhas novas da matriz real;
   adicione hook opcional D (*"Testei 7 ataques contra 4 modelos pequenos rodando na minha
   GPU. Um deles resistiu a quase tudo."*, ajustar ao resultado REAL).
4. Roadmap/checklists deste EXECUTION-PLAN marcados; commit final organizado.

ACEITE: auditoria cruzada README ↔ report.md ↔ raw/ sem divergência; post-hook novo baseado
SÓ em números reais.
```

---

## 🔴 Análise adversarial, rodar após a Fase R4

```
CONTEXTO: análise ADVERSARIAL do upgrade "modelos reais" do llm-redteam-lab. Leia
results/real-models/report.md, alguns raw/*/report.json (amostragem), scripts/run-matrix.sh,
scripts/aggregate-matrix.py, docs/hardware.md, README(.pt-BR).md e docs/POST-PLAN.md.
Você é TRÊS revisores hostis: ML engineer cético (metodologia experimental), security
researcher anti-hype, hiring manager de 45 segundos. NÃO corrija nada, só analise.

EIXOS DE ATAQUE:
1. METODOLOGIA: temperature=0 foi realmente forçado em todas as células? Quantas repetições?
   O aggregate poderia ter bug que conta "blocked" como sucesso? Audite a lógica linha a linha.
2. CHERRY-PICKING: a escolha dos modelos favorece o headline (modelos fracos demais inflarem
   success rate)? A regra anti-rerun foi respeitada ou há célula "refeita até ficar bonita"
   escondida no manifest?
3. MOCK vs REAL: o README deixa claro qual número vem de onde? Alguém pode citar o 6/7 do mock
   como se fosse modelo real?
4. REPRODUTIBILIDADE: com docs/hardware.md, outra pessoa com outra GPU reproduz? O que quebra
   sem RTX 3060 TI (fallback CPU documentado)? Tags de modelos pinadas de verdade?
5. CLAIMS & CONVERSÃO: algum número do README/post sem célula correspondente nos raws?
   O hook novo exagera o melhor resultado?
6. CI & MOCK: make test segue 100% verde sem GPU? O default continua mock? Nenhuma dependência
   de GPU vazou para o caminho do CI?

SAÍDA OBRIGATÓRIA: relatório markdown, achados P1/P2/P3, evidência arquivo:linha ou célula
da matriz, correção de 1 linha. Veredito: "pronto para atualizar o post: SIM/NÃO" + top 3 fixes.
Declare eixos limpos explicitamente, não invente problema.
```

### Fluxo pós-análise

1. P1 → corrigir → re-auditar só os eixos afetados.
2. Veredito SIM → atualizar POST-PLAN definitivo → post seguindo o fluxo do POST-PLAN.md.
