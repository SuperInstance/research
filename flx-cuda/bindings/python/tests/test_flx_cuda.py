"""test_flx_cuda.py — Python port test suite for flx-cuda CPU fallback.

Runs without CUDA. Tests the same invariants as the C++ test suite.

Run with: python3 test_flx_cuda.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flx_cuda import OpCell, PriorityScheduler, QuiltSchedulerView


def test_submit_and_dispatch():
    """Submit 3 ops at different priorities; dispatch should return highest first."""
    sched = PriorityScheduler(use_cuda=False)
    sched.submit(OpCell(kind=0, priority=5, size=4096))
    sched.submit(OpCell(kind=1, priority=9, ptr=0x1000))
    sched.submit(OpCell(kind=2, priority=3, ptr=0x2000))

    op = sched.dispatch()
    assert op is not None, "expected first dispatch to succeed"
    assert op.priority == 9, f"expected priority 9, got {op.priority}"
    sched.complete(op.id)

    op = sched.dispatch()
    assert op.priority == 5, f"expected priority 5, got {op.priority}"
    sched.complete(op.id)

    op = sched.dispatch()
    assert op.priority == 3, f"expected priority 3, got {op.priority}"
    sched.complete(op.id)

    op = sched.dispatch()
    assert op is None, "expected empty queue"

    print("test_submit_and_dispatch: ok")


def test_drain():
    """Drain should empty a bucket."""
    sched = PriorityScheduler(use_cuda=False)
    for i in range(5):
        sched.submit(OpCell(kind=0, priority=5, size=1024 * (i + 1)))

    counts = sched.queue_counts()
    assert counts[5 - sched.min_priority] == 5

    removed = sched.drain(5)
    assert removed == 5, f"expected 5 removed, got {removed}"

    counts = sched.queue_counts()
    assert counts[5 - sched.min_priority] == 0

    print("test_drain: ok")


def test_quilt_projection():
    """The 5+1 Quilt opcodes applied to the scheduler."""
    sched = PriorityScheduler(use_cuda=False)
    view = QuiltSchedulerView(sched)

    # BIND
    view.bind()

    # EFFECT submit
    view.effect_submit(OpCell(kind=0, priority=5, size=8192))
    view.effect_submit(OpCell(kind=1, priority=7, ptr=0x3000))

    # VIEW
    counts = view.view_counts()
    assert counts[5 - sched.min_priority] == 1
    assert counts[7 - sched.min_priority] == 1

    # TICK
    view.tick(dt=1)
    assert sched.tick_count == 1

    # EFFECT dispatch (highest first)
    op = view.effect_dispatch()
    assert op.priority == 7, f"expected priority 7, got {op.priority}"

    # EFFECT complete
    view.effect_complete(op.id)

    # Next dispatch
    op = view.effect_dispatch()
    assert op.priority == 5

    # FORGET
    view.forget(priority=5)

    # Witness chain
    assert len(view.witness) >= 7, f"expected ≥7 witness events, got {len(view.witness)}"

    print("test_quilt_projection: ok")


def test_priority_out_of_range():
    """Submitting with priority out of [min, max] should still work (bucket lookup)."""
    sched = PriorityScheduler(use_cuda=False, min_priority=0, max_priority=9)
    sched.submit(OpCell(kind=0, priority=3, size=4096))
    op = sched.dispatch()
    assert op.priority == 3
    print("test_priority_out_of_range: ok")


def main():
    failed = 0
    for test in [test_submit_and_dispatch, test_drain, test_quilt_projection, test_priority_out_of_range]:
        try:
            test()
        except AssertionError as e:
            print(f"FAIL {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {test.__name__}: {e}")
            failed += 1

    if failed == 0:
        print(f"\nAll {len([test_submit_and_dispatch, test_drain, test_quilt_projection, test_priority_out_of_range])} flx-cuda Python tests passed.")
        return 0
    print(f"\n{failed} test(s) failed.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
