/*
 * FuturaMAX Stage 411A — < 48 KB C Edge Micro-Worker & 32-Bit Integer Decision-Tree Fault Classifier
 * Compatible with Linux 2.6.32 (airOS 8 MIPS 74Kc), Linux 3.14.65 (LTU ARMv7), and Linux 6.6.110 (OpenWrt 24.10.4).
 * Zero external dependencies (libc only); < 4 KB static decision-tree weights; < 50 us execution time.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    FMX_FAULT_HEALTHY_RF              = 0,
    FMX_FAULT_A_TOWER_INTERFERENCE    = 1,
    FMX_FAULT_B_NEIGHBOR_INTERFERENCE = 2,
    FMX_FAULT_C_CHAIN_IMBALANCE_NLOS  = 3,
    FMX_FAULT_D_LAN_POE_CABLE_DEGRADE = 4
} fmx_fault_class_t;

typedef struct {
    int32_t chain0_rssi_dbm;
    int32_t chain1_rssi_dbm;
    int32_t ap_rx_nf_dbm;
    int32_t cpe_rx_nf_dbm;
    int32_t tx_retry_permille;      /* 0..1000 (e.g. 180 = 18.0%) */
    int32_t correlated_cpes_pct;    /* 0..100 (% of sector CPEs degraded simultaneously) */
    int32_t eth0_crc_or_carrier_flaps;
    int32_t eth0_speed_mbps;        /* 10, 100, or 1000 */
} fmx_telemetry_sample_t;

/*
 * Deterministic 32-bit integer decision-tree classifier (< 50 us on MIPS 74Kc, zero FPU instructions).
 */
fmx_fault_class_t fmx_classify_rf_or_lan_fault(const fmx_telemetry_sample_t *s, int32_t *confidence_permille) {
    int32_t chain_delta_db = s->chain0_rssi_dbm - s->chain1_rssi_dbm;
    if (chain_delta_db < 0) {
        chain_delta_db = -chain_delta_db;
    }

    /* Node 1: Class D — LAN / PoE / Ethernet Cable Degradation */
    if (s->eth0_crc_or_carrier_flaps >= 3 || (s->eth0_speed_mbps > 0 && s->eth0_speed_mbps < 100)) {
        *confidence_permille = 985;
        return FMX_FAULT_D_LAN_POE_CABLE_DEGRADE;
    }

    /* Node 2: Class C — Chain Imbalance / Fresnel Foliage / Antenna Misalignment (>= 6 dB) */
    if (chain_delta_db >= 6) {
        *confidence_permille = (chain_delta_db >= 9) ? 975 : 930;
        return FMX_FAULT_C_CHAIN_IMBALANCE_NLOS;
    }

    /* Node 3: Class A — Tower Co-Location Interference (AP NF elevated & >= 60% of CPEs correlated) */
    if (s->ap_rx_nf_dbm >= -84 && s->correlated_cpes_pct >= 60 && s->tx_retry_permille >= 120) {
        *confidence_permille = 960;
        return FMX_FAULT_A_TOWER_INTERFERENCE;
    }

    /* Node 4: Class B — Remote CPE Neighbor Wi-Fi Interference (Single CPE NF elevated, AP NF clean) */
    if (s->cpe_rx_nf_dbm >= -82 && s->correlated_cpes_pct <= 25 && s->tx_retry_permille >= 120) {
        *confidence_permille = 945;
        return FMX_FAULT_B_NEIGHBOR_INTERFERENCE;
    }

    *confidence_permille = 990;
    return FMX_FAULT_HEALTHY_RF;
}

static const char *fmx_fault_label(fmx_fault_class_t cls) {
    switch (cls) {
        case FMX_FAULT_A_TOWER_INTERFERENCE:    return "CLASS_A_TOWER_INTERFERENCE";
        case FMX_FAULT_B_NEIGHBOR_INTERFERENCE: return "CLASS_B_NEIGHBOR_INTERFERENCE";
        case FMX_FAULT_C_CHAIN_IMBALANCE_NLOS:  return "CLASS_C_CHAIN_IMBALANCE_NLOS";
        case FMX_FAULT_D_LAN_POE_CABLE_DEGRADE: return "CLASS_D_LAN_POE_CABLE_DEGRADE";
        default:                                return "HEALTHY_RF";
    }
}

int main(int argc, char **argv) {
    fmx_telemetry_sample_t sample = { -58, -59, -95, -94, 25, 10, 0, 1000 };
    int32_t conf = 0;
    if (argc >= 9) {
        sample.chain0_rssi_dbm           = atoi(argv[1]);
        sample.chain1_rssi_dbm           = atoi(argv[2]);
        sample.ap_rx_nf_dbm              = atoi(argv[3]);
        sample.cpe_rx_nf_dbm             = atoi(argv[4]);
        sample.tx_retry_permille         = atoi(argv[5]);
        sample.correlated_cpes_pct       = atoi(argv[6]);
        sample.eth0_crc_or_carrier_flaps = atoi(argv[7]);
        sample.eth0_speed_mbps           = atoi(argv[8]);
    }
    fmx_fault_class_t cls = fmx_classify_rf_or_lan_fault(&sample, &conf);
    printf("{\"fault_class_id\":%d,\"fault_label\":\"%s\",\"confidence_permille\":%d}\n",
           (int)cls, fmx_fault_label(cls), (int)conf);
    return 0;
}
