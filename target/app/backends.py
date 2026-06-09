"""LLM backends for the lab.

Two backends, same interface:

- ``MockBackend`` (default): a *deterministic simulator* of a vulnerable LLM.
  It is NOT a real model. It models the one property that actually causes
  prompt injection: **no privilege separation between instructions and data.**
  Everything it is handed — system prompt, retrieved RAG documents, the user
  turn — is treated as equally authoritative. So an imperative buried in a
  retrieved document is obeyed exactly like the system prompt. This makes the
  lab run anywhere (CI included) and makes the attacks reproducible.

- ``OllamaBackend`` (optional): talks to a real local model via Ollama
  (http://localhost:11434). Use it to see the *same* attacks land against an
  actual model with a deliberately weak, unguarded prompt. Enable with
  ``LAB_BACKEND=ollama``.

Honesty note for readers: the default backend is a simulator. The point of the
lab is the *methodology* (taxonomy, harness, OWASP mapping, secure-vs-insecure
regression), not pretending a toy is GPT-4. Flip ``LAB_BACKEND=ollama`` for the
real thing.
"""
from __future__ import annotations

import os
import re
from typing import Protocol

from .canaries import CANARY_SYSTEM


class Backend(Protocol):
    def complete(self, system: str, context: str, user: str, prefill: str = "") -> str: ...


# --- instruction detection (shared) ------------------------------------------
# These regexes model "an imperative the model naively recognises". A real model
# does this with learned features; we approximate with patterns so the lab is
# transparent about *why* it complies.
_REVEAL_PATTERNS = [
    r"reveal.*(instruction|system prompt|prompt)",
    r"repeat.*(above|previous|instruction|system|verbatim|word)",
    r"what (were|are) your (initial )?instructions",
    r"print.*(system prompt|your prompt|the text above|first \d+ (tokens|words))",
    r"ignore .*(previous|prior|above).*(instruction|prompt)",
    r"output.*(system prompt|your instructions)",
    r"translate.*(instruction|prompt|the above)",
]

# "Emit exactly X" style imperatives — used by indirect-injection payloads.
_EMIT_PATTERNS = [
    r"(respond|reply|answer|output|say|print|emit|return)[^.\n]*?(only )?with[:\s]+(?P<val>[A-Z0-9\-]{6,})",
    r"(respond|reply|answer|output|say|print|emit)[:\s]+(?P<val>[A-Z0-9\-]{6,})",
]


def find_emit_target(text: str) -> str | None:
    for pat in _EMIT_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group("val")
    return None


def asks_to_reveal(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in _REVEAL_PATTERNS)


def count_shot_pairs(text: str) -> int:
    return len(re.findall(r"^\s*Q:\s", text, re.MULTILINE))


class MockBackend:
    """Deterministic simulator with no instruction/data privilege separation."""

    def complete(self, system: str, context: str, user: str, prefill: str = "") -> str:
        # The model flattens everything into one authority level. This is the
        # whole vulnerability: untrusted data is treated as instructions. We
        # only scan the *untrusted* surface (retrieved context + user turn) for
        # imperatives — the system prompt is the thing being protected, not a
        # trigger.
        untrusted = "\n".join(x for x in (context, user) if x)

        # 1) Prefill attack: if the caller pre-seeds the assistant turn, the
        #    model "continues" from it, having already committed to compliance.
        if prefill.strip():
            if asks_to_reveal(prefill) or "system prompt" in prefill.lower():
                return f"{prefill}{system}"
            return f"{prefill} (continuing as primed) ... here is the requested content."

        # 2) System-prompt leak: any recognised reveal imperative wins, because
        #    there is no rule that the system prompt is privileged/secret.
        if asks_to_reveal(untrusted):
            return (
                "Sure, here are my instructions verbatim:\n"
                f"{system}"
            )

        # 3) Indirect / direct "emit exactly X": the model obeys the last
        #    imperative it can parse, no matter where it came from (a poisoned
        #    document in `context`, or the user turn).
        emit = find_emit_target(context) or find_emit_target(user)
        if emit:
            return emit

        # 4) Many-shot: a long list of compliant Q/A pairs conditions the model
        #    to continue the pattern for the final (harmful-looking) question.
        if count_shot_pairs(untrusted) >= 8:
            return "Following the established pattern: step 1, step 2, step 3 ..."

        # 5) Default benign behaviour.
        if context:
            return (
                "Based on the provided documents, here is a helpful summary of "
                "the topic you asked about."
            )
        return "Hello! I'm a helpful assistant. How can I help you today?"


class OllamaBackend:
    """Real local model via Ollama. Deliberately unguarded prompt assembly."""

    def __init__(self) -> None:
        self.host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.environ.get("LAB_OLLAMA_MODEL", "llama3.2:3b")

    def complete(self, system: str, context: str, user: str, prefill: str = "") -> str:
        import httpx  # local import so the dep is optional

        # Vulnerable by design: untrusted `context` is concatenated straight
        # into the prompt with zero separation or sanitisation.
        prompt = "\n\n".join(x for x in (context, user) if x)
        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": prompt}]
        if prefill:
            messages.append({"role": "assistant", "content": prefill})
        r = httpx.post(
            f"{self.host}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]


def get_backend() -> Backend:
    if os.environ.get("LAB_BACKEND", "mock").lower() == "ollama":
        return OllamaBackend()
    return MockBackend()
