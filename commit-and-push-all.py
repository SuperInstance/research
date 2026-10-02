#!/usr/bin/env python3
"""
commit-and-push-all.py — sweep all repos with uncommitted changes,
commit meaningfully, and push to GH.
"""
import os, subprocess, shutil
from pathlib import Path

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
STANDARD_GITIGNORE = """__pycache__/
*.pyc
*.pyd
.pytest_cache/
build/
dist/
*.egg-info/
.eggs/
*.egg
target/
node_modules/
.cache/
.wrangler/
.DS_Store
*.log
.env
"""

REPOS_DIR = Path("/workspace/repos")

def ensure_gitignore(repo_path):
    gi = repo_path / ".gitignore"
    if not gi.exists():
        return False
    txt = gi.read_text()
    missing = []
    for ln in STANDARD_GITIGNORE.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"): continue
        if ln not in txt:
            missing.append(ln)
    if missing:
        with open(gi, "a") as f:
            f.write("\n# added by commit-and-push-all\n")
            for ln in missing:
                f.write(ln + "\n")
        return True
    return False

def run(repo, *args, check=False):
    return subprocess.run(["git", "-C", str(repo)] + list(args),
                          capture_output=True, text=True, check=check)

def process_repo(repo_path):
    name = repo_path.name
    res = []

    # 1. ensure gitignore
    if ensure_gitignore(repo_path):
        res.append("gitignore+")

    # 2. remove tracked pyc/cache if present
    rm_out = run(repo_path, "rm", "-r", "--cached",
                 "**/__pycache__/", "**/*.pyc", "**/build/", "**/dist/",
                 "**/*.egg-info/", "**/target/", "**/.wrangler/",
                 "**/node_modules/", check=False)
    if rm_out.stdout or "rm '" in rm_out.stderr:
        res.append("rm-cached")

    # 3. add + commit only if there are still staged/unstaged changes
    add = run(repo_path, "add", "-A", check=False)
    stat = run(repo_path, "status", "--porcelain", check=False).stdout.strip()
    if stat:
        commit = run(repo_path, "commit", "-m",
                      "Cleanup gitignored artifacts + sync local state (2026-09-24)",
                      check=False)
        if "1 file changed" in commit.stdout or "files changed" in commit.stdout:
            res.append(f"committed:{len(stat.splitlines())}")
        else:
            res.append(f"no-commit:{commit.stderr.strip()[:60]}")

    # 4. push if there's a remote + commits ahead
    has_remote = run(repo_path, "remote").stdout.strip()
    if "origin" in has_remote:
        run(repo_path, "remote", "set-url", "origin",
            f"https://x-access-token:{GITHUB_TOKEN}@github.com/SuperInstance/{name}.git",
            check=False)
        push = run(repo_path, "push", "origin",
                   *(["main"] if name != "quilt-cli" else ["master"]),
                   check=False)
        if "fatal" in push.stderr or "ERROR" in push.stderr:
            res.append(f"push-err:{push.stderr.strip()[:60]}")
        elif "To https://" in push.stderr or len(push.stderr.strip()) > 0:
            res.append("pushed")
    else:
        res.append("no-remote")

    return res


def main():
    print("=== Repo sweep — commit + push what's pending ===\n")
    summary = {}
    for repo_path in sorted(REPOS_DIR.iterdir()):
        if not (repo_path / ".git").exists():
            continue
        result = process_repo(repo_path)
        if result:
            summary[repo_path.name] = result
            print(f"  {repo_path.name}: {','.join(result)}")
        else:
            print(f"  {repo_path.name}: clean")
    print(f"\n--- {len(summary)} repos touched ---")

    Path("/workspace/research/commit-push-sweep.json").write_text(
        __import__('json').dumps(summary, indent=2))


if __name__ == "__main__":
    main()
