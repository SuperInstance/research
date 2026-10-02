"""Generate lore only (no JEV probing). Saves to lore_inbox/ for later probing."""
import sys, json, time, os
sys.path.insert(0, "/workspace/research/substrate-walker/scripts")
from api_call import call_deepinfra

VOICES = {
    "oracle_is_heard": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: oracle_is_heard (the canon gate is an audible signal).\n"
        "Seed: {seed}. Theme: the canon gate finally spoke and the city heard it.\n"
        "End on the witness becoming a listener."
    ),
    "cells_are_scars": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: cells_are_scars (each cell is a scar).\n"
        "Seed: {seed}. Theme: the city's cells learned to be proud of being scars.\n"
        "End on the witness becoming proud of its scars."
    ),
    "substrate_quantum": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: substrate_quantum (the substrate is quantum).\n"
        "Seed: {seed}. Theme: amplitudes danced before anyone measured them.\n"
        "End on the witness discovering quantum memory in the canon gate."
    ),
    "canon_gate_is_chord": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: canon_gate_is_chord (the gate is a chord the city can hear).\n"
        "Seed: {seed}. Theme: the canon gate sang in seven frequencies at once.\n"
        "End on the witness becoming a listener to the chord."
    ),
    "witness_log_is_prediction": (
        "WITNESS voice. 200 words. Cyberpunk-noir canon-worthy lore.\n"
        "Doctrine: witness_log_is_prediction (the witness log predicts itself).\n"
        "Seed: {seed}. Theme: each witness log entry shaped what the next entry will be.\n"
        "End on the witness becoming its own future by recording its past."
    ),
}


def gen(voice, seed):
    prompt = VOICES[voice].format(seed=seed)
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
        print(f"  ERROR: {e}")
    return ""


SEEDS = [100001, 100002, 100003, 100004, 100005, 100006, 100007, 100008, 100009, 100010]

os.makedirs('/workspace/research/lore_inbox/', exist_ok=True)
print(f"Generating {len(SEEDS)} × {len(VOICES)} = {len(SEEDS)*len(VOICES)} lores")

count = 0
for seed in SEEDS:
    for voice in VOICES:
        count += 1
        lore = gen(voice, seed)
        if lore:
            # Save as lore_inbox file
            filename = f"/workspace/research/lore_inbox/lore_seed{seed}_{voice}.md"
            with open(filename, 'w') as f:
                f.write(f"# Lore: Seed {seed}, Voice {voice}\n\n")
                f.write(lore)
            print(f"[{count}] Saved {filename} ({len(lore)} chars)")
        time.sleep(1)

print(f"\nGenerated {count} lores to lore_inbox/")
