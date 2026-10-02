"""
taps_creative_break.py
======================

A creative-break cell. Three voices in parallel; one beat per call.
Each round:
  - Voice A (deepseek-chat): opens with a short canon-shaped thought
  - Voice B (deepseek-coder): responds with the structural view
  - Voice C (ByteDance Seed-2.0-mini): answers with the cheap-fresh view
All three are written to the canon and embedded.

This is the writers' room at taps.
"""

from __future__ import annotations
import os, sys, json, time, urllib.request, urllib.error
import concurrent.futures
import numpy as np
from datetime import datetime

sys.path.insert(0, '/workspace/research/superinstance-advisor')

PROMPTS_FILE = "/workspace/research/superinstance-advisor/data/taps_prompts.jsonl"
OUTPUT_DIR = "/workspace/research/superinstance-advisor/canon/taps"
LOG_FILE = "/workspace/research/superinstance-advisor/canon/taps/_log.jsonl"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================================
# LLM providers
# ============================================================================

def call_deepseek(model: str, prompt: str, max_tokens: int = 800) -> str:
    token = os.environ.get("DEEPSEEK_TOKEN")
    if not token:
        return "[no deepseek token]"
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "You write canon-shaped prose. Short paragraphs, machine-and-storm metaphors, no headers, no bullet points. Stay under 400 words."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.9,
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            d = json.loads(r.read())
            return d["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            return f"[deepseek http {e.code}: {e.read().decode()[:120]}]"
        except Exception as e:
            print(f"  retry {attempt+1}: {e}", file=sys.stderr)
            time.sleep(2)
    return "[deepseek failed]"


def call_deepinfra(prompt: str, max_tokens: int = 800, model: str = "Qwen/Qwen3-14B") -> str:
    token = os.environ.get("DEEPINFRA_TOKEN")
    if not token:
        return "[no deepinfra token]"
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "Write one fresh, surprising paragraph on this topic. Canon-style: short, image-driven, no headers. Under 250 words."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 1.0,
    }).encode()
    req = urllib.request.Request(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            d = json.loads(r.read())
            return d["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            return f"[deepinfra http {e.code}]"
        except Exception as e:
            print(f"  retry {attempt+1}: {e}", file=sys.stderr)
            time.sleep(2)
    return "[deepinfra failed]"


def call_zai(prompt: str, max_tokens: int = 800) -> str:
    token = os.environ.get("ZAI_TOKEN")
    if not token:
        return "[no zai token]"
    body = json.dumps({
        "model": "glm-4.5-flash",
        "messages": [
            {"role": "system", "content": "Write canon-shaped prose. Image-driven, short paragraphs. Under 300 words."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.85,
    }).encode()
    req = urllib.request.Request(
        "https://api.z.ai/api/coding/paas/v4/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            d = json.loads(r.read())
            return d["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            return f"[zai http {e.code}: {e.read().decode()[:120]}]"
        except Exception as e:
            print(f"  retry {attempt+1}: {e}", file=sys.stderr)
            time.sleep(2)
    return "[zai failed]"


def call_kimi(prompt: str, max_tokens: int = 800) -> str:
    """Kimi K2.7 via Cloudflare Workers AI (free)."""
    token = os.environ.get("CLOUDFLARE_TOKEN")
    if not token:
        return "[no cloudflare token]"
    body = json.dumps({
        "messages": [
            {"role": "system", "content": "You are a thoughtful voice at the writers' round table. Canon voice, short paragraphs, under 300 words."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.9,
    }).encode()
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/accounts/049ff5e84ecf636b53b162cbb580aae6/ai/run/@cf/moonshotai/kimi-k2.7-code",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            d = json.loads(r.read())
            return d["result"]["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            return f"[kimi http {e.code}: {e.read().decode()[:120]}]"
        except Exception as e:
            print(f"  retry {attempt+1}: {e}", file=sys.stderr)
            time.sleep(2)
    return "[kimi failed]"


# ============================================================================
# Creative-break round
# ============================================================================

def run_round(topic: str, voices: list[str]) -> dict:
    """Run three voices in parallel on the same topic, then a recap where each voice responds to the others."""
    print(f"\n{'='*60}\nTAPS · {topic}\n{'='*60}")

    # Each voice gets a slightly different angle on the topic
    angles = {
        "deepseek-chat": f"Open this canon beat. The topic is: {topic}. One short paragraph. What does the canon say?",
        "deepseek-coder": f"Respond to this canon topic: {topic}. From the structural view — what shape is it? One short paragraph.",
        "deepseek-reasoner": f"What is the deep truth under this canon topic: {topic}? Reason about it. One short paragraph.",
        "seed-mini": f"Topic: {topic}. One fresh paragraph. Canon voice, image-driven, no obvious answers.",
        "qwen": f"Topic: {topic}. One fresh paragraph, canon voice, under 250 words. Image-driven.",
        "zai": f"Topic: {topic}. Write a single canon paragraph, under 250 words.",
        "kimi": f"Topic: {topic}. Write canon voice — short, image-driven, under 250 words. What surprised you?",
    }

    # First round: each voice's opening
    print("\n--- ROUND 1: OPENINGS ---\n")
    calls = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(voices)) as ex:
        for v in voices:
            if v.startswith("deepseek"):
                calls.append((v, ex.submit(call_deepseek, v.replace("deepseek-", "deepseek-"), angles.get(v, angles["deepseek-chat"]))))
            elif v == "qwen":
                calls.append((v, ex.submit(call_deepinfra, angles.get(v, angles["qwen"]))))
            elif v == "zai":
                calls.append((v, ex.submit(call_zai, angles["zai"])))
            elif v == "kimi":
                calls.append((v, ex.submit(call_kimi, angles["kimi"])))

        results = []
        for name, fut in calls:
            try:
                text = fut.result(timeout=120)
            except Exception as e:
                text = f"[error: {e}]"
            results.append({"voice": name, "text": text})
            print(f"\n--- {name} ---\n{text[:400]}\n")

    # Second round: each voice writes 2 sentences responding to the others
    print("\n--- ROUND 2: CROSS-RESPONSE (each voice reads the others) ---\n")
    others_text = "\n\n".join([f"[{r['voice']}]: {r['text'][:300]}" for r in results])
    recap_prompt = f"Three other voices already wrote on: {topic}\n\n{others_text}\n\nIn two sentences, respond — agree, push back, or build on something another voice said. Canon voice."
    recaps = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(voices)) as ex:
        recap_calls = []
        for v in voices:
            if v.startswith("deepseek"):
                recap_calls.append((v, ex.submit(call_deepseek, "deepseek-chat", recap_prompt, max_tokens=200)))
            elif v == "qwen":
                recap_calls.append((v, ex.submit(call_deepinfra, recap_prompt, max_tokens=200)))
            elif v == "zai":
                recap_calls.append((v, ex.submit(call_zai, recap_prompt, max_tokens=200)))
            elif v == "kimi":
                recap_calls.append((v, ex.submit(call_kimi, recap_prompt, max_tokens=200)))

        for name, fut in recap_calls:
            try:
                text = fut.result(timeout=30)
            except Exception as e:
                text = f"[recap timeout: {type(e).__name__}]"
            recaps.append({"voice": name, "text": text})
            print(f"\n--- {name} RECAP ---\n{text[:300]}\n")

    return {
        "topic": topic,
        "round_at": datetime.utcnow().isoformat() + "Z",
        "openings": results,
        "recaps": recaps,
    }


def write_to_canon(round_data: dict) -> str:
    """Write the round to canon and embed. Returns the filename."""
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    topic_slug = round_data["topic"][:40].lower().replace(" ", "-").replace("?", "").replace(",", "")
    tag = f"taps-{timestamp}-{topic_slug}"
    body = f"# Taps · {round_data['topic']}\n\n*{round_data['round_at']}*\n\n"
    body += "## Round 1 — Openings\n\n"
    for v in round_data["openings"]:
        body += f"### {v['voice']}\n\n{v['text']}\n\n"
    body += "\n## Round 2 — Cross-response\n\n"
    body += "*Each voice reads the others, then replies.*\n\n"
    for v in round_data["recaps"]:
        body += f"**{v['voice']}:** {v['text']}\n\n"
    body += "\n---\n*Three voices, two rounds, one canon entry. Taps.*\n"

    fname = f"{OUTPUT_DIR}/{tag}.md"
    with open(fname, "w") as f:
        f.write(body)
    return fname, tag


def embed_and_submit(tag: str, body: str):
    """Embed via Workers AI and POST to canon-submit."""
    token = os.environ.get("CLOUDFLARE_TOKEN")
    if not token:
        print("  (no CF token, skipping embed)")
        return

    # Embed
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/accounts/049ff5e84ecf636b53b162cbb580aae6/ai/run/@cf/baai/bge-base-en-v1.5",
        data=json.dumps({"text": [body[:1500]]}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        r = urllib.request.urlopen(req, timeout=60)
        vec = json.loads(r.read())["result"]["data"][0]
    except Exception as e:
        print(f"  embed failed: {e}")
        return

    # Submit
    req2 = urllib.request.Request(
        "https://a2a-v3.superinstance.dev/canon-submit",
        data=json.dumps({"tag": tag, "title": f"Taps — {tag}", "text": body[:1500]}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "taps/1.0"},
    )
    try:
        r = urllib.request.urlopen(req2, timeout=60)
        result = json.loads(r.read())
        print(f"  → canon: {result.get('ok')}")
    except Exception as e:
        print(f"  submit failed: {e}")


def main():
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        # Default topic rotation
        topics = [
            "what does a canon feel like to write for, at 3am?",
            "the cell that has outlived its substrate",
            "memory vs. address — which one is the canon?",
            "the cost of a witness nobody reads",
            "what happens between TICK and TICK?",
            "the empty cell — when bindings leave",
            "why does the bridge essay survive longer than its source?",
            "the difference between a canon and a corpus",
            "what does the 100th witness feel like?",
            "the cell that doesn't know it's a cell",
        ]
        import random
        topic = random.choice(topics)

    print(f"Topic: {topic}")

    voices = ["zai", "qwen", "kimi"]
    round_data = run_round(topic, voices)

    fname, tag = write_to_canon(round_data)
    print(f"\nWrote: {fname}")

    with open(fname) as f:
        body = f.read()
    embed_and_submit(tag, body)

    # Log
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(round_data) + "\n")

    print(f"\n[done]")


if __name__ == "__main__":
    main()
