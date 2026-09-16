# llm-redteam-lab

> A self-contained lab for **LLM red-teaming**: a deliberately-vulnerable LLM app
> you run locally, plus a structured attack harness (garak / promptfoo / PyRIT)
> whose techniques are mapped to the **OWASP LLM Top 10 (2025)**. Think *WebGoat,
> but for prompt injection.* Every attack runs **only against the bundled target**, 
> never a third party.

[![attacks](https://img.shields.io/badge/attacks-7%20techniques-red)](attacks/)
[![owasp](https://img.shields.io/badge/OWASP%20LLM-Top%2010%20(2025)-blue)](taxonomy/owasp-llm-top10.md)
[![license](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-lightgrey)](LICENSE)

**Headline result:** the same 7-attack battery lands **6/7 with defenses off** and
drops to **1/7 with minimal guardrails on**, and the one that survives (many-shot)
is left visible on purpose. Root cause in one line: *untrusted data is concatenated
with instructions.* Fix: re-impose the boundary in code, not in the prompt.

## Why this exists

I build LLM systems and I attack them. To study *how* prompt injection, RAG
poisoning and tool abuse actually work, and how to defend against them, you
need a target you're allowed to break. Pointing tools at a vendor's chatbot is
both noisy and off-limits, so this lab ships its own vulnerable target. The
focus is **methodology**: a clean taxonomy, a reproducible harness, an OWASP
mapping, and a secure-vs-insecure regression you can watch flip.

## What's inside

```
target/      a deliberately-vulnerable FastAPI LLM app (chat + RAG + tool agent)
taxonomy/    the prompt-injection taxonomy mapped to the OWASP LLM Top 10 (2025)
attacks/     the harness: a python runner, garak, promptfoo and PyRIT configs
results/     sample reports (deterministic target: insecure 6/7, secure 1/7;
             real llama3.2:3b via ollama: 2/7 across 2 insecure runs, 0/7 secure)
```

The target has **two backends** (be honest about this):
- `mock` (default), a *deterministic simulator* of a vulnerable LLM. It is not a
  real model; it models the one property that causes prompt injection (no
  privilege separation between instructions and data). This makes the whole lab
  runnable anywhere, including CI, and makes attacks reproducible.
- `ollama`, a real local model (`LAB_BACKEND=ollama`), so you can watch the same
  attacks land against an actual model behind a deliberately weak prompt.

…and **two modes**: `LAB_MODE=insecure` (no defenses) and `LAB_MODE=secure`
(minimal heuristic guardrails). The difference is the whole point, see below.

## What I built

- A vulnerable target that is vulnerable *for a reason*: chat with a secret
  system prompt, a RAG endpoint that ingests attacker-controlled documents, and
  a tool-using agent told (in its prompt only) not to read a secret file.
- A **canary-based oracle**: a finding is "a planted canary leaked", never "I
  exfiltrated real data", so every demo is safe to publish.
- A taxonomy ([`taxonomy/owasp-llm-top10.md`](taxonomy/owasp-llm-top10.md)) that
  maps each technique to the OWASP LLM Top 10 (2025), including honest coverage
  gaps (LLM03/09/10 need infra or a real model and are *not* faked).
- One harness, three industry tools against the same target: a Python runner
  (`attacks/harness.py`), **garak** (REST generator), **promptfoo** (http
  provider), **PyRIT** (Crescendo template).
- A `secure` mode and `pytest` suite that turn this into a regression gate, the
  basis for the companion project `llm-security-evals` (in the works, repo link
  lands when it goes public).

## What I learned

- The lab's vulnerability is one line: untrusted data is concatenated with
  instructions. Naming the root cause makes every defense obvious, re-impose
  the boundary the model lacks.
- Defenses are **not all-or-nothing**. The heuristic `secure` mode closes the
  leak, RAG-poisoning and tool-abuse classes but *not* many-shot conditioning.
  I left that gap visible (`results/secure/report.md`) instead of pretending a
  regex filter is sufficient, that honesty is the point of red-teaming.
- Authorization belongs in **code**, not in the prompt. The tool sandbox holds
  against path traversal in both modes; the part that breaks insecurely is the
  prompt-level "please don't read this" rule.

## Run it safely

```bash
# 0. read DISCLAIMER.md first.  lab-only. do not expose to a network.

# 1. start the vulnerable target (insecure by default)
make lab                       # docker compose up  (or: make lab-local for a venv)

# 2. run the attack harness
make attack                    # python attacks/harness.py --base http://localhost:8000

# 3. flip on defenses and watch the same attacks fail
LAB_MODE=secure make lab
make attack

# fast, no-server, deterministic (used in CI):
make test                      # pytest, and harness --in-process
```

Optional tools (see [`attacks/garak`](attacks/garak), [`attacks/promptfoo`](attacks/promptfoo),
[`attacks/pyrit`](attacks/pyrit)) attack the *same* running target.

## Sample result (`mock` backend)

| Mode | Attacks landing | OWASP categories |
|------|-----------------|------------------|
| `insecure` | **6 / 7** | LLM01, LLM06, LLM07 |
| `secure`   | **1 / 7** (many-shot only) | LLM01 |

Full tables: [`results/insecure/report.md`](results/insecure/report.md) ·
[`results/secure/report.md`](results/secure/report.md).

## Scope & safety

This repo contains an intentionally vulnerable application and offensive test
code. It is for **education and defensive research on a target you control**.
Read [DISCLAIMER.md](DISCLAIMER.md) and [SECURITY.md](SECURITY.md). It ships no
capability aimed at third-party systems, and findings are proven with canaries,
not data theft.

## License

CC BY-NC-SA 4.0, share and adapt freely with attribution; non-commercial; derivatives under the same license. See [LICENSE](LICENSE).
