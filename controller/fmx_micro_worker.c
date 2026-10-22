/*
 * fmx_micro_worker.c — FuturaMAX Safe RAM-Only Edge Micro-Worker
 *
 * Compatible with:
 *   1. Stock airOS 8 (WA/XC): MIPS 74Kc Big-Endian, Linux 2.6.32.68, uClibc 0.9.33.2
 *   2. OpenWrt 24.10.4 (ath79): MIPS 24Kc/74Kc Big-Endian, Linux 6.6.110, musl 1.2.4
 *   3. Stock LTU (afltu): ARMv7 Cortex-A9 Little-Endian, Linux 3.14.65, uClibc/glibc
 *
 * Hard Safety Guarantees (OpenMax Section 5):
 *   - Runs strictly from /tmp (tmpfs RAM); zero MTD/flash writes.
 *   - Zero shell execution (system/popen/execve forbidden); fixed integer opcodes only.
 *   - Uses only Linux >= 2.6.32 POSIX syscalls (clock_gettime CLOCK_MONOTONIC, nanosleep, open/read/close).
 *   - Explicit micro-slice duty-cycle throttling (50 ms period, 1%..20% cap) + nice(19).
 *   - Preempts within <= 150 ms (< 200 ms hard gate) when ath0/eth0 traffic exceeds threshold.
 *   - Aborts immediately if (MemFree + Cached) drops below 16,384 kB (16 MB).
 *   - Hard monotonic lease TTL dead-man switch (max 180s).
 */

#define _POSIX_C_SOURCE 200112L
#define _XOPEN_SOURCE 600
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

/* Exit codes for deterministic controller classification */
#define EXIT_OK                 0
#define EXIT_INVALID_ARGS      64
#define EXIT_KILL_SWITCH       72
#define EXIT_LEASE_EXPIRED     73
#define EXIT_TRAFFIC_PREEMPT   74
#define EXIT_MEM_PRESSURE      75
#define EXIT_TELEMETRY_ERROR   76

/* Safety hard bounds */
#define MIN_FREE_RAM_KB     16384UL
#define MAX_DUTY_PCT           20U
#define SLICE_PERIOD_NS  50000000ULL  /* 50 ms total slice period */
#define GUARD_CHECK_SLICES      3U    /* Check traffic/RAM every 3 slices = 150 ms (< 200 ms gate) */
#define MAX_LEASE_TTL_SEC     180U
#define STOP_FILE_PATH       "/tmp/fmx_worker.stop"

/* Supported fixed opcodes (no arbitrary shell or dynamic code) */
#define OP_INT_MONTE_CARLO      1U
#define OP_FNV1A_HASH_SWEEP     2U
#define OP_RF_HISTOGRAM_DIGEST  3U

static uint64_t monotonic_ns(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        fprintf(stderr, "{\"status\":\"ERR_CLOCK\"}\n");
        exit(EXIT_TELEMETRY_ERROR);
    }
    return ((uint64_t)ts.tv_sec * 1000000000ULL) + (uint64_t)ts.tv_nsec;
}

static void sleep_ns(uint64_t ns) {
    struct timespec req, rem;
    req.tv_sec = (time_t)(ns / 1000000000ULL);
    req.tv_nsec = (long)(ns % 1000000000ULL);
    while (nanosleep(&req, &rem) == -1 && errno == EINTR) {
        req = rem;
    }
}

/* Read MemFree + Cached from /proc/meminfo without stdio heap allocations */
static unsigned long read_usable_ram_kb(void) {
    char buf[1024];
    int fd = open("/proc/meminfo", O_RDONLY);
    if (fd < 0) {
        return 0;
    }
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) {
        return 0;
    }
    buf[n] = '\0';

    unsigned long mem_free = 0;
    unsigned long cached = 0;
    unsigned long buffers = 0;
    unsigned long shmem = 0;
    unsigned int found = 0;
    const char *p = buf;
    while (*p) {
        /* Later unrelated meminfo fields may exceed this bounded read. Only
         * complete required lines count; a partial final line proves nothing. */
        const char *nl = strchr(p, '\n');
        if (!nl) break;
        if (strncmp(p, "MemFree:", 8) == 0) {
            mem_free = strtoul(p + 8, NULL, 10);
            found |= 1;
        } else if (strncmp(p, "Buffers:", 8) == 0) {
            buffers = strtoul(p + 8, NULL, 10);
            found |= 2;
        } else if (strncmp(p, "Cached:", 7) == 0) {
            cached = strtoul(p + 7, NULL, 10);
            found |= 4;
        } else if (strncmp(p, "Shmem:", 6) == 0) {
            shmem = strtoul(p + 6, NULL, 10);
            found |= 8;
        }
        p = nl + 1;
    }
    if (found != 15 || UINT64_MAX - mem_free < (uint64_t)buffers + cached)
        return 0;
    uint64_t usable = (uint64_t)mem_free + buffers + cached;
    /* Cached tmpfs/shmem is not reclaimable cache. Never count it as headroom. */
    if (usable < shmem || usable - shmem > (unsigned long)-1)
        return 0;
    return (unsigned long)(usable - shmem);
}

/* Sum RX + TX bytes on ath0 and eth0 from /proc/net/dev */
static int read_interface_bytes(uint64_t *out_total_bytes) {
    char buf[2048];
    int fd = open("/proc/net/dev", O_RDONLY);
    if (fd < 0) {
        return -1;
    }
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0 || n == (ssize_t)sizeof(buf) - 1) {
        return -1;
    }
    buf[n] = '\0';

    uint64_t total = 0;
    unsigned int interfaces = 0;
    const char *p = buf;
    while (*p) {
        while (*p == ' ' || *p == '\t') p++;
        if (strncmp(p, "ath0:", 5) == 0 || strncmp(p, "eth0:", 5) == 0 ||
            strncmp(p, "br0:", 4) == 0) {
            const char *colon = strchr(p, ':');
            if (colon) {
                unsigned long long f[16];
                if (sscanf(colon + 1, "%llu %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu",
                    &f[0], &f[1], &f[2], &f[3], &f[4], &f[5], &f[6], &f[7],
                    &f[8], &f[9], &f[10], &f[11], &f[12], &f[13], &f[14], &f[15]) != 16)
                    return -1;
                if (UINT64_MAX - f[0] < f[8] || UINT64_MAX - total < f[0] + f[8])
                    return -1;
                total += f[0] + f[8];
                interfaces++;
            }
        }
        const char *nl = strchr(p, '\n');
        if (!nl) break;
        p = nl + 1;
    }
    if (!interfaces) return -1;
    *out_total_bytes = total;
    return 0;
}

/* Deterministic 32-bit Xorshift PRNG (zero FPU required on MIPS 74Kc) */
static inline uint32_t xorshift32(uint32_t *state) {
    uint32_t x = *state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return x;
}

/* Fixed-point quarter-circle Monte Carlo step (integer only, no soft-float trap) */
static uint32_t run_kernel_step(uint32_t opcode, uint32_t *rng_state, uint32_t *accum, uint32_t batch) {
    uint32_t hits = 0;
    uint32_t s = *rng_state;
    uint32_t acc = *accum;

    if (opcode == OP_INT_MONTE_CARLO) {
        for (uint32_t i = 0; i < batch; i++) {
            uint32_t r = xorshift32(&s);
            uint32_t x = r & 0xFFFFU;
            uint32_t y = (r >> 16) & 0xFFFFU;
            uint64_t dist2 = (uint64_t)x * (uint64_t)x + (uint64_t)y * (uint64_t)y;
            if (dist2 <= 0xFFFFFFFFULL) {
                hits++;
            }
        }
        acc += hits;
    } else if (opcode == OP_FNV1A_HASH_SWEEP) {
        for (uint32_t i = 0; i < batch; i++) {
            uint32_t r = xorshift32(&s);
            acc ^= (r & 0xFFU);
            acc *= 16777619U;
            acc ^= ((r >> 8) & 0xFFU);
            acc *= 16777619U;
        }
    } else {
        /* OP_RF_HISTOGRAM_DIGEST: compact rolling integer digest */
        for (uint32_t i = 0; i < batch; i++) {
            uint32_t r = xorshift32(&s);
            acc = (acc << 7) | (acc >> 25);
            acc ^= (r * 2654435761U);
        }
    }

    *rng_state = s;
    *accum = acc;
    return batch;
}

static int parse_uint(const char *text, uint64_t maximum, uint64_t *out) {
    const char *p;
    char *end;
    if (!text || !*text) return -1;
    for (p = text; *p; p++) if (*p < '0' || *p > '9') return -1;
    errno = 0;
    unsigned long long value = strtoull(text, &end, 10);
    if (errno == ERANGE || *end || value > maximum) return -1;
    *out = value;
    return 0;
}

int main(int argc, char **argv) {
    /*
     * Usage: /tmp/fmx_micro_worker <opcode:1..3> <seed> <total_iters> <duty_pct:1..20> <lease_ttl_s:1..180> <max_kbps>
     */
    if (argc != 7) {
        fprintf(stderr, "{\"status\":\"ERR_ARGS\"}\n");
        return EXIT_INVALID_ARGS;
    }

    uint64_t args[6];
    for (int i = 0; i < 6; i++) {
        if (parse_uint(argv[i + 1], i == 2 ? UINT64_MAX : UINT32_MAX, &args[i]))
            return EXIT_INVALID_ARGS;
    }
    uint32_t opcode = (uint32_t)args[0], seed = (uint32_t)args[1];
    uint64_t target_iters = args[2];
    uint32_t duty_pct = (uint32_t)args[3], lease_ttl_s = (uint32_t)args[4];
    uint32_t max_kbps = (uint32_t)args[5];

    if (opcode < 1U || opcode > 3U || seed == 0U || target_iters == 0ULL) {
        return EXIT_INVALID_ARGS;
    }
    if (duty_pct < 1U || duty_pct > MAX_DUTY_PCT ||
        lease_ttl_s < 1U || lease_ttl_s > MAX_LEASE_TTL_SEC)
        return EXIT_INVALID_ARGS;

    /* Lower scheduling priority before starting work loop */
    if (nice(19) == -1 && errno != 0) {
        /* Non-fatal if unprivileged */
    }

    uint64_t start_ns = monotonic_ns();
    uint64_t deadline_ns = start_ns + ((uint64_t)lease_ttl_s * 1000000000ULL);
    uint64_t work_budget_ns = (SLICE_PERIOD_NS * (uint64_t)duty_pct) / 100ULL;

    unsigned long free_ram_kb = read_usable_ram_kb();
    if (free_ram_kb < MIN_FREE_RAM_KB) {
        printf("{\"status\":\"PREEMPT_MEM\",\"free_ram_kb\":%lu}\n", free_ram_kb);
        return EXIT_MEM_PRESSURE;
    }

    uint64_t prev_net_bytes = 0;
    uint64_t prev_guard_ns = start_ns;
    if (read_interface_bytes(&prev_net_bytes)) return EXIT_TELEMETRY_ERROR;

    uint32_t rng_state = seed;
    uint32_t accum = (opcode == OP_FNV1A_HASH_SWEEP) ? 2166136261U : 0U;
    uint64_t done_iters = 0;
    uint32_t slice_idx = 0;

    while (done_iters < target_iters) {
        /* 1. Check local kill switch file every 50 ms slice */
        if (access(STOP_FILE_PATH, F_OK) == 0) {
            printf("{\"status\":\"STOP_FILE\",\"done_iters\":%llu}\n",
                   (unsigned long long)done_iters);
            return EXIT_KILL_SWITCH;
        }

        uint64_t slice_start_ns = monotonic_ns();
        if (slice_start_ns >= deadline_ns) {
            printf("{\"status\":\"LEASE_EXPIRED\",\"done_iters\":%llu}\n",
                   (unsigned long long)done_iters);
            return EXIT_LEASE_EXPIRED;
        }

        /* 2. Periodic RAM & Customer Traffic Preemption Guard (every 150 ms < 200 ms requirement) */
        if (slice_idx > 0 && (slice_idx % GUARD_CHECK_SLICES) == 0) {
            free_ram_kb = read_usable_ram_kb();
            if (free_ram_kb < MIN_FREE_RAM_KB) {
                printf("{\"status\":\"PREEMPT_MEM\",\"free_ram_kb\":%lu,\"done_iters\":%llu}\n",
                       free_ram_kb, (unsigned long long)done_iters);
                return EXIT_MEM_PRESSURE;
            }

            uint64_t cur_net_bytes = 0;
            if (read_interface_bytes(&cur_net_bytes) || cur_net_bytes < prev_net_bytes)
                return EXIT_TELEMETRY_ERROR;
            {
                uint64_t delta_ns = slice_start_ns - prev_guard_ns;
                if (delta_ns > 0) {
                    uint64_t delta_bytes = cur_net_bytes - prev_net_bytes;
                    /* kbps = (delta_bytes * 8 * 1e9) / (delta_ns * 1000) = (delta_bytes * 8000000) / delta_ns */
                    uint64_t observed_kbps = (delta_bytes * 8000000ULL) / delta_ns;
                    if (observed_kbps > (uint64_t)max_kbps) {
                        printf("{\"status\":\"PREEMPT_TRAFFIC\",\"observed_kbps\":%llu,\"done_iters\":%llu}\n",
                               (unsigned long long)observed_kbps, (unsigned long long)done_iters);
                        return EXIT_TRAFFIC_PREEMPT;
                    }
                }
                prev_net_bytes = cur_net_bytes;
                prev_guard_ns = slice_start_ns;
            }
        }

        /* 3. Execute bounded work sub-batches until work_budget_ns (e.g. 2.5ms @ 5% or 5.0ms @ 10%) is used */
        while (done_iters < target_iters) {
            uint32_t step_batch = 1024U;
            if (target_iters - done_iters < (uint64_t)step_batch) {
                step_batch = (uint32_t)(target_iters - done_iters);
            }
            done_iters += run_kernel_step(opcode, &rng_state, &accum, step_batch);
            uint64_t now_ns = monotonic_ns();
            if (now_ns >= deadline_ns) return EXIT_LEASE_EXPIRED;
            if (now_ns - slice_start_ns >= work_budget_ns) {
                break;
            }
        }

        /* 4. Explicit nanosleep for the remainder of the 50 ms slice */
        uint64_t elapsed_work_ns = monotonic_ns() - slice_start_ns;
        if (elapsed_work_ns < SLICE_PERIOD_NS && done_iters < target_iters) {
            sleep_ns(SLICE_PERIOD_NS - elapsed_work_ns);
        }
        slice_idx++;
    }

    uint64_t total_ms = (monotonic_ns() - start_ns) / 1000000ULL;
    printf("{\"status\":\"OK\",\"opcode\":%u,\"seed\":%u,\"done_iters\":%llu,\"accum\":%u,\"elapsed_ms\":%llu}\n",
           opcode, seed, (unsigned long long)done_iters, accum, (unsigned long long)total_ms);
    return EXIT_OK;
}
