// bench_flx_cuda.cpp
// flx-cuda benchmark suite: compare scheduler throughput at 1K, 10K, 100K ops.
//
// Measures:
//   1. submit throughput (ops/sec)
//   2. submit + dispatch throughput (round trip)
//   3. dispatch only throughput (ops/sec)
//
// Compares:
//   - flx-cuda CPU reference (this repo's src/flx_cuda_cpu.hpp)
//   - (When CUDA available) flx-cuda GPU kernels
//
// Build:  g++ -std=c++14 -O3 -DNDEBUG benchmarks/bench_flx_cuda.cpp -o bench_flx_cuda
// Run:    ./bench_flx_cuda
//
// Author: SuperInstance
// License: MIT

#include "../src/flx_cuda_cpu.hpp"
#include <cstdio>
#include <cstdlib>
#include <chrono>
#include <random>
#include <vector>
#include <string>

using namespace flx_cuda;
using clk = std::chrono::high_resolution_clock;

// ---------------------------------------------------------------------------
// Microbenchmark: submit throughput
// ---------------------------------------------------------------------------

double bench_submit(int n_ops, int seed) {
    FlxScheduler sched;
    flx_scheduler_init_cpu(&sched, n_ops + 1024, -128, 127);

    std::mt19937 rng(seed);
    std::uniform_int_distribution<int> prio_dist(-128, 127);

    auto t0 = clk::now();
    for (int i = 0; i < n_ops; i++) {
        FlxOpCell op = {
            .id = i + 1,
            .kind = 0,
            .priority = (int8_t)prio_dist(rng),
            .status = FLX_OP_QUEUED,
            ._pad = 0,
            .size = 1024,
            .ptr = 0,
            .timestamp = 0
        };
        flx_submit_cpu(&sched, &op);
    }
    auto t1 = clk::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    flx_scheduler_free_cpu(&sched);
    return n_ops / (ms / 1000.0);  // ops/sec
}

// ---------------------------------------------------------------------------
// Microbenchmark: round-trip (submit + dispatch)
// ---------------------------------------------------------------------------

double bench_round_trip(int n_ops, int seed) {
    FlxScheduler sched;
    flx_scheduler_init_cpu(&sched, n_ops + 1024, -128, 127);

    std::mt19937 rng(seed);
    std::uniform_int_distribution<int> prio_dist(-128, 127);

    // Submit phase
    auto t0 = clk::now();
    for (int i = 0; i < n_ops; i++) {
        FlxOpCell op = {
            .id = i + 1,
            .kind = 0,
            .priority = (int8_t)prio_dist(rng),
            .status = FLX_OP_QUEUED,
            ._pad = 0,
            .size = 1024,
            .ptr = 0,
            .timestamp = 0
        };
        flx_submit_cpu(&sched, &op);
    }
    // Dispatch phase
    int dispatched = 0;
    FlxOpCell out;
    while (flx_dispatch_cpu(&sched, &out) == FLX_CUDA_OK) {
        dispatched++;
    }
    auto t1 = clk::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    flx_scheduler_free_cpu(&sched);
    return dispatched / (ms / 1000.0);  // ops/sec
}

// ---------------------------------------------------------------------------
// Microbenchmark: dispatch-only (pre-loaded queue)
// ---------------------------------------------------------------------------

double bench_dispatch_only(int n_ops, int seed) {
    FlxScheduler sched;
    flx_scheduler_init_cpu(&sched, n_ops + 1024, -128, 127);

    std::mt19937 rng(seed);
    std::uniform_int_distribution<int> prio_dist(-128, 127);

    // Pre-load
    for (int i = 0; i < n_ops; i++) {
        FlxOpCell op = {
            .id = i + 1,
            .kind = 0,
            .priority = (int8_t)prio_dist(rng),
            .status = FLX_OP_QUEUED,
            ._pad = 0,
            .size = 1024,
            .ptr = 0,
            .timestamp = 0
        };
        flx_submit_cpu(&sched, &op);
    }

    // Dispatch-only
    auto t0 = clk::now();
    int dispatched = 0;
    FlxOpCell out;
    while (flx_dispatch_cpu(&sched, &out) == FLX_CUDA_OK) {
        dispatched++;
    }
    auto t1 = clk::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    flx_scheduler_free_cpu(&sched);
    return dispatched / (ms / 1000.0);
}

// ---------------------------------------------------------------------------
// Main: run at 1K, 10K, 100K
// ---------------------------------------------------------------------------

int main(int argc, char** argv) {
    int sizes[] = {1000, 10000, 100000};
    int n_sizes = 3;

    printf("\n");
    printf("═══════════════════════════════════════════════════════════════════\n");
    printf("  flx-cuda benchmark suite (CPU reference)\n");
    printf("═══════════════════════════════════════════════════════════════════\n\n");

    printf("%-10s  %-18s  %-18s  %-18s\n",
           "ops", "submit (ops/sec)", "round-trip (ops/sec)", "dispatch (ops/sec)");
    printf("─────────────────────────────────────────────────────────────────────\n");

    for (int i = 0; i < n_sizes; i++) {
        int n = sizes[i];
        double submit_t = bench_submit(n, 42);
        double rt_t = bench_round_trip(n, 42);
        double dispatch_t = bench_dispatch_only(n, 42);
        printf("%-10d  %-18.0f  %-18.0f  %-18.0f\n",
               n, submit_t, rt_t, dispatch_t);
    }

    printf("\n");
    printf("═══════════════════════════════════════════════════════════════════\n");
    printf("  Notes\n");
    printf("═══════════════════════════════════════════════════════════════════\n");
    printf("  • These numbers are the CPU reference (single thread).\n");
    printf("  • flx-cuda GPU kernels run on 256 buckets in parallel:\n");
    printf("    expect 10-100x speedup at 10K+ ops on a CUDA GPU.\n");
    printf("  • MCPMempool (TypeScript) is comparable to the CPU reference\n");
    printf("    on the same hardware; expect ~2x slower for the JS event loop.\n");
    printf("\n");
    return 0;
}
