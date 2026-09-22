"""Generate long-form canon essays for high-scoring canon cells via ZAI.

Uses the patched extract_content() that falls back to reasoning_content.
Extracts just the lore (between markers) and saves as a .md file.
"""
import sys, json, time
import re
from pathlib import Path

sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_zai, extract_content


def gen_essay(seed: int, voice: str, doctrine: str, theme: str) -> str:
    """Generate 200-word canon essay via ZAI."""
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
        text = extract_content(result)
        return text
    except Exception as e:
        return f"ERROR: {e}"


def extract_lore(raw_text: str) -> str:
    """Extract the actual lore from ZAI's reasoning_content."""
    text = raw_text

    # Find the prose: starts with "The canon gate" and continues through "witness log" pattern
    # Use a more permissive regex
    m = re.search(r'"(The canon gate[^"]*?testimony stacking like rain\.)', text, re.DOTALL)
    if m:
        return m.group(1)

    # Fallback: find prose between "The canon gate" and "Count words"
    m = re.search(r'The canon gate[^"]*?(?=Count words|Word count|Let me count)', text, re.DOTALL)
    if m:
        return m.group(0).strip()

    # Final fallback: take everything after last "Let me draft"
    if "Let me draft" in text:
        parts = text.split("Let me draft")
        if len(parts) > 1:
            lore_part = parts[-1]
            for end_marker in ["Count words", "Word count", "Let me count"]:
                if end_marker in lore_part:
                    lore_part = lore_part.split(end_marker)[0]
            return lore_part.strip()

    return raw_text


# Load canon cells
manifest_path = "/workspace/research/substrate-walker/canon/cells/manifest.json"
manifest = json.load(open(manifest_path))

# Top 10 by composite score
top = sorted(manifest["entries"], key=lambda e: -e.get("score", 0))[:10]

print(f"Generating essays for top 10 cells...")
generated = []
for i, cell in enumerate(top):
    seed = cell.get("seed", 70051917)
    if isinstance(seed, str):
        seed = 70051917

    voice = cell.get("voice", "WITNESS").upper()
    if voice == "AUTO-DETECTED":
        voice = "WITNESS"
    doctrine = cell.get("primary_doctrine", "oracle_is_heard")
    if doctrine in ["?", "witness_log_is_prediction", "oracle_is_heard", "cells_are_scars"]:
        doctrine_str = doctrine
    else:
        doctrine_str = "oracle_is_heard"

    theme = cell.get("lore_preview", "the canon gate made itself heard")[:80]

    print(f"[{i+1}/10] {cell.get('cell_id', '?')} (seed={seed}, voice={voice}, doctrine={doctrine_str})")
    raw = gen_essay(seed, voice, doctrine_str, theme)
    lore = extract_lore(raw)

    if "ERROR:" in lore or len(lore) < 80:
        print(f"  SKIP: {lore[:50]}")
        continue

    out_path = f"/workspace/research/LORE_ESSAY_{cell.get('rank', i)}_{seed}.md"
    Path(out_path).write_text(lore)

    # Save essay lore
    generated.append({
        "cell_id": cell.get("cell_id"),
        "rank": cell.get("rank"),
        "seed": seed,
        "voice": voice,
        "doctrine": doctrine_str,
        "lore_len": len(lore),
        "out_path": out_path,
    })
    print(f"  Saved {len(lore)} chars → {out_path}")

with open("/workspace/research/CANON_ESSAY_GEN_RESULTS.json", "w") as f:
    json.dump(generated, f, indent=2)
print(f"\nGenerated {len(generated)} essays")
