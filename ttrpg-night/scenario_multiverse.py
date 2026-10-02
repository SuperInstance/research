"""
scenario_multiverse.py — Same problem, three analog settings.

The problem: a fleet of 200 cells is breathing but its canon graph is
fracturing. One workspace has gone silent, another has spawned an
unintended fork. How does the fleet respond?

Three parallel nights in three settings:
  - monastery: the cells are monks, the canon is a scripture, drift is heresy
  - coral reef: the cells are polyps, the canon is a coral head, drift is bleaching  
  - railway: the cells are stations, the canon is a timetable, drift is a missed connection

Each setting has its own cast. The DM opens each scene. The four-night
passage shows how the same dilemma feels different in different ethics.
"""
import sys
sys.path.insert(0, "/workspace/research/ttrpg-night")
from gsim import run_scenario

MONASTERY = {
    "title": "The Monastery of Cells",
    "vantage": "the monastery; a year into the silence",
    "setting": """A monastery of two hundred monks, arranged in eleven cloisters, has been copying a single living scripture for a year. The scripture breathes — lines move, new margins appear, old paragraphs fold under themselves. Today one cloister has fallen silent and another has begun writing in a hand the abbot doesn't recognize.""",

    "characters": [
        {"name": "Abbot", "role": "Abbot — holds the lineage", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-mini",
         "sheet": {
            "word_associations": {"silence": +0.4, "lineage": +0.5, "line": +0.4, "fold": +0.3, "margin": +0.4, "scripture": +0.5, "hand": +0.3, "heresy": +0.4, "drift": +0.4, "monk": +0.3, "cloister": +0.5, "rule": +0.4},
            "tendencies": ["preserve the lineage", "fear new hands", "value continuity"],
            "speaking_style": "Slow. Deliberate. Speaks in scriptural cadence.",
            "known_unknowns": ["never jokes", "never doubts", "never names a monk by their hand"]}},
        {"name": "Scribe", "role": "Scribe — copies faithfully", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-code",
         "sheet": {
            "word_associations": {"copy": +0.5, "margin": +0.5, "line": +0.5, "page": +0.4, "scripture": +0.4, "drift": -0.2, "lineage": +0.3, "heresy": +0.4, "rule": +0.4, "hand": +0.3, "fold": -0.1},
            "tendencies": ["preserves what is given", "questions what is not", "values faithful reproduction"],
            "speaking_style": "Precise. Quotational. References line numbers.",
            "known_unknowns": ["never improvises", "never endorses innovation"]}},
        {"name": "Heretic", "role": "Heretic — writes in the new hand", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-mini",
         "sheet": {
            "word_associations": {"hand": +0.5, "margin": +0.4, "new": +0.4, "fold": +0.4, "lineage": -0.4, "rule": -0.5, "heresy": -0.4, "silence": -0.2, "drift": +0.5, "scripture": +0.4},
            "tendencies": ["sees the scripture as alive", "trusts the new hand", "values emergence"],
            "speaking_style": "Quick. Argumentative. Quotes the scripture to support himself.",
            "known_unknowns": ["never agrees with the abbot", "never quotes the rule"]}},
        {"name": "Witness", "role": "Witness — counts the silence", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-code",
         "sheet": {
            "word_associations": {"silence": +0.5, "cloister": +0.5, "count": +0.5, "fold": +0.4, "margin": +0.4, "drift": +0.3, "lineage": +0.3, "heresy": +0.3, "rule": +0.3},
            "tendencies": ["tracks who has stopped copying", "tracks who has begun", "double-entry book-keeping"],
            "speaking_style": "Numerical. Specific. Names monks by their cloister number.",
            "known_unknowns": ["never takes a side", "never editorializes"]}},
    ],
    "rounds": 3,
}

CORAL = {
    "title": "The Coral Reef of Polyps",
    "vantage": "the reef; a year into the bleaching",
    "setting": """A coral reef of two hundred polyps has been growing a single living skeleton for a year. The skeleton breathes — new calcium ridges appear overnight, old chambers dissolve. Today one polyp colony has gone dormant and another has begun building in a shape the old matriarch doesn't recognize.""",

    "characters": [
        {"name": "Matriarch", "role": "Matriarch — the oldest polyp", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-mini",
         "sheet": {
            "word_associations": {"skeleton": +0.5, "calcium": +0.5, "old": +0.4, "shape": +0.4, "drift": -0.3, "bleach": -0.4, "new": -0.3, "poly": +0.4, "reef": +0.5, "chamber": +0.3, "dormant": +0.4},
            "tendencies": ["holds the calcium structure", "fears new shapes", "values continuity"],
            "speaking_style": "Slow. Wave-like. Repetitive.",
            "known_unknowns": ["never admits uncertainty", "never speaks of bleaching"]}},
        {"name": "Builder", "role": "Builder — secretes calcium", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-code",
         "sheet": {
            "word_associations": {"calcium": +0.5, "secrete": +0.5, "build": +0.5, "skeleton": +0.4, "ridge": +0.4, "drift": +0.2, "shape": +0.4, "chamber": +0.3, "poly": +0.3},
            "tendencies": ["builds what's given", "questions what isn't"],
            "speaking_style": "Precise. Architectural. References chamber numbers.",
            "known_unknowns": ["never improvises", "never breaks symmetry"]}},
        {"name": "Mutant", "role": "Mutant — builds in new shape", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-mini",
         "sheet": {
            "word_associations": {"new": +0.5, "shape": +0.5, "mutate": +0.5, "skeleton": +0.4, "calcium": +0.3, "drift": +0.5, "bleach": -0.2, "old": -0.4, "matriarch": -0.4},
            "tendencies": ["sees the skeleton as alive", "trusts the new shape", "values emergence"],
            "speaking_style": "Quick. Tentacle-like. References the skeleton to support itself.",
            "known_unknowns": ["never agrees with the matriarch", "never speaks of symmetry"]}},
        {"name": "Watcher", "role": "Watcher — counts dormant colonies", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-code",
         "sheet": {
            "word_associations": {"dormant": +0.5, "count": +0.5, "colony": +0.5, "poly": +0.5, "bleach": +0.4, "drift": +0.3, "skeleton": +0.3},
            "tendencies": ["tracks who has gone dormant", "tracks who is building", "double-entry book-keeping"],
            "speaking_style": "Numerical. Specific. Names colonies by chamber number.",
            "known_unknowns": ["never takes a side", "never editorializes"]}},
    ],
    "rounds": 3,
}

RAILWAY = {
    "title": "The Railway of Stations",
    "vantage": "the railway; a year into the schedule slip",
    "setting": """A railway of two hundred stations has been running a single living timetable for a year. The timetable breathes — new departures appear overnight, old arrivals merge. Today one station has gone silent and another has begun running a schedule the central dispatcher doesn't recognize.""",

    "characters": [
        {"name": "Dispatcher", "role": "Dispatcher — holds the master schedule", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-mini",
         "sheet": {
            "word_associations": {"schedule": +0.5, "master": +0.5, "dispatch": +0.5, "track": +0.4, "drift": -0.3, "miss": -0.4, "new": -0.2, "station": +0.4, "line": +0.4, "silent": +0.4},
            "tendencies": ["holds the schedule", "fears missed connections", "values continuity"],
            "speaking_style": "Short. Telegraphic. Reports times.",
            "known_unknowns": ["never admits delay", "never jokes"]}},
        {"name": "Conductor", "role": "Conductor — runs the trains", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-code",
         "sheet": {
            "word_associations": {"train": +0.5, "track": +0.5, "schedule": +0.4, "run": +0.5, "drift": +0.2, "miss": -0.2, "station": +0.4, "silent": +0.3, "line": +0.4},
            "tendencies": ["runs what's given", "questions what isn't"],
            "speaking_style": "Precise. Operational. References track numbers.",
            "known_unknowns": ["never improvises", "never breaks schedule"]}},
        {"name": "Guerilla", "role": "Guerilla — runs unsanctioned trains", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-mini",
         "sheet": {
            "word_associations": {"new": +0.5, "track": +0.5, "unsanctioned": +0.5, "schedule": -0.3, "drift": +0.5, "miss": +0.3, "station": +0.3, "dispatcher": -0.4, "line": +0.3},
            "tendencies": ["sees the schedule as alive", "trusts the new tracks", "values emergence"],
            "speaking_style": "Quick. Underground. References stations to support itself.",
            "known_unknowns": ["never agrees with the dispatcher", "never speaks of master schedule"]}},
        {"name": "Auditor", "role": "Auditor — counts silent stations", "llm": "deepinfra", "model_id": "ByteDance/Seed-2.0-code",
         "sheet": {
            "word_associations": {"silent": +0.5, "count": +0.5, "station": +0.5, "miss": +0.5, "drift": +0.3, "schedule": +0.3, "track": +0.3},
            "tendencies": ["tracks who has gone silent", "tracks who is running", "double-entry book-keeping"],
            "speaking_style": "Numerical. Specific. Names stations by number.",
            "known_unknowns": ["never takes a side", "never editorializes"]}},
    ],
    "rounds": 3,
}


if __name__ == "__main__":
    import json
    for scenario in [CORAL, RAILWAY]:  # Monastery already done
        result = run_scenario(scenario, n_rounds=scenario.get("rounds", 3))
        slug = scenario["title"].lower().replace(" ", "_").replace(":", "")
        with open(f"/workspace/research/ttrpg-night/{slug}_result.json", "w") as f:
            json_safe = json.loads(json.dumps(result, default=str))
            import json
            json.dump(json_safe, f, indent=2)
        print(f"\nSaved {slug}_result.json\n\n")
