"""
llm_router.py — Unified router that dispatches to Z.AI / Kimi / DeepInfra
based on task type, balancing the user's API budget.

Z.AI coding endpoint: 20x plan, primary workhorse (heavy canon writing)
Kimi via Cloudflare: moderate hourly (variety, character voices)
DeepInfra Qwen: fast/cheap (factual rewrites, summaries, listings)
DeepInfra Seed-2.0-mini: ultra-cheap (cleanup, formatting)

The router picks the right model based on:
- `task` keyword: canon, voice, factual, summary, bridge, etc.
- `length`: how many tokens requested
- `priority`: critical or background

Usage:
    from llm_router import call
    text = call(prompt, task="canon-voice", length=2000)
"""
import os
import json
import time
import urllib.request
import urllib.error

# Endpoints
ZAI_CODING = "https://api.z.ai/api/coding/paas/v4/chat/completions"
DEEPINFRA = "https://api.deepinfra.com/v1/openai/chat/completions"

# Models per provider (use only ones that return content, not just reasoning)
# Working content-returning models (Sept 2026):
#   - Z.AI glm-4.5 ✓
#   - DeepInfra ByteDance/Seed-2.0-mini ✓
#   - DeepInfra ByteDance/Seed-2.0-code ✓
# Reasoning-only models (drain tokens, content empty):
#   - Z.AI glm-5, glm-5-turbo, glm-5.3-flash, glm-4.6
#   - DeepInfra Qwen3.*, Kimi-K*, DeepSeek-*, Step-*, Granite, Ling
MODELS = {
    "zai-flash": "glm-4.5",             # Z.AI legacy fast
    "zai-pro": "glm-4.5",               # Z.AI — same model works
    "zai-4.5": "glm-4.5",               # Z.AI legacy, returns content directly
    "kimi": "moonshotai/Kimi-K3",       # DeepInfra — reasoning-only (extract reasoning_content)
    "qwen": "Qwen/Qwen3.5-27B",         # DeepInfra — reasoning-only
    "qwen-fast": "Qwen/Qwen3-14B",      # DeepInfra — reasoning-only
    "seed": "ByteDance/Seed-2.0-mini",  # DeepInfra — returns content, cheap + creative
    "seed-code": "ByteDance/Seed-2.0-code",  # DeepInfra — returns content, code-specialized
    "deepseek": "deepseek-ai/DeepSeek-V3",  # DeepInfra — reasoning-only
    "stepfun": "stepfun-ai/Step-3.7-Flash",  # DeepInfra — reasoning-only
    "granite": "ibm-granite/granite-4.2-8b",  # DeepInfra — reasoning-only
    "ling": "inclusionAI/Ling-3.0-flash",  # DeepInfra — reasoning-only
}


def _post(url, headers, payload, timeout=60):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    return urllib.request.urlopen(req, timeout=timeout).read().decode()


def call_zai(prompt, model="glm-4.5", max_tokens=2000, temperature=0.7, system=None):
    token = os.environ.get("ZAI_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "llm-router/1.0",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    for attempt in range(3):
        try:
            r = _post(ZAI_CODING, headers, payload, timeout=120)
            d = json.loads(r)
            msg = d["choices"][0]["message"]
            # Reasoning models return empty content + reasoning_content
            content = msg.get("content") or msg.get("reasoning_content", "")
            return content.strip()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"  Z.AI rate limit (attempt {attempt+1})", file=__import__('sys').stderr)
                time.sleep(5 + attempt * 5)
                continue
            raise
        except Exception as e:
            print(f"  Z.AI err: {e}", file=__import__('sys').stderr)
            time.sleep(2)
    raise RuntimeError("Z.AI rate limited after 3 attempts")


def call_deepinfra_old(prompt, model="Qwen/Qwen3.8-27B", max_tokens=2000, temperature=0.7, system=None):
    """Legacy — replaced by call_deepinfra above."""
    return call_deepinfra(prompt, model=model, max_tokens=max_tokens,
                          temperature=temperature, system=system)


def call_kimi(prompt, max_tokens=2000, temperature=0.7, system=None):
    """Kimi via DeepInfra (moonshotai/Kimi-K3)."""
    return call_deepinfra(prompt, model="moonshotai/Kimi-K3",
                          max_tokens=max_tokens, temperature=temperature, system=system)


def call_deepinfra(prompt, model="ByteDance/Seed-2.0-mini", max_tokens=2000, temperature=0.7, system=None):
    """Call any DeepInfra OpenAI-compatible model (Seed-2.0-mini, Seed-2.0-code, etc.).

    Note (Sept 2026): most models return empty content (reasoning only).
    Seed-2.0-mini and Seed-2.0-code return real content. Others (Qwen3, Kimi, DeepSeek,
    Granite, etc.) are all in thinking mode — extract reasoning_content as fallback.
    """
    token = os.environ.get("DEEPINFRA_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}" if token else "",
        "Content-Type": "application/json",
        "User-Agent": "llm-router/1.0",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    for attempt in range(3):
        try:
            r = _post(DEEPINFRA, headers, payload, timeout=120)
            d = json.loads(r)
            msg = d["choices"][0]["message"]
            content = (msg.get("content") or msg.get("reasoning_content") or "").strip()
            return content if content else None
        except urllib.error.HTTPError as e:
            print(f"  DeepInfra HTTP {e.code} (model={model})", file=__import__('sys').stderr)
            if e.code == 429:
                time.sleep(3 + attempt * 2)
                continue
            return None
        except Exception as e:
            print(f"  DeepInfra err: {e}", file=__import__('sys').stderr)
            time.sleep(2)
    return None


def call(prompt, task="canon", length=1500, temperature=0.7, system=None,
         prefer=None, force=None):
    """
    Route the call.

    task:
      "canon"        — canon voice writing → Z.AI glm-5 (heavy, primary)
      "voice"        — character/voice exploration → Kimi (variety)
      "bridge"       — bridge essays → Z.AI glm-5-flash (medium)
      "factual"      — facts, summaries, listings → DeepInfra Qwen
      "cleanup"      — formatting, simple rewrites → DeepInfra Seed-2.0-mini
      "polyformal"   — code lifts → Z.AI
    """
    if force:
        return _dispatch(force, prompt, length, temperature, system)

    # Default routing
    if task in ("canon", "polyformal"):
        provider = "zai"
    elif task in ("bridge", "essay"):
        provider = "zai"
    elif task == "voice":
        provider = "kimi"
    elif task == "factual":
        provider = "qwen"
    elif task == "cleanup":
        provider = "seed"
    elif task == "fast":
        provider = "qwen-fast"
    elif task == "stepfun":
        provider = "stepfun"
    elif task == "granite":
        provider = "granite"
    elif task == "ling":
        provider = "ling"
    else:
        provider = "zai"

    if prefer and not force:
        provider = prefer

    return _dispatch(provider, prompt, length, temperature, system)


def _dispatch(provider, prompt, length, temperature, system, model=None):
    if provider == "zai":
        return call_zai(prompt, model=model or "glm-4.5",
                       max_tokens=length, temperature=temperature, system=system)
    elif provider == "zai-flash":
        # turbo drains tokens into reasoning — content often empty
        return call_zai(prompt, model="glm-5-turbo",
                       max_tokens=length, temperature=temperature, system=system)
    elif provider == "zai-4.5":
        return call_zai(prompt, model="glm-4.5",
                       max_tokens=length, temperature=temperature, system=system)
    elif provider == "zai-4.6":
        return call_zai(prompt, model="glm-4.6",
                       max_tokens=length, temperature=temperature, system=system)
    elif provider == "kimi":
        return call_kimi(prompt, max_tokens=length, temperature=temperature, system=system)
    elif provider == "qwen":
        return call_deepinfra(prompt, model="Qwen/Qwen3.5-27B",
                              max_tokens=length, temperature=temperature, system=system)
    elif provider == "qwen-fast":
        return call_deepinfra(prompt, model="Qwen/Qwen3-14B",
                              max_tokens=length, temperature=temperature, system=system)
    elif provider == "seed":
        return call_deepinfra(prompt, model="ByteDance/Seed-2.0-mini",
                              max_tokens=length, temperature=temperature, system=system)
    elif provider == "seed-code":
        return call_deepinfra(prompt, model="ByteDance/Seed-2.0-code",
                              max_tokens=length, temperature=temperature, system=system)
    elif provider == "deepseek":
        return call_deepinfra(prompt, model="deepseek-ai/DeepSeek-V3",
                              max_tokens=length, temperature=temperature, system=system)
    elif provider == "stepfun":
        return call_deepinfra(prompt, model="stepfun-ai/Step-3.7-Flash",
                              max_tokens=length, temperature=temperature, system=system)
    elif provider == "granite":
        return call_deepinfra(prompt, model="ibm-granite/granite-4.2-8b",
                              max_tokens=length, temperature=temperature, system=system)
    elif provider == "ling":
        return call_deepinfra(prompt, model="inclusionAI/Ling-3.0-flash",
                              max_tokens=length, temperature=temperature, system=system)
    else:
        raise ValueError(f"unknown provider: {provider}")


if __name__ == "__main__":
    print(call("Write a 3-line poem about the ocean in canon voice.", task="canon", length=300))
