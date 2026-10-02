#!/usr/bin/env python3
"""
Field-guide.html multi-reviewer playtest.

Tests the new field-guide.html against 5 reviewer lenses in parallel.
Each reviewer scores 4 dimensions and proposes 3 concrete fixes.

Uses:
- ZAI (GLM-4.5, Z.ai creative/balanced)
- Groq (qwen/qwen3.8-27b default, fast)
- DeepInfra (DeepSeek V4-Flash, writer-editor)
- 2x DeepInfra (variety for skepticism/skeptic/non-determinism)

Output: /tmp/field_guide_playtest_results.json
"""
import json, os, time, urllib.request, urllib.error, concurrent.futures
from pathlib import Path

REVIEWERS = [
    {"name": "skeptic", "provider": "zai", "model": "glm-4.5",
     "focus": "outsider, first 60 seconds, technical credibility"},
    {"name": "frontend_engineer", "provider": "deepinfra", "model": "Qwen/Qwen3-Coder-480B-A35B-Instruct-Turbo",
     "focus": "UX, navigation, visual design, accessibility"},
    {"name": "writer_editor", "provider": "deepinfra", "model": "deepseek-ai/DeepSeek-V4-Flash",
     "focus": "voice consistency, readability, design-writing fit"},
    {"name": "ux_designer", "provider": "groq", "model": "qwen/qwen3.8-27b",
     "focus": "cognitive load, mobile responsiveness, polish"},
    {"name": "skeptic_r2", "provider": "deepinfra", "model": "Qwen/Qwen3-235B-Instruct-2507",
     "focus": "second skeptic run (test non-determinism)"},
]

# Load the actual page content
HTML_PATH = Path("/tmp/field-guide.html")
HTML_CONTENT = HTML_PATH.read_text()
# Strip CSS/script for the prompt
import re
TEXT_ONLY = re.sub(r'<style[^>]*>.*?</style>', '', HTML_CONTENT, flags=re.DOTALL)
TEXT_ONLY = re.sub(r'<script[^>]*>.*?</script>', '', TEXT_ONLY, flags=re.DOTALL)
TEXT_ONLY = re.sub(r'<[^>]+>', ' ', TEXT_ONLY)
TEXT_ONLY = re.sub(r'\s+', ' ', TEXT_ONLY).strip()
PAGE_PREVIEW = TEXT_ONLY[:6000]

PROMPT_TEMPLATE = """You are a reviewer in a 5-LLM playtest of a website.

Your lens: {focus}

The page being reviewed is a "Field Guide" for the SuperInstance fleet (a collection of open-source AI agent software). It is the NEW companion page to the existing landing page, designed to address specific reviewer feedback from previous rounds (rounds 2-4 of the playtest).

Your previous round feedback said:
- Skeptic: "First-impression clarity" 2/10 → "Add a one-sentence plain-English definition at the top"
- GLM-4.5 (frontend): "Add a clear navigation structure with a sidebar or table of contents"
- Qwen3-Coder (skeptic): "Add verifiable technical specifications with code examples and links to actual GitHub repos"
- Gemini (UX): "Implement clear content sections with visual separation; progressive disclosure for technical details"
- Skeptic again: "Add a glossary for technical terms like polyformalism and L1-L8"

The new page attempts to address every one of those concerns. Here is the page content (css/scripts stripped):

--- PAGE TEXT ---
{preview}
--- END PAGE TEXT ---

Specifically the page includes:
- A plain-English lede in the hero section
- A sticky sidebar nav with TOC (Lede, 4 projects, Pick your path, Hash is the contract, L1-L8 stack, By the numbers, Glossary)
- 4 project cards (Quilt, Federated TinyML Vessel, The Tap, Tidepool) with live links to GitHub repos
- 6 "Pick your entry point" paths for different audiences
- A FNV-1a 64-bit hash credibility anchor with a verifiable browser demo (all 3 reference test vectors match)
- An L1-L8 architecture diagram
- Single repo count (~130 public repos)
- 18-entry glossary

Score on 4 dimensions (1-10):
1. First-impression clarity (does the page make its purpose clear in 60 seconds?)
2. Navigation quality (can users find what they need?)
3. Technical credibility (does it earn trust, or still feel like vaporware?)
4. Verifiability (does it show code/links to actual repos?)

Then give 3 concrete improvements that would make the next round score higher.

Respond in JSON only:
{{"scores": {{"first_impression": <int>, "navigation": <int>, "credibility": <int>, "verifiability": <int>}}, "improvements": ["...", "...", "..."], "summary": "2-3 sentence verdict"}}
"""

def call_zai(model, prompt):
    """ZAI (api.z.ai) — uses their OpenAI-compatible API"""
    url = "https://api.z.ai/api/coding/paas/v4/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.4,
        "thinking": {"type": "disabled"}
    }).encode()
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Authorization', f'Bearer {os.environ["ZAI_TOKEN"]}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read())
        return data['choices'][0]['message']['content']

def call_groq(model, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.4
    }).encode()
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Authorization', f'Bearer {os.environ["GROQ_TOKEN"]}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        return data['choices'][0]['message']['content']

def call_deepinfra(model, prompt):
    url = "https://api.deepinfra.com/v1/openai/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.4,
    }).encode()
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Authorization', f'Bearer {os.environ["DEEPINFRA_TOKEN"]}')
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read())
        return data['choices'][0]['message']['content']

def call_reviewer(reviewer):
    prompt = PROMPT_TEMPLATE.format(focus=reviewer['focus'], preview=PAGE_PREVIEW)
    try:
        if reviewer['provider'] == 'zai':
            text = call_zai(reviewer['model'], prompt)
        elif reviewer['provider'] == 'groq':
            text = call_groq(reviewer['model'], prompt)
        elif reviewer['provider'] == 'deepinfra':
            text = call_deepinfra(reviewer['model'], prompt)
        else:
            return {**reviewer, "error": "unknown provider"}

        # Try to parse JSON from the response
        text = text.strip()
        if text.startswith('```'):
            text = '\n'.join(text.split('\n')[1:])
            if text.endswith('```'):
                text = text[:-3]
        # Find JSON object
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            parsed = json.loads(text[start:end])
        else:
            parsed = {"raw": text}
        return {**reviewer, "result": parsed}
    except Exception as e:
        return {**reviewer, "error": str(e)[:200]}

def main():
    print(f"Running {len(REVIEWERS)} reviewers in parallel against field-guide.html")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(call_reviewer, r): r for r in REVIEWERS}
        results = []
        for f in concurrent.futures.as_completed(futures):
            r = f.result()
            results.append(r)
            name = r.get('name', '?')
            if 'error' in r:
                print(f"  [{name}] ERROR: {r['error']}")
            else:
                sc = r['result'].get('scores', {})
                print(f"  [{name}] impression={sc.get('first_impression','?')}/10 nav={sc.get('navigation','?')}/10 cred={sc.get('credibility','?')}/10 verif={sc.get('verifiability','?')}/10")

    out_path = Path("/tmp/field_guide_playtest_results.json")
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults written to {out_path}")

    # Aggregate
    valid = [r['result'] for r in results if 'result' in r and 'scores' in r.get('result', {})]
    if valid:
        n = len(valid)
        avg = {
            'first_impression': sum(r['scores'].get('first_impression', 0) for r in valid) / n,
            'navigation': sum(r['scores'].get('navigation', 0) for r in valid) / n,
            'credibility': sum(r['scores'].get('credibility', 0) for r in valid) / n,
            'verifiability': sum(r['scores'].get('verifiability', 0) for r in valid) / n,
        }
        print(f"\nAVERAGES ({n} reviewers):")
        for k, v in avg.items():
            bar = "█" * int(v) + "░" * (10 - int(v))
            print(f"  {k:20s} {v:.1f}/10 {bar}")

if __name__ == "__main__":
    main()
