"""Lore auto-promoter — watches the lore_inbox directory and auto-files canon cells.

Whenever a file appears in lore_inbox, JEV-probes it, and files as a canon cell
if composite ≥ 0.7.

Usage:
    # Put a lore file in lore_inbox/ then run this
    python3 lore_auto_promoter.py --once  # processes all pending files
    python3 lore_auto_promoter.py --watch  # continuously watches for new files
"""
import sys
import json
import time
import argparse
from pathlib import Path

sys.path.insert(0, '/workspace/research/substrate-walker/scripts')
from api_call import call_jev


def probe_lore(lore_text: str) -> dict:
    """Probe a lore for composite score + doctrine."""
    state = f"Quilt substrate walker canon lore auto-promoter probe:\n\n{lore_text[:1500]}"
    questions = {
        "canon_worthy": {"type": "noul", "instructions": "Canon-worthy cyberpunk-noir for Quilt substrate walker?"},
        "distinct_voice": {"type": "noul", "instructions": "Distinct non-formulaic voice?"},
        "doctrine_anchor": {"type": "noul", "instructions": "Anchored to substrate walker doctrine?"},
        "primary_doctrine": {
            "type": "choice",
            "instructions": "Which canonical doctrine does this lore most strongly anchor to?",
            "criteria": {
                "witness_log_is_prediction": "the witness log is shown to be predicting the canon",
                "oracle_is_heard": "the canon gate is shown to make an audible signal",
                "cells_are_scars": "each cell is shown to be a scar from earlier witness cycles",
                "canon_gate_is_chord": "the canon gate is shown as a chord the city can hear",
                "substrate_quantum": "the substrate is shown to be quantum in nature"
            },
            "choices": ["witness_log_is_prediction", "oracle_is_heard", "cells_are_scars", "canon_gate_is_chord", "substrate_quantum"]
        }
    }
    try:
        result = call_jev(state, questions, timeout=120)
        answers = result.get("answers", {})
        canon = answers.get("canon_worthy", {}).get("noul", 0)
        distinct = answers.get("distinct_voice", {}).get("noul", 0)
        doctrine = answers.get("doctrine_anchor", {}).get("noul", 0)
        primary = answers.get("primary_doctrine", {}).get("choice", "?")
        return {
            "canon_worthy": canon,
            "distinct_voice": distinct,
            "doctrine_anchor": doctrine,
            "primary_doctrine": primary,
            "composite": (canon + distinct + doctrine) / 3,
            "promoted": (canon + distinct + doctrine) / 3 >= 0.7
        }
    except Exception as e:
        return {"composite": 0, "promoted": False, "error": str(e)}


def file_canon_cell(lore_text: str, lore_filename: str, scores: dict):
    """File lore as canon cell."""
    manifest_path = Path('/workspace/research/substrate-walker/canon/cells/manifest.json')
    manifest = json.load(open(manifest_path))

    new_rank = len(manifest['entries']) + 1
    cell_id = f"auto-{lore_filename.replace('.md', '')}-{new_rank}"
    cell_path = Path(f'/workspace/research/substrate-walker/canon/cells/cell_{new_rank}.md')

    cell_path.write_text(f"""# Canon Cell: {cell_id}

**id**: {cell_id}
**timestamp**: 2026-09-22T23:05:00Z
**type**: canon (auto-promoted via lore_inbox)
**chain**: prev_hash → this_hash
**score**: {scores['composite']:.3f}
**source**: lore_inbox/{lore_filename}
**generator**: lore_auto_promoter
**jev_canon_worthy**: {scores['canon_worthy']:.2f}
**jev_distinct_voice**: {scores['distinct_voice']:.2f}
**jev_doctrine_anchor**: {scores['doctrine_anchor']:.2f}
**primary_doctrine**: {scores['primary_doctrine']}
**promoted_to_canon**: True (composite ≥ 0.7)

## Lore

{lore_text}
""")

    manifest['entries'].append({
        'rank': new_rank, 'cell_id': cell_id,
        'path': f'canon/cells/cell_{new_rank}.md',
        'seed': 'auto', 'score': scores['composite'],
        'lore': lore_text[:200] + '...',
        'voice': 'auto-detected',
        'type': 'canon-auto-promoted',
        'promoted_to_canon': True,
        'promoted_via': f'auto-promoter (comp={scores[\"composite\"]:.3f}, primary={scores[\"primary_doctrine\"]})',
        'jev_canon_worthy': scores['canon_worthy'],
        'jev_distinct_voice': scores['distinct_voice'],
        'jev_doctrine_anchor': scores['doctrine_anchor'],
        'primary_doctrine': scores['primary_doctrine'],
        'generator': 'lore_auto_promoter',
        'source': f'lore_inbox/{lore_filename}',
        'timestamp': '2026-09-22T23:05:00Z',
    })
    manifest['total_cells'] = len(manifest['entries'])
    manifest['promoted_to_canon_count'] = sum(1 for e in manifest['entries'] if e.get('promoted_to_canon'))
    manifest['version'] = '2.18.0'
    manifest['updated_at'] = '2026-09-22T23:05:00Z'

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    return new_rank, cell_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='process all pending files once')
    parser.add_argument('--watch', action='store_true', help='continuously watch for new files')
    args = parser.parse_args()

    inbox = Path('/workspace/research/lore_inbox')

    if args.once or args.watch:
        processed = set()
        if (inbox / '.processed').exists():
            processed = set(json.load(open(inbox / '.processed')))

        while True:
            pending = [f for f in inbox.glob('*.md')
                       if f.name not in processed and f.stat().st_size > 50]

            for f in pending:
                print(f"\nProcessing {f.name}...", flush=True)
                lore = f.read_text()
                if '## Lore' in lore:
                    lore = lore.split('## Lore')[1]
                    if '## ' in lore:
                        lore = lore.split('## ')[0]
                lore = lore.strip()
                if len(lore) < 80:
                    print(f"  Lore too short ({len(lore)} chars), skipping")
                    processed.add(f.name)
                    continue

                scores = probe_lore(lore)
                print(f"  Composite: {scores['composite']:.3f} | doctrine: {scores.get('primary_doctrine', '?')}", flush=True)
                if scores.get('promoted'):
                    rank, cell_id = file_canon_cell(lore, f.name, scores)
                    print(f"  🌟 PROMOTED as cell {rank}: {cell_id}")
                    processed.add(f.name)
                else:
                    print(f"  Not promoted (composite < 0.7)")
                    processed.add(f.name)

            json.dump(list(processed), open(inbox / '.processed', 'w'))

            if not args.watch:
                break
            time.sleep(5)

if __name__ == "__main__":
    main()
