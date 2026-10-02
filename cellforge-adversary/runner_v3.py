"""Multi-LLM Adversary runner v3 — fixed Groq, more voices.

Working voice list (verified Sept 23, 2026):
- Groq: qwen/qwen3.8-27b (returns text directly), openai/gpt-oss-120b (reasoning model)
- DeepInfra: NousResearch/Hermes-3-Llama-3.1-405B, ByteDance/Seed-2.0-pro, 
              Qwen/Qwen3-Max-Thinking, mistralai/Mistral-Small-24B-Instruct-2501,
              google/gemma-4-31B-it-Ultra, deepseek-ai/DeepSeek-V4-Pro
- DeepSeek direct: deepseek-reasoner (rate-limited)
- ZAI: glm-4.5-flash (intermittent)
- JEV: api.typesafe.ai/v1/systemone (works!)

Sequential (not concurrent) per Casey's directive.
"""
import datetime
import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

ADVERSARY_BASE = Path("/workspace/research/cellforge-adversary")
ADVERSARY_BASE.mkdir(parents=True, exist_ok=True)
PLAYHEAD_DOC = Path("/workspace/research/cellforge-ideation/CELLFORGE_PLAYHEAD.md")
DEEPINFRA_KEY = os.environ.get("DEEPINFRA_TOKEN", "")
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_TOKEN", "")
GROQ_KEY = os.environ.get("GROQ_TOKEN", "")
ZAI_KEY = os.environ.get("ZAI_TOKEN", "")
TYPESAFEAI_KEY = os.environ.get("TYPESAFEAI_KEY", "")


def call_deepinfra(model: str, prompt: str, max_tokens: int = 1500) -> Optional[str]:
    if not DEEPINFRA_KEY: return None
    body = json.dumps({
        "model": model, "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens, "temperature": 0.7,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.deepinfra.com/v1/openai/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {DEEPINFRA_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "curl/7.88.0",
            },
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERR {type(e).__name__}: {str(e)[:80]}]"


def call_groq(prompt: str, model: str = "qwen/qwen3.8-27b", max_tokens: int = 1500) -> Optional[str]:
    """Groq — needs explicit User-Agent (Cloudflare 1010 blocking)."""
    if not GROQ_KEY: return None
    body = json.dumps({
        "model": model, "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens, "temperature": 0.7,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "curl/7.88.0",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            d = json.loads(resp.read())
            return d["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERR {type(e).__name__}: {str(e)[:80]}]"


def call_zai(prompt: str, model: str = "glm-4.5-flash", max_tokens: int = 1500) -> Optional[str]:
    """ZAI — glm-4.5-flash works when budget allows."""
    if not ZAI_KEY: return None
    body = json.dumps({
        "model": model, "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens, "temperature": 0.7,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.z.ai/api/paas/v4/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {ZAI_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "curl/7.88.0",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERR {type(e).__name__}: {str(e)[:80]}]"


def call_deepseek(prompt: str, model: str = "deepseek-reasoner", max_tokens: int = 1500) -> Optional[str]:
    if not DEEPSEEK_KEY: return None
    body = json.dumps({
        "model": model, "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "curl/7.88.0",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERR {type(e).__name__}: {str(e)[:80]}]"


def call_jev(state: str, questions: dict) -> dict:
    """JEV (Joint Embedding Validator) — api.typesafe.ai/v1/systemone.

    questions is a dict {name: {type: 'score'|'noul'|'choice', instructions: ..., criteria: [...]}}
    """
    if not TYPESAFEAI_KEY: return {}
    body = json.dumps({
        "model": "jev-latest",
        "state": state,
        "questions": questions,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.typesafe.ai/v1/systemone",
            data=body,
            headers={
                "Authorization": f"Bearer {TYPESAFEAI_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "curl/7.88.0",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:80]}"}


ADVERSARY_PROMPT = """You are the Adversary in a Generator-Adversary design loop.

The Generator just designed cellforge v0.4.0 — a cellular-substrate ML training
system. The dispatcher cell has 6 modes (IDLE/PLAYING/PAUSED/REWINDING/PREDICTING/EXPERIMENTAL),
11 cell kinds, JEV oracle integration, JEPA stub, vector-clock witness chain.

Read the design doc briefly:

{playhead_doc}

Find 3 specific things from your unique lens:

{voice_angle}

Format:
## Finding 1: <title>
<concrete example>

## Finding 2: <title>
<concrete example>

## Finding 3: <title>
<concrete example>
"""

VOICE_ANGLES = {
    # Groq
    "groq_qwen": "\n[Voice: Groq qwen3.8-27b — efficient direct content. Focus on what's PRACTICAL and what SHIPS.]",
    "groq_gpt_oss": "\n[Voice: Groq gpt-oss-120b — reasoning model. Focus on hidden logic and causal chains.]",
    # DeepInfra
    "di_hermes": "\n[Voice: Hermes-405B — PHILOSOPHICAL and METHODOLOGICAL. What pattern is this part of? What does it become in 5 years?]",
    "di_seed_pro": "\n[Voice: Seed-2.0-pro — production reality check. What's the smallest shippable version? What should be cut?]",
    "di_qwen_thinking": "\n[Voice: Qwen3-Max-Thinking — rigorous mathematical thinking. Find the deepest hidden assumption about TIME or STATE.]",
    "di_mistral": "\n[Voice: Mistral-Small-24B — efficiency. Drop features to ship faster.]",
    "di_gemma": "\n[Voice: Gemma-4 — pedagogical. If a 10-year-old asked 'what is this for', what's the answer? Where does it break for non-experts?]",
    "di_deepseek_pro": "\n[Voice: DeepSeek-V4-Pro — high-concept. What is cellforge REALLY for? Where does it sit relative to GPT/Claude?]",
    # ZAI
    "zai": "\n[Voice: ZAI glm-4.5-flash — deep reasoning. Find orthogonal assumptions the Generator misses.]",
    # JEV (oracle)
    "jev": "\n[Voice: JEV oracle. Score the cellforge design on canon, novelty, paradigm-shift, inversion.]",
}


def run_round_v3(round_num: int, voices: list, prompt_context: str = "") -> Path:
    """Run voices SEQUENTIALLY with small delay to avoid rate limits."""
    out_path = ADVERSARY_BASE / f"round_{round_num}.md"
    started = datetime.datetime.utcnow().isoformat() + "Z"
    context = prompt_context or PLAYHEAD_DOC.read_text()[:6000]
    print(f"[round {round_num}] running {len(voices)} voices sequentially...")

    t0 = time.time()
    results = {}

    for i, voice in enumerate(voices):
        # Small delay between voices to avoid rate limits
        if i > 0:
            time.sleep(1.5)
        angle = VOICE_ANGLES.get(voice, "")
        if voice == "jev":
            r = call_jev(context, questions={
                'canon_score': {
                    'type': 'score',
                    'instructions': 'How canon-worthy is this cellforge design?',
                    'criteria': ['Spam', 'Derivative', 'Solid canon', 'Brilliant paradigm']
                },
                'novelty': {
                    'type': 'score',
                    'instructions': 'How novel is the state/execution inversion?',
                    'criteria': ['Same-old', 'Remix', 'Notable shift', 'Genuinely paradigm-shifting']
                },
                'is_inversion': {
                    'type': 'noul',
                    'instructions': 'Does this invert the state/execution relationship?'
                }
            })
            r_text = json.dumps(r, indent=2) if r else "[empty]"
        else:
            prompt = ADVERSARY_PROMPT.format(playhead_doc=context, voice_angle=angle)
            if voice == "zai":
                r_text = call_zai(prompt)
            elif voice == "groq_qwen":
                r_text = call_groq(prompt, model="qwen/qwen3.8-27b")
            elif voice == "groq_gpt_oss":
                r_text = call_groq(prompt, model="openai/gpt-oss-120b", max_tokens=2000)
            elif voice == "di_hermes":
                r_text = call_deepinfra(model="NousResearch/Hermes-3-Llama-3.1-405B", prompt=prompt)
            elif voice == "di_seed_pro":
                r_text = call_deepinfra(model="ByteDance/Seed-2.0-pro", prompt=prompt)
            elif voice == "di_qwen_thinking":
                r_text = call_deepinfra(model="Qwen/Qwen3-Max-Thinking", prompt=prompt)
            elif voice == "di_mistral":
                r_text = call_deepinfra(model="mistralai/Mistral-Small-24B-Instruct-2501", prompt=prompt)
            elif voice == "di_gemma":
                r_text = call_deepinfra(model="google/gemma-4-31B-it-Ultra", prompt=prompt)
            elif voice == "di_deepseek_pro":
                r_text = call_deepinfra(model="deepseek-ai/DeepSeek-V4-Pro", prompt=prompt)
            else:
                r_text = None
        results[voice] = r_text
        ok = r_text and not r_text.startswith("[")
        print(f"  [{voice}] {'OK' if ok else 'skip/error'}")
    dt = time.time() - t0

    with open(out_path, "w") as f:
        f.write(f"# Adversary Round {round_num}\n\n")
        f.write(f"**Date**: {started}\n")
        f.write(f"**Duration**: {dt:.1f}s sequential\n")
        f.write(f"**Voices**: {', '.join(voices)}\n\n---\n\n")
        for v, r in results.items():
            f.write(f"## {v}\n\n")
            f.write((r or "*(none)*") + "\n\n---\n\n")
    print(f"[round {round_num}] wrote {out_path} in {dt:.1f}s")
    return out_path


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    voices = sys.argv[2:] if len(sys.argv) > 2 else [
        "groq_qwen", "di_seed_pro", "di_qwen_thinking", "di_hermes",
        "di_mistral", "di_gemma", "di_deepseek_pro", "jev"
    ]
    run_round_v3(n, voices)
