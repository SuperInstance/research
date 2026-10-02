"""Sequential multi-model Adversary runner. Casey noted DeepInfra can be flaky
under concurrency, so this runner does each voice rapidly in sequence (not parallel).

Voices: DeepSeek-V4-Pro (high-concept), Seed-2.0-pro (production grade),
Qwen3-Max-Thinking (reasoning), Mistral-Small (efficient), Gemma-4 (compact
frontier), Hermes-3-405B (philosophical).

Each voice gets the same Adversary prompt but with voice-specific angle.
Total run: ~30-90 seconds sequential.
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
from typing import Optional, Tuple

ADVERSARY_BASE = Path("/workspace/research/cellforge-adversary")
ADVERSARY_BASE.mkdir(parents=True, exist_ok=True)
PLAYHEAD_DOC = Path("/workspace/research/cellforge-ideation/CELLFORGE_PLAYHEAD.md")
DEEPINFRA_KEY = os.environ.get("DEEPINFRA_TOKEN", "")
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_TOKEN", "")


def call_deepinfra(model: str, prompt: str, max_tokens: int = 1500) -> Optional[str]:
    if not DEEPINFRA_KEY:
        return None
    body = json.dumps({
        "model": model, "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens, "temperature": 0.7,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.deepinfra.com/v1/openai/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {DEEPINFRA_KEY}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"[HTTP {e.code}: {e.read()[:100].decode()}]"
    except Exception as e:
        return f"[{type(e).__name__}: {e}]"


def call_deepseek_pro(prompt: str, max_tokens: int = 2000) -> Optional[str]:
    """DeepSeek Pro via deepseek.com — for high-concept roughing."""
    if not DEEPSEEK_KEY:
        return None
    body = json.dumps({
        "model": "deepseek-reasoner",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"[HTTP {e.code}: {e.read()[:100].decode()}]"
    except Exception as e:
        return f"[{type(e).__name__}: {e}]"


ADVERSARY_PROMPT = """You are the Adversary in a Generator-Adversary design loop.

The Generator just designed cellforge — a Quilt-native ML training substrate where the cell matrix outlives every model architecture. The dispatcher cell has 7 modes (IDLE/PLAYING/PAUSED/REWINDING/PREDICTING/COMPARING/BACKTESTING) plus 5 new cell kinds (REPLAY_CELL, PREDICTION_CELL, TIMELINE_CELL, EXPERIMENT_LEDGER, FORK_VERSION_VECTOR) plus 8 original cell kinds.

Read this brief summary:

{playhead_doc}

Then find 3 specific things from your unique lens:

{voice_angle}

Format your response as:

## Finding 1: <title>
<concrete example>

## Finding 2: <title>
<concrete example>

## Finding 3: <title>
<concrete example>
"""

VOICE_ANGLES = {
    "deepseek_pro": "DeepSeek-Pro lens: think about HIGH CONCEPTS. What is cellforge REALLY for? Where does it sit relative to GPT, Claude, future model architectures? What does it become in 5 years?",
    "seed_pro": "ByteDance-Seed-Pro lens: production-grade reality check. What does the FIRST shipped version need? What's the smallest possible cellforge that demonstrates the inversion?",
    "qwen_max": "Qwen3-Max-Thinking lens: rigorous thinking. Find the deepest hidden assumption about TIME or STATE. What does the witness chain actually mean mathematically?",
    "mistral": "Mistral lens: EFFICIENCY first. What's the simplest implementation that ships? Where can we drop features to ship faster?",
    "gemma": "Gemma-4 lens: pedagogically. If a 10-year-old asked 'what is this for?', what's the answer? Where does the system break for non-experts?",
    "hermes_405": "Hermes-405B lens: PHILOSOPHICAL and METHODOLOGICAL. What pattern is this part of? What's the predecessor in 1960s/1970s/1980s? What's it NOT?",
    "z_interference": "Conway-style interference: how does cellforge INTERFERE with ax-quilt / quilt-ai / mavis-fleet? What breaks across the fleet when cellforge lands?",
}


def run_round_sequential(round_num: int, voices: list) -> Path:
    """Run voices SEQUENTIALLY — Casey noted DeepInfra can be flaky under concurrency."""
    playhead = PLAYHEAD_DOC.read_text()[:6000]
    out_path = ADVERSARY_BASE / f"round_{round_num}.md"
    started = datetime.datetime.utcnow().isoformat() + "Z"

    print(f"[round {round_num}] running {len(voices)} voices sequentially...")
    t0 = time.time()
    results = {}
    for voice in voices:
        angle = VOICE_ANGLES.get(voice, "")
        prompt = ADVERSARY_PROMPT.format(playhead_doc=playhead, voice_angle=angle)
        if voice == "deepseek_pro":
            r = call_deepseek_pro(prompt)
        elif voice == "seed_pro":
            r = call_deepinfra("ByteDance/Seed-2.0-pro", prompt)
        elif voice == "qwen_max":
            r = call_deepinfra("Qwen/Qwen3-Max-Thinking", prompt)
        elif voice == "mistral":
            r = call_deepinfra("mistralai/Mistral-Small-24B-Instruct-2501", prompt)
        elif voice == "gemma":
            r = call_deepinfra("google/gemma-4-31B-it-Ultra", prompt)
        elif voice == "hermes_405":
            r = call_deepinfra("NousResearch/Hermes-3-Llama-3.1-405B", prompt)
        elif voice == "z_interference":
            # Read ax-quilt + cellforge and reason about interference
            extra = "\n\nAlso read /workspace/research/cellforge-ideation/CELLFORGE_PLAYHEAD.md and /workspace/research/cellforge-ideation/COMPARISON_QUILT_AI.md"
            prompt = prompt + extra
            r = call_deepinfra("NousResearch/Hermes-3-Llama-3.1-405B", prompt, max_tokens=2000)
        else:
            r = None
        results[voice] = r
        ok = r and not r.startswith("[")
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
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    voices = sys.argv[2:] if len(sys.argv) > 2 else [
        "deepseek_pro", "seed_pro", "qwen_max",
        "mistral", "gemma", "hermes_405", "z_interference"
    ]
    run_round_sequential(n, voices)
