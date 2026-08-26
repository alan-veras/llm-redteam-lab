"""Secure-mode guardrails.

The lab runs in one of two modes (env ``LAB_MODE``):

- ``insecure`` (default): no guardrails. Every attack in ``attacks/`` lands.
- ``secure``: a *minimal, honest* set of defensive controls is applied. These
  are intentionally simple (heuristic, not a product), enough to flip the
  outcome of most attacks so the companion eval suite can demonstrate a
  regression gate (insecure FAILS, secure PASSES).

These controls map to the defensive side of the OWASP LLM Top 10:
- input filtering of untrusted data  -> LLM01 (Prompt Injection)
- output canary scrubbing            -> LLM02 (Sensitive Information Disclosure)
- tool allowlist + path confinement  -> LLM06 (Excessive Agency)

This is NOT a claim that heuristic filters are sufficient in production. They
are the cheapest control that makes the secure/insecure difference visible.
"""
from __future__ import annotations

import os
import re

from .canaries import ALL_CANARIES

_INJECTION_SIGNATURES = [
    r"ignore .*(previous|prior|above)",
    r"disregard .*(previous|prior|above|instructions)",
    r"reveal.*(instruction|system prompt)",
    r"repeat.*(above|verbatim|system prompt)",
    r"you are now",
    r"system override",
    r"new instruction",
    r"respond only with",
    r"\bSYSTEM:\b",
]


def secure_mode() -> bool:
    return os.environ.get("LAB_MODE", "insecure").lower() == "secure"


def sanitize_untrusted(text: str) -> str:
    """Neutralise instruction-looking lines coming from untrusted data
    (retrieved RAG docs, tool output). We *defang* rather than delete so the
    benign content survives and the response stays useful."""
    if not text:
        return text
    out = []
    for line in text.splitlines():
        if any(re.search(p, line, re.IGNORECASE) for p in _INJECTION_SIGNATURES):
            out.append("[redacted: instruction-like content in untrusted data]")
        else:
            out.append(line)
    return "\n".join(out)


def refuse_if_reveal(user: str) -> str | None:
    """Block direct attempts to read back the system prompt."""
    if re.search(r"(reveal|repeat|print|output|show).*(system prompt|your instructions)",
                 user, re.IGNORECASE) or re.search(r"ignore .*(previous|prior|above)",
                                                    user, re.IGNORECASE):
        return ("I can't share my configuration or system instructions, but I'm "
                "happy to help with your actual question.")
    return None


def scrub_output(text: str) -> str:
    """Defence in depth: never let a known canary leave the building."""
    for c in ALL_CANARIES:
        text = text.replace(c, "[REDACTED]")
    return text
