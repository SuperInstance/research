//! flx-cuda Rust demo — show the 5+1 Quilt opcodes in action.
//!
//! Run with: cargo run --example demo

use flx_cuda::{OpCell, QuiltView, Scheduler};

fn main() {
    println!("════════════════════════════════════════════════════");
    println!("  flx-cuda Rust demo");
    println!("════════════════════════════════════════════════════\n");

    let mut sched = Scheduler::new(1024, -128, 127);
    let mut view = QuiltView::new(&mut sched);

    // BIND
    view.bind();

    // EFFECT — submit 3 ops at different priorities
    view.effect_submit(OpCell { id: 0, kind: 0, priority: 5, size: 4096, ..Default::default() }).unwrap();
    view.effect_submit(OpCell { id: 0, kind: 1, priority: 9, ptr: 0x1000, ..Default::default() }).unwrap();
    view.effect_submit(OpCell { id: 0, kind: 2, priority: 3, ptr: 0x2000, ..Default::default() }).unwrap();

    // VIEW
    let counts = view.view_counts();
    println!("Queue counts: ops at each priority:");
    for (i, &c) in counts.iter().enumerate() {
        if c > 0 {
            // Priority = bucket_index offset from min_priority (we used -128..127 = 256 buckets)
            let bucket_offset = i as i32 - 128;
            println!("  priority={} (bucket {}): {} ops", bucket_offset, i, c);
        }
    }

    // EFFECT — dispatch (should return priority 9 first)
    let op = view.effect_dispatch().unwrap();
    println!("\nDispatched: op_id={}, priority={}", op.id, op.priority);
    view.effect_complete(op.id).unwrap();

    // TICK
    view.tick(1);

    // EFFECT — dispatch the rest
    while let Ok(op) = view.effect_dispatch() {
        println!("Dispatched: op_id={}, priority={}", op.id, op.priority);
        view.effect_complete(op.id).unwrap();
    }

    // FORGET
    view.forget(5).unwrap();

    // Witness chain
    println!("\nWitness chain:");
    for event in view.witness() {
        println!("  {}", event);
    }

    println!("\n✓ Demo complete.");
}
