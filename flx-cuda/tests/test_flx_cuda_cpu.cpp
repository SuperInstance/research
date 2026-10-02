// test_flx_cuda_cpu.cpp
// flx-cuda CPU test harness — runs without CUDA.
// Tests the same algorithm and witness chain as the CUDA kernels.
//
// Build:  g++ -std=c++14 -O2 tests/test_flx_cuda_cpu.cpp src/flx_cuda_cpu.hpp -o test_cpu
// Run:    ./test_cpu
//
// When CUDA is available, build with: cmake .. && make (which links the GPU kernels)

#include "../src/flx_cuda_cpu.hpp"
#include <cassert>
#include <cstdio>

using namespace flx_cuda;

#define EXPECT_OK(call)                                                       \
    do {                                                                      \
        flx_cuda_status s = (call);                                           \
        if (s != FLX_CUDA_OK) {                                               \
            fprintf(stderr, "FAIL %s:%d: expected OK got %d\n",              \
                    __FILE__, __LINE__, s);                                   \
            return 1;                                                         \
        }                                                                    \
    } while (0)

#define EXPECT_STATUS(call, expected)                                         \
    do {                                                                      \
        flx_cuda_status s = (call);                                           \
        if (s != (expected)) {                                                \
            fprintf(stderr, "FAIL %s:%d: expected %d got %d\n",               \
                    __FILE__, __LINE__, (expected), s);                       \
            return 1;                                                         \
        }                                                                    \
    } while (0)

int test_init_and_free() {
    printf("test_init_and_free ... ");
    FlxScheduler sched;
    EXPECT_OK(flx_scheduler_init_cpu(&sched, 1024, -128, 127));
    EXPECT_OK(flx_scheduler_free_cpu(&sched));
    printf("ok\n");
    return 0;
}

int test_submit_and_dispatch() {
    printf("test_submit_and_dispatch ... ");
    FlxScheduler sched;
    EXPECT_OK(flx_scheduler_init_cpu(&sched, 1024, 0, 9));

    FlxOpCell op1 = {1, 0, 5, FLX_OP_QUEUED, 0, 4096, 0, 0};
    FlxOpCell op2 = {2, 1, 9, FLX_OP_QUEUED, 0, 0, 0x1000, 0};
    FlxOpCell op3 = {3, 2, 3, FLX_OP_QUEUED, 0, 0, 0x2000, 0};

    EXPECT_OK(flx_submit_cpu(&sched, &op1));
    EXPECT_OK(flx_submit_cpu(&sched, &op2));
    EXPECT_OK(flx_submit_cpu(&sched, &op3));

    FlxOpCell out;
    EXPECT_OK(flx_dispatch_cpu(&sched, &out));
    assert(out.id == 2); assert(out.priority == 9);
    EXPECT_OK(flx_complete_cpu(&sched, 2));

    EXPECT_OK(flx_dispatch_cpu(&sched, &out));
    assert(out.id == 1); assert(out.priority == 5);
    EXPECT_OK(flx_complete_cpu(&sched, 1));

    EXPECT_OK(flx_dispatch_cpu(&sched, &out));
    assert(out.id == 3); assert(out.priority == 3);
    EXPECT_OK(flx_complete_cpu(&sched, 3));

    EXPECT_STATUS(flx_dispatch_cpu(&sched, &out), FLX_CUDA_ERR_QUEUE_EMPTY);
    EXPECT_OK(flx_scheduler_free_cpu(&sched));
    printf("ok\n");
    return 0;
}

int test_drain() {
    printf("test_drain ... ");
    FlxScheduler sched;
    // Use enough capacity so that bucket 133 (priority 5) can hold 5 ops.
    // 256 buckets × 5 ops = 1280 minimum, give 2048 with room to spare.
    EXPECT_OK(flx_scheduler_init_cpu(&sched, 2048, -128, 127));
    for (int i = 0; i < 5; i++) {
        FlxOpCell op = {100 + i, 0, 5, FLX_OP_QUEUED, 0, 1024 * (i + 1), 0, 0};
        EXPECT_OK(flx_submit_cpu(&sched, &op));
    }
    int32_t counts[256];
    EXPECT_OK(flx_queue_counts_cpu(&sched, counts));
    assert(counts[133] == 5);  // priority 5 → bucket index 133
    EXPECT_OK(flx_drain_cpu(&sched, 5));
    EXPECT_OK(flx_queue_counts_cpu(&sched, counts));
    assert(counts[133] == 0);
    EXPECT_OK(flx_scheduler_free_cpu(&sched));
    printf("ok\n");
    return 0;
}

int test_quilt_projection_invariants() {
    printf("test_quilt_projection_invariants ... ");
    FlxScheduler sched;
    EXPECT_OK(flx_scheduler_init_cpu(&sched, 1024, 0, 9));

    // BIND (implicit in init) — witness event recorded
    // EFFECT submit
    FlxOpCell op = {1, 0, 5, FLX_OP_QUEUED, 0, 8192, 0, 0};
    EXPECT_OK(flx_submit_cpu(&sched, &op));

    // VIEW
    int32_t counts[10];
    EXPECT_OK(flx_queue_counts_cpu(&sched, counts));
    assert(counts[5] == 1);

    // TICK
    flx_tick_cpu(&sched, 1);
    assert(sched.tick_count == 1);

    // EFFECT dispatch
    FlxOpCell out;
    EXPECT_OK(flx_dispatch_cpu(&sched, &out));
    assert(out.id == 1);
    assert(out.status == FLX_OP_RUNNING);

    // EFFECT complete
    EXPECT_OK(flx_complete_cpu(&sched, out.id));

    // FORGET
    EXPECT_OK(flx_drain_cpu(&sched, 5));

    // Witness chain should have at least 7 events
    assert(sched.witness.size() >= 7);
    EXPECT_OK(flx_scheduler_free_cpu(&sched));
    printf("ok\n");
    return 0;
}

int test_priority_ordering_under_load() {
    printf("test_priority_ordering_under_load ... ");
    // Stress: submit 100 ops at random priorities; dispatch should yield
    // them in priority-descending order.
    FlxScheduler sched;
    EXPECT_OK(flx_scheduler_init_cpu(&sched, 256, -128, 127));

    // Submit 100 ops with priorities ranging -50 to 50
    for (int i = 0; i < 100; i++) {
        FlxOpCell op = {i + 1, 0, (int8_t)((i % 100) - 50), FLX_OP_QUEUED, 0, 1024, 0, 0};
        EXPECT_OK(flx_submit_cpu(&sched, &op));
    }

    // Dispatch all; verify monotonically non-increasing priority
    FlxOpCell prev;
    bool first = true;
    int32_t out_count = 0;
    while (true) {
        FlxOpCell out;
        flx_cuda_status s = flx_dispatch_cpu(&sched, &out);
        if (s == FLX_CUDA_ERR_QUEUE_EMPTY) break;
        if (s != FLX_CUDA_OK) { fprintf(stderr, "dispatch err\n"); return 1; }
        if (!first) {
            assert(out.priority <= prev.priority);  // non-increasing
        }
        prev = out;
        first = false;
        out_count++;
    }
    assert(out_count == 100);

    EXPECT_OK(flx_scheduler_free_cpu(&sched));
    printf("ok\n");
    return 0;
}

int main() {
    int failed = 0;
    failed += test_init_and_free();
    failed += test_submit_and_dispatch();
    failed += test_drain();
    failed += test_quilt_projection_invariants();
    failed += test_priority_ordering_under_load();

    if (failed == 0) {
        printf("\nAll 5 flx-cuda CPU tests passed.\n");
        return 0;
    }
    fprintf(stderr, "\n%d test(s) failed.\n", failed);
    return 1;
}
