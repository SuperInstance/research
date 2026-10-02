#!/usr/bin/env python3
"""InstinctBands — Vibecoder priority queue.

Inspired by aboracle (SuperInstance): SURVIVE → FLEE → GUARD → CURIOUS → COOPERATE.

Maps the substrate's task priority into a work-queue that the vibecoder
vibecoder agent can use. Each instinct has a numeric threshold; only tasks
above the threshold are picked.

SURVIVE (1.0)   — emit canonical piece / fix critical bug
GUARD  (0.7)   — maintain canon / pin canary
CURIOUS (0.5)  — explore / investigate / probe
COOPERATE (0.3) — help other agents / cross-pollinate
FLEE (0.0)     — park / abandon / decline
"""
from enum import Enum

class Instinct(Enum):
    SURVIVE = "survive"
    GUARD = "guard"
    CURIOUS = "curious"
    COOPERATE = "cooperate"
    FLEE = "flee"

# Priority weights (higher = more urgent)
INSTINCT_WEIGHTS = {
    Instinct.SURVIVE: 1.0,
    Instinct.GUARD: 0.7,
    Instinct.CURIOUS: 0.5,
    Instinct.COOPERATE: 0.3,
    Instinct.FLEE: 0.0,
}

# Default ordering: high to low
DEFAULT_ORDER = [Instinct.SURVIVE, Instinct.GUARD, Instinct.CURIOUS, Instinct.COOPERATE, Instinct.FLEE]

def rank_task(task_priority: float) -> Instinct:
    """Map a 0-1 priority to an instinct."""
    if task_priority >= 0.85:
        return Instinct.SURVIVE
    elif task_priority >= 0.60:
        return Instinct.GUARD
    elif task_priority >= 0.40:
        return Instinct.CURIOUS
    elif task_priority >= 0.10:
        return Instinct.COOPERATE
    else:
        return Instinct.FLEE

def work_queue(tasks: list) -> list:
    """Sort tasks by instinct priority (highest first)."""
    def sort_key(task):
        priority = task.get('priority', 0.5)
        instinct = rank_task(priority)
        return -INSTINCT_WEIGHTS[instinct]

    return sorted(tasks, key=sort_key)

def main():
    print('=== InstinctBands — Vibecoder Work Queue ===\n')

    tasks = [
        {'name': 'Fix test_typesafe_client env pollution', 'priority': 0.95, 'reason': 'BLOCKING merge'},
        {'name': 'Add canary pin to substrate-llm-client', 'priority': 0.90, 'reason': 'FLEET CANARY'},
        {'name': 'Bump jev-quilt on PyPI to 0.0.2', 'priority': 0.70, 'reason': 'main has new code'},
        {'name': 'Build cross-pollination atlas', 'priority': 0.55, 'reason': 'Visualize canon network'},
        {'name': 'JEV session 23 (more bedrock probes)', 'priority': 0.50, 'reason': 'Validate canon'},
        {'name': 'Help Casey with PR review', 'priority': 0.40, 'reason': 'Cooperative'},
        {'name': 'WR21 (5 more cross-pollinated pieces)', 'priority': 0.30, 'reason': 'Cooperative'},
        {'name': 'Try the procedural canon game demo', 'priority': 0.20, 'reason': 'Exploration'},
        {'name': 'Look at agent-priming-toolkit repo', 'priority': 0.15, 'reason': 'Background scan'},
        {'name': 'Investigate substrate-llm-client memory leak', 'priority': 0.05, 'reason': 'Speculative, low priority'},
    ]

    # Group by instinct
    queue = work_queue(tasks)
    print('--- Sorted by instinct ---')
    for t in queue:
        instinct = rank_task(t['priority'])
        marker = '🔥' if instinct == Instinct.SURVIVE else '🛡' if instinct == Instinct.GUARD else '🔍' if instinct == Instinct.CURIOUS else '🤝' if instinct == Instinct.COOPERATE else '💨'
        print(f'  {marker} [{instinct.value:9s}]  {t["name"]:50s}  pri={t["priority"]}')

    # Stats
    from collections import Counter
    instincts = Counter(rank_task(t['priority']).value for t in tasks)
    print(f'\n--- Distribution ---')
    for k, v in instincts.items():
        print(f'  {k}: {v}')

if __name__ == '__main__':
    main()
