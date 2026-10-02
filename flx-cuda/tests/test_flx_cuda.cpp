// test_flx_cuda.cpp
// flx-cuda tests: cover the priority scheduler's basic invariants.
// Requires CUDA toolkit (nvcc) to build. Skipped gracefully if not available.
//
// Run with: ./test_flx_cuda
// Or via ctest: ctest --output-on-failure

#include "../src/flx_cuda.cuh"
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <vector>

using namespace flx_cuda;

// Helper: check return value
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
    EXPECT_OK(flx_scheduler_init(&sched, 1024, -128, 127));
    EXPECT_OK(flx_scheduler_free(&sched));
    printf("ok\n");
    return 0;
}

int test_submit_and_dispatch() {
    printf("test_submit_and_dispatch ... ");
    FlxScheduler sched;
    EXPECT_OK(flx_scheduler_init(&sched, 1024, 0, 9));

    // Submit 3 ops with different priorities
    FlxOpCell op1 = {.id = 1, .kind = 0, .priority = 5, .status = FLX_OP_QUEUED,
                     .size = 4096, .ptr = 0, .timestamp = 0};
    FlxOpCell op2 = {.id = 2, .kind = 1, .priority = 9, .status = FLX_OP_QUEUED,
                     .size = 0, .ptr = 0x1000, .timestamp = 0};
    FlxOpCell op3 = {.id = 3, .kind = 2, .priority = 3, .status = FLX_OP_QUEUED,
                     .size = 0, .ptr = 0x2000, .timestamp = 0};

    EXPECT_OK(flx_submit(&sched, &op1));
    EXPECT_OK(flx_submit(&sched, &op2));
    EXPECT_OK(flx_submit(&sched, &op3));

    // Dispatch should return op2 (highest priority)
    FlxOpCell out;
    EXPECT_OK(flx_dispatch(&sched, &out));
    assert(out.id == 2);
    assert(out.priority == 9);
    EXPECT_OK(flx_complete(&sched, 2));

    // Next dispatch: op1 (priority 5)
    EXPECT_OK(flx_dispatch(&sched, &out));
    assert(out.id == 1);
    assert(out.priority == 5);
    EXPECT_OK(flx_complete(&sched, 1));

    // Next dispatch: op3 (priority 3)
    EXPECT_OK(flx_dispatch(&sched, &out));
    assert(out.id == 3);
    assert(out.priority == 3);
    EXPECT_OK(flx_complete(&sched, 3));

    // Queue should be empty
    EXPECT_STATUS(flx_dispatch(&sched, &out), FLX_CUDA_ERR_QUEUE_EMPTY);

    EXPECT_OK(flx_scheduler_free(&sched));
    printf("ok\n");
    return 0;
}

int test_drain() {
    printf("test_drain ... ");
    FlxScheduler sched;
    EXPECT_OK(flx_scheduler_init(&sched, 256, -128, 127));

    // Submit 5 ops at priority 5
    for (int i = 0; i < 5; i++) {
        FlxOpCell op = {.id = 100 + i, .kind = 0, .priority = 5,
                         .status = FLX_OP_QUEUED, .size = 1024 * (i + 1),
                         .ptr = 0, .timestamp = 0};
        EXPECT_OK(flx_submit(&sched, &op));
    }

    // Drain the priority 5 bucket
    EXPECT_OK(flx_drain(&sched, 5));

    // Counts should be zero for priority 5
    int32_t counts[256];
    EXPECT_OK(flx_queue_counts(&sched, counts));
    assert(counts[5 + 128] == 0);  // priority 5 is bucket index 133

    EXPECT_OK(flx_scheduler_free(&sched));
    printf("ok\n");
    return 0;
}

int test_quilt_projection_invariants() {
    printf("test_quilt_projection_invariants ... ");
    // The 5+1 Quilt opcodes applied to the scheduler.
    FlxScheduler sched;
    EXPECT_OK(flx_scheduler_init(&sched, 1024, 0, 9));

    int32_t next_id = 0;

    // BIND (mount) — implicit in flx_scheduler_init
    // EFFECT (submit) — every submit appends an op cell
    FlxOpCell op = {.id = next_id++, .kind = 0, .priority = 5,
                    .status = FLX_OP_QUEUED, .size = 8192, .ptr = 0,
                    .timestamp = 0};
    EXPECT_OK(flx_submit(&sched, &op));

    // VIEW (read state)
    int32_t counts[256];
    EXPECT_OK(flx_queue_counts(&sched, counts));
    assert(counts[5] == 1);

    // TICK (clock advance)
    flx_tick(&sched, 1);
    assert(sched.tick_count == 1);

    // EFFECT (dispatch — the op runs)
    FlxOpCell out;
    EXPECT_OK(flx_dispatch(&sched, &out));
    assert(out.id == 0);
    assert(out.status == FLX_OP_RUNNING);

    // EFFECT (complete)
    EXPECT_OK(flx_complete(&sched, out.id));

    // FORGET (drain)
    EXPECT_OK(flx_drain(&sched, 5));

    EXPECT_OK(flx_scheduler_free(&sched));
    printf("ok\n");
    return 0;
}

int main() {
    int failed = 0;
    failed += test_init_and_free();
    failed += test_submit_and_dispatch();
    failed += test_drain();
    failed += test_quilt_projection_invariants();

    if (failed == 0) {
        printf("\nAll flx-cuda tests passed.\n");
        return 0;
    }
    fprintf(stderr, "\n%d test(s) failed.\n", failed);
    return 1;
}
