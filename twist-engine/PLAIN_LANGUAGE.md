# twist-engine — in plain language

What the four modes actually do, without the physics jargon.

---

## TWIST — the magic of two grates at the wrong angle

You have a window screen. You put another window screen behind it. Most
of the time the patterns blur together. But twist one of them by exactly
**1.05°** and suddenly a new pattern appears — a giant star shape that
neither screen had on its own.

This is **moiré interference**. It's real physics: twist two identical
crystal lattices and at certain angles superconductivity emerges. (MIT,
2018. Big deal.)

The TWIST mode lets you do this with two hex grids. Drag the slider and
watch the resonance curve (top right) — it's the live measurement of
how much the two grids align. Most angles are flat (boring blur). At
**magic windows** the curve peaks and a giant supercell appears.

The math: λ = s / (2 sin(θ/2)) — at small angles the supercell gets
huge, which is why bilayer graphene works.

**What it feels like to play with**: turn the knob slowly. Most of it is
mush. Then suddenly, *click* — the pattern snaps into focus. That's the
canon's core idea: emergence is rare, and you measure it instead of
asserting it.

---

## FLOCK — same birds, four words

Take 200 birds with the same body and the same three rules (stay near
your neighbors, match their heading, don't crowd them). They make
shapes. The shapes depend on **which word** you used to describe the
group:

- **MURMURATION** (starlings at dusk): high alignment, low cohesion,
  strong separation → loose, swirling, no leader.
- **PACK** (wolves): pursuit. There's a *thing* to chase (orange dot in
  the demo). The pack forms around it.
- **KENNEL** (penned dogs): weak alignment, weak cohesion, low speed.
  The circle is the fence.
- **PARLIAMENT** (owls): ring formation. They orbit a center. The owl
  that has watched the longest speaks last — but the demo doesn't
  enforce that; it just shows the geometry.

Same birds. Same rules. Different word. Different world.

The chart on the right is **polarization** — |mean heading|. When the
birds are all pointing the same way it climbs. When they swirl, it
falls. The *word* is what changes polarization, not the physics.

**What it feels like to play with**: cycle through the four nouns. The
birds don't change; the group does. This is the operational-fiction
thesis: a word is a parameter.

---

## CHIRP — listen in time for what you can't see in space

You have 12 speakers in a row along the bottom of the screen. They all
play the same tone. Normally you'd just get louder in the middle.

But if you delay each speaker by a tiny bit more than the last (the
"twist per element"), the waves line up in some directions and cancel
in others. The result: a **beam** that points wherever you twist.

This is how real sonar and radar work. The antenna never moves. Only the
clock does. (A phased-array radar is exactly this — a row of emitters
with a phase ramp.)

The fish in the demo are detected *only through the interference field*.
Range from ping strength. Bearing from where the field is loudest.
Closure rate from two pings in a row.

**What it feels like to play with**: hit AUTO-SWEEP. The beam rotates.
When it sweeps past a fish, the contact panel on the right logs a hit.
Range + bearing + closing/opening rate, just like a real warship.

---

## QUILT — the holes are real

A 24×24 grid of cells. Each cell has a phase (a clock hand). Each clock
runs slightly faster than its neighbor's — the **tempo twist** is the
offset (δ parameter). When a cell's clock hand completes a full turn,
it *snaps*. Briefly.

Two cells that snap near each other in time are **neighbors**. The
demo draws a graph: vertices = recently-snapped cells, edges = nearby
snaps. Then it counts the holes:

> **b1 = E − V + C**

That's the first Betti number — the number of independent loops in the
fabric. **V** is vertices. **E** is edges. **C** is connected
components. b1 is the difference; it's the circuit rank.

Push δ higher → cells snap faster → more edges → more holes.
STEP BACK zooms out so you can see the fabric.

**What it feels like to play with**: at δ = 0, every cell snaps roughly
together; b1 is small (the graph is mostly one component). Push δ to
0.3+ and the cells desync — b1 climbs toward 8 or 10. The fabric
becomes *topologically interesting*. The cells are dumb. The holes are
real.

This is the **Quilt canon's substrate in physics form**. In the canon,
the cells are witnesses, the tempo twist is the merkle-chain tick rate,
and b1 is the topology of the citation graph. Same math, different
language.

---

## Why these four together

Each mode is the same theorem wearing different clothes:

- **TWIST** says: layers in space + rotation = new geometry
- **FLOCK** says: agents + a rule book = a group
- **CHIRP** says: emitters + a clock twist = a beam
- **QUILT** says: oscillators + tempo offset = topology

The shared principle: **interference is the cheapest computation there
is, and a deliberate offset is the cheapest program.** No new atoms —
just a new angle. The property emerges.

---

## What you can do with it

1. **Educate yourself** — open it, cycle through the modes, watch the
   charts. Five minutes per mode.
2. **Compare with the canon** — QUILT mode is the physics-form of the
   Quilt canon. See `QUILT_NOTES.md` for the mapping.
3. **Use it as a teaching tool** — show someone what moiré / flocking /
   beamforming / topology looks like *running*, not asserted.
4. **Read the source** — `app.js` is 30 KB of plain JS. Read the whole
   thing in one sitting.
