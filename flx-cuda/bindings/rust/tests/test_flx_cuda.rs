//! flx-cuda Rust test suite — same invariants as C++/Python test suites.
//!
//! Run with: cargo test
//!
//! Author: SuperInstance
//! License: MIT

use flx_cuda::{Error, OpCell, OpStatus, QuiltView, Scheduler};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn make_op(id: i32, kind: i8, priority: i8, size: i32, ptr: u64) -> OpCell {
    OpCell {
        id,
        kind,
        priority,
        status: OpStatus::Queued as i8,
        _pad: 0,
        size,
        ptr,
        timestamp: 0,
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[test]
fn test_init_and_bind() {
    let mut sched = Scheduler::new(1024, -128, 127);
    sched.bind();
    assert_eq!(sched.tick_count(), 0);
    assert_eq!(sched.total_ops(), 0);
    assert!(!sched.witness().is_empty(), "BIND event should be recorded");
    assert!(sched.witness()[0].contains("BIND"));
}

#[test]
fn test_submit_and_dispatch_priority_order() {
    let mut sched = Scheduler::new(1024, 0, 9);
    sched.bind();

    // Submit at priorities 5, 9, 3
    sched.submit(make_op(1, 0, 5, 4096, 0)).unwrap();
    sched.submit(make_op(2, 1, 9, 0, 0x1000)).unwrap();
    sched.submit(make_op(3, 2, 3, 0, 0x2000)).unwrap();

    // Dispatch should yield priority 9 first
    let op = sched.dispatch().unwrap();
    assert_eq!(op.id, 2);
    assert_eq!(op.priority, 9);
    sched.complete(op.id).unwrap();

    let op = sched.dispatch().unwrap();
    assert_eq!(op.id, 1);
    assert_eq!(op.priority, 5);
    sched.complete(op.id).unwrap();

    let op = sched.dispatch().unwrap();
    assert_eq!(op.id, 3);
    assert_eq!(op.priority, 3);
    sched.complete(op.id).unwrap();

    // Queue empty
    assert_eq!(sched.dispatch().unwrap_err(), Error::QueueEmpty);
}

#[test]
fn test_drain() {
    // Capacity must be enough: 256 buckets × 5 ops/bucket = 1280 minimum.
    let mut sched = Scheduler::new(2048, -128, 127);
    sched.bind();

    for i in 0..5 {
        sched.submit(make_op(100 + i, 0, 5, 1024 * (i + 1), 0)).unwrap();
    }
    let counts = sched.view_counts();
    assert_eq!(counts[133], 5);  // priority 5 → bucket 133

    let removed = sched.drain(5).unwrap();
    assert_eq!(removed, 5);

    let counts = sched.view_counts();
    assert_eq!(counts[133], 0);
}

#[test]
fn test_priority_out_of_range() {
    let mut sched = Scheduler::new(1024, 0, 9);
    sched.bind();
    let r = sched.submit(make_op(1, 0, 100, 1024, 0));
    assert_eq!(r.unwrap_err(), Error::InvalidPriority);
}

#[test]
fn test_quilt_projection_invariants() {
    // The 5+1 Quilt opcodes applied via the QuiltView
    let mut sched = Scheduler::new(1024, 0, 9);
    let mut view = QuiltView::new(&mut sched);

    view.bind();
    view.effect_submit(make_op(1, 0, 5, 8192, 0)).unwrap();
    view.effect_submit(make_op(2, 1, 7, 0, 0x3000)).unwrap();

    let counts = view.view_counts();
    assert_eq!(counts[5], 1);
    assert_eq!(counts[7], 1);

    view.tick(1);
    assert_eq!(view.scheduler.tick_count(), 1);

    let op = view.effect_dispatch().unwrap();
    assert_eq!(op.priority, 7);

    view.effect_complete(op.id).unwrap();

    let op = view.effect_dispatch().unwrap();
    assert_eq!(op.priority, 5);

    view.forget(5).unwrap();

    // Witness chain should be non-empty and contain key events
    let witness = view.witness();
    let has_bind = witness.iter().any(|w| w.contains("BIND"));
    let has_submit = witness.iter().any(|w| w.contains("submit"));
    let has_dispatch = witness.iter().any(|w| w.contains("dispatch"));
    let has_complete = witness.iter().any(|w| w.contains("complete"));
    let has_drain = witness.iter().any(|w| w.contains("FORGET"));

    assert!(has_bind, "BIND event missing");
    assert!(has_submit, "submit event missing");
    assert!(has_dispatch, "dispatch event missing");
    assert!(has_complete, "complete event missing");
    assert!(has_drain, "FORGET event missing");
}

#[test]
fn test_priority_ordering_under_load() {
    // Submit 100 ops at random priorities; dispatch yields them
    // in priority-descending order.
    let mut sched = Scheduler::new(1024, -128, 127);
    sched.bind();

    for i in 0..100 {
        // Deterministic priority sequence in range [-100, 100] (no overflow)
        let priority = (((i * 37) % 200) - 100) as i8;
        sched.submit(make_op(i + 1, 0, priority, 1024, 0)).unwrap();
    }

    let mut prev = i8::MAX;
    let mut count = 0;
    while let Ok(op) = sched.dispatch() {
        assert!(op.priority <= prev, "priority must be non-increasing");
        prev = op.priority;
        count += 1;
        sched.complete(op.id).unwrap();
    }
    assert_eq!(count, 100);
}

#[test]
fn test_auto_id_assignment() {
    let mut sched = Scheduler::new(1024, 0, 9);
    sched.bind();
    sched.submit(make_op(0, 0, 5, 1024, 0)).unwrap();
    sched.submit(make_op(0, 0, 5, 1024, 0)).unwrap();
    let op = sched.dispatch().unwrap();
    assert_eq!(op.id, 1);
    let op = sched.dispatch().unwrap();
    assert_eq!(op.id, 2);
}
