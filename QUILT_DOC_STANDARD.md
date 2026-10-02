# Quilt-Elevated Repo — Documentation Standard

**Date:** 2026-09-15 · **For:** every forked/upstream project that becomes Quilt-first-class

---

## The principle

When we import a fork or upstream project and elevate it with Quilt, the
docs serve **three readers at once**:

1. **The original author** — the upstream is preserved; they see we
   respected their work.
2. **The applied engineer** — knows the domain, doesn't necessarily
   know Quilt; reads the engineering docs in plain professional English.
3. **The working person** — captains, mechanics, deckhands, ops people.
   Smart, hands-on, no patience for jargon. Reads the short version that
   tells them *what this does for them* in their own work.

Every Quilt-elevated repo ships three docs that hit all three readers:

```
docs/
├── UPSTREAM.md           # The original repo, faithfully documented
├── QUILT.md              # The Quilt projection layer (engineering English)
└── PLAIN_LANGUAGE.md     # What this does, in working-people terms
```

And the README.md is rewritten as a **landing page** that points to all three.

---

## The three documents

### 1. `UPSTREAM.md` — original repo, faithfully documented

The original repo's README and architecture, **unmodified in spirit**.
If the upstream had a great README, link to it. If the upstream README
was thin, write a faithful summary that captures what the original
project did. **Do not impose Quilt framing on the original.**

Sections:
- What the upstream is (in their words)
- What the upstream does (the original use case)
- How the upstream works (the original architecture)
- The upstream's own installation / running / testing
- Credits and license (upstream author first; Quilt layer second)
- Notes on the fork (date, what was preserved, what was added)

### 2. `QUILT.md` — the Quilt projection layer

The Quilt framing, in professional applied-engineering English. The
audience is an engineer who knows distributed systems / databases /
robotics / etc. but doesn't necessarily know Quilt.

Sections:
- What this looks like as a cell-graph (the 5+1 opcodes, the typed links)
- The Quilt substrate (which cells, which links, which witnesses)
- The polyformal port plan (if applicable)
- The integration with the broader Quilt ecosystem
- Code examples (Python — the reference port)
- The honest scope (what's a port, what's a wrapper, what's projected)

Tone: **"We took [X] and made it visible as a cell-graph. Here's how."**
Not: "We replaced [X] with Quilt." The Quilt is the projection layer,
not the runtime.

### 3. `PLAIN_LANGUAGE.md` — for captains, mechanics, deckhands

The short version. The audience is a working person who is smart but
not interested in cell theory. They want to know: **what does this do,
and why should I care?**

Sections:
- One paragraph: what this is
- One paragraph: what you can do with it
- A small example (one paragraph, no code)
- A bullet list: 3-5 things you could do today
- "If you only have 60 seconds, read this"

Tone: **"Imagine X. Now imagine you can see X working. That's this."**
Like talking to a mechanic who's about to use a new tool. Plain,
direct, no abstractions.

---

## The README.md — the landing page

The README is the **dispatcher**. It opens, names the project, and
points to the right doc for the right reader.

Sections (always in this order):
1. **The headline** — one sentence, what this is
2. **The three doors** — link to UPSTREAM.md, QUILT.md, PLAIN_LANGUAGE.md
3. **Status** — what's working, what's WIP, what's stub
4. **Quick start** — depends on the port; minimal runnable example
5. **Cell-graph summary** (one diagram, the canonical substrate)
6. **The honest log** — what we kept from upstream, what we added

---

## The rules

1. **Never lie about the upstream.** If you didn't keep something, say so.
2. **Never pretend the Quilt layer is the runtime.** The Quilt is the projection; the original code runs.
3. **Never use jargon in PLAIN_LANGUAGE.md.** "Substrate" is fine; "BIND idempotence" is not.
4. **Always show a working demo.** Even if the demo is "click a button, see a cell-graph update."
5. **Always preserve the upstream's license.** Add the Quilt layer's license alongside.
6. **Always credit the original author first.** The Quilt layer is the *elevation*, not the *replacement*.

---

## The template — copy this structure for every Quilt-elevated repo

```
README.md                   # Landing page
docs/
├── UPSTREAM.md             # Original repo, faithfully documented
├── QUILT.md                # Quilt projection layer (engineering English)
├── PLAIN_LANGUAGE.md       # For captains, mechanics, deckhands
├── ARCHITECTURE.md         # The cell-graph diagram + typed links
└── PORT_LOG.md             # What was ported, what was stubbed, what was deferred
LICENSE                     # Upstream license (preserved)
LICENSE-QUILT               # Quilt layer's license (added)
```

---

## Why this matters

Every repo in the SuperInstance fleet should:
- **Stand alone** — kill as a solo piece even if you've never heard of Quilt
- **Synergize** — connect to other repos in the ecosystem via cell-graph primitives
- **Cross-pollinate** — patterns from one repo (witness chain, EFFECT inverses) inform others

The three-document standard ensures every Quilt-elevated repo hits all three
goals. The original work is honored. The Quilt layer is documented for
engineers. The plain-language version makes it accessible to working
people who are smart but not theoretical.

---

## Apply this to: ChainForgeLegend-Quilt, collaborative-realtime-drawing-system-quilt

These two repos were just imported. The next step:
1. Fetch the full upstream README and preserve it in UPSTREAM.md
2. Write the QUILT.md (cell-graph projection layer)
3. Write the PLAIN_LANGUAGE.md (captains, mechanics, deckhands version)
4. Rewrite README.md as a landing page

Same template for the existing repos (Quilt-Robotic-Arm, quilt-Countroller)
and for any future Quilt-elevation.

**This is the standard. Use it.**
