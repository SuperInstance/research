"""
canon_parallel_grower.py — Track L

Grow the canon to 100+ pieces by having multiple LLM voices write new
canon entries in parallel. Each piece:
  - gets a fresh topic
  - writes a 250-400 word canon-shaped piece
  - finds top-K existing pieces via cosine (cite_discoverer logic)
  - cites them in front-matter
  - embeds via Workers AI
  - POSTs to /canon-submit

After this runs: 51 → ~70+ pieces (depending on parallel count), b1 climbs
because every new piece brings its own cites.
"""
from __future__ import annotations
import os, sys, json, time, urllib.request, urllib.error
import concurrent.futures
import numpy as np

ACCT = "049ff5e84ecf636b53b162cbb580aae6"
CANON_NPZ = "/workspace/research/quilt-corpus/quilt_pieces_v3.npz"
SUBMIT_URL = "https://a2a-v3.superinstance.dev/canon-submit"
SEARCH_URL = "https://a2a-v3.superinstance.dev/canon-search"
LIST_URL = "https://a2a-v3.superinstance.dev/canon-list"
EMBED_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/ai/run/@cf/baai/bge-base-en-v1.5"

CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN")

TOPICS = [
    "the canon's 100th witness — what it would say",
    "what a canon forgets when it grows past 100 papers",
    "the bridge essay as a canon's immune response",
    "why every canon needs a witness nobody reads",
    "the cell that doesn't know it's the canonical example",
    "the cost of consensus across heterogeneous substrates",
    "the topology of a canon at 1000 papers",
    "what the operator's view of a 200-piece canon looks like",
    "the substrate's slow drift under witness pressure",
    "how a canon learns to doubt itself",
    "what happens when a bridge essay outlives its sources",
    "the canon's natural frequency — what makes a witness resonate",
    "the cell that writes to the canon and the canon that writes back",
    "the witness log as a memory of a memory",
    "why the merkle root outlives the cell",
    "the canon at half-life",
    "what 50 citation graphs look like at once",
    "the topology of forgetting",
    "the witness that nobody reads and the bridge nobody takes",
    "what the canon would say if asked the right question",
]


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "canon-grower/1.0", **(headers or {})})
    for _ in range(3):
        try:
            return json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception as e:
            print(f"  retry: {e}", file=sys.stderr)
            time.sleep(2)
    return None


def embed_cloudflare(text):
    """Embed via Cloudflare Workers AI."""
    if not CF_TOKEN:
        return None
    body = json.dumps({"text": [text[:2000]]}).encode()
    req = urllib.request.Request(
        EMBED_URL, data=body,
        headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"},
    )
    for _ in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            return json.loads(r.read())["result"]["data"][0]
        except Exception as e:
            time.sleep(2)
    return None


def call_zai(prompt):
    token = os.environ.get("ZAI_TOKEN")
    if not token:
        return None
    body = json.dumps({
        "model": "glm-4.5-flash",
        "messages": [
            {"role": "system", "content": "Write canon-shaped prose. Short paragraphs, image-driven, machine-and-storm metaphors, no headers, no bullets. Stay under 350 words."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 600,
        "temperature": 0.92,
    }).encode()
    req = urllib.request.Request(
        "https://api.z.ai/api/coding/paas/v4/chat/completions",
        data=body, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for _ in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
        except Exception as e:
            time.sleep(2)
    return None


def call_qwen(prompt):
    token = os.environ.get("DEEPINFRA_TOKEN")
    if not token:
        return None
    body = json.dumps({
        "model": "Qwen/Qwen3-14B",
        "messages": [
            {"role": "system", "content": "Write one fresh, surprising paragraph on this topic. Canon-style: short, image-driven, no headers. Under 300 words."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 500,
        "temperature": 1.0,
    }).encode()
    req = urllib.request.Request(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        data=body, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for _ in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
        except Exception as e:
            time.sleep(2)
    return None


def post_piece(tag, title, body, cites):
    payload = json.dumps({"tag": tag, "title": title, "text": body[:1500], "cites": cites}).encode()
    req = urllib.request.Request(
        SUBMIT_URL, data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "canon-grower/1.0"},
        method="POST",
    )
    for _ in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            return json.loads(r.read())
        except Exception as e:
            time.sleep(2)
    return {"ok": False, "err": "max retries"}


def cosine_search(query, k=3):
    """Use the worker's semantic search."""
    url = f"{SEARCH_URL}?q={urllib.parse.quote(query)}&k={k}"
    return fetch(url) or {"matches": []}


def grow_one(topic: str, voice: str) -> dict:
    """Generate one canon piece and submit it."""
    prompt = f"Topic: {topic}\n\nOne fresh canon paragraph. Image-driven, short, under 350 words."
    if voice == "zai":
        body = call_zai(prompt)
    else:
        body = call_qwen(prompt)
    if not body:
        return {"ok": False, "err": f"{voice} call failed", "topic": topic}

    # Find top-K cites via semantic search
    search = cosine_search(body[:500], k=3)
    cites = []
    for m in (search.get("matches") or []):
        if m.get("cosine", 0) > 0.65:
            cites.append(m["tag"])

    # Tag
    safe_topic = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:40]
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    tag = f"grow-{voice}-{timestamp}-{safe_topic}"

    # Submit
    title = topic.capitalize()
    r = post_piece(tag, title, body.strip(), cites)
    return {"ok": r.get("ok"), "tag": tag, "title": title, "body_len": len(body), "cites": cites, "err": r.get("err"), "topic": topic}


def main():
    print("=" * 60)
    print("rune-quilt · canon grower (Track L)")
    print("=" * 60)

    # Pre-flight: get current canon state
    list_r = fetch(LIST_URL)
    if list_r:
        print(f"Starting canon: {list_r['count']} pieces")

    # Run all 20 topics in parallel, alternating voices
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures = []
        for i, topic in enumerate(TOPICS):
            voice = "zai" if i % 2 == 0 else "qwen"
            futures.append(ex.submit(grow_one, topic, voice))
        for fut in concurrent.futures.as_completed(futures):
            try:
                r = fut.result(timeout=120)
            except Exception as e:
                r = {"ok": False, "err": str(e)}
            results.append(r)
            status = "✓" if r.get("ok") else "✗"
            tag = r.get("tag", "?")[:50]
            cites = len(r.get("cites", []))
            print(f"  {status} [{r.get('voice', '?')}] {tag:50} cites={cites}")

    print()
    ok_count = sum(1 for r in results if r.get("ok"))
    print(f"Done: {ok_count}/{len(results)} pieces written")

    # New canon state
    list_r = fetch(LIST_URL)
    if list_r:
        print(f"Ending canon: {list_r['count']} pieces")

    b1 = fetch("https://a2a-v3.superinstance.dev/canon-b1")
    if b1:
        print(f"New b1: V={b1['V']}, E={b1['E']}, C={b1['C']}, b1={b1['b1']}")

    # Save report
    report_file = "/tmp/canon-grower-report.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Report saved: {report_file}")


import re
if __name__ == "__main__":
    main()
