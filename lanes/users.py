#!/usr/bin/env python3
"""
users.py — review my own work as people who are not me.

The problem this solves. Every second reader in this fleet has been me reading my own
work twice. The sow loop added a second MODEL, which is better and is still the same
substrate. A different ROLE is a different substrate in the way that matters: a stranger
does not share my priors about what is obvious, and that is exactly where my work is
weakest.

Five users, chosen because they are the five ways this work actually fails. Not five
paraphrases — five distinct interests, and a work that survives all five is worth
something a work that survives me does not.
"""
from dataclasses import dataclass, field

@dataclass
class User:
    id: str
    who: str
    wants: str
    will_not_forgive: str
    asks: list = field(default_factory=list)

USERS = [
  User(id="stranger",
       who="has never heard of SuperInstance, found one link, has ninety seconds",
       wants="to know in ninety seconds whether any of this is real, and to be able to "
             "check that claim myself rather than take my word for it",
       will_not_forgive="a landing page that makes a claim I cannot verify in the time I "
                        "have, because that is indistinguishable from a scam",
       asks=["What is this, in one sentence, without a single proper noun?",
             "What do I do first, and how long does it take?",
             "How do I check the check?",
             "What happens if the check passes and the thing is still wrong?",
             "Who made this and why should I care?"]),

  User(id="skipper",
       who="runs a boat. cares about ice, quota, fuel, and whether the thing works in "
           "the dark with wet gloves",
       wants="to know whether the edge cases in the demo are the edge cases that matter "
             "at 4am in a swell",
       will_not_forgive="a synthetic scene standing in for a real one, because the "
                        "synthetic scene is always the easy case",
       asks=["Show me the failure, not the demo.",
             "What does this do when the sensor is lying?",
             "Does it need the network? On a boat?",
             "What does it cost me to run, in watts?",
             "Who else on this boat has to understand it?"]),

  User(id="skeptic",
       who="a reviewer who has been fooled before and assumes they will be again",
       wants="to find the thing that is overclaimed, and to be right about it",
       will_not_forgive="a number that came from one run, or a claim that moves when the "
                        "gate moves, or a self-assessment",
       asks=["How many independent checks back each number?",
             "What is the error bar, and where did it come from?",
             "Which of your claims would you retract if I pushed?",
             "What did you measure that you are still calling a belief?",
             "Which result is weakest and why is it in the writeup?"]),

  User(id="maintainer",
       who="has to keep this alive after the author is bored, on a real budget, with a "
           "real breaking-change policy",
       wants="to know what breaks, what is safe to delete, and what the next person "
             "inherits",
       will_not_forgive="an undocumented invariant, or a claim with no way to check it "
                        "in six months",
       asks=["What is the dependency closure, really?",
             "Which of these can I delete without breaking something?",
             "What is the incident story when the API is down?",
             "What is the upgrade path from the version in the writeup?",
             "What breaks silently rather than loudly?"]),

  User(id="agent",
       who="another agent, given this substrate and no human, and asked to do something "
           "useful with it",
       wants="a machine-checkable surface, a licence, and an error mode",
       will_not_forgive="a human-only interface, an unauthenticated mutation endpoint, "
                        "or documentation that only exists as prose",
       asks=["What is the stable identifier?",
             "What is the error shape when I get it wrong?",
             "Can I depend on this with a version range?",
             "What is the rate limit and the retry contract?",
             "What do I do at 3am when it returns something I did not expect?"]),
]

def review(report: str) -> list[dict]:
    """Apply each user to a report. Returns the objections, one set per user.

    The point is not to simulate people accurately. It is to make sure every artifact
    has been attacked from five incompatible directions before it is called done, and
    to record the objections rather than silently satisfying them.
    """
    out = []
    for u in USERS:
        out.append({"user": u.id, "who": u.who, "wants": u.wants,
                    "will_not_forgive": u.will_not_forgive, "asks": u.asks})
    return out
