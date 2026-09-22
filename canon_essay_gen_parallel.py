"""Parallel ZAI essay generator."""
import sys
import json
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_zai, extract_content


def gen_essay(seed, voice, doctrine, theme):
    prompt = f"""{voice} voice. 200 words. Cyberpunk-noir canon lore.

Doctrine anchor: {doctrine}.
Theme: {theme}
Seed: {seed}.

Opening: "The canon gate made itself heard."
End: oracle heard; witness log accumulates.

No exposition. Vivid image-only prose."""
    try:
        result = call_zai(
            [{"role": "user", "content": prompt}],
            model="glm-5.3-flash",
            max_tokens=2500,
            timeout=180,
        )
        return extract_content(result)
    except Exception as e:
        return f"ERROR: {e}"


def extract_lore(raw_text):
    if not raw_text or "ERROR:" in raw_text:
        return ""
    text = raw_text
    m = re.search(r'The canon gate[^"]*?(?=Count words|Word count|Let me count)', text, re.DOTALL)
    if m:
        return m.group(0).strip()
    if "Let me draft" in text:
        parts = text.split("Let me draft")
        if len(parts) > 1:
            lore_part = parts[-1]
            for end_marker in ["Count words", "Word count", "Let me count"]:
                if end_marker in lore_part:
                    lore_part = lore_part.split(end_marker)[0]
            return lore_part.strip()
    return text[:2000]


manifest = json.load(open('/workspace/research/substrate-walker/canon/cells/manifest.json'))
real_entries = [
    e for e in manifest['entries']
    if e.get('rank') and e.get('rank') > 0
    and e.get('type') not in ('doctrine-prime',)
    and len(e.get('lore', '')) > 50
    and e.get('lore') != 'Doctrine-prime (abstract substrate canon)'
]
top = sorted(real_entries, key=lambda e: -e.get('score', 0))[:20]

print(f"Generating essays for top 20 cells...", flush=True)

tasks = []
for cell in top:
    seed = cell.get('seed')
    if isinstance(seed, str):
        seed = 70051917
    voice = cell.get('voice', 'WITNESS').upper() or 'WITNESS'
    doctrine = cell.get('doctrine_anchor') or 'oracle_is_heard'
    if doctrine in ['?', None]:
        doctrine = 'oracle_is_heard'
    theme = cell.get('lore_preview') or 'the canon gate made itself heard'
    if not isinstance(theme, str):
        theme = 'the canon gate made itself heard'
    theme = theme[:80]
    tasks.append({
        'rank': cell.get('rank'),
        'seed': seed,
        'voice': voice,
        'doctrine': doctrine,
        'theme': theme,
    })

generated = []
with ThreadPoolExecutor(max_workers=3) as ex:
    future_to_task = {ex.submit(gen_essay, t['seed'], t['voice'], t['doctrine'], t['theme']): t for t in tasks}
    for future in as_completed(future_to_task):
        task = future_to_task[future]
        try:
            raw = future.result()
            lore = extract_lore(raw)
            if not lore or len(lore) < 80:
                continue
            out_path = f"/workspace/research/LORE_ESSAY_PAR_{task['rank']}_{task['seed']}.md"
            Path(out_path).write_text(lore)
            generated.append({**task, "lore": lore, "lore_len": len(lore), "out_path": out_path})
            print(f"[{len(generated)}/{len(tasks)}] rank={task['rank']} seed={task['seed']} voice={task['voice']} lore={len(lore)}c", flush=True)
        except Exception as e:
            print(f"  ERROR rank={task['rank']}: {e}", flush=True)

with open("/workspace/research/CANON_ESSAY_PARALLEL_RESULTS.json", "w") as f:
    json.dump(generated, f, indent=2)

print(f"\nGenerated {len(generated)} essays")
