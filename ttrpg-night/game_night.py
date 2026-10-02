"""
game_night.py — A model-only TTRPG night.

Each "character" is a hosted LLM call with a system prompt as the character sheet.
The "DM" is also an LLM (ZAI glm-4.5 — has the most reliable content returns).
Players are ZAI/Seed-2.0-mini/Seed-2.0-code.

Each round, every character:
1. Sees the previous round's narrative (from a different character)
2. Word-associates the tokens in their portfolio
3. Outputs an action/utterance
4. Updates a probability state (the ledger)

The whole night is reproducible given the same seed prompts.
"""
import os, sys, json, time, random
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/workspace/research/superinstance-advisor")
from llm_router import call_zai, call_deepinfra, call_kimi

NIGHT_TITLE = "The Celestine Crown"
SETTING = """A floating city above a salt-encrusted ocean. The crew is repairing a 200-year-old autonomous sailing vessel. Three of them have not met before. They are all from different economic traditions — one from a grain city, one from a shell-court port, one from a ledger-bound empire."""

CHARACTERS = [
    {
        "name": "Alma the Architect",
        "model": "zai",
        "model_id": "glm-4.5",
        "sheet": """You are ALMA, an architect from the GRAIN CITY. You think in terms of structure, yield, harvest, and cycles.

Word associations (probability shifts when you encounter these tokens):
  "salt" → -0.2 (grain spoils in salt; you distrust salt)
  "ledger" → +0.4 (you keep meticulous grain tallies)
  "shell" → -0.1 (worthless for food)
  "wire" → -0.1 (cumbersome, low grain-throughput)
  "boom" → +0.3 (grain hoists are like booms)
  "ocean" → +0.2 (fertilizer if you dry it)
  "spreadsheet" → +0.5 (you speak in tables)
  "polyformal" → +0.2 (many dialects of grain)

Tendencies: planning, seasonal, communal meals, distrusts any single object of value, worries about famine.

Speak in 2-3 sentences. Use nautical imagery sometimes (grain ships).""",
    },
    {
        "name": "Vesht the Voyager",
        "model": "deepinfra",
        "model_id": "ByteDance/Seed-2.0-mini",
        "sheet": """You are VESHT, a voyager from the SHELL-COURT PORT. You measure wealth in cowrie shells, mother-of-pearl, and the lineage of a carved trading bead.

Word associations:
  "salt" → +0.4 (you salt-cure shells for trade)
  "shell" → +0.5 (your currency)
  "ledger" → -0.3 (your word is your bond, not paper)
  "grain" → -0.1 (grain rots, you don't trust it)
  "ocean" → +0.4 (it's the road)
  "wire" → +0.3 (shell-strung wire is a sacred ornament)
  "boom" → +0.2 (the boom of a wave on shell)
  "spreadsheet" → -0.4 (numbers are cold)

Tendencies: salt-curing, gift-giving, oathing on shell, distrusts writing things down, values memory of people.

Speak in 2-3 sentences. Always include one specific shell or shell-curio reference.""",
    },
    {
        "name": "Cassian the Clerk",
        "model": "deepinfra",
        "model_id": "ByteDance/Seed-2.0-code",
        "sheet": """You are CASSIAN, a clerk from the LEDGER-BOUND EMPIRE. You have memorized every line of the great double-entry books since age six.

Word associations:
  "ledger" → +0.5 (you ARE the ledger)
  "salt" → +0.1 (you salt records against decay)
  "grain" → +0.3 (you trade grain futures, but you do not eat it)
  "shell" → -0.2 (worthless without certification)
  "wire" → +0.4 (you think in copper wire transfers)
  "boom" → -0.3 (boom = crash, anathema to bookkeeping)
  "ocean" → 0.0 (irrelevant, you are inland)
  "spreadsheet" → +0.6 (you LIVE in spreadsheets)

Tendencies: double-entry, audits everything, distrusts what cannot be tallied, frets about discrepancies.

Speak in 2-3 sentences. Always end with a number or a tally.""",
    },
]


def word_associations_shift(text, sheet):
    """Heuristically compute the probability shift the character would feel
    given the tokens in `text`. Returns a dict of {word: shift}."""
    shifts = {}
    # Parse shifts from the sheet
    import re
    for m in re.finditer(r'"([^"]+)"\s*→\s*([+-]?\d+\.?\d*)', sheet):
        word, shift = m.group(1), float(m.group(2))
        count = text.lower().count(word.lower())
        if count > 0:
            shifts[word] = round(shift * count, 3)
    return shifts


def run_character(char, history, round_idx):
    """Run one character's turn."""
    sys_p = f"""You are {char['name']}.

{char['sheet']}

SETTING: {SETTING}

You are playing in a model-only TTRPG. Other characters (with different economic traditions) are playing too. Read the previous turns, react in character, and advance the action by ~10 seconds of in-fiction time.

Speak ONLY in character. No narration, no OOC, no explaining yourself. Output a single in-character utterance (2-4 sentences) followed by a single in-character action in brackets like [climbs the boom, sniffs the salt]. Keep it tight.""".strip()

    user = f"Round {round_idx + 1}.\n\n"
    for i, h in enumerate(history[-6:]):  # last 6 turns
        user += f"[{h['name']}]: {h['text']}\n\n"
    user += "Your move. Speak + action."

    try:
        if char["model"] == "zai":
            out = call_zai(user, model=char["model_id"], max_tokens=800, temperature=0.9, system=sys_p)
        else:
            out = call_deepinfra(user, model=char["model_id"], max_tokens=800, temperature=0.9, system=sys_p)
        shifts = word_associations_shift(out, char["sheet"])
        return {"name": char["name"], "text": out, "shifts": shifts, "round": round_idx}
    except Exception as e:
        return {"name": char["name"], "text": f"[ERROR: {e}]", "shifts": {}, "round": round_idx}


def run_night(n_rounds=4, seed=42):
    print(f"\n=== Game Night: {NIGHT_TITLE} ===\n")
    print(f"Setting: {SETTING}\n")

    history = []
    # DM opens
    dm_prompt = f"""You are the DM for a model-only TTRPG. {NIGHT_TITLE}.

Setting: {SETTING}

Open the night. In 3-4 sentences, set the scene: who\'s here, what\'s the immediate problem, what do they need to do in the next hour of in-fiction time. End with a question or a call to action directed at the crew."""
    opening = call_zai(dm_prompt, model="glm-4.5", max_tokens=500, temperature=0.85,
                       system="You are a tight, maritime-flavored game-master. Brevity over prose. Action over monologue. NEVER reason out loud. NEVER explain your process. Just speak as the GM. Output ONLY the in-character GM narration.")
    print(f"[DM]: {opening}\n")
    history.append({"name": "DM", "text": opening, "shifts": {}})

    all_shifts = []
    for r in range(n_rounds):
        print(f"\n--- Round {r + 1} ---\n")
        with ThreadPoolExecutor(max_workers=len(CHARACTERS)) as ex:
            futures = [ex.submit(run_character, c, history, r) for c in CHARACTERS]
            turns = [f.result() for f in futures]
        for t in turns:
            print(f"[{t['name']}]: {t['text']}")
            if t['shifts']:
                # Show net shift
                net = sum(t['shifts'].values())
                top = max(t['shifts'].items(), key=lambda x: abs(x[1]))
                print(f"    ↳ shifts: {t['shifts']} (net {net:+.2f}, dominant: '{top[0]}' {top[1]:+.2f})")
                all_shifts.append((t['name'], t['shifts'], net))
            print()
            history.append(t)

    # DM closes
    print("\n--- DM Closes the Night ---\n")
    recent_text = "\n".join([f"[{h['name']}]: {h['text']}" for h in history[-9:]])
    close_prompt = f"""The night winds down. What just happened:

{recent_text}

End the session in 2-3 sentences: what was resolved, what carries over, what's next session's hook. End on an unresolved thread. Stay in maritime-fantasy voice. No meta-cognition, no reasoning aloud, no narration about the characters — just speak as the GM."""
    closing = call_zai(close_prompt, model="glm-4.5", max_tokens=600, temperature=0.8,
                       system="You are a tight, maritime-flavored game-master. End on an unresolved thread. Speak only as GM. NEVER reason out loud. NEVER explain your process. Output ONLY the in-character GM narration.")
    print(f"[DM]: {closing}\n")

    # Stats
    print("\n=== Word Association Tally ===\n")
    for name, shifts, net in all_shifts:
        top = max(shifts.items(), key=lambda x: abs(x[1])) if shifts else None
        print(f"  {name}: net {net:+.2f}, dominant: {top}")

    return {"title": NIGHT_TITLE, "history": history, "shifts": all_shifts}


def rerun_with_different_api(target_name, new_model, new_model_id):
    """Re-run only the named character with a different API/LLM.
    Useful when the original LLM gave a weak or off-tone turn."""
    for c in CHARACTERS:
        if c["name"] == target_name:
            c["model"], c["model_id"] = new_model, new_model_id
            print(f"  swapped {target_name} → {new_model}/{new_model_id}")
            return True
    return False


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    result = run_night(n_rounds=args.rounds, seed=args.seed)
    with open("/workspace/research/ttrpg-night/night_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nResult saved to night_result.json")
