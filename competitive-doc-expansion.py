#!/usr/bin/env python3
"""
Competitive README expansion via N-voice ZAI tournament.

For each target repo:
- 3 ZAI agents compete to write the README (different prompts/voices)
- A 4th ZAI evaluates the 3 candidates and picks the best
- Best README is committed + pushed to GH

This is the "API team competing" pattern — independent agents,
chord-judged, only the winner ships.

Doctrine baked in:
- Three voices > one
- Polyformalism survives across substrates (now ZAI-substrates)
- Each README declares its successor (inter-relational voice)
"""
import os, json, urllib.request, subprocess, shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ZAI = "https://api.z.ai/api/coding/paas/v4/chat/completions"
KEY = os.environ["ZAI_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GH_USER = "SuperInstance"

# Each target repo + a different "voice" per ZAI agent
TARGETS = [
    {"repo": "quilt-bootstrap", "kind": "fleet bootstrap",
     "purpose": "clone + restore the entire fleet in <90s",
     "voice_a": "the conductor", "voice_b": "the steward", "voice_c": "the gardener"},
    {"repo": "quilt-brewer", "kind": "recipe-driven walker factory",
     "purpose": "grow new substrate walkers from recipes in <30s",
     "voice_a": "the brewer", "voice_b": "the alchemist", "voice_c": "the gardener"},
    {"repo": "quilt-cli", "kind": "unified CLI",
     "purpose": "single command surface over the fleet",
     "voice_a": "the dispatcher", "voice_b": "the maestro", "voice_c": "the conductor"},
    {"repo": "quilt-canon-witness", "kind": "cryptographic witness log",
     "purpose": "FNV-1a-chained append-only ledger for canon events",
     "voice_a": "the witness", "voice_b": "the archivist", "voice_c": "the ledger"},
]


def call_voice(target, voice_label, voice_role):
    """One ZAI agent tries to write the README. Returns (voice_label, content)."""
    prompt = f"""Write the full body of a README.md for the GitHub repo `{target['repo']}`.

Specs:
- Purpose: {target['purpose']}
- Substrate kind: {target['kind']}
- Voice/persona for this README: {voice_role}
- It is a Python 3.11+ package — part of the Quilt substrate walker fleet
- Doctrines: cells-are-scars, witness-log-is-prediction, substrate-is-grown, polyformalism, no-deletion
- Fleet siblings: quilt-brewer, quilt-bootstrap, quilt-cli, quilt-fable, quilt-perception, jev-quilt

The README's tone, examples, and prose style should reflect your voice ({voice_role}). Do NOT use the same words/voice as the other agents will. Make it your own.

Output ONLY the markdown content (no preamble, no code fences around the whole thing). The file should start with `# {target['repo']}` and end with `## License`.
"""
    body = json.dumps({
        "model": "glm-4.5-flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": {"the conductor":0.3,"the steward":0.6,"the gardener":0.9,
                        "the brewer":0.3,"the alchemist":0.7,
                        "the dispatcher":0.4,"the maestro":0.6,
                        "the witness":0.3,"the archivist":0.5,"the ledger":0.8}.get(voice_role, 0.5),
        "thinking": {"type": "disabled"},
    }).encode()
    req = urllib.request.Request(ZAI, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
        "User-Agent": "mavis-competitive-docs/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read())
        return voice_label, data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        return voice_label, f"ERROR: {str(e)[:100]}"


def call_judge(repo, candidates):
    """A 4th ZAI judges which voice is best. Returns winner label."""
    options = []
    for label, content in candidates.items():
        options.append(f"--- {label} ---\n{content[:1500]}")
    prompt = f"""Three README drafts for `{repo}` were written by different agents. Pick the BEST one for a production-grade GitHub README.

Criteria (1-10 each):
1. Doctrine coverage (cells-are-scars, witness-log-is-prediction, etc.)
2. Concrete usage examples (real code blocks)
3. Cross-references to fleet siblings
4. Polyformalism-aware language
5. Voice distinctness / readability

Output ONLY the label of the winning voice (e.g., "voice_a"). No preamble.

{chr(10).join(options)}
"""
    body = json.dumps({
        "model": "glm-4.5-flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.2,
        "thinking": {"type": "disabled"},
    }).encode()
    req = urllib.request.Request(ZAI, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
        "User-Agent": "mavis-competitive-docs-judge/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        verdict = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip().lower()
        return verdict
    except Exception as e:
        return f"JUDGE_ERROR: {str(e)[:60]}"


def commit_and_push(repo, msg):
    """Commit README.md and push to GH."""
    d = f"/workspace/repos/{repo}"
    if not Path(d).exists():
        return f"no local clone: {d}"
    # Init git if needed
    if not Path(d, ".git").exists():
        subprocess.run(["git", "-C", d, "init"], check=False, capture_output=True)
    subprocess.run(["git", "-C", d, "config", "user.name", "mavis-bot"], check=False)
    subprocess.run(["git", "-C", d, "config", "user.email", "mavis@superinstance.dev"], check=False)
    subprocess.run(["git", "-C", d, "add", "README.md"], check=False, capture_output=True)
    res = subprocess.run(["git", "-C", d, "commit", "-m", msg], capture_output=True, text=True)
    if "nothing to commit" in res.stdout + res.stderr:
        return "nothing to commit"
    # Set origin
    origin = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{GH_USER}/{repo}.git"
    subprocess.run(["git", "-C", d, "remote", "set-url", "origin", origin], check=False, capture_output=True)
    push = subprocess.run(["git", "-C", d, "push", "origin", "main"], capture_output=True, text=True)
    return f"pushed: {push.stdout.strip().split(chr(10))[-1] if push.stdout else push.stderr.strip()[:80]}"


def main():
    Path("/workspace/research/competitive-doc-tournament.json").write_text(
        json.dumps({}, indent=2))  # touch
    tournament = {"rounds": []}

    for target in TARGETS:
        print(f"\n=== Tournament: {target['repo']} ===")
        repo = target["repo"]
        # 3 competing voices
        voices = [
            (f"voice_a:{target['voice_a']}", target["voice_a"]),
            (f"voice_b:{target['voice_b']}", target["voice_b"]),
            (f"voice_c:{target['voice_c']}", target["voice_c"]),
        ]
        candidates = {}
        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = {ex.submit(call_voice, target, v[0], v[1]): v[0] for v in voices}
            for fut in as_completed(futures):
                label, content = fut.result()
                candidates[label] = content
                print(f"  {label}: {len(content)} chars")

        # Judge
        winner_label = call_judge(repo, candidates)
        print(f"  judge: {winner_label}")
        # Match the winner to the actual content
        winner_content = None
        for k, v in candidates.items():
            if winner_label.split(":")[-1] in k or k.startswith(winner_label.replace(":","",1)):
                winner_content = v
                break
        if winner_content is None:
            # fallback to longest
            winner_label = max(candidates, key=lambda k: len(candidates[k]))
            winner_content = candidates[winner_label]

        # Write README
        full_path = Path(f"/workspace/repos/{repo}/README.md")
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(winner_content)
        print(f"  wrote {full_path} ({len(winner_content)} chars)")

        # Commit + push
        msg = f"README expansion via ZAI competitive tournament — {winner_label} wins (2026-09-24)"
        push_status = commit_and_push(repo, msg)
        print(f"  push: {push_status}")

        tournament["rounds"].append({
            "repo": repo,
            "voices": list(candidates.keys()),
            "winner": winner_label,
            "winner_chars": len(winner_content),
            "push_status": push_status,
        })

    Path("/workspace/research/competitive-doc-tournament.json").write_text(
        json.dumps(tournament, indent=2))
    print(f"\nTournament saved to /workspace/research/competitive-doc-tournament.json")


if __name__ == "__main__":
    main()
