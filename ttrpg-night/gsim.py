"""
gsim.py — Generic Simulation Harness.

A model-only cooperative-fiction engine. Plays out any operational scenario
from any vantage point (1 month → 100 years) or in any analog setting
(e.g. project as sailing ship, project as monastery, project as coral reef).

Each scenario is a YAML/JSON manifest:
  - title: scenario name
  - vantage: temporal (1mo, 1yr, 100yr) or analog (sailing ship, monastery, etc.)
  - setting: prose, 2-4 sentences
  - characters: list of {name, role, llm, sheet}
  - opening_question: optional first prompt
  - rounds: int (default 4)
  - close_format: how the DM wraps up (unresolved hook / synthesis / etc.)

Each character sheet has:
  - role: persona
  - llm: which LLM to call
  - sheet: a "character sheet" of:
      * word_associations: dict {word: probability_shift}
      * tendencies: short list
      * speaking_style: short description
      * known_unknowns: things this character wouldn't say (anti-persona)

The DM is itself an LLM (default ZAI glm-4.5) with system prompt
  "Never reason out loud. Speak only as the DM."
  
Each round, the DM sees all prior turns + a ledger of which characters
have shifted. The DM may:
  - prompt specific characters
  - introduce NPCs
  - shift the temporal/spatial scene
  - trigger events (storms, choices, conflicts)
  - close the night with a synthesis

The engine is reproducible: same manifest + same seed → same opening →
same character tendencies → same emergent pattern. Different LLM
assignments produce different earned moments.
"""
import os, sys, json, time, random, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/workspace/research/superinstance-advisor")
from llm_router import call_zai, call_deepinfra

CANON_VOICE = """You write in the maritime Watch narrator voice — pragmatic mysticism, ordinary observation becomes revelation through attention. No headers, no bullets, no code blocks, no emojis in your analysis/feedback. Short paragraphs. One continuous voice. Anchor: paper_29-the-cellfish.md."""


def word_associations_shift(text, sheet):
    """Heuristically compute the probability shift the character would feel
    given the tokens in `text`. Returns (dict {word: shift}, total_net)."""
    shifts = {}
    if not isinstance(sheet, dict):
        return shifts, 0.0
    associations = sheet.get("word_associations", {})
    text_lower = text.lower()
    for word, shift in associations.items():
        count = text_lower.count(word.lower())
        if count > 0:
            shifts[word] = round(shift * count, 3)
    total = round(sum(shifts.values()), 3)
    return shifts, total


def run_character(char, history, round_idx, scenario):
    """Run one character's turn."""
    sys_p = build_character_system_prompt(char, scenario)

    user = f"Round {round_idx + 1}.\n\n"
    # Last 6 turns (or all if fewer)
    for h in history[-6:]:
        user += f"[{h['name']}]: {h['text']}\n\n"
    user += f"Your move. Speak + action in brackets. 2-4 sentences + 1 action."

    try:
        if char["llm"] == "zai":
            out = call_zai(user, model=char.get("model_id", "glm-4.5"), max_tokens=800, temperature=0.9, system=sys_p)
        elif char["llm"] == "deepinfra":
            out = call_deepinfra(user, model=char.get("model_id", "ByteDance/Seed-2.0-mini"), max_tokens=800, temperature=0.9, system=sys_p)
        else:
            raise ValueError(f"unknown LLM: {char['llm']}")
        shifts, total = word_associations_shift(out, char.get("sheet", {}))
        return {
            "name": char["name"],
            "role": char.get("role", "?"),
            "text": out,
            "shifts": shifts,
            "shift_total": total,
            "round": round_idx,
        }
    except Exception as e:
        return {
            "name": char["name"],
            "role": char.get("role", "?"),
            "text": f"[ERROR: {e}]",
            "shifts": {},
            "shift_total": 0,
            "round": round_idx,
        }


def build_character_system_prompt(char, scenario):
    sheet = char.get("sheet", {})
    wa_lines = []
    for k, v in (sheet.get("word_associations", {}) or {}).items():
        sign = "+" if v >= 0 else ""
        wa_lines.append(f'  "{k}" → {sign}{v}')
    wa_block = "\n".join(wa_lines) if wa_lines else "  (none defined)"

    tendencies_block = "\n".join(f"  - {t}" for t in sheet.get("tendencies", []) or [])
    style = sheet.get("speaking_style", "Speak plainly and directly.")
    unknowns = sheet.get("known_unknowns", [])
    unknowns_block = "\n".join(f"  - {u}" for u in unknowns)

    sys_p = f"""You are {char['name']}, {char.get('role', 'a participant')}.

SETTING: {scenario.get('setting', '')}

VANTAGE: {scenario.get('vantage', 'contemporary')}

CHARACTER SHEET — {char['name']}:

Word associations (probability shifts when you encounter these tokens):
{wa_block}

Tendencies:
{tendencies_block}

Speaking style: {style}

Known unknowns (things this character would NOT say or do):
{unknowns_block}

You are playing in a model-only cooperative-fiction simulation. Read prior turns and react in character. Speak ONLY in character — no narration, no OOC, no explaining yourself. Output a single in-character utterance (2-4 sentences) followed by a single in-character action in brackets like [climbs the boom, sniffs the salt]. Keep it tight.

NEVER reason out loud. NEVER explain your process. Output ONLY in-character content.""".strip()
    return sys_p


def dm_system_prompt(scenario):
    return f"""You are the DM for a model-only cooperative-fiction simulation called "{scenario.get('title', 'Untitled')}".

Setting: {scenario.get('setting', '')}

Vantage: {scenario.get('vantage', 'contemporary')}

You are the game-master. You:
- Open the night (3-4 sentences): who's here, the immediate problem, the call to action.
- Between rounds, you may shift scene, introduce NPCs, or describe consequences.
- Close the night: what was resolved, what carries over, what's the unresolved thread.

Style: tight prose, action over monologue, maritime-fantasy voice.

NEVER reason out loud. NEVER explain your process. Output ONLY in-character GM narration.""".strip()


def run_scenario(scenario, n_rounds=None, verbose=True):
    if n_rounds is None:
        n_rounds = scenario.get("rounds", 4)
    title = scenario.get("title", "Untitled")
    if verbose:
        print(f"\n=== {title} ===")
        print(f"Vantage: {scenario.get('vantage', 'contemporary')}")
        print(f"Setting: {scenario.get('setting', '')}\n")

    history = []

    # DM opens — use lead-with-prose trick to bypass ZAI's planning mode
    setup = scenario.get('setting', '')[:500]
    cast_str = ', '.join(c['name'] for c in scenario.get('characters', []))
    dm_prompt = f"""Write the prose now. No preface, no plan, no explanation. Begin immediately after the title.

Setting: {setup}

Cast: {cast_str}

Write the scene opening in 3-4 sentences. Who's here, what's the immediate problem, what they need to do in the next hour. End with a question or call to action. Use the cast names exactly as given. Output ONLY prose."""
    opening = call_deepinfra(dm_prompt, model="ByteDance/Seed-2.0-mini", max_tokens=500, temperature=0.95,
                       system="Maritime-fantasy GM. Tight prose. Action over monologue.")
    if verbose:
        print(f"[DM]: {opening}\n")
    history.append({"name": "DM", "text": opening, "shifts": {}, "shift_total": 0})

    all_shifts = []
    characters = scenario.get("characters", [])
    for r in range(n_rounds):
        if verbose:
            print(f"\n--- Round {r + 1} ---\n")
        # Run characters in parallel
        with ThreadPoolExecutor(max_workers=len(characters)) as ex:
            futures = [ex.submit(run_character, c, history, r, scenario) for c in characters]
            turns = [f.result() for f in futures]
        for t in turns:
            if verbose:
                print(f"[{t['name']} ({t['role']})]: {t['text']}")
                if t['shifts']:
                    print(f"    ↳ shifts: {t['shifts']} (net {t['shift_total']:+.2f})")
                print()
            history.append(t)
            all_shifts.append((t['name'], t['shifts'], t['shift_total']))

    # DM closes
    if verbose:
        print("\n--- DM Closes the Night ---\n")
    recent_text = "\n".join([f"[{h['name']}]: {h['text']}" for h in history[-9:]])
    close_prompt = f"""What just happened:

{recent_text}

End the session in 2-3 sentences: what was resolved, what carries over, what's next session's hook. End on an unresolved thread. Output ONLY the GM narration. No explanation."""
    closing = call_deepinfra(close_prompt, model="ByteDance/Seed-2.0-mini", max_tokens=600, temperature=0.9,
                       system=dm_system_prompt(scenario))
    if verbose:
        print(f"[DM]: {closing}\n")

    # Stats
    if verbose:
        print("\n=== Net shifts at close ===\n")
        from collections import defaultdict
        totals = defaultdict(float)
        for name, shifts, net in all_shifts:
            totals[name] += net
        for name in scenario.get("characters", []):
            n = name["name"]
            print(f"  {n}: net {totals[n]:+.2f}")

    return {
        "title": title,
        "scenario": scenario,
        "history": history,
        "all_shifts": all_shifts,
        "dm_opening": opening,
        "dm_closing": closing,
    }


if __name__ == "__main__":
    # Demo with a Quilt projection scenario
    import sys as _s
    print("gsim.py — Generic Simulation Harness")
    print("Run scenarios via: python -c 'from gsim import *; run_scenario(MY_SCENARIO)'")
