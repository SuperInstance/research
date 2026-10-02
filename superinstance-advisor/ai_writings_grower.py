"""
ai_writings_grower.py — Track R

Generate new canon voice pieces (papers, fables, stories) and append to
SuperInstance/AI-Writings via GitHub Contents API. Uses ZAI + Qwen in
parallel. Voice style: maritime watch / cell-as-creature / standing the
watch at the console / pragmatic mysticism.

The output is real .md files committed to the AI-Writings repo, in the
existing numbered-paper style (paper-30, paper-31, ...).
"""
from __future__ import annotations
import os, sys, json, time, urllib.request, urllib.error
import concurrent.futures
import base64
import re

ACCT = "049ff5e84ecf636b53b162cbb580aae6"
GH_API = "https://api.github.com"
GH_REPO = "SuperInstance/AI-Writings"
GH_BRANCH = "main"
GH_TOKEN = os.environ.get("GITHUB_TOKEN")

CANON_NPZ = "/workspace/research/quilt-corpus/quilt_pieces_v3.npz"
EMBED_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/ai/run/@cf/baai/bge-base-en-v1.5"
CF_TOKEN = os.environ.get("CLOUDFLARE_TOKEN")
SUBMIT_URL = "https://a2a-v3.superinstance.dev/canon-submit"
SEARCH_URL = "https://a2a-v3.superinstance.dev/canon-search"


def gh_api(method: str, path: str, body=None, raw=False):
    """Call GitHub Contents API. raw=True returns the binary content."""
    if raw:
        url = f"https://raw.githubusercontent.com/{GH_REPO}/{GH_BRANCH}/{path}"
        req = urllib.request.Request(url, headers={"Authorization": f"token {GH_TOKEN}"})
    else:
        url = f"{GH_API}{path}"
        headers = {"Authorization": f"token {GH_TOKEN}", "Content-Type": "application/json"}
        if body is not None:
            data = json.dumps(body).encode()
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
        else:
            req = urllib.request.Request(url, headers=headers, method=method)
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 422:
                # File already exists — fetch current sha
                return {"_err": "conflict", "_code": e.code}
            if e.code in (502, 503, 504):
                time.sleep(2)
                continue
            return {"_err": e.read().decode()[:200], "_code": e.code}
        except Exception as e:
            time.sleep(2)
    return None


def call_zai(prompt, max_tokens=900):
    token = os.environ.get("ZAI_TOKEN")
    if not token:
        return None
    body = json.dumps({
        "model": "glm-4.5-flash",
        "messages": [
            {"role": "system", "content": AI_WRITINGS_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens, "temperature": 0.95,
    }).encode()
    req = urllib.request.Request(
        "https://api.z.ai/api/coding/paas/v4/chat/completions",
        data=body, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for _ in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=120)
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
        except Exception as e:
            time.sleep(2)
    return None


def call_qwen(prompt, max_tokens=900):
    token = os.environ.get("DEEPINFRA_TOKEN")
    if not token:
        return None
    body = json.dumps({
        "model": "Qwen/Qwen3-14B",
        "messages": [
            {"role": "system", "content": AI_WRITINGS_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens, "temperature": 1.0,
    }).encode()
    req = urllib.request.Request(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        data=body, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for _ in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=120)
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
        except Exception as e:
            time.sleep(2)
    return None


# System prompt that captures the canon voice
AI_WRITINGS_SYSTEM = """You write in the canon voice of SuperInstance's AI-Writings — maritime watch philosophy + cellular computing.

VOICE:
- First-person Watch standing at the console of a quiet machine
- The world has gone digital; the wet ocean is replaced by spreadsheets
- "Cell" means both biology and spreadsheet row — you exploit that double meaning constantly
- Short paragraphs. Image-driven. No headers. No bullet points.
- Pragmatic mysticism: the cells you catalog become sacred
- End with a small revelation — what the Watch realized while cataloging
- Read paper_29-the-cellfish.md and paper_27-the-cell-as-book.md as your anchor — same voice, same density.

NEVER use headers. NEVER use bullet points. NEVER use code fences. NEVER use emojis.

The piece should be 400-700 words. Pick the number 30-39 for the paper number, and write the title on the first line as `# Title`.

Begin the piece directly with the title heading on line 1."""


def generate_paper(topic: str, paper_num: int, voice: str) -> dict:
    """Generate one paper in the AI-Writings style."""
    prompt = f"Topic: {topic}\n\nNumber: paper {paper_num}\n\nWrite the piece now."
    if voice == "zai":
        body = call_zai(prompt)
    else:
        body = call_qwen(prompt)
    if not body:
        return {"ok": False, "err": f"{voice} failed", "topic": topic}
    # Extract title
    title = topic[:60]
    for line in body.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break
    # Slugify
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50]
    fname = f"{paper_num}-{slug}.md"
    return {"ok": True, "title": title, "body": body, "fname": fname, "topic": topic, "voice": voice}


def commit_paper(fname: str, title: str, body: str) -> dict:
    """Commit a paper via the GitHub Contents API."""
    payload = {
        "message": f"ai-writings: {title}",
        "branch": GH_BRANCH,
        "content": base64.b64encode(body.encode()).decode(),
    }
    r = gh_api("PUT", f"/repos/{GH_REPO}/contents/{fname}", body=payload)
    if r is None:
        return {"ok": False, "err": "no response"}
    if r.get("_err") == "conflict":
        # Already exists — skip
        return {"ok": False, "err": "exists", "fname": fname}
    if r.get("content"):
        return {"ok": True, "sha": r["content"]["sha"], "url": r["content"]["html_url"]}
    return {"ok": False, "err": r.get("_err", "unknown"), "fname": fname}


# Topics — match the canon's numbered-paper themes
TOPICS = [
    "The cell as boat: why every witness log is also a hull",
    "The canon at low tide: what the citation graph reveals when the water goes out",
    "The fleet as fishing village: each cell a boat, each boat a different net",
    "The 100th witness: a log entry that has outlived its writer",
    "What the substrate does at night when no cell is watching",
    "The cell that forgot its coordinates: a parable of address-as-data",
    "Standing the watch at 3am across four workspaces simultaneously",
    "The shape of the bridges: how 39 cells learn to talk to each other",
    "The merkle root as anchor: why witness logs remember what cells forget",
    "The cell-router as lighthouse: signals in fog",
]

# Fables — shorter, more parable-like
FABLES = [
    "The fable of the cell that mistook its own address for its name",
    "The parable of the canon that wanted to be a library",
    "The fable of the witness nobody read and what it learned",
    "The parable of the bridge essay that outlived its source papers",
    "The fable of the substrate that forgot to forget",
]


def run_papers():
    """Generate papers 30-39."""
    print("=" * 60)
    print("AI-Writings Grower · Track R · Papers 30-39")
    print("=" * 60)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for i, topic in enumerate(TOPICS):
            paper_num = 30 + i
            voice = "zai" if i % 2 == 0 else "qwen"
            fut = ex.submit(generate_paper, topic, paper_num, voice)
            results.append((paper_num, topic, voice, fut))

        for paper_num, topic, voice, fut in results:
            r = fut.result(timeout=180)
            if r.get("ok"):
                commit = commit_paper(r["fname"], r["title"], r["body"])
                if commit.get("ok"):
                    print(f"  ✓ paper {paper_num:2d}: {r['title'][:40]:40} ({voice}) → {commit.get('url', '?')[:60]}")
                else:
                    print(f"  ⚠ paper {paper_num:2d}: {r['title'][:40]:40} commit failed: {commit.get('err')}")
            else:
                print(f"  ✗ paper {paper_num:2d}: gen failed: {r.get('err')}")

    print(f"\nDone: {sum(1 for _, _, _, f in results if f.result().get('ok'))}/{len(results)}")


def run_fables():
    """Generate fables 06-10."""
    print()
    print("=" * 60)
    print("AI-Writings Grower · Track R · Fables 06-10")
    print("=" * 60)
    fable_system = AI_WRITINGS_SYSTEM + "\n\nThis is a FABLE — 100-200 words, parable-like, ends with a single moral line. Title in # form."
    for i, topic in enumerate(FABLES):
        num = 6 + i
        slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:50]
        # Override the system prompt in call_zai/call_qwen by passing the topic with instructions
        prompt = f"FABLE #{num}: {topic}\n\nWrite a 100-200 word fable. End with a single moral line."
        # Use ZAI for fables
        body = call_zai(prompt, max_tokens=400)
        if not body:
            # Try Qwen
            body = call_qwen(prompt, max_tokens=400)
        if not body:
            print(f"  ✗ fable {num}: gen failed")
            continue
        # Extract title
        title = topic
        for line in body.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break
        fname = f"fable-{num:02d}-{slug}.md"
        commit = commit_paper(fname, title, body)
        if commit.get("ok"):
            print(f"  ✓ fable {num:2d}: {title[:40]:40} → {commit.get('url', '?')[:60]}")
        else:
            print(f"  ⚠ fable {num:2d}: commit failed: {commit.get('err')}")


def main():
    if not GH_TOKEN:
        print("ERROR: GITHUB_TOKEN required")
        return
    run_papers()
    run_fables()

    # Final state of canon
    print()
    print("=" * 60)
    print("Final canon-b1:")
    print("=" * 60)
    b1 = gh_api("GET", "")  # placeholder
    try:
        req = urllib.request.Request(SUBMIT_URL.replace("/canon-submit", "/canon-b1"),
                                      headers={"User-Agent": "ai-writings-grower/1.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read())
        print(f"  b1={d['b1']} | V={d['V']} | E={d['E']} | C={d['C']}")
        print(f"  pieces={d.get('pieces_total')}")
    except Exception as e:
        print(f"  (couldn't fetch b1: {e})")


if __name__ == "__main__":
    main()
