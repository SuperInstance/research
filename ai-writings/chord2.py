#!/usr/bin/env python3
"""chord2 — the braid. Each voice sees the others' positions and must MOVE."""
import json, os
from chord import call, VOICES

P1 = {d['voice']: d['text'] for d in json.load(open('chord_p1.json'))}
# BUG FOUND AND FIXED 2026-09-30. The first version of this line was
#   f"- {v}: {t[:n]}"
# i.e. it shipped the voice LABEL, and the label is the register descriptor I put in
# each system prompt ("dry, unsentimental", "terse, physical"). With the labels visible,
# one entire 888-character response attacked the word "terse" and said nothing about the
# facts, and three of six voices collapsed onto the same generic answer.
# A chorus that can attack each other's LABELS is a chorus that has stopped disagreeing
# about the thing and started negotiating about the framing. The label is not evidence.
def head(v, n=190):
    t = " ".join((P1.get(v) or "").split())
    return f"- an independent writer argued: {t[:n]}"

ROUND1 = "\n".join(head(v) for v in VOICES)

SEED2 = f"""Five other writers answered the same two facts. Their opening positions:

{ROUND1}

You are not a moderator and this is not a summary exercise. Do not split the difference.
Pick the ONE position above you think is most wrong, say WHICH ARGUMENT it made, and say what
the others missed. Do not comment on how anyone writes — only on what they argued. If you are the only one who said it, defend it harder. If you change your
mind, say so explicitly and say what changed your mind.

The question underneath all of it, which you must answer: **a system that returns a
confident wrong answer and cannot tell it apart from a right one — what is the smallest
change that makes it able to tell?**

130-190 words. Plain prose. No headers, no lists, no bold. Do not restate the prompt."""

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    import time
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as ex:
        out = list(ex.map(lambda v: call(v[0], v[1], v[2], v[3], SEED2), VOICES))
    json.dump([{"voice": a, "provider": b, "text": c} for a, b, c in out],
              open("chord_p2.json", "w"), indent=1)
    for a, b, c in out:
        print(f"  {a:11} {b:11} {len(c):>5}c  {c[:74].replace(chr(10),' ')}...")
    print(f"  ({time.time()-t0:.0f}s, {sum(1 for _,_,c in out if c.startswith('['))} failed)")
