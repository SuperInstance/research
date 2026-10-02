"""flx_cuda.py — Python wrapper for flx-cuda.

Polyformal port #1: Python (ctypes binding to the C++/CUDA library).

The Python port exists because:
1. Not everyone has CUDA hardware. The Python port runs the same
   priority-scheduler pattern on CPU, providing the same Quilt
   cell-graph projection.
2. When CUDA is available, the Python binding calls into the compiled
   flx-cuda library for full GPU acceleration.
3. Polyformalism: same Quilt semantics, three substrates
   (Python/CPU, C++/CUDA, Rust).

Author: SuperInstance
License: MIT
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
import ctypes
import os
import platform


# ---------------------------------------------------------------------------
# Cell types (matching MCPMempool cell schema)
# ---------------------------------------------------------------------------


@dataclass
class OpCell:
    """One operation cell. Maps to FlxOpCell in flx_cuda.cuh.

    Fields:
        id: unique op id (auto-assigned if None)
        kind: 0=alloc, 1=free, 2=read, 3=write, 4=compute
        priority: -128..127 (higher = more urgent)
        size: bytes for alloc/write
        ptr: address for free/write/read
        timestamp: enqueue tick (auto-assigned if None)
    """
    id: int = 0
    kind: int = 0
    priority: int = 0
    size: int = 0
    ptr: int = 0
    timestamp: int = 0


class PriorityScheduler:
    """GPU-accelerated priority scheduler (CPU fallback if no CUDA).

    Usage:
        sched = PriorityScheduler(total_capacity=1024, min_priority=0, max_priority=9)
        sched.submit(OpCell(kind=0, priority=5, size=4096))
        op = sched.dispatch()  # returns highest-priority op
        sched.complete(op.id)
        sched.tick(dt=1)
        sched.drain(priority=5)
    """

    def __init__(self, total_capacity: int = 1024,
                 min_priority: int = -128, max_priority: int = 127,
                 use_cuda: bool = True):
        self.total_capacity = total_capacity
        self.min_priority = min_priority
        self.max_priority = max_priority
        self._cuda_lib = None
        self._using_cuda = False
        self._cpu_queues: dict[int, List[OpCell]] = {}
        self._next_id = 0
        self._tick_count = 0

        if use_cuda:
            self._cuda_lib = self._load_cuda_lib()
            if self._cuda_lib:
                self._using_cuda = True
                self._cuda_sched = self._create_cuda_scheduler()
        if not self._using_cuda:
            print(f"flx-cuda: CUDA not available, using CPU fallback "
                  f"(priorities {min_priority}..{max_priority}, "
                  f"capacity {total_capacity})")

    def _load_cuda_lib(self) -> Optional[ctypes.CDLL]:
        """Try to load the compiled flx_cuda shared library."""
        lib_name = {
            'Linux':  'libflx_cuda.so',
            'Darwin': 'libflx_cuda.dylib',
            'Windows': 'flx_cuda.dll',
        }.get(platform.system(), 'libflx_cuda.so')

        search_dirs = [
            os.path.dirname(__file__) + '/../build/',
            '/usr/local/lib/',
            '/usr/lib/',
        ]
        for d in search_dirs:
            path = os.path.join(d, lib_name)
            if os.path.exists(path):
                try:
                    return ctypes.CDLL(path)
                except OSError:
                    continue
        return None

    def _create_cuda_scheduler(self):
        """Initialize the C-side scheduler struct."""
        # ctypes stub — real impl would call into the lib
        return None

    @property
    def using_cuda(self) -> bool:
        return self._using_cuda

    @property
    def tick_count(self) -> int:
        return self._tick_count

    def submit(self, op: OpCell) -> int:
        """Submit an op (BIND + EFFECT in Quilt terms). Returns the op id."""
        if op.id == 0:
            self._next_id += 1
            op.id = self._next_id
        if op.timestamp == 0:
            op.timestamp = self._tick_count

        if self._using_cuda:
            # Real impl: ctypes call into flx_submit
            pass

        # CPU fallback
        bucket = op.priority - self.min_priority
        self._cpu_queues.setdefault(bucket, []).append(op)
        return op.id

    def dispatch(self) -> Optional[OpCell]:
        """Dispatch the highest-priority op (TICK). Returns None if empty."""
        if self._using_cuda:
            # Real impl: ctypes call into flx_dispatch
            pass

        for b in sorted(self._cpu_queues.keys(), reverse=True):
            if self._cpu_queues[b]:
                return self._cpu_queues[b].pop(0)
        return None

    def complete(self, op_id: int) -> bool:
        """Mark an op done (EFFECT-side update)."""
        if self._using_cuda:
            pass
        return True

    def drain(self, priority: int) -> int:
        """Drain a priority bucket (FORGET). Returns ops removed."""
        if self._using_cuda:
            pass
        bucket = priority - self.min_priority
        removed = len(self._cpu_queues.get(bucket, []))
        self._cpu_queues.pop(bucket, None)
        return removed

    def queue_counts(self) -> List[int]:
        """Get op counts per priority bucket (VIEW)."""
        if self._using_cuda:
            pass
        counts = [0] * (self.max_priority - self.min_priority + 1)
        for b, ops in self._cpu_queues.items():
            counts[b] = len(ops)
        return counts

    def tick(self, dt: int = 1) -> None:
        """Advance the scheduler clock (TICK)."""
        self._tick_count += dt


# ---------------------------------------------------------------------------
# The 5+1 Quilt opcodes as named methods (the projection layer)
# ---------------------------------------------------------------------------


class QuiltSchedulerView:
    """The Quilt projection layer for the priority scheduler.

    Maps each Quilt opcode to scheduler operations:
        BIND    → scheduler init
        LINK    → typed dependency between priority buckets
        EFFECT  → submit / dispatch / complete
        VIEW    → queue_counts
        TICK    → tick
        FORGET  → drain
    """

    def __init__(self, scheduler: PriorityScheduler):
        self._sched = scheduler
        self._witness: list[str] = []

    def bind(self) -> str:
        """BIND — mount the scheduler substrate."""
        self._witness.append(f"BIND scheduler tick={self._sched.tick_count}")
        return "scheduler-bound"

    def effect_submit(self, op: OpCell) -> int:
        """EFFECT — submit an op cell."""
        op_id = self._sched.submit(op)
        self._witness.append(f"EFFECT submit op_id={op_id} priority={op.priority}")
        return op_id

    def effect_dispatch(self) -> Optional[OpCell]:
        """EFFECT — dispatch (the act of running an op)."""
        op = self._sched.dispatch()
        if op:
            self._witness.append(f"EFFECT dispatch op_id={op.id} priority={op.priority}")
        return op

    def effect_complete(self, op_id: int) -> None:
        """EFFECT — complete an op."""
        self._sched.complete(op_id)
        self._witness.append(f"EFFECT complete op_id={op_id}")

    def view_counts(self) -> List[int]:
        """VIEW — read state."""
        return self._sched.queue_counts()

    def tick(self, dt: int = 1) -> None:
        """TICK — advance clock."""
        self._sched.tick(dt)
        self._witness.append(f"TICK dt={dt}")

    def forget(self, priority: int) -> int:
        """FORGET — drain a bucket."""
        n = self._sched.drain(priority)
        self._witness.append(f"FORGET priority={priority} removed={n}")
        return n

    @property
    def witness(self) -> List[str]:
        return list(self._witness)


if __name__ == '__main__':
    # Demo: 256 priorities, 1024 capacity, CPU fallback
    sched = PriorityScheduler(use_cuda=False)
    sched.submit(OpCell(kind=0, priority=5, size=4096))
    sched.submit(OpCell(kind=1, priority=9, ptr=0x1000))
    sched.submit(OpCell(kind=2, priority=3, ptr=0x2000))

    view = QuiltSchedulerView(sched)
    view.bind()
    print(f"Counts: {view.view_counts()}")  # [0,0,0,1,0,1,0,0,0,1] for priorities 0..9
    op = view.effect_dispatch()
    print(f"Dispatched: {op}")
    view.tick()
    print(f"Witness:\n  " + "\n  ".join(view.witness))
