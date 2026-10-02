# PLAIN_LANGUAGE — Robotic Arm for captains, mechanics, deckhands

You don't need to know Python. You don't need to know servos. You don't
need to know Quilt. This is the short version.

## What this is

A **robotic arm you control with a glove**. You wear the glove, you move
your hand, the arm moves the same way. If you grab something with your
hand, the arm grabs the same thing.

If you've used a remote-controlled gripper, it's like that — but you
control it with hand gestures instead of joysticks.

## What you can do with it

- Put on the glove
- Power on the arm
- Move your hand — the arm mirrors it
- Curl your fingers — the gripper closes
- Reach for something — the arm reaches for it
- Pick it up, move it, put it down — exactly what your hand does

That's the whole thing.

## Small example

You're working on a boat with engine parts that are too hot or too small
to handle directly. You put on the glove. You grab a part with your
hand — the robotic arm grabs the same part. You move your hand to the
workbench — the arm moves the part there. You release the part — the
gripper releases.

Your hands stay safe. The arm does the awkward work.

For a kid learning how robotics works: you give them the glove + arm,
you say "make the arm pick up the block," and they see their hand
gestures become arm movements in real time. **That's robotics in 30
seconds.**

For a captain who needs a tool that does the same physical task the
same way every time: you put on the glove, you show the motion once,
the arm can replay it. (That's the FK + witness chain magic.)

## What you could do today

If you wanted, you could:

1. **Use it as-is.** Build the Python project, plug in the glove and
   arm, use it for pick-and-place. Standard Python tooling.
2. **Replace the glove input.** Use a different sensor (eye tracking,
   EMG muscle signals, brain interface) — the cell-graph makes this a
   one-line change at the EFFECT layer.
3. **Make it a teaching tool.** Hand one to a student, watch them
   learn robotics by gesture. The arm is small enough to live on a desk.
4. **Use it for unsafe tasks.** Welding, chemical handling,
   biohazard — anywhere you want the operator's hands to stay out.

That's the whole landscape. The robotic arm is an **input-mirroring
platform** — what you put on the input side is up to you.

## If you only have 60 seconds

- A robotic arm controlled by a gesture glove.
- You move your hand, the arm moves the same way.
- The arm has 4 joints + a gripper.
- The Python code is small enough to read in 15 minutes.
- The Quilt version makes every joint + sensor a cell you can tap and
  inspect.
- If you're an engineer and you want to know about the cell-graph,
  read `QUILT.md`. If you want the upstream story, read `UPSTREAM.md`.
- If you want to actually port this to a microcontroller, read
  `QUILT_PORT.md`.

## What's not here yet

The project is intentionally a **college-style demonstration**. It does not:

- Have a polished production enclosure
- Run on real-time hardware (it's Python, with limited sampling rate)
- Connect to the cloud (no Wi-Fi)
- Have force feedback (the arm doesn't feel what it's gripping)
- Have a safety system (what if the arm hits a crewmate?)

Those are all reasonable next steps. None of them are wired up. The
code is small enough to read in 15 minutes and the diagrams in
`designs/` are clear about the hardware plumbing.

---

Read time: ~2 minutes. Build time if you start from scratch: ~2-4 hours
to install Python, plug in the hardware, and make the arm move with
your hand.
