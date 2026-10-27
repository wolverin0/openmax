/* SPDX-License-Identifier: ISC */
/* Stage 350A — Cooperative CPE Control-Plane Differential Sensing Micro-Classifier */
#ifndef _FMX_COOPERATIVE_CPE_CLASSIFIER_H_
#define _FMX_COOPERATIVE_CPE_CLASSIFIER_H_

enum fmx_sector_fault_class {
	FMX_FAULT_HEALTHY_SECTOR = 0,
	FMX_FAULT_TOWER_AP_COLLOCATION_INTERFERENCE = 1,
	FMX_FAULT_LOCALIZED_NEIGHBOR_RF_INTERFERENCE = 2,
	FMX_FAULT_SINGLE_CPE_FRESNEL_FOLIAGE_OBSTRUCTION = 3,
	FMX_FAULT_LAN_POE_CABLE_CARRIER_FAULT = 4,
};

struct fmx_cpe_diff_telemetry {
	int evm_db_x10;
	int pilot_evm_std_db_x10;
	int rx_phy_err_per_sec;
	int chain_delta_db_x10;
	int bmiss_count;
	int eth0_carrier_changes;
	int eth0_crc_errors;
};

static inline enum fmx_sector_fault_class fmx_classify_cpe_differential(
	const struct fmx_cpe_diff_telemetry *s,
	int sector_phy_err_pct,
	int sector_bmiss_pct)
{
	if (s->eth0_carrier_changes > 0 || s->eth0_crc_errors > 0)
		return FMX_FAULT_LAN_POE_CABLE_CARRIER_FAULT;
	if (sector_phy_err_pct >= 60 && sector_bmiss_pct >= 50 && s->rx_phy_err_per_sec >= 80)
		return FMX_FAULT_TOWER_AP_COLLOCATION_INTERFERENCE;
	if (s->chain_delta_db_x10 >= 60 && s->pilot_evm_std_db_x10 >= 25 && s->rx_phy_err_per_sec < 80)
		return FMX_FAULT_SINGLE_CPE_FRESNEL_FOLIAGE_OBSTRUCTION;
	if (sector_phy_err_pct < 60 && s->rx_phy_err_per_sec >= 80 && s->chain_delta_db_x10 < 45)
		return FMX_FAULT_LOCALIZED_NEIGHBOR_RF_INTERFERENCE;
	return FMX_FAULT_HEALTHY_SECTOR;
}

#endif /* _FMX_COOPERATIVE_CPE_CLASSIFIER_H_ */
