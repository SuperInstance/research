# PLAIN_LANGUAGE — flx-cuda for captains, mechanics, deckhands

You don't need to know CUDA. You don't need to know C++. You don't
need to know what a "ring buffer" is. This is the short version.

## What this is

A **very fast task scheduler** that runs on a graphics card (GPU).

A task scheduler is a thing that decides which task to do next. You
give it a list of tasks. Each task has a priority (urgent or routine).
The scheduler picks the most-urgent one and runs it. Then the next
most-urgent. And so on.

This particular scheduler is special because it runs on the GPU
(graphics card) instead of the CPU (main processor). Graphics cards
are good at doing many small things in parallel. So if you have lots
and lots of pending tasks (thousands per second), this scheduler can
keep up while a CPU scheduler would choke.

## Small example

You're the captain of a fishing boat. You have 1,000 net locations to
check. Some are urgent (the net has fish, you need to pull it now).
Some are routine (the net is empty, but you should check it before
you head back to port).

A CPU scheduler checks the priorities one at a time. That's fine for
100 tasks. For 1,000 tasks, it starts to slow down.

A GPU scheduler checks the priorities in parallel. 1,000 tasks is
trivial. 10,000 is still fast. 100,000 is still real-time.

## What you could do today

If you wanted, you could:

1. **Use the Python version** on any computer. It runs on the CPU
   (not the GPU), but it works the same way. Good for prototyping
   and small workloads.
2. **Compile the C++/CUDA version** if you have a CUDA-capable GPU
   (NVIDIA, Volta or newer recommended). Fast.
3. **Wrap it in your own application.** The cell-graph pattern means
   every task is observable: you can ask "what's the highest-priority
   task right now?" at any time.

## If you only have 60 seconds

- A priority-scheduling library.
- GPU-accelerated.
- Same scheduler pattern as MCPMempool, but on the GPU.
- Cell-graph projection: every task is a cell; the queue is a cell;
  the scheduler is a cell.
- If you're an engineer and you want to know about the cell-graph,
  read `QUILT.md`. If you want the design lineage, read `UPSTREAM.md`.
- The Python port is a good starting point if you want to try it
  without compiling CUDA.

## What's not here yet

- **Async submit/complete** — currently the calls are synchronous.
  Async is in the roadmap.
- **Multi-GPU** — currently runs on one GPU.
- **Persistent kernel mode** — currently launches a kernel per call.
  Persistent mode is faster but more complex; tracked as future work.
- **WebGPU port** — would let this run in a browser. Not built yet.

## What's the practical difference?

If you have 100 pending tasks per second, **don't bother**. Use the
plain CPU scheduler.

If you have 10,000 pending tasks per second, **this is when flx-cuda
starts to matter**. The GPU can chew through them in real-time; the
CPU cannot.

If you have 100,000 pending tasks per second, **this is when
flx-cuda is necessary**, not optional.

## Who built this and why

Built by SuperInstance. The SuperInstance fleet has many projects that
need to schedule many tasks: the collaborative drawing system
schedules 1,000+ strokes per second; the robotic arm schedules 50+
sensor reads per frame; the mempool schedules thousands of memory ops.
This is the unified scheduler for those workloads, running on GPU.

Read time: ~2 minutes. Build time: ~15 minutes on a CUDA-capable
machine (CMake + nvcc).
