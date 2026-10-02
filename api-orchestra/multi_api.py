"""
Multi-API orchestra for parallel agent work.

Works with: DeepInfra + DeepSeek (the ones that respond with our tokens).
"""

import os
import json
import asyncio
from typing import List, Dict, Optional, Any
import urllib.request
import urllib.error

PROVIDERS = {
    "deepinfra": {
        "token_env": "DEEPINFRA_TOKEN",
        "base": "https://api.deepinfra.com/v1/openai",
        # Note: Qwen3 models use reasoning mode and return empty content.
        # Prefer non-reasoning models for chat tasks.
        "models": [
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",   # FAST, no reasoning
            "google/gemini-3.1-flash-lite",                   # FLASH, no reasoning
            "mistralai/Mistral-Small-3.2-24B-Instruct-2506",  # Medium, no reasoning
            "meta-llama/Llama-3.3-70B-Instruct-Turbo",        # Large
            "google/gemma-3-27b-it",                          # Medium
            "Qwen/Qwen2.5-72B-Instruct",                      # Qwen 2.5 (no reasoning)
            "Qwen/Qwen2.5-7B-Instruct",                       # Qwen 2.5 small (no reasoning)
        ],
    },
    "deepseek": {
        "token_env": "DEEPSEEK_TOKEN",
        "base": "https://api.deepseek.com/v1",
        "models": [
            "deepseek-chat",
            "deepseek-reasoner",
        ],
    },
}


def get_token(provider: str) -> str:
    return os.environ.get(PROVIDERS[provider]["token_env"], "")


def chat(provider: str, messages: List[Dict], model: Optional[str] = None,
         max_tokens: int = 1024, temperature: float = 0.7, timeout: int = 30) -> str:
    """Sync chat call to any provider."""
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")

    cfg = PROVIDERS[provider]
    token = get_token(provider)
    if not token:
        return f"[{provider} no token]"

    model = model or cfg["models"][0]

    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    url = cfg["base"] + "/chat/completions"
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                  headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"[{provider}/{model} HTTP {e.code}]"
    except Exception as e:
        return f"[{provider}/{model} ERROR: {str(e)[:80]}]"


async def achat(provider: str, messages: List[Dict], model: Optional[str] = None,
                max_tokens: int = 1024, temperature: float = 0.7) -> str:
    """Async chat wrapper."""
    return await asyncio.to_thread(chat, provider, messages, model, max_tokens, temperature)


async def parallel_chat(calls: List[Dict]) -> List[str]:
    """Run multiple chat calls in parallel."""
    tasks = []
    for c in calls:
        tasks.append(achat(
            c["provider"],
            c["messages"],
            c.get("model"),
            c.get("max_tokens", 1024),
            c.get("temperature", 0.7)
        ))
    return await asyncio.gather(*tasks, return_exceptions=True)


# Speed tiers per model (1=fastest, 5=slowest)
SPEED_TIERS = {
    "Qwen/Qwen2.5-7B-Instruct": 1,
    "google/gemini-3.1-flash-lite": 1,
    "meta-llama/Llama-3.3-70B-Instruct-Turbo": 2,
    "mistralai/Mistral-Small-3.2-24B-Instruct-2506": 2,
    "Qwen/Qwen2.5-72B-Instruct": 3,
    "google/gemma-3-27b-it": 3,
    "Qwen/Qwen3-Next-80B-A3B-Instruct": 4,
    "deepseek-ai/DeepSeek-V3": 4,
    "deepseek-chat": 4,
    "deepseek-reasoner": 5,
}


if __name__ == "__main__":
    test_msg = [{"role": "user", "content": "Reply with just 'OK'."}]
    for model in PROVIDERS["deepinfra"]["models"][:4]:
        result = chat("deepinfra", test_msg, model=model, max_tokens=10)
        print(f"{model}: {result[:50]}")
    result = chat("deepseek", test_msg, model="deepseek-chat", max_tokens=10)
    print(f"deepseek-chat: {result[:50]}")
