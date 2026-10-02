# PLAIN_LANGUAGE — Collaborative Drawing for captains, mechanics, deckhands

You don't need to know Java. You don't need to know TCP sockets. You
don't need to know Quilt. This is the short version.

## What this is

A drawing program you can share. You open it on your computer, your
crew opens it on theirs, and what one of you draws the others see in
real time.

If you've ever used a shared whiteboard on a video call, it's that. If
you've ever drawn on a chart and wanted the deck officer to see what
you marked without walking over, it's that.

## What you can do with it

- Open the program on your laptop
- Sign in with a name
- Draw
- See what other people are drawing in real time
- All of you share the same canvas
- That's the whole program

## Small example

You're at the chart table. The captain's at the helm. You sketch out a
proposed course on the chart — the captain sees your strokes appear on
their screen as you make them. The captain sketches a correction. You
see their strokes appear on yours. By the time you're done talking, you
both have the same chart annotations.

That sounds almost too small to be a real piece of software. **It is
small.** The cleverness is in the network plumbing — making it work
across multiple computers in real time. The drawing itself is the
smallest possible part.

## What you could do today

If you wanted, you could:

1. **Use it as-is.** Get Java and Maven installed, build it, run the
   server, run two clients, draw. Standard IT setup.
2. **Replace the network.** Right now it uses TCP sockets on the same
   network. You could swap that for a web socket, a Cloudflare Worker,
   or WebRTC for cross-internet use.
3. **Use it for marine charts.** The drawing canvas is generic. Replace
   the background image with a chart, and you've got a shared chart
   annotator.
4. **Use it for rigging checks.** Draw the rig, mark tension points,
   share with the bosun in real time.
5. **Use it for engine diagnostics.** Sketch the engine bay, mark what
   you've checked, share with the chief engineer.

That's the whole landscape. The drawing tool is a **collaborative
canvas** — what you put on it is up to you.

## If you only have 60 seconds

- A shared drawing program. Multiple people, one canvas, real time.
- You draw, the others see your strokes as you make them.
- Requires Java 25 and Maven to build. Standard Java tooling.
- The original is a Java desktop app; the Quilt version makes the
  data flow visible as a cell-graph.
- If you're an engineer and you want to know about the cell-graph,
  read `QUILT.md`. If you want the upstream story, read `UPSTREAM.md`.

## What's not here yet

This program is intentionally a **minimal proof of the multi-user
pattern**. It does not:

- Save the canvas when everyone disconnects
- Authenticate against your existing crew accounts
- Encrypt the TCP traffic
- Render charts or maps as the background
- Run on phones or tablets (it's JavaFX desktop only)

Those are all reasonable next steps. None of them are wired up. If you
need one of them, the upstream is a fine place to start — the code is
small enough that you can read the whole thing.

---

Read time: ~2 minutes. Build time if you start from scratch: ~30 minutes
to get Java + Maven installed and the first client connected.
