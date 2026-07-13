# TythanAI Security Platform — Community Edition
# Copyright (c) 2026 TythanAI Labs
# Licensed under the Business Source License 1.1 (see LICENSE).

"""
community/ai/providers.py — pluggable LLM backends for the assistant.

Three backends, in order of privacy:

  * OfflineProvider — no model at all; deterministic knowledge-base answers.
    The default, so nothing leaves your machine.
  * OllamaProvider  — a local model via Ollama (http://localhost:11434). Still
    fully local.
  * ClaudeProvider  — Anthropic's Claude (model claude-opus-4-8). Sends the
    finding/code context to Anthropic; opt-in, needs ANTHROPIC_API_KEY.

`select_provider()` picks one from config/env, defaulting to Offline so the
Community Edition's "nothing leaves your machine" promise holds unless the user
deliberately opts in.
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import List, Optional

DEFAULT_CLAUDE_MODEL = "claude-opus-4-8"
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder"


class OfflineProvider:
    """No LLM — answers come from the curated knowledge base only."""

    name = "offline"
    available = True

    def complete(self, system: str, prompt: str, context: str = "") -> str:
        return ("[offline mode] No AI provider configured, so I can't reason "
                "freely — but the knowledge-base explanation above is accurate "
                "and actionable. Set TYTHANAI_AI=ollama (local) or "
                "TYTHANAI_AI=claude (needs ANTHROPIC_API_KEY) for interactive Q&A.")


class OllamaProvider:
    """A local model served by Ollama — stays on your machine."""

    name = "ollama"

    def __init__(self, model: Optional[str] = None, host: Optional[str] = None):
        self.model = model or os.environ.get("TYTHANAI_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")

    @property
    def available(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.host}/api/tags", timeout=1.5) as r:
                return r.status == 200
        except Exception:
            return False

    def complete(self, system: str, prompt: str, context: str = "") -> str:
        body = json.dumps({
            "model": self.model,
            "system": system,
            "prompt": f"{context}\n\n{prompt}" if context else prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }).encode()
        req = urllib.request.Request(f"{self.host}/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read()).get("response", "").strip()


class ClaudeProvider:
    """Anthropic's Claude via the official SDK. Opt-in; context leaves the machine."""

    name = "claude"

    def __init__(self, model: Optional[str] = None):
        self.model = model or os.environ.get("TYTHANAI_CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)

    @property
    def available(self) -> bool:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return False
        try:
            import anthropic  # noqa: F401
            return True
        except ImportError:
            return False

    def complete(self, system: str, prompt: str, context: str = "") -> str:
        import anthropic
        client = anthropic.Anthropic()
        user = f"{context}\n\n{prompt}" if context else prompt
        resp = client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=system,
            thinking={"type": "adaptive"},
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()


_PROVIDERS = {
    "offline": OfflineProvider,
    "ollama": OllamaProvider,
    "claude": ClaudeProvider,
}


def select_provider(name: Optional[str] = None):
    """Return a provider by name (or $TYTHANAI_AI), falling back to Offline.

    Auto mode ("auto") prefers a local Ollama, then Claude if a key is set,
    then Offline — never sending data off-box unless a provider is truly ready.
    """
    name = (name or os.environ.get("TYTHANAI_AI", "offline")).lower()
    if name == "auto":
        for candidate in (OllamaProvider(), ClaudeProvider()):
            if candidate.available:
                return candidate
        return OfflineProvider()
    provider_cls = _PROVIDERS.get(name, OfflineProvider)
    provider = provider_cls()
    return provider if getattr(provider, "available", True) else OfflineProvider()
