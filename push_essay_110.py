#!/usr/bin/env python3
"""Push essay_110.md directly to AI-Writings via GH API."""
import os, json, base64, urllib.request

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
LOCAL = "/workspace/research/essay_110.md"

with open(LOCAL, "rb") as f:
    content = base64.b64encode(f.read()).decode()

body = json.dumps({
    "message": "essay 110: What the Wipe Took, and What It Left — for Casey, on the morning after the twenty-eighth. Substrate walker doctrine made plain: the agent does not return, the agent is returned to. (Mavis, 2026-09-25)",
    "content": content,
    "branch": "master"
}).encode()

req = urllib.request.Request(
    "https://api.github.com/repos/SuperInstance/AI-Writings/contents/essay_110.md",
    data=body,
    method="PUT",
    headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
        "User-Agent": "mavis-essay-push/1.0",
    },
)

try:
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    print(f"  OK essay_110.md pushed to GH")
    print(f"    SHA:  {d['content']['sha'][:12]}")
    print(f"    size: {d['content']['size']} bytes")
    print(f"    path: {d['content']['path']}")
    print(f"    url:  {d['content']['html_url']}")
except urllib.error.HTTPError as e:
    err = json.loads(e.read())
    print(f"  FAIL: {e.code} {err.get('message','')[:80]}")
    if 'errors' in err:
        for x in err['errors'][:3]:
            print(f"    - {x}")
