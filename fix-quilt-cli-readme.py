#!/usr/bin/env python3
"""Quick fix for quilt-cli README — ZAI got 429 mid-tournament."""
import os, json, urllib.request, subprocess
from pathlib import Path

ZAI = "https://api.z.ai/api/coding/paas/v4/chat/completions"
KEY = os.environ["ZAI_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

prompt = """Write the full body of README.md for `quilt-cli`.

Specs:
- Unified CLI surface for the entire Quilt substrate walker fleet
- 21 commands: cell / quilt / qult / fleet / edge / sim / voice / mesh / canon / init / doctor / version + bootstrap / brew / trace / scout / chord / legalese / holodeck / vessel / compose
- Each subcommand is a substrate in the CLI's cell architecture
- Doctrines: cells-are-scars, witness-log-is-prediction, substrate-is-grown, polyformalism
- Fleet siblings: quilt-bootstrap, quilt-brewer, quilt-perception, quilt-fable, quilt-orchestrator, quilt-linker

Output ONLY the markdown. Tone: technical but warm. Voice: the conductor — orchestrating the fleet through a single command surface. Make it concrete with real code examples."""

body = json.dumps({
    "model": "glm-4.5-flash",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 2000,
    "temperature": 0.6,
    "thinking": {"type": "disabled"},
}).encode()
req = urllib.request.Request(ZAI, data=body, headers={
    "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
    "User-Agent": "mavis-fix-quilt-cli-readme/1.0",
})

for attempt in range(3):
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read())
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if content:
            Path("/workspace/repos/quilt-cli/README.md").write_text(content)
            print(f"  attempt {attempt+1}: wrote {len(content)} chars")
            break
    except Exception as e:
        print(f"  attempt {attempt+1}: {str(e)[:80]}")
        import time; time.sleep(5)

# Commit + push
subprocess.run(["git", "-C", "/workspace/repos/quilt-cli", "add", "README.md"], check=False)
r = subprocess.run(["git", "-C", "/workspace/repos/quilt-cli", "commit", "-m",
                     "Fix README — ZAI 429 mid-tournament caused error string; regenerate (2026-09-24)"],
                    capture_output=True, text=True)
print("commit:", r.stdout.strip()[:100] or r.stderr.strip()[:100])
subprocess.run(["git", "-C", "/workspace/repos/quilt-cli",
                "remote", "set-url", "origin",
                f"https://x-access-token:{GITHUB_TOKEN}@github.com/SuperInstance/quilt-cli.git"],
               check=False)
p = subprocess.run(["git", "-C", "/workspace/repos/quilt-cli", "push", "origin", "main"],
                   capture_output=True, text=True)
print("push:", p.stdout.strip()[-100:] if p.stdout else p.stderr.strip()[:80])
