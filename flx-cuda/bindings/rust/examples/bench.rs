//! flx-cuda Rust benchmark suite: 1K, 10K, 100K ops.
//!
//! Run with: cargo run --example bench --release

use flx_cuda::{OpCell, Scheduler};
use std::time::Instant;

fn bench_submit(n_ops: usize, seed: u64) -> f64 {
    // Capacity must be >= n_ops × (256/avg_per_bucket). For uniform random
    // priority distribution, 8x over-provisioning is safe.
    let capacity = (n_ops as i32) * 8;
    let mut sched = Scheduler::new(capacity, -128, 127);
    sched.bind();

    let mut state = seed;
    let t0 = Instant::now();
    for i in 0..n_ops {
        // Linear congruential RNG for deterministic priorities
        state = state.wrapping_mul(1103515245).wrapping_add(12345);
        let priority = (((state >> 16) % 256) as i32 - 128) as i8;
        let op = OpCell {
            id: (i + 1) as i32,
            kind: 0,
            priority,
            status: 0,
            _pad: 0,
            size: 1024,
            ptr: 0,
            timestamp: 0,
        };
        sched.submit(op).unwrap();
    }
    let t1 = Instant::now();
    let ms = t1.duration_since(t0).as_secs_f64() * 1000.0;
    n_ops as f64 / (ms / 1000.0)
}

fn bench_round_trip(n_ops: usize, seed: u64) -> f64 {
    let mut sched = Scheduler::new((n_ops as i32) * 8, -128, 127);
    sched.bind();

    let mut state = seed;
    let t0 = Instant::now();
    for i in 0..n_ops {
        state = state.wrapping_mul(1103515245).wrapping_add(12345);
        let priority = (((state >> 16) % 256) as i32 - 128) as i8;
        let op = OpCell {
            id: (i + 1) as i32,
            kind: 0,
            priority,
            status: 0,
            _pad: 0,
            size: 1024,
            ptr: 0,
            timestamp: 0,
        };
        sched.submit(op).unwrap();
    }
    let mut dispatched = 0;
    while sched.dispatch().is_ok() {
        dispatched += 1;
    }
    let t1 = Instant::now();
    let ms = t1.duration_since(t0).as_secs_f64() * 1000.0;
    dispatched as f64 / (ms / 1000.0)
}

fn bench_dispatch_only(n_ops: usize, seed: u64) -> f64 {
    let mut sched = Scheduler::new((n_ops as i32) * 8, -128, 127);
    sched.bind();

    let mut state = seed;
    // Pre-load
    for i in 0..n_ops {
        state = state.wrapping_mul(1103515245).wrapping_add(12345);
        let priority = (((state >> 16) % 256) as i32 - 128) as i8;
        let op = OpCell {
            id: (i + 1) as i32,
            kind: 0,
            priority,
            status: 0,
            _pad: 0,
            size: 1024,
            ptr: 0,
            timestamp: 0,
        };
        sched.submit(op).unwrap();
    }

    let t0 = Instant::now();
    let mut dispatched = 0;
    while sched.dispatch().is_ok() {
        dispatched += 1;
    }
    let t1 = Instant::now();
    let ms = t1.duration_since(t0).as_secs_f64() * 1000.0;
    dispatched as f64 / (ms / 1000.0)
}

fn main() {
    let sizes = [1_000, 10_000, 100_000];

    println!("\n");
    println!("═══════════════════════════════════════════════════════════════════");
    println!("  flx-cuda Rust benchmark suite (CPU reference)");
    println!("═══════════════════════════════════════════════════════════════════\n");

    println!(
        "{:<10}  {:<20}  {:<20}  {:<20}",
        "ops", "submit (ops/sec)", "round-trip (ops/sec)", "dispatch (ops/sec)"
    );
    println!("─────────────────────────────────────────────────────────────────────");

    for &n in &sizes {
        let submit_t = bench_submit(n, 42);
        let rt_t = bench_round_trip(n, 42);
        let dispatch_t = bench_dispatch_only(n, 42);
        println!(
            "{:<10}  {:<20.0}  {:<20.0}  {:<20.0}",
            n, submit_t, rt_t, dispatch_t
        );
    }

    println!("\n");
    println!("═══════════════════════════════════════════════════════════════════");
    println!("  Notes");
    println!("═══════════════════════════════════════════════════════════════════");
    println!("  • Single-threaded CPU reference (matches C++ numbers).");
    println!("  • flx-cuda CUDA kernels run on 256 buckets in parallel:");
    println!("    expect 10-100x speedup at 10K+ ops on a CUDA GPU.");
    println!();
}
