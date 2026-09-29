"""Groq LLM client with a safe fallback.

Groq is the recommended LLM for this hackathon (fast, generous free tier). We use the
official `groq` SDK. If no GROQ_API_KEY is set, we fall back to a deterministic,
memory-grounded response so the project still runs and demos end-to-end offline.

The docs warn to "have your agent ready to handle function calling errors", so all LLM
calls are wrapped with retry + graceful degradation.
"""
from __future__ import annotations

import textwrap
from typing import Any

from . import config


class LLMResult:
    def __init__(self, text: str, model: str, used_fallback: bool = False):
        self.text = text
        self.model = model
        self.used_fallback = used_fallback


class GroqLLM:
    def __init__(self, api_key: str, model: str):
        from groq import Groq  # imported lazily

        self._client = Groq(api_key=api_key)
        self.model = model

    def complete(self, system: str, user: str, temperature: float = 0.2) -> LLMResult:
        last_err: Exception | None = None
        for attempt in range(3):
            try:
                resp = self._client.chat.completions.create(
                    model=self.model,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                return LLMResult(resp.choices[0].message.content or "", self.model)
            except Exception as exc:  # network / rate limit / function-calling errors
                last_err = exc
        raise RuntimeError(f"Groq call failed after retries: {last_err}")


class FallbackLLM:
    """Deterministic, memory-grounded responder used when no Groq key is present.

    It is NOT an LLM — it templates a structured incident response from the recalled
    memories and runbooks so the app is fully runnable offline. Set GROQ_API_KEY to get
    real reasoning.
    """

    model = "fallback (no GROQ_API_KEY)"

    def complete(self, system: str, user: str, temperature: float = 0.2) -> LLMResult:
        return LLMResult(_template_from_context(user), self.model, used_fallback=True)


def get_llm() -> GroqLLM | FallbackLLM:
    if config.llm_configured():
        try:
            return GroqLLM(config.GROQ_API_KEY, config.GROQ_MODEL)
        except Exception as exc:
            print(f"[llm] Groq init failed ({exc}); using offline fallback.")
    return FallbackLLM()


def _template_from_context(user_prompt: str) -> str:
    """Build a believable structured answer from the context block in the prompt.

    The agent packs recalled memories under a 'RECALLED MEMORIES' header; we parse the
    first one to ground the fallback answer.
    """
    memory_block = ""
    if "RECALLED MEMORIES" in user_prompt:
        # take everything after the RECALLED MEMORIES header line
        after = user_prompt.split("RECALLED MEMORIES", 1)[1]
        memory_block = after.split("\n", 1)[1] if "\n" in after else after
    top_line = ""
    matched_id = ""
    for line in memory_block.splitlines():
        raw = line.strip()
        if not raw.startswith("- "):
            continue
        # bullet format: "- (2026-08-15, score=24.48) [INC-2064] checkout-service: ..."
        body = raw[2:]
        if ")" in body:
            body = body.split(")", 1)[1].strip()
        top_line = body
        for tok in body.replace("[", " ").replace("]", " ").split():
            if tok.startswith("INC-"):
                matched_id = tok.rstrip(".,)")
                break
        break

    if top_line:
        return textwrap.dedent(
            f"""
            **Assessment** — Symptoms strongly match a past incident in memory.

            **Most likely root cause** — {top_line[:180]} _(confidence 78% — grounded in memory{f', {matched_id}' if matched_id else ''})_

            **Immediate actions**
            1. Apply the resolution that worked previously (see Memory used below).
            2. Watch the golden signals (errors, latency, saturation) for recovery.
            3. If a recent deploy correlates, roll it back first, diagnose second.

            **Verification** — Error rate returns to baseline within ~5 minutes.

            **If that fails** — Treat as novel; escalate to SEV2 and capture a fresh postmortem.

            **Memory used** — {matched_id or 'closest recalled incident above'}

            _(Offline fallback response — set GROQ_API_KEY for full LLM reasoning.)_
            """
        ).strip()

    return textwrap.dedent(
        """
        **Assessment** — No prior memory matched; this looks novel.

        **Most likely root cause** — Undetermined _(confidence low)_. Reason from the golden
        signals: check recent deploys, then saturation (pool/memory/CPU), then dependencies.

        **Immediate actions**
        1. Correlate the spike start with the deploy timeline; roll back if aligned.
        2. Check the most constrained resource (connection pool, memory, disk, queue depth).
        3. Inspect error signatures and recent config changes.

        **Verification** — Confirm the affected golden signal returns to baseline.

        **If that fails** — Escalate to SEV2 and page the service owner.

        **Memory used** — No prior memory matched — this looks novel.

        _(Offline fallback response — set GROQ_API_KEY for full LLM reasoning.)_
        """
    ).strip()
