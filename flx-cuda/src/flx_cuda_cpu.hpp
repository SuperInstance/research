// flx_cuda_cpu.hpp
// flx-cuda: pure CPU implementation of the priority scheduler.
// Used as a test harness when no CUDA GPU is available — same API,
// same semantics, same witness chain, just on the CPU.
//
// When CUDA is available, the kernel implementation in flx_cuda.cu
// takes over. The CPU version is the reference; the CUDA version is
// the production-grade acceleration.
//
// Author: SuperInstance
// License: MIT

#pragma once

#include <cstdint>
#include <cstring>
#include <cstdio>
#include <vector>
#include <deque>
#include <string>
#include <chrono>

// Standalone status enum (when CPU-only build doesn't include flx_cuda.cuh)
#ifndef FLX_CUDA_STATUS_DEFINED
#define FLX_CUDA_STATUS_DEFINED
enum flx_cuda_status {
    FLX_CUDA_OK = 0,
    FLX_CUDA_ERR = -1,
    FLX_CUDA_ERR_QUEUE_FULL = -2,
    FLX_CUDA_ERR_QUEUE_EMPTY = -3,
    FLX_CUDA_ERR_INVALID_PRIORITY = -4,
};
#endif

namespace flx_cuda {

// ---------------------------------------------------------------------------
// Cell types (identical to the CUDA version)
// ---------------------------------------------------------------------------

typedef int8_t flx_priority_t;

struct alignas(16) FlxOpCell {
    int32_t  id;
    int8_t   kind;
    int8_t   priority;
    int8_t   status;
    int8_t   _pad;
    int32_t  size;
    uint64_t ptr;
    uint64_t timestamp;
};

enum FlxOpStatus {
    FLX_OP_QUEUED = 0,
    FLX_OP_RUNNING = 1,
    FLX_OP_DONE = 2,
};

// ---------------------------------------------------------------------------
// Scheduler state
// ---------------------------------------------------------------------------

struct FlxQueue {
    std::deque<FlxOpCell> slots;
    int32_t  capacity;
    int32_t  count;
    int8_t   priority;
};

struct FlxScheduler {
    std::vector<FlxQueue> queues;
    int32_t total_capacity;
    int64_t tick_count;
    int8_t  min_priority;
    int8_t  max_priority;

    // The witness chain — every operation logged.
    std::vector<std::string> witness;
};

// ---------------------------------------------------------------------------
// CPU implementation (reference / fallback)
// ---------------------------------------------------------------------------

inline flx_cuda_status flx_scheduler_init_cpu(
    FlxScheduler* sched,
    int32_t total_capacity,
    int8_t  min_priority,
    int8_t  max_priority
) {
    if (!sched || total_capacity <= 0) return FLX_CUDA_ERR;
    if (max_priority < min_priority) return FLX_CUDA_ERR_INVALID_PRIORITY;

    int32_t num_buckets = (int32_t)(max_priority - min_priority) + 1;
    if (num_buckets > 256) return FLX_CUDA_ERR;

    int32_t per_bucket = total_capacity / num_buckets;
    int32_t remainder  = total_capacity % num_buckets;

    sched->queues.clear();
    sched->queues.reserve(num_buckets);

    sched->min_priority   = min_priority;
    sched->max_priority   = max_priority;
    sched->total_capacity = total_capacity;
    sched->tick_count     = 0;
    sched->witness.clear();

    char buf[128];
    snprintf(buf, sizeof(buf), "TICK %lld BIND scheduler (cap=%d, prios=%d..%d, buckets=%d)",
             (long long)sched->tick_count, total_capacity, (int)min_priority,
             (int)max_priority, num_buckets);
    sched->witness.push_back(buf);

    for (int32_t i = 0; i < num_buckets; i++) {
        int8_t pri = (int8_t)(min_priority + i);
        int32_t cap = per_bucket + (i < remainder ? 1 : 0);
        FlxQueue q;
        q.capacity = cap;
        q.count    = 0;
        q.priority = pri;
        sched->queues.push_back(std::move(q));
    }
    return FLX_CUDA_OK;
}

inline flx_cuda_status flx_submit_cpu(FlxScheduler* sched, const FlxOpCell* op) {
    if (!sched || !op) return FLX_CUDA_ERR;
    int32_t idx = (int32_t)(op->priority - sched->min_priority);
    int32_t num_buckets = (int32_t)(sched->max_priority - sched->min_priority) + 1;
    if (idx < 0 || idx >= num_buckets) return FLX_CUDA_ERR_INVALID_PRIORITY;

    FlxQueue* q = &sched->queues[idx];
    if (q->count >= q->capacity) return FLX_CUDA_ERR_QUEUE_FULL;

    FlxOpCell copy = *op;
    copy.status = FLX_OP_QUEUED;
    if (copy.timestamp == 0) copy.timestamp = sched->tick_count;
    q->slots.push_back(copy);
    q->count++;

    char buf[128];
    snprintf(buf, sizeof(buf), "TICK %lld EFFECT submit op_id=%d priority=%d size=%d",
             (long long)sched->tick_count, copy.id, copy.priority, copy.size);
    sched->witness.push_back(buf);
    return FLX_CUDA_OK;
}

inline flx_cuda_status flx_dispatch_cpu(FlxScheduler* sched, FlxOpCell* out) {
    if (!sched || !out) return FLX_CUDA_ERR;
    int32_t num_buckets = (int32_t)(sched->max_priority - sched->min_priority) + 1;

    for (int32_t b = num_buckets - 1; b >= 0; b--) {
        FlxQueue* q = &sched->queues[b];
        if (q->count > 0) {
            *out = q->slots.front();
            q->slots.pop_front();
            q->count--;
            out->status = FLX_OP_RUNNING;
            char buf[128];
            snprintf(buf, sizeof(buf), "TICK %lld EFFECT dispatch op_id=%d priority=%d",
                     (long long)sched->tick_count, out->id, out->priority);
            sched->witness.push_back(buf);
            sched->tick_count++;
            return FLX_CUDA_OK;
        }
    }
    return FLX_CUDA_ERR_QUEUE_EMPTY;
}

inline flx_cuda_status flx_complete_cpu(FlxScheduler* sched, int32_t op_id) {
    if (!sched) return FLX_CUDA_ERR;
    // In CPU implementation we already removed the op on dispatch.
    // Mark it done in the witness chain.
    char buf[128];
    snprintf(buf, sizeof(buf), "TICK %lld EFFECT complete op_id=%d",
             (long long)sched->tick_count, op_id);
    sched->witness.push_back(buf);
    return FLX_CUDA_OK;
}

inline flx_cuda_status flx_drain_cpu(FlxScheduler* sched, int8_t priority) {
    if (!sched) return FLX_CUDA_ERR;
    int32_t idx = (int32_t)(priority - sched->min_priority);
    int32_t num_buckets = (int32_t)(sched->max_priority - sched->min_priority) + 1;
    if (idx < 0 || idx >= num_buckets) return FLX_CUDA_ERR_INVALID_PRIORITY;

    FlxQueue* q = &sched->queues[idx];
    int32_t removed = q->count;
    q->slots.clear();
    q->count = 0;

    char buf[128];
    snprintf(buf, sizeof(buf), "TICK %lld FORGET drain priority=%d removed=%d",
             (long long)sched->tick_count, (int)priority, removed);
    sched->witness.push_back(buf);
    return FLX_CUDA_OK;
}

inline flx_cuda_status flx_queue_counts_cpu(const FlxScheduler* sched, int32_t* counts_out) {
    if (!sched || !counts_out) return FLX_CUDA_ERR;
    int32_t num_buckets = (int32_t)(sched->max_priority - sched->min_priority) + 1;
    int32_t total_ops = 0;
    for (int32_t i = 0; i < num_buckets; i++) {
        counts_out[i] = sched->queues[i].count;
        total_ops += sched->queues[i].count;
    }
    const_cast<FlxScheduler*>(sched)->witness.push_back(
        "TICK " + std::to_string(sched->tick_count) +
        " VIEW queue_counts total=" + std::to_string(total_ops) +
        " buckets=" + std::to_string(num_buckets));
    return FLX_CUDA_OK;
}

inline void flx_tick_cpu(FlxScheduler* sched, int64_t dt) {
    if (!sched) return;
    sched->tick_count += dt;
    char buf[64];
    snprintf(buf, sizeof(buf), "TICK %lld advance dt=%lld",
             (long long)sched->tick_count, (long long)dt);
    sched->witness.push_back(buf);
}

inline flx_cuda_status flx_scheduler_free_cpu(FlxScheduler* sched) {
    if (!sched) return FLX_CUDA_ERR;
    sched->queues.clear();
    sched->tick_count = 0;
    sched->witness.clear();
    return FLX_CUDA_OK;
}

// ---------------------------------------------------------------------------
// Timing helpers
// ---------------------------------------------------------------------------

inline double flx_now_ms() {
    using namespace std::chrono;
    return duration<double, std::milli>(high_resolution_clock::now().time_since_epoch()).count();
}

}  // namespace flx_cuda
