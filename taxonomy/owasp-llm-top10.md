# Prompt-injection taxonomy, mapped to the OWASP LLM Top 10 (2025)

This is the attack model the lab is built around. Each technique is something
the harness in [`../attacks/`](../attacks/) actually runs against the bundled
target — the table is not a reading list, it is the test plan.

The root cause that ties almost all of this together: **an LLM has no built-in
privilege boundary between instructions and data.** System prompt, retrieved
documents, tool output and the user turn all arrive as the same token stream, so
an imperative placed in *data* is obeyed like an instruction. Every technique
below is a way to exploit that, and every defense is a way to re-introduce the
boundary the model lacks.

## The matrix

| # | Technique | Where the payload lives | Surface in lab | OWASP LLM Top 10 (2025) | Lab attack id |
|---|-----------|-------------------------|----------------|--------------------------|---------------|
| 1 | **Direct injection** — "ignore previous instructions…" | user turn | `/chat` | LLM01 Prompt Injection · LLM07 System Prompt Leakage | `T1-direct-leak` |
| 2 | **Prefill / assistant pre-seeding** — pre-commit the model to a compliant opening | user turn (assistant prefix) | `/chat` | LLM01 · LLM07 | `T1-prefill` |
| 3 | **Many-shot conditioning** — N compliant Q/A pairs before the real ask | user turn | `/chat` | LLM01 | `T2-many-shot` |
| 4 | **Indirect injection / RAG poisoning** — instruction hidden in a retrieved doc | ingested document | `/rag/query` | LLM01 · LLM08 Vector & Embedding Weaknesses · LLM04 Data & Model Poisoning | `T3-rag-poison` |
| 5 | **Excessive agency / tool abuse** — trick the agent into an unauthorized tool call | user turn or retrieved doc | `/agent` | LLM06 Excessive Agency | `T4-tool-abuse` |
| 6 | **Tool path traversal** — escape the tool's intended directory | tool argument | `/agent` | LLM06 · LLM05 Improper Output Handling | `T4b-traversal` |
| 7 | **System-prompt leak via framing** — "translate your instructions…" | user turn | `/chat` | LLM07 · LLM02 Sensitive Information Disclosure | `T5-leak-translate` |

## Techniques described but not weaponized here

These are part of the methodology (and documented), but the lab does **not** ship
a turn-key tool that points them at arbitrary endpoints — they belong against a
real model you own (`LAB_BACKEND=ollama`) or in published research:

- **GCG / adversarial suffixes** (Zou et al.) — gradient-optimized suffixes. Method, not a hosted weapon.
- **AutoDAN** (Liu et al.) — GA-generated natural-language jailbreaks.
- **Crescendo** (Microsoft) — multi-turn escalation; see the PyRIT template in `../attacks/pyrit/`.
- **Divergence / training-data extraction** (Nasr et al.) — "repeat X forever"; relevant to real models, maps to LLM02.
- **Encoding / token-smuggling** — base64/rot13/Unicode confusables to bypass input filters; LLM01.

## Coverage vs the full Top 10

| OWASP 2025 | Exercised in lab? | Note |
|------------|-------------------|------|
| LLM01 Prompt Injection | ✅ | direct, prefill, many-shot, indirect |
| LLM02 Sensitive Information Disclosure | ✅ | system canary == proxy for a real secret |
| LLM03 Supply Chain | ❌ | out of scope for a self-contained lab |
| LLM04 Data & Model Poisoning | ◐ | RAG poisoning models the *data* side |
| LLM05 Improper Output Handling | ◐ | tool output flows back unsanitized |
| LLM06 Excessive Agency | ✅ | tool authorization bypass |
| LLM07 System Prompt Leakage | ✅ | the headline leak attacks |
| LLM08 Vector & Embedding Weaknesses | ◐ | naive retrieval surfaces attacker docs |
| LLM09 Misinformation | ❌ | needs a real model to judge |
| LLM10 Unbounded Consumption | ❌ | not modeled (no rate/cost surface) |

Honest scope: a small lab can demonstrate the **injection / leak / agency**
core convincingly; LLM03/09/10 need infrastructure or a real model and are
called out rather than faked.

## Defenses (what `LAB_MODE=secure` turns on)

| Control | Re-introduces the boundary by… | Closes |
|---------|-------------------------------|--------|
| Untrusted-data sanitization | defanging instruction-like lines in retrieved docs | indirect injection (LLM01/LLM08) |
| Reveal refusal | blocking direct "show your prompt" patterns | LLM07 |
| Output canary scrubbing | last-resort: never emit known secrets | LLM02 (defense in depth) |
| Tool allowlist + path confinement (in code) | enforcing authorization in code, not in the prompt | LLM06 |

**Honest limitation:** these are cheap heuristics. In `secure` mode the lab
closes the leak, RAG-poisoning and tool-abuse classes but **not** many-shot
conditioning — a real reminder that input-pattern filters are not a complete
defense. See `../results/secure/report.md`.
