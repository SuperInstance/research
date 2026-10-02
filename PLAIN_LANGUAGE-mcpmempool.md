# PLAIN_LANGUAGE — MCPMempool for captains, mechanics, deckhands

You don't need to know TypeScript. You don't need to know memory pools.
You don't need to know Quilt. This is the short version.

## What this is

A **waiting room for memory operations**. A computer program asks the
mempool for memory; the mempool keeps the request in a queue, sorts it
by priority, and hands out memory when it's available.

If you've ever been to a deli counter where the person behind the
counter takes a number and serves people in order — that's a mempool.
The number is the priority. The order they call you is the scheduler.

## What you can do with it

If you're running software that needs memory and you've got many
requests happening at once:

- Each request gets a priority (some are urgent, some can wait)
- The mempool queues them
- The auto-scaler grows the queue when things get busy, shrinks when
  they calm down
- High-priority requests get handled first
- The audit trail (the witness chain) shows exactly what happened and
  when

## Small example

Imagine a chart plotter on a boat. Every position update from the GPS
is a memory operation. Most are routine. Some are urgent — "the GPS
just lost signal, log the last known position now." With a mempool:

- The urgent position log gets priority 9
- The routine updates get priority 5
- The mempool serves the urgent one first
- The audit trail shows the exact order everything was processed
- If the mempool gets overwhelmed, it auto-scales to handle the load

That sounds like plumbing you'd never touch as a mechanic. **It is
plumbing.** That's the point. It's the kind of plumbing that makes the
whole chart plotter work correctly under load.

## What you could do today

If you wanted, you could:

1. **Use it as-is.** Install Node.js, build the TypeScript, integrate
   it into your application. Standard tooling.
2. **Replace the priority policy.** Right now it's "highest priority
   first." You could change it to "oldest first" or "smallest first" or
   any other policy. The cell-graph makes this a one-line change.
3. **Make it visible.** Add the "tappable cell" UI and you can see
   every operation as it queues, runs, and completes. Useful for
   debugging.
4. **Use it for non-memory queues.** The pattern generalizes. Any
   resource that's allocated and freed can use the same mempool
   pattern: dock slots, fuel reserves, radio channels, crew shifts.

That's the whole landscape. The mempool is a general-purpose queue
with priorities.

## If you only have 60 seconds

- A queue with priorities. Things get added, things get served, the
  order is auditable.
- Used by systems that need to handle many requests fairly.
- The Quilt version makes every operation a cell you can tap and
  inspect.
- If you're an engineer and you want to know about the cell-graph,
  read `QUILT.md`. If you want the upstream story, read `UPSTREAM.md`.

## What's not here yet

This program is intentionally small. It does not:

- Have a UI for tapping cells (the data model is there; the UI is a
  separate project)
- Persist state across restarts
- Distribute across multiple machines
- Authenticate who can enqueue operations
- Have a fancy visualization

Those are all reasonable next steps. None of them are wired up. The
code is small enough that you can read the whole thing in 5 minutes.

---

Read time: ~2 minutes. Build time if you start from scratch: ~10 minutes
to install Node, build the TypeScript, and enqueue your first operation.
