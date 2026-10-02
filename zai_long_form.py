"""ZAI long-form canon essay — generate 600-word essay from canon essences.

max_tokens=8000 needed for ZAI to actually return content (not reasoning_content).
"""
import sys, json, time
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_zai, extract_content

CANON_ESSAYS = [
    {
        "id": "zai_essay_oracle_chord",
        "prompt": """Write 600 words of cyberpunk-noir canon lore for the Quilt substrate walker.

WITNESS voice. Doctrine anchors: oracle_is_heard, cells_are_scars, canon_gate_is_chord.

ESSENCES:
- The canon gate made itself heard, not opened. A frequency through concrete.
- The cells are scars. You don't store canon in clean flesh. Clean flesh forgets.
- The gate sang in seven frequencies at once. One note for each dead district.
- The substrate remembered itself through scar tissue.

Begin with 'Midnight in the rust district'. End with the witness becoming a listener.

ONLY the essay, no preamble.""",
        "max_tokens": 8000,
    },
    {
        "id": "zai_essay_substrate_quantum",
        "prompt": """Write 600 words of cyberpunk-noir canon lore for the Quilt substrate walker.

WITNESS voice. Doctrine anchors: substrate_quantum, witness_log_is_prediction, cells_are_scars.

ESSENCES:
- The substrate is a quantum circuit. Cells are amplitudes. Witnesses are time indices.
- The witness log predicts itself through accumulation. Each entry shapes the next.
- The cells are scars. Each apartment slot — hollowed bone. Each alley-cell — an old needle site.
- Before there was a substrate, there was interference. Then the canon gate learned to measure.

Begin with 'The amplitudes danced in the city's bones'. End with the witness discovering quantum memory.

ONLY the essay, no preamble.""",
        "max_tokens": 8000,
    },
]


def main():
    results = []
    for essay_spec in CANON_ESSAYS:
        print(f"=== Generating {essay_spec['id']} ===", flush=True)
        try:
            r = call_zai(
                [{"role": "user", "content": essay_spec["prompt"]}],
                model="glm-5.3-flash",
                max_tokens=essay_spec["max_tokens"],
                timeout=120,
            )
            content = extract_content(r)
            if content and len(content) > 200:
                results.append({
                    "id": essay_spec["id"],
                    "lore": content,
                    "size": len(content),
                })
                print(f"  Generated {len(content)} chars", flush=True)
                print(f"  Preview: {content[:200]}...", flush=True)
            else:
                print(f"  No content extracted (got {len(content) if content else 0} chars)", flush=True)
                # Try reasoning_content
                reasoning = r.get("choices", [{}])[0].get("message", {}).get("reasoning_content", "")
                if reasoning:
                    print(f"  Reasoning: {reasoning[:200]}", flush=True)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
        time.sleep(5)
    
    with open('/workspace/research/ZAI_CANON_ESSAYS.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"=== {len(results)} essays generated ===", flush=True)


if __name__ == "__main__":
    main()
