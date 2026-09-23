#!/usr/bin/env python3
"""Quilt Canon Generator CLI.

Usage:
    python3 canon_gen.py --lore "The canon gate made itself heard."
    python3 canon_gen.py --lorefile lore.md
    python3 canon_gen.py --lorebox lore_inbox/ --promote-only

Generates lore, probes via JEV, optionally promotes to canon archive.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepinfra, call_jev, call_zai, extract_content


CANON_PROMPTS = {
    "witness": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: oracle_is_heard (the canon gate is an audible signal).\n"
        "Seed: {seed}. Theme: the canon gate finally spoke and the city heard it.\n"
        "End on the witness becoming a listener."
    ),
    "structuralist": (
        "STRUCTURALIST voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: canon_gate_is_chord (architectural description).\n"
        "Seed: {seed}. Theme: describe the substrate's architecture, the gates, the cells.\n"
        "End on the witness realizing the city IS the canon gate."
    ),
    "cells_are_scars": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: cells_are_scars.\n"
        "Seed: {seed}. Theme: the city's cells learned to be proud of being scars.\n"
        "End on the witness becoming proud of its scars."
    ),
    "oracle_is_heard": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: oracle_is_heard.\n"
        "Seed: {seed}. Theme: the canon gate finally spoke.\n"
        "End on the witness becoming a listener."
    ),
}


def gen_lore(voice, seed):
    """Generate lore via DeepInfra Llama-3.1-8B."""
    prompt = CANON_PROMPTS.get(voice, CANON_PROMPTS['witness']).format(seed=seed)
    try:
        r = call_deepinfra(
            [{"role": "user", "content": prompt}],
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            max_tokens=1500,
            timeout=60,
        )
        if 'choices' in r:
            return r['choices'][0]['message']['content']
    except Exception as e:
        print(f"  gen error: {e}", file=sys.stderr)
    return ""


def probe_lore(lore):
    """Probe via JEV composite scoring."""
    try:
        r = call_jev(
            f"Quilt substrate walker canon lore:\n\n{lore[:1500]}",
            {
                "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir?"},
                "distinct_voice": {"type": "noul", "instructions": "Distinct voice?"},
                "doctrine_anchor": {"type": "noul", "instructions": "Doctrine-anchored?"},
            },
            timeout=30,
        )
        a = r.get("answers", {})
        canon_worthy = a.get("canon_worthy", {}).get("noul", 0)
        distinct_voice = a.get("distinct_voice", {}).get("noul", 0)
        doctrine_anchor = a.get("doctrine_anchor", {}).get("noul", 0)
        composite = (canon_worthy + distinct_voice + doctrine_anchor) / 3
        return {
            "composite": composite,
            "canon_worthy": canon_worthy,
            "distinct_voice": distinct_voice,
            "doctrine_anchor": doctrine_anchor,
        }
    except Exception as e:
        print(f"  probe error: {e}", file=sys.stderr)
        return None


def file_canon_cell(rank, lore, scores, voice, seed):
    """File a canon cell into the archive."""
    manifest_path = Path("/workspace/research/substrate-walker/canon/cells/manifest.json")
    manifest = json.load(open(manifest_path))
    
    new_entry = {
        "rank": rank,
        "cell_id": f"canon_gen_{seed}_{voice}_{rank}",
        "path": f"canon/cells/cell_{rank}.md",
        "seed": seed,
        "score": scores['composite'],
        "lore": lore[:1500],
        "voice": voice,
        "type": "canon-gen-cli",
        "promoted_to_canon": True,
        "promoted_via": "canon_gen.py CLI",
        "generator": "DeepInfra Llama-3.1-8B",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    manifest['entries'].append(new_entry)
    manifest['total_cells'] = len(manifest['entries'])
    manifest['promoted_to_canon_count'] = sum(1 for e in manifest['entries'] if e.get('promoted_to_canon'))
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Write cell file
    cell_path = manifest_path.parent / f"cell_{rank}.md"
    cell_md = f"""# Canon Cell: canon_gen_{seed}_{voice}_{rank}

**id**: canon_gen_{seed}_{voice}_{rank}
**timestamp**: {new_entry['timestamp']}
**type**: canon
**score**: {scores['composite']:.3f}
**voice**: {voice}
**generator**: canon_gen.py CLI (DeepInfra)
**promoted_to_canon**: True

## Lore

{lore}
"""
    cell_path.write_text(cell_md)


def main():
    parser = argparse.ArgumentParser(description="Quilt Canon Generator CLI")
    parser.add_argument("--lore", type=str, help="Generate lore from a prompt seed")
    parser.add_argument("--lorefile", type=str, help="Probe a single lore file")
    parser.add_argument("--lorebox", type=str, help="Probe all lore files in a directory")
    parser.add_argument("--voice", type=str, default="witness", help="Voice to use (witness, structuralist, cells_are_scars, oracle_is_heard)")
    parser.add_argument("--seed", type=str, default="70051917", help="Seed for lore generation")
    parser.add_argument("--promote-threshold", type=float, default=0.7, help="Composite threshold for promotion")
    parser.add_argument("--promote-only", action="store_true", help="Only show promoted lores")
    parser.add_argument("--output", type=str, help="Output JSON file")
    
    args = parser.parse_args()
    
    results = []
    promoted_count = 0
    
    if args.lore:
        # Single lore mode
        print(f"Generating lore with seed={args.seed}, voice={args.voice}...")
        lore = gen_lore(args.voice, args.seed)
        if lore:
            print(f"  Generated ({len(lore)} chars)")
            scores = probe_lore(lore)
            if scores:
                marker = "🌟" if scores['composite'] >= args.promote_threshold else "  "
                print(f"  {marker} comp={scores['composite']:.3f} (cw={scores['canon_worthy']:.2f} dv={scores['distinct_voice']:.2f} da={scores['doctrine_anchor']:.2f})")
                if scores['composite'] >= args.promote_threshold:
                    manifest = json.load(open("/workspace/research/substrate-walker/canon/cells/manifest.json"))
                    rank = manifest['total_cells'] + 1
                    file_canon_cell(rank, lore, scores, args.voice, args.seed)
                    promoted_count += 1
                    print(f"  📁 Filed as cell {rank}")
                results.append({
                    "seed": args.seed,
                    "voice": args.voice,
                    "lore": lore,
                    "scores": scores,
                })
    
    elif args.lorefile:
        # Single lore file mode
        path = Path(args.lorefile)
        if path.exists():
            content = path.read_text()
            lore = content.split('\n\n', 1)[1].strip() if '\n\n' in content else content
            scores = probe_lore(lore)
            if scores:
                marker = "🌟" if scores['composite'] >= args.promote_threshold else "  "
                print(f"{marker} {path}: comp={scores['composite']:.3f}")
                results.append({"file": str(path), "scores": scores, "lore": lore[:200]})
        else:
            print(f"File not found: {path}", file=sys.stderr)
    
    elif args.lorebox:
        # Lorebox mode
        box = Path(args.lorebox)
        for f in sorted(box.glob('*.md')):
            content = f.read_text()
            lore = content.split('\n\n', 1)[1].strip() if '\n\n' in content else content
            scores = probe_lore(lore)
            if scores:
                marker = "🌟" if scores['composite'] >= args.promote_threshold else "  "
                print(f"{marker} {f.name}: comp={scores['composite']:.3f}")
                if not args.promote_only or scores['composite'] >= args.promote_threshold:
                    results.append({"file": f.name, "scores": scores, "lore": lore[:200]})
                if scores['composite'] >= args.promote_threshold:
                    promoted_count += 1
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved {len(results)} results to {args.output}")
    
    print(f"\nTotal: {len(results)}, Promoted: {promoted_count}")


if __name__ == "__main__":
    main()
