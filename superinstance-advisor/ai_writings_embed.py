"""
ai_writings_embed.py — Pull the 13 new AI-Writings pieces I just pushed
and submit them to the canon worker so they show up in /canon-list,
/canon-search, /canon-b1.

This closes the loop: the papers/fables exist as real GitHub commits
AND as canon pieces the worker can query.
"""
import os, sys, json, time, urllib.request, urllib.error
import base64, re

GH_API = "https://api.github.com"
GH_REPO = "SuperInstance/AI-Writings"
GH_BRANCH = "main"
GH_TOKEN = os.environ.get("GITHUB_TOKEN")
SUBMIT_URL = "https://a2a-v3.superinstance.dev/canon-submit"

ACCT = "049ff5e84ecf636b53b162cbb580aae6"
EMBED_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/ai/run/@cf/baai/bge-base-en-v1.5"

NEW_FILES = [
    "30-the-cell-as-boat.md",  # may be slightly different slug
    "31-the-canon-at-low-tide.md",
    "32-the-fleet-as-fishing-village.md",
    "33-the-100th-witness.md",
    "35-the-cell-that-forgot-its-coordinates.md",
    "37-the-shape-of-the-bridges.md",
    "38-the-merkle-root-as-anchor.md",
    "39-the-cell-router-as-lighthouse.md",
    "fable-06-the-fable-of-the-cell-that-mistook-its-own-address.md",
    "fable-07-the-parable-of-the-canon-that-wanted-to-be-a-library.md",
    "fable-08-the-fable-of-the-witness-nobody-read.md",
    "fable-09-the-parable-of-the-bridge-essay-that-outlived-its-source-papers.md",
    "fable-10-the-fable-of-the-substrate-that-forgot-to-forget.md",
]


def gh_get(path):
    """Get a file's raw content from main."""
    url = f"https://raw.githubusercontent.com/{GH_REPO}/{GH_BRANCH}/{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"token {GH_TOKEN}"})
    for attempt in range(3):
        try:
            return urllib.request.urlopen(req, timeout=30).read().decode()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return None


def gh_list_files(prefix):
    """List all files in the repo matching a prefix."""
    url = f"{GH_API}/repos/{GH_REPO}/contents/?per_page=100"
    req = urllib.request.Request(url, headers={"Authorization": f"token {GH_TOKEN}"})
    items = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return [i["name"] for i in items if isinstance(i, dict) and i["name"].startswith(prefix)]


def post_canon(tag, title, body, cites):
    payload = json.dumps({"tag": tag, "title": title, "text": body[:1500], "cites": cites}).encode()
    req = urllib.request.Request(SUBMIT_URL, data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "ai-writings-embed/1.0"},
        method="POST")
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(req, timeout=60)
            return json.loads(r.read())
        except Exception as e:
            time.sleep(2)
    return {"ok": False}


def main():
    print("=" * 60)
    print("AI-Writings Embed — pushing to canon worker")
    print("=" * 60)

    # Fetch each new file's content + extract title and body
    # Also pick cites from existing canon
    submitted = 0
    for fname in NEW_FILES:
        content = gh_get(fname)
        if not content:
            print(f"  ⚠ {fname} — not found (slug mismatch?)")
            continue

        # Title = first # heading
        title = fname.replace(".md", "").replace("-", " ").title()
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break
        # Skip front-matter
        body = content
        if body.startswith("---"):
            end = body.find("\n---", 3)
            if end > 0:
                body = body[end + 4:]
        # Strip markdown noise
        body = re.sub(r"^\*+ ", "", body, flags=re.MULTILINE)
        body = re.sub(r"^#+\s+", "", body, flags=re.MULTILINE)

        # Tag
        slug = fname.replace(".md", "").replace("-", "_")
        if not slug.startswith("fable"):
            tag = f"ai-{slug}"
        else:
            tag = f"ai-{slug.replace('fable_', 'fable-')}"

        # Cite the bridge essays + a couple of grow-* hubs
        cites = [
            "bridge-from-fleet-to-canon",
            "bridge-from-cell-to-fleet",
            "bridge-from-witness-to-shape",
            "grow-qwen-20260916-032230-what-a-canon-forgets-whe",
        ]

        result = post_canon(tag, title, body.strip(), cites)
        if result.get("ok"):
            submitted += 1
            print(f"  ✓ {tag[:50]:50} ({len(body):4} chars)")
        else:
            print(f"  ✗ {tag[:50]:50} {result.get('err')}")

        time.sleep(0.3)

    print()
    print(f"Submitted: {submitted}/{len(NEW_FILES)}")

    # Final state
    b1 = None
    try:
        req = urllib.request.Request(
            SUBMIT_URL.replace("/canon-submit", "/canon-b1"),
            headers={"User-Agent": "ai-writings-embed/1.0"},
        )
        b1 = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except Exception:
        pass
    if b1:
        print(f"Final b1: V={b1['V']}, E={b1['E']}, b1={b1['b1']}")


if __name__ == "__main__":
    main()
