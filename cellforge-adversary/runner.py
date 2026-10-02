"""
Multi-LLM Adversary runner for cellforge ideation.

Calls 5+ LLMs in parallel (ZAI glm-4.5, Groq llama-3.3-70b, DeepSeek flash,
DeepInfra hermes-405b, DeepInfra seed-mini) plus MOTH (substrate-quantum oracle).
Each gets a different angle of the Adversary prompt. Aggregates, runs JEV-style
promotion gate, writes top insights to round doc.

Designed for cheap/fast parallel execution:
- ZAI: 20x max plan, use extensively
- Groq: cheap/fast, novel angle
- DeepSeek flash: cheap/fast, different model-view
- DeepInfra: diverse models in parallel

Output: /workspace/research/cellforge-adversary/round_<N>.md
"""
import datetime
import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# CONFIG
# ============================================================

ADVERSARY_BASE = Path("/workspace/research/cellforge-adversary")
ADVERSARY_BASE.mkdir(parents=True, exist_ok=True)
PLAYHEAD_DOC = Path("/workspace/research/cellforge-ideation/CELLFORGE_PLAYHEAD.md")

# Load API keys
ZAI_KEY = os.environ.get("ZAI_TOKEN", "")
GROQ_KEY = os.environ.get("GROQ_TOKEN", "")
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_TOKEN", "")
DEEPINFRA_KEY = os.environ.get("DEEPINFRA_TOKEN", "")
MOTH_KEY = os.environ.get("MOTH_API_KEY", "")


# ============================================================
# VOICES (each calls a different LLM with a different angle)
# ============================================================

def call_zai(prompt: str, model: str = "glm-4.5", max_tokens: int = 2000) -> Optional[str]:
    """ZAI glm-4.5 — main deep reasoning voice."""
    if not ZAI_KEY:
        return None
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.z.ai/api/paas/v4/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {ZAI_KEY}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[zai ERROR: {type(e).__name__}: {e}]"


def call_groq(prompt: str, model: str = "llama-3.3-70b-versatile", max_tokens: int = 2000) -> Optional[str]:
    """Groq — fast, novel angle."""
    if not GROQ_KEY:
        return None
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.8,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[groq ERROR: {type(e).__name__}: {e}]"


def call_deepseek(prompt: str, model: str = "deepseek-chat", max_tokens: int = 2000) -> Optional[str]:
    """DeepSeek — different model-view, cheap/fast."""
    if not DEEPSEEK_KEY:
        return None
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_KEY}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[deepseek ERROR: {type(e).__name__}: {e}]"


# Correct model names on DeepInfra (verified Sept 23, 2026)
DEEPINFRA_HERMES = "NousResearch/Hermes-3-Llama-3.1-405B"  # 405B variant
DEEPINFRA_SEED = "ByteDance/Seed-2.0-mini"  # smaller / faster
DEEPINFRA_QWEN_MAX = "Qwen/Qwen3.8-Max"  # if available
DEEPINFRA_LLAMA4 = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
DEEPINFRA_DEEPSEEK_FLASH = "deepseek-ai/DeepSeek-V4-Flash"


def call_deepinfra(prompt: str, model: str, max_tokens: int = 2000) -> Optional[str]:
    """DeepInfra — diverse models (hermes-405b, seed-mini, etc)."""
    if not DEEPINFRA_KEY:
        return None
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode()
    endpoints = [
        "https://api.deepinfra.com/v1/openai/chat/completions",
        "https://api.deepinfra.com/v1/chat/completions",
    ]
    last_err = None
    for url in endpoints:
        try:
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Authorization": f"Bearer {DEEPINFRA_KEY}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            continue
    return f"[deepinfra ERROR: {type(last_err).__name__}: {last_err}]"


def call_moth(prompt: str) -> Optional[str]:
    """MOTH — substrate-quantum oracle. Different angle entirely."""
    if not MOTH_KEY:
        return None
    # MOTH is a substrate-quantum canary endpoint — call it as oracle
    body = json.dumps({
        "operation": "adversary_poke",
        "prompt": prompt,
        "substrate": "cellforge-playhead",
    }).encode()
    try:
        req = urllib.request.Request(
            "https://api.mothquantum.com/v1/canary",
            data=body,
            headers={
                "Authorization": f"Bearer {MOTH_KEY}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return data.get("oracle_response", data.get("text", str(data)))
    except Exception as e:
        return f"[moth ERROR: {type(e).__name__}: {e}]"


# ============================================================
# PROMPT ANGLES (each voice gets a slightly different question)
# ============================================================

ADVERSARY_BASE_PROMPT = """You are the Adversary in a Generator-Adversary design loop.

The Generator just proposed a design for cellforge's dispatcher cell — a state machine
with 7 modes (IDLE/PLAYING/PAUSED/REWINDING/PREDICTING/COMPARING/BACKTESTING) plus 4
new cell kinds (REPLAY_CELL, PREDICTION_CELL, TIMELINE_CELL, EXPERIMENT_LEDGER).

Your job: find what's BROKEN or HIDDEN. Find the orthogonal assumption. Don't just
restate what's there — poke the holes the Generator doesn't want to admit.

Read this design doc:

{playhead_doc}

Now find 3 specific things:
1. A hidden assumption the Generator made that could break at scale
2. An orthogonal concept that's NOT in the design but should be
3. A test case that would prove the design wrong

Be concrete. Give examples. No fluff.

{voice_specific}

Format your response as:

## Finding 1: <title>
<explanation with concrete example>

## Finding 2: <title>
<explanation with concrete example>

## Finding 3: <title>
<explanation with concrete example>
"""

VOICE_ANGLES = {
    "zai": "\n[Voice: ZAI glm-4.5 — think deeply about state machine correctness, race conditions, and what happens at zone boundaries.]",
    "groq": "\n[Voice: Groq llama-3.3-70b — think about novel/orthogonal metaphors. What if the dispatcher is something else entirely? What if the cell kinds should be different?]",
    "deepseek": "\n[Voice: DeepSeek — think about practical ML training realities. What breaks when you actually try to use this on a real transformer training run?]",
    "deepinfra_hermes": "\n[Voice: DeepInfra Hermes-3-405B — think philosophically and methodologically. What is this REALLY for? What does it become in 5 years?]",
    "deepinfra_seed": "\n[Voice: DeepInfra Seed-2.0-mini — be minimalist. What's the ONE thing that matters? Strip everything else away.]",
    "deepinfra_qwen": "\n[Voice: DeepInfra Qwen3.8-Max — think about scale, multi-modality, and what this becomes when 100 zones are running simultaneously.]",
    "deepinfra_llama4": "\n[Voice: DeepInfra Llama-4-Maverick — think like a frontier model trainer. What's the killer app? What does Meta / DeepMind need that this solves?]",
    "deepinfra_deepseek": "\n[Voice: DeepInfra DeepSeek-V4-Flash — think about cheap/fast iteration. What if every developer could run this on a laptop?]",
    "moth": "\n[Voice: MOTH substrate-quantum oracle — speak from substrate perspective. What does the WITNESS chain actually mean? What's the geometry of forked ledgers?]",
}


# ============================================================
# PARALLEL EXECUTION
# ============================================================

def run_voice(name: str, model: Optional[str], prompt: str) -> Tuple[str, str, Optional[str]]:
    """Run one voice, return (voice_name, prompt_used, response)."""
    voice_specific = VOICE_ANGLES.get(name, "")
    full_prompt = ADVERSARY_BASE_PROMPT.format(
        playhead_doc=PLAYHEAD_DOC.read_text()[:8000],  # truncate to fit
        voice_specific=voice_specific,
    )
    if name == "zai":
        resp = call_zai(full_prompt)
    elif name == "groq":
        resp = call_groq(full_prompt)
    elif name == "deepseek":
        resp = call_deepseek(full_prompt)
    elif name == "deepinfra_hermes":
        resp = call_deepinfra(full_prompt, model or DEEPINFRA_HERMES)
    elif name == "deepinfra_seed":
        resp = call_deepinfra(full_prompt, model or DEEPINFRA_SEED)
    elif name == "deepinfra_qwen":
        resp = call_deepinfra(full_prompt, model or DEEPINFRA_QWEN_MAX)
    elif name == "deepinfra_llama4":
        resp = call_deepinfra(full_prompt, model or DEEPINFRA_LLAMA4)
    elif name == "deepinfra_deepseek":
        resp = call_deepinfra(full_prompt, model or DEEPINFRA_DEEPSEEK_FLASH)
    elif name == "moth":
        resp = call_moth(full_prompt)
    else:
        resp = None
    return (name, full_prompt, resp)


def run_round(round_num: int, voices: List[str] = None) -> Path:
    """Run one Adversary round, write results."""
    if voices is None:
        voices = ["zai", "groq", "deepseek", "deepinfra_hermes", "deepinfra_seed",
                  "deepinfra_qwen", "deepinfra_llama4", "deepinfra_deepseek", "moth"]

    print(f"[adversary round {round_num}] launching {len(voices)} voices in parallel...")
    t0 = time.time()
    results = {}
    with ThreadPoolExecutor(max_workers=len(voices)) as ex:
        futures = {ex.submit(run_voice, v, None, ""): v for v in voices}
        for fut in as_completed(futures):
            name, prompt, resp = fut.result()
            results[name] = resp
            print(f"  [{name}] {'OK' if resp and not resp.startswith('[') else 'skip/error'}")
    dt = time.time() - t0
    print(f"[adversary round {round_num}] done in {dt:.1f}s")

    # Write round doc
    round_path = ADVERSARY_BASE / f"round_{round_num}.md"
    with open(round_path, "w") as f:
        f.write(f"# Adversary Round {round_num}\n\n")
        f.write(f"**Date**: {datetime.datetime.utcnow().isoformat()}Z\n")
        f.write(f"**Duration**: {dt:.1f}s\n")
        f.write(f"**Voices**: {', '.join(voices)}\n\n")
        f.write("---\n\n")
        for name, resp in results.items():
            f.write(f"## {name}\n\n")
            if resp:
                f.write(resp + "\n\n")
            else:
                f.write("*(no response)*\n\n")
            f.write("---\n\n")

    print(f"[adversary round {round_num}] wrote {round_path}")
    return round_path


# ============================================================
# JEV-STYLE PROMOTION (cosine similarity across findings)
# ============================================================

def fnv1a_64(s: str) -> int:
    h = 0xcbf29ce484222325
    for b in s.encode("utf-8"):
        h = h ^ b
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h


def jaccard_similarity(a: str, b: str) -> float:
    """Token-level Jaccard. Cheap proxy for semantic similarity."""
    a_tokens = set(a.lower().split())
    b_tokens = set(b.lower().split())
    if not a_tokens or not b_tokens:
        return 0.0
    intersection = a_tokens & b_tokens
    union = a_tokens | b_tokens
    return len(intersection) / len(union)


def promote_findings(round_num: int, threshold: float = 0.3) -> Path:
    """Find findings that appear across multiple voices (JEV-style promotion)."""
    round_doc = ADVERSARY_BASE / f"round_{round_num}.md"
    text = round_doc.read_text()

    # Extract findings (## Finding N: ...)
    import re
    findings = re.findall(r"## Finding \d+: (.+?)(?:\n)([\s\S]*?)(?=\n## Finding|\n## \w+\n|\Z)", text)
    if not findings:
        # Try voice section format
        sections = re.split(r"\n## (\w+)\n", text)
        # Pair them up
        findings = []
        for i in range(1, len(sections), 2):
            voice = sections[i]
            content = sections[i+1] if i+1 < len(sections) else ""
            findings.append((voice, content))

    # Pairwise similarity
    n = len(findings)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = jaccard_similarity(findings[i][1], findings[j][1])

    # Average similarity per finding (proxy for "appears across voices")
    avg_sim = [sum(matrix[i]) / max(n - 1, 1) for i in range(n)]

    # Sort by average similarity (high = appears in multiple voices)
    ranked = sorted(zip(findings, avg_sim), key=lambda x: -x[1])

    promoted_path = ADVERSARY_BASE / f"promoted_{round_num}.md"
    with open(promoted_path, "w") as f:
        f.write(f"# Promoted Findings — Round {round_num}\n\n")
        f.write(f"**Date**: {datetime.datetime.utcnow().isoformat()}Z\n")
        f.write(f"**Threshold**: avg pairwise Jaccard >= {threshold}\n\n")
        f.write(f"**Method**: Jaccard token similarity across {n} voice responses. ")
        f.write(f"High average similarity = finding recurs across voices = canon-worthy.\n\n")
        f.write("---\n\n")
        for (title, content), score in ranked:
            promoted = score >= threshold
            tag = "🟢 **CANON**" if promoted else "🟡 noise"
            f.write(f"## {title} — Jaccard {score:.3f} {tag}\n\n")
            f.write(content[:2000] + "\n\n")
            f.write("---\n\n")
    print(f"[promotion] wrote {promoted_path}")
    return promoted_path


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "promote":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        promote_findings(n)
    else:
        n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        voices = sys.argv[2:] if len(sys.argv) > 2 else None
        run_round(n, voices)
