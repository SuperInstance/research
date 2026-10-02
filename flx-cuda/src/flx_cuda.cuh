// flx_cuda.cuh
// flx-cuda: GPU-accelerated priority scheduler for cell-graph queues
// Author: SuperInstance
// License: MIT
//
// flx-cuda runs the same priority-scheduler pattern as MCPMempool on the
// GPU. The use case: thousands of pending cell-graph operations
// (mempool ops, drawing strokes, sensor reads) where the CPU scheduler
// is the bottleneck.
//
// The Quilt projection: every operation is a cell. The scheduler
// becomes a typed LINK between BIND'd queue cells. EFFECT submits
// ops (with priorities). VIEW polls state. TICK advances the
// scheduler clock. FORGET drains queues.

#pragma once

#include <cuda_runtime.h>
#include <stdint.h>

namespace flx_cuda {

// ---------------------------------------------------------------------------
// Error handling
// ---------------------------------------------------------------------------

#define FLX_CUDA_CHECK(call)                                                  \
    do {                                                                      \
        cudaError_t err = (call);                                             \
        if (err != cudaSuccess) {                                             \
            fprintf(stderr, "flx-cuda error at %s:%d: %s\n",                  \
                    __FILE__, __LINE__, cudaGetErrorString(err));             \
            return FLX_CUDA_ERR;                                             \
        }                                                                    \
    } while (0)

enum flx_cuda_status {
    FLX_CUDA_OK = 0,
    FLX_CUDA_ERR = -1,
    FLX_CUDA_ERR_QUEUE_FULL = -2,
    FLX_CUDA_ERR_QUEUE_EMPTY = -3,
    FLX_CUDA_ERR_INVALID_PRIORITY = -4,
};

// ---------------------------------------------------------------------------
// Cell types (matching MCPMempool cell schema)
// ---------------------------------------------------------------------------

// Priority is an int8_t (range -128..127). Higher = more urgent.
// MCPMempool priority 5 = routine, 9 = urgent. flx-cuda uses the same range.
typedef int8_t flx_priority_t;

// One operation cell. Maps directly to MCPMempool's cell:op_n schema:
//   {kind, size, ptr, priority, status, timestamp}
struct alignas(16) FlxOpCell {
    int32_t  id;                // unique op id
    int8_t   kind;              // 0=alloc, 1=free, 2=read, 3=write, 4=compute
    int8_t   priority;          // -128..127
    int8_t   status;            // 0=queued, 1=running, 2=done
    int8_t   _pad;
    int32_t  size;              // bytes for alloc/write; unused for free/read
    uint64_t ptr;               // address for free/write/read; unused for alloc
    uint64_t timestamp;         // enqueue tick
};

// Status enum (matching MCPMempool cell state)
enum FlxOpStatus {
    FLX_OP_QUEUED = 0,
    FLX_OP_RUNNING = 1,
    FLX_OP_DONE = 2,
};

// ---------------------------------------------------------------------------
// GPU queue (one per priority bucket)
// ---------------------------------------------------------------------------

// A priority queue cell on GPU. Sits between MCPMempool's op cells and
// the scheduler. The queue is a ring buffer of FlxOpCell slots.
struct FlxQueue {
    FlxOpCell* slots;           // device pointer to ring buffer
    int32_t   capacity;         // max ops in queue
    int32_t   head;             // next slot to read (host-visible via cudaMemcpy)
    int32_t   tail;             // next slot to write
    int32_t   count;            // current op count
    int8_t    priority;         // this queue's priority level
    int8_t    _pad[3];
};

// One scheduler substrate = one queue per priority bucket.
// For 256 priorities (-128..127), that's 256 queues.
struct FlxScheduler {
    FlxQueue  queues[256];      // device-pointer queues, indexed by priority+128
    int32_t   total_capacity;   // sum of all queue capacities
    int32_t   total_ops;        // sum of all queue counts
    int64_t   tick_count;       // scheduler clock
    int8_t    min_priority;     // typically -128
    int8_t    max_priority;     // typically 127
    int8_t    _pad[6];
};

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

// Initialize a scheduler on the GPU. Each priority bucket gets its
// share of total_capacity. Returns FLX_CUDA_OK or FLX_CUDA_ERR.
flx_cuda_status flx_scheduler_init(
    FlxScheduler* sched,
    int32_t total_capacity,
    int8_t  min_priority,
    int8_t  max_priority
);

// Free all device memory. Safe to call multiple times.
flx_cuda_status flx_scheduler_free(FlxScheduler* sched);

// Submit an op (BIND + EFFECT in Quilt terms). The op is enqueued
// at its priority bucket on the GPU.
flx_cuda_status flx_submit(
    FlxScheduler* sched,
    const FlxOpCell* op   // host-side; copied to device
);

// Dispatch the highest-priority op (TICK in Quilt terms). Returns
// the op via the out parameter and marks it running. Returns
// FLX_CUDA_ERR_QUEUE_EMPTY if no ops are queued.
flx_cuda_status flx_dispatch(
    FlxScheduler* sched,
    FlxOpCell* out_op      // host-side result
);

// Mark an op as done (EFFECT-side update).
flx_cuda_status flx_complete(
    FlxScheduler* sched,
    int32_t op_id
);

// Drain a queue (FORGET in Quilt terms). Removes all ops with
// the given priority bucket.
flx_cuda_status flx_drain(
    FlxScheduler* sched,
    int8_t priority
);

// Poll state (VIEW in Quilt terms). Returns counts per priority bucket.
flx_cuda_status flx_queue_counts(
    const FlxScheduler* sched,
    int32_t* counts_out    // 256-element array
);

// Advance the scheduler clock by dt (TICK).
void flx_tick(FlxScheduler* sched, int64_t dt);

}  // namespace flx_cuda
