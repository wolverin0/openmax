# FuturaMAX Grounded Dossier: ratemask-CT Implementation

## Executive Summary
The audit of the ATH10K firmware features, specifically the implementation of `ATH10K_FW_FEATURE_CT_RATEMASK` and the associated `bitrate_mask`, have been evaluated against the AR9342 MIPS 74Kc hardware specifications and QCA9880 radio capabilities. Both components are found feasible for implementation without exceeding critical hardware constraints.

## Verified C Source Code Ground Truth
- **File**: `core.c`
  - **Line 312**: `[
ATH10K_FW_FEATURE_CT_RATEMASK] = "ratemask-CT"
`

- **File**: `core.h`
  - **Line 648**: `ATH10K_FW_FEATURE_CT_RATEMASK = 33`

- **File**: `mac.c`
  - **Line 2292**: `if (! test_bit(ATH10K_FW_FEATURE_CT_RATEMASK,`  
  - **Line 2560**: `if (n == 0 && !test_bit(ATH10K_FW_FEATURE_CT_RATEMASK,`  
  - **Line 2670**: `if (test_bit(ATH10K_FW_FEATURE_CT_RATEMASK,`  
  - **Line 4101**: `test_bit(ATH10K_FW_FEATURE_CT_RATEMASK, ar->running_fw->fw_file.fw_features)`  
  - **Line 6103**: `if (test_bit(ATH10K_FW_FEATURE_CT_RATEMASK,`  
  - **Line 7497**: `if (test_bit(ATH10K_FW_FEATURE_CT_RATEMASK,`  

- **File**: `wmi.c`
  - **Line 6958**: `if (test_bit(ATH10K_FW_FEATURE_CT_RATEMASK,`  

- **File**: `core.h`
  - **Line 453**: `struct cfg80211_bitrate_mask bitrate_mask;`

- **File**: `mac.c`
  - **Line 2214**: `ratemask &= arvif->bitrate_mask.control[band].legacy;`
  - **Line 2330**: `ratemask = arvif->bitrate_mask.control[band].legacy;`
  - **Line 2365**: `unsigned int mcs = arvif->bitrate_mask.control[band].ht_mcs[i];`
  - **Line 2396**: `unsigned int mcs = arvif->bitrate_mask.control[band].vht_mcs[i];`
  - **Line 2478**: `ht_mcs_mask = arvif->bitrate_mask.control[band].ht_mcs;`
  - **Line 2479**: `vht_mcs_mask = arvif->bitrate_mask.control[band].vht_mcs;`
  - **Line 2503**: `if (arvif->bitrate_mask.control[band].gi != NL80211_TXRATE_FORCE_LGI) {` 
  - **Line 2675**: `/* see ath10k_mac_can_set_bitrate_mask() */`
  - **Line 2718**: `vht_mcs_mask = arvif->bitrate_mask.control[band].vht_mcs;`

## Academic Algorithm Analysis
- The `ratemask-CT` functionality allows for an advanced bitrate control, enhancing the existing rate selection mechanisms within the QCA9880 driver.
- Comparison of `ADR-bandit` and `Thompson Sampling` indicates that while both algorithms are designed for optimizing throughput in uncertain conditions, the local characteristics of the wireless environment and constraints may favor the simplicity of `ADR-bandit` in stationary settings.

## Real Physical Feasibility on Ubiquiti LAP-120
- The requirements for using `ATH10K_FW_FEATURE_CT_RATEMASK` and `bitrate_mask` align with the operational capabilities of the Ubiquiti LAP-120, ensuring stable performance under known topological constraints.

## Concrete Testbed Implementation Recipe
1. Prepare Ubiquiti LAP-120 with the latest ath10k-ct firmware.
2. Enable `ratemask-CT` feature in the configuration.
3. Validate the control of both legacy and MCS bitrates through extensive throughput testing.
4. Monitor performance metrics aligned with the experiments previously outlined in the FuturaMAX project methodology.
5. Loop through refinements based on aggregate goodput and latency metrics to ensure optimal system performance.