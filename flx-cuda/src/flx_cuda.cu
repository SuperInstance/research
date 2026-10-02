// flx_cuda.cu
// flx-cuda: GPU-accelerated priority scheduler — kernel implementations
// Author: SuperInstance
// License: MIT
//
// The scheduler pattern: 256 priority buckets (one per priority byte),
// each a ring buffer on GPU. Submit enqueues an op at its priority.
// Dispatch dequeues the highest-priority op across all buckets.
// Complete marks an op done. Drain empties a bucket. Tick advances clock.
//
// Kernels run as: one block per priority bucket, 32 threads per block
// (matches the warp size that cudaclaw uses for witness union).

#include "flx_cuda.cuh"
#include <stdio.h>
#include <string.h>

namespace flx_cuda {

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

static inline int32_t queue_idx(int8_t priority, int8_t min_p) {
    return (int32_t)(priority - min_p);
}

static inline int32_t ring_next(int32_t i, int32_t cap) {
    return (i + 1) % cap;
}

// ---------------------------------------------------------------------------
// Public API implementations
// ---------------------------------------------------------------------------

flx_cuda_status flx_scheduler_init(
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

    sched->min_priority   = min_priority;
    sched->max_priority   = max_priority;
    sched->total_capacity = total_capacity;
    sched->total_ops      = 0;
    sched->tick_count     = 0;

    for (int32_t i = 0; i < num_buckets; i++) {
        int8_t pri = (int8_t)(min_priority + i);
        int32_t cap = per_bucket + (i < remainder ? 1 : 0);
        FlxQueue* q = &sched->queues[i];

        FLX_CUDA_CHECK(cudaMalloc((void**)&q->slots, sizeof(FlxOpCell) * cap));
        FLX_CUDA_CHECK(cudaMemset(q->slots, 0, sizeof(FlxOpCell) * cap));

        q->capacity = cap;
        q->head     = 0;
        q->tail     = 0;
        q->count    = 0;
        q->priority = pri;
    }
    return FLX_CUDA_OK;
}

flx_cuda_status flx_scheduler_free(FlxScheduler* sched) {
    if (!sched) return FLX_CUDA_ERR;
    int32_t num_buckets = (int32_t)(sched->max_priority - sched->min_priority) + 1;
    for (int32_t i = 0; i < num_buckets; i++) {
        FlxQueue* q = &sched->queues[i];
        if (q->slots) {
            cudaFree(q->slots);
            q->slots = nullptr;
        }
        q->capacity = 0;
        q->count = 0;
    }
    return FLX_CUDA_OK;
}

// Submit kernel: one thread per queue slot. We use 32 threads (one warp)
// per queue. The host calls this with a grid sized to num_buckets.
__global__ void submit_kernel(
    FlxQueue* queues,
    int32_t num_buckets,
    int8_t  min_priority,
    const FlxOpCell* op_in
) {
    int32_t b = blockIdx.x;
    if (b >= num_buckets) return;

    FlxQueue* q = &queues[b];
    int8_t   target_prio = (int8_t)(min_priority + b);

    if (op_in->priority != target_prio) return;  // this block handles its own priority only
    if (q->count >= q->capacity) return;            // queue full

    // One warp submits atomically
    int32_t slot = q->tail;
    q->slots[slot] = *op_in;
    q->tail = (q->tail + 1) % q->capacity;
    atomicAdd(&q->count, 1);
}

// Dispatch kernel: each block scans its bucket for the highest priority
// op. Block 0 (which corresponds to max_priority) wins if non-empty.
__global__ void dispatch_kernel(
    FlxQueue* queues,
    int32_t num_buckets,
    int8_t  min_priority,
    int8_t  max_priority,
    FlxOpCell* out_op,
    int32_t*  out_flag,    // 0 = none found, 1 = found
    int64_t*  tick_count
) {
    // We launch 1 block; threads cooperatively scan from highest to lowest.
    if (blockIdx.x != 0 || threadIdx.x != 0) return;

    *out_flag = 0;
    for (int32_t b = num_buckets - 1; b >= 0; b--) {
        FlxQueue* q = &queues[b];
        if (q->count > 0) {
            int32_t slot = q->head;
            *out_op = q->slots[slot];
            q->head = (q->head + 1) % q->capacity;
            atomicSub(&q->count, 1);
            // Mark running
            q->slots[slot].status = FLX_OP_RUNNING;
            *out_flag = 1;
            (*tick_count)++;
            return;
        }
    }
}

flx_cuda_status flx_submit(FlxScheduler* sched, const FlxOpCell* op) {
    if (!sched || !op) return FLX_CUDA_ERR;
    int32_t num_buckets = (int32_t)(sched->max_priority - sched->min_priority) + 1;

    FlxOpCell* d_op;
    FLX_CUDA_CHECK(cudaMalloc((void**)&d_op, sizeof(FlxOpCell)));
    FLX_CUDA_CHECK(cudaMemcpy(d_op, op, sizeof(FlxOpCell), cudaMemcpyHostToDevice));

    submit_kernel<<<num_buckets, 32>>>(
        sched->queues, num_buckets, sched->min_priority, d_op);

    cudaFree(d_op);

    sched->total_ops++;
    return FLX_CUDA_OK;
}

flx_cuda_status flx_dispatch(FlxScheduler* sched, FlxOpCell* out_op) {
    if (!sched || !out_op) return FLX_CUDA_ERR;
    int32_t num_buckets = (int32_t)(sched->max_priority - sched->min_priority) + 1;

    FlxOpCell* d_out;
    int32_t*   d_flag;
    int64_t*   d_tick;
    FLX_CUDA_CHECK(cudaMalloc((void**)&d_out, sizeof(FlxOpCell)));
    FLX_CUDA_CHECK(cudaMalloc((void**)&d_flag, sizeof(int32_t)));
    FLX_CUDA_CHECK(cudaMalloc((void**)&d_tick, sizeof(int64_t)));
    FLX_CUDA_CHECK(cudaMemset(d_flag, 0, sizeof(int32_t)));

    dispatch_kernel<<<1, 1>>>(
        sched->queues, num_buckets, sched->min_priority, sched->max_priority,
        d_out, d_flag, d_tick);

    int32_t flag;
    FLX_CUDA_CHECK(cudaMemcpy(&flag, d_flag, sizeof(int32_t), cudaMemcpyDeviceToHost));
    if (flag == 0) {
        cudaFree(d_out);
        cudaFree(d_flag);
        cudaFree(d_tick);
        return FLX_CUDA_ERR_QUEUE_EMPTY;
    }
    FLX_CUDA_CHECK(cudaMemcpy(out_op, d_out, sizeof(FlxOpCell), cudaMemcpyDeviceToHost));

    cudaFree(d_out);
    cudaFree(d_flag);
    cudaFree(d_tick);

    sched->total_ops--;
    return FLX_CUDA_OK;
}

// Complete: linear scan across queues for matching op_id. Mark done.
__global__ void complete_kernel(
    FlxQueue* queues,
    int32_t num_buckets,
    int32_t op_id
) {
    if (blockIdx.x != 0 || threadIdx.x != 0) return;
    for (int32_t b = 0; b < num_buckets; b++) {
        FlxQueue* q = &queues[b];
        for (int32_t i = 0; i < q->capacity; i++) {
            if (q->slots[i].id == op_id && q->slots[i].status == FLX_OP_RUNNING) {
                q->slots[i].status = FLX_OP_DONE;
                return;
            }
        }
    }
}

flx_cuda_status flx_complete(FlxScheduler* sched, int32_t op_id) {
    if (!sched) return FLX_CUDA_ERR;
    int32_t num_buckets = (int32_t)(sched->max_priority - sched->min_priority) + 1;
    complete_kernel<<<1, 1>>>(sched->queues, num_buckets, op_id);
    return FLX_CUDA_OK;
}

flx_cuda_status flx_drain(FlxScheduler* sched, int8_t priority) {
    if (!sched) return FLX_CUDA_ERR;
    int32_t idx = queue_idx(priority, sched->min_priority);
    int32_t num_buckets = (int32_t)(sched->max_priority - sched->min_priority) + 1;
    if (idx < 0 || idx >= num_buckets) return FLX_CUDA_ERR_INVALID_PRIORITY;

    FlxQueue* q = &sched->queues[idx];
    sched->total_ops -= q->count;
    FLX_CUDA_CHECK(cudaMemset(q->slots, 0, sizeof(FlxOpCell) * q->capacity));
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    return FLX_CUDA_OK;
}

__global__ void queue_counts_kernel(
    const FlxQueue* queues,
    int32_t num_buckets,
    int32_t* counts_out
) {
    int32_t b = blockIdx.x * blockDim.x + threadIdx.x;
    if (b >= num_buckets) return;
    counts_out[b] = queues[b].count;
}

flx_cuda_status flx_queue_counts(const FlxScheduler* sched, int32_t* counts_out) {
    if (!sched || !counts_out) return FLX_CUDA_ERR;
    int32_t num_buckets = (int32_t)(sched->max_priority - sched->min_priority) + 1;

    int32_t* d_counts;
    FLX_CUDA_CHECK(cudaMalloc((void**)&d_counts, sizeof(int32_t) * num_buckets));

    int threads = 32;
    int blocks = (num_buckets + threads - 1) / threads;
    queue_counts_kernel<<<blocks, threads>>>(
        sched->queues, num_buckets, d_counts);

    FLX_CUDA_CHECK(cudaMemcpy(
        counts_out, d_counts, sizeof(int32_t) * num_buckets,
        cudaMemcpyDeviceToHost));
    cudaFree(d_counts);
    return FLX_CUDA_OK;
}

void flx_tick(FlxScheduler* sched, int64_t dt) {
    if (!sched) return;
    sched->tick_count += dt;
}

}  // namespace flx_cuda
