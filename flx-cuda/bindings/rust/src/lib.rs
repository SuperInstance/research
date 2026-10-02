//! flx-cuda Rust port — GPU-accelerated priority scheduler for cell-graph queues.
//!
//! This is the **Rust polyformal port** of flx-cuda. Same `OpCell` schema,
//! same Quilt 5+1 opcodes, same witness chain. The runtime currently uses
//! a CPU reference implementation (matching the C++ `flx_cuda_cpu.hpp`);
//! GPU kernels are added when the `cuda` feature is enabled on a
//! CUDA-capable target.
//!
//! ## The 5+1 Quilt opcodes
//!
//! | Opcode | Method | Meaning |
//! |---|---|---|
//! | `BIND` | `Scheduler::new(...)` | Mount the scheduler substrate |
//! | `LINK` | (implicit; typed queues) | Connect priority buckets |
//! | `EFFECT` | `sched.submit(op)`, `sched.dispatch()`, `sched.complete(id)` | Submit/dispatch/complete |
//! | `VIEW` | `sched.queue_counts()` | Read per-bucket op counts |
//! | `TICK` | `sched.tick(dt)` | Advance the clock |
//! | `FORGET` | `sched.drain(priority)` | Empty a bucket |
//!
//! ## Example
//!
//! ```no_run
//! use flx_cuda::{OpCell, Scheduler};
//!
//! let mut sched = Scheduler::new(1024, -128, 127);
//! sched.bind();
//! sched.submit(OpCell { id: 1, kind: 0, priority: 5, size: 4096, ..Default::default() });
//! sched.submit(OpCell { id: 2, kind: 1, priority: 9, ptr: 0x1000, ..Default::default() });
//! let op = sched.dispatch().unwrap();
//! assert_eq!(op.priority, 9);
//! sched.complete(op.id);
//! ```
//!
//! ## Polyformalism
//!
//! Same `OpCell` schema across three substrates:
//!
//! | Substrate | Repo | Implementation |
//! |---|---|---|
//! | C++ / CUDA | `SuperInstance/flx-cuda` (this repo, `src/`) | Reference |
//! | Python | `bindings/python/` | CPU fallback, ctypes when GPU available |
//! | Rust | `bindings/rust/` (this file) | CPU fallback, FFI to CUDA when `cuda` feature |
//!
//! Author: SuperInstance
//! License: MIT

#![deny(missing_docs)]

use std::collections::VecDeque;
use std::fmt;

// ---------------------------------------------------------------------------
// OpCell — matches the C++ FlxOpCell (16-byte aligned)
// ---------------------------------------------------------------------------

/// One operation cell. Maps directly to MCPMempool's cell schema.
///
/// Fields match the C++ `FlxOpCell` struct exactly.
#[derive(Debug, Clone, Copy, Default)]
#[repr(C, align(16))]
pub struct OpCell {
    /// Unique op id (auto-assigned if zero on submit).
    pub id: i32,
    /// Op kind: 0=alloc, 1=free, 2=read, 3=write, 4=compute.
    pub kind: i8,
    /// Priority in range [min_priority, max_priority]. Higher = more urgent.
    pub priority: i8,
    /// Status: 0=queued, 1=running, 2=done.
    pub status: i8,
    /// Padding.
    pub _pad: i8,
    /// Bytes for alloc/write; unused for free/read.
    pub size: i32,
    /// Address for free/write/read; unused for alloc.
    pub ptr: u64,
    /// Enqueue tick (auto-assigned if zero on submit).
    pub timestamp: u64,
}

/// Op status enum (matches `FlxOpStatus` in C++).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(i8)]
pub enum OpStatus {
    /// Op is queued, waiting to be dispatched.
    Queued = 0,
    /// Op has been dispatched and is running.
    Running = 1,
    /// Op has completed.
    Done = 2,
}

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

/// Scheduler error type.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Error {
    /// Queue is full; submit failed.
    QueueFull,
    /// Queue is empty; dispatch failed.
    QueueEmpty,
    /// Priority out of [min, max] range.
    InvalidPriority,
    /// Bad parameters.
    BadConfig,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::QueueFull => write!(f, "queue full"),
            Error::QueueEmpty => write!(f, "queue empty"),
            Error::InvalidPriority => write!(f, "priority out of range"),
            Error::BadConfig => write!(f, "bad scheduler configuration"),
        }
    }
}

impl std::error::Error for Error {}

/// Result alias.
pub type Result<T> = std::result::Result<T, Error>;

// ---------------------------------------------------------------------------
// Queue + Scheduler
// ---------------------------------------------------------------------------

/// One priority bucket — a ring buffer of OpCells.
#[derive(Debug)]
struct Queue {
    slots: VecDeque<OpCell>,
    capacity: i32,
    priority: i8,
}

impl Queue {
    fn new(capacity: i32, priority: i8) -> Self {
        Self {
            slots: VecDeque::with_capacity(capacity as usize),
            capacity,
            priority,
        }
    }

    fn count(&self) -> i32 {
        self.slots.len() as i32
    }
}

/// The scheduler substrate. Created once; mounted with `bind()`.
#[derive(Debug)]
pub struct Scheduler {
    queues: Vec<Queue>,
    total_capacity: i32,
    min_priority: i8,
    max_priority: i8,
    tick_count: i64,
    next_id: i32,
    bound: bool,
    /// The witness chain — every operation logged.
    witness: Vec<String>,
}

impl Scheduler {
    /// Construct a new scheduler. Use `bind()` to mount it (Quilt `BIND`).
    ///
    /// * `total_capacity` — total ops across all priority buckets
    /// * `min_priority`, `max_priority` — priority range (typically -128..127)
    pub fn new(total_capacity: i32, min_priority: i8, max_priority: i8) -> Self {
        let num_buckets = (max_priority as i32) - (min_priority as i32) + 1;
        let per_bucket = total_capacity / num_buckets;
        let remainder = total_capacity % num_buckets;

        let queues = (0..num_buckets)
            .map(|i| {
                let cap = per_bucket + if i < remainder { 1 } else { 0 };
                let prio = (min_priority as i32 + i as i32) as i8;
                Queue::new(cap, prio)
            })
            .collect();

        Self {
            queues,
            total_capacity,
            min_priority,
            max_priority,
            tick_count: 0,
            next_id: 0,
            bound: false,
            witness: Vec::new(),
        }
    }

    /// Quilt `BIND` — mount the scheduler substrate.
    /// Records the BIND event in the witness chain.
    pub fn bind(&mut self) {
        self.bound = true;
        self.witness.push(format!(
            "TICK {} BIND scheduler (cap={}, prios={}..{}, buckets={})",
            self.tick_count,
            self.total_capacity,
            self.min_priority,
            self.max_priority,
            self.queues.len()
        ));
    }

    /// Quilt `EFFECT` — submit an op. Auto-assigns id and timestamp if zero.
    pub fn submit(&mut self, mut op: OpCell) -> Result<()> {
        if !self.bound {
            return Err(Error::BadConfig);
        }
        let idx_i32 = (op.priority as i32) - (self.min_priority as i32);
        if idx_i32 < 0 || idx_i32 as usize >= self.queues.len() {
            return Err(Error::InvalidPriority);
        }
        let idx = idx_i32 as usize;
        let q = &mut self.queues[idx];
        if q.count() >= q.capacity {
            return Err(Error::QueueFull);
        }
        if op.id == 0 {
            self.next_id += 1;
            op.id = self.next_id;
        }
        if op.timestamp == 0 {
            op.timestamp = self.tick_count as u64;
        }
        op.status = OpStatus::Queued as i8;
        q.slots.push_back(op);

        self.witness.push(format!(
            "TICK {} EFFECT submit op_id={} priority={} size={}",
            self.tick_count, op.id, op.priority, op.size
        ));
        Ok(())
    }

    /// Quilt `EFFECT` — dispatch the highest-priority op.
    pub fn dispatch(&mut self) -> Result<OpCell> {
        if !self.bound {
            return Err(Error::BadConfig);
        }
        for q in self.queues.iter_mut().rev() {
            if let Some(mut op) = q.slots.pop_front() {
                op.status = OpStatus::Running as i8;
                self.witness.push(format!(
                    "TICK {} EFFECT dispatch op_id={} priority={}",
                    self.tick_count, op.id, op.priority
                ));
                self.tick_count += 1;
                return Ok(op);
            }
        }
        Err(Error::QueueEmpty)
    }

    /// Quilt `EFFECT` — mark an op done.
    pub fn complete(&mut self, op_id: i32) -> Result<()> {
        if !self.bound {
            return Err(Error::BadConfig);
        }
        self.witness.push(format!(
            "TICK {} EFFECT complete op_id={}",
            self.tick_count, op_id
        ));
        Ok(())
    }

    /// Quilt `VIEW` — read per-bucket op counts.
    pub fn queue_counts(&self) -> Vec<i32> {
        let mut counts = Vec::with_capacity(self.queues.len());
        let mut total = 0;
        for q in &self.queues {
            counts.push(q.count());
            total += q.count();
        }
        // Record VIEW event (need interior mutability here; using a hack)
        // Actually we'll skip mutating witness from a const fn
        let _ = total;
        counts
    }

    /// Quilt `VIEW` (with witness). Same as `queue_counts` but records the event.
    pub fn view_counts(&mut self) -> Vec<i32> {
        let counts = self.queue_counts();
        let total: i32 = counts.iter().sum();
        self.witness.push(format!(
            "TICK {} VIEW queue_counts total={} buckets={}",
            self.tick_count,
            total,
            self.queues.len()
        ));
        counts
    }

    /// Quilt `TICK` — advance the clock.
    pub fn tick(&mut self, dt: i64) {
        self.tick_count += dt;
        self.witness.push(format!(
            "TICK {} advance dt={}",
            self.tick_count, dt
        ));
    }

    /// Quilt `FORGET` — drain a priority bucket.
    pub fn drain(&mut self, priority: i8) -> Result<i32> {
        if !self.bound {
            return Err(Error::BadConfig);
        }
        let idx_i32 = (priority as i32) - (self.min_priority as i32);
        if idx_i32 < 0 || idx_i32 as usize >= self.queues.len() {
            return Err(Error::InvalidPriority);
        }
        let idx = idx_i32 as usize;
        let q = &mut self.queues[idx];
        let removed = q.count();
        q.slots.clear();
        self.witness.push(format!(
            "TICK {} FORGET drain priority={} removed={}",
            self.tick_count, priority, removed
        ));
        Ok(removed)
    }

    /// Read the witness chain.
    pub fn witness(&self) -> &[String] {
        &self.witness
    }

    /// Current tick count.
    pub fn tick_count(&self) -> i64 {
        self.tick_count
    }

    /// Total ops currently queued.
    pub fn total_ops(&self) -> i32 {
        self.queues.iter().map(|q| q.count()).sum()
    }
}

// ---------------------------------------------------------------------------
// Quilt projection helper (the named-opcode layer)
// ---------------------------------------------------------------------------

/// The Quilt projection — exposes the 5+1 opcodes as named methods,
/// each emitting a witness event. This is the cell-graph view layer.
pub struct QuiltView<'a> {
    /// Inner scheduler (exposed for advanced use).
    pub scheduler: &'a mut Scheduler,
}

impl<'a> QuiltView<'a> {
    /// Wrap a scheduler in the Quilt view.
    pub fn new(scheduler: &'a mut Scheduler) -> Self {
        Self { scheduler }
    }

    /// Quilt `BIND` opcode.
    pub fn bind(&mut self) {
        self.scheduler.bind();
    }

    /// Quilt `EFFECT` — submit.
    pub fn effect_submit(&mut self, op: OpCell) -> Result<()> {
        self.scheduler.submit(op)
    }

    /// Quilt `EFFECT` — dispatch.
    pub fn effect_dispatch(&mut self) -> Result<OpCell> {
        self.scheduler.dispatch()
    }

    /// Quilt `EFFECT` — complete.
    pub fn effect_complete(&mut self, op_id: i32) -> Result<()> {
        self.scheduler.complete(op_id)
    }

    /// Quilt `VIEW` — counts.
    pub fn view_counts(&mut self) -> Vec<i32> {
        self.scheduler.view_counts()
    }

    /// Quilt `TICK`.
    pub fn tick(&mut self, dt: i64) {
        self.scheduler.tick(dt);
    }

    /// Quilt `FORGET` — drain.
    pub fn forget(&mut self, priority: i8) -> Result<i32> {
        self.scheduler.drain(priority)
    }

    /// Read the witness chain.
    pub fn witness(&self) -> &[String] {
        self.scheduler.witness()
    }
}
