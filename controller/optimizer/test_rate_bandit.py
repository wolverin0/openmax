"""
Test suite and dynamic fading benchmark for ADR-Bandit Rate Mask Controller.
Simulates a fixed outdoor wireless link transitioning through clear sky -> rain fade.
"""

import random
from controller.optimizer.rate_bandit import ADRBanditRateController


def simulate_wireless_channel(arm_idx: int, channel_state: str) -> tuple:
    """
    Simulate physical PHY performance for each rate mask arm:
    Arm 0: MCS0-9 (Unbounded)
    Arm 1: MCS0-8 (Ban MCS9)
    Arm 2: MCS0-7 (64-QAM Ceiling)
    Arm 3: MCS0-5 (16-QAM Ceiling)
    Arm 4: MCS0-3 (QPSK Robust)
    """
    noise = random.uniform(-1.0, 1.0)
    
    if channel_state == "CLEAR_SKY":
        # Link has 28 dB SNR: MCS7 is rock-solid (0% PER, 60 Mbps),
        # MCS8 is good (50 Mbps), MCS9 has 30% PER (wasting airtime!)
        if arm_idx == 0:  # MCS0-9: probes MCS9 and suffers retries
            return (48.0 + noise, 0.25, 0.35)
        elif arm_idx == 1:  # MCS0-8: avoids MCS9, high goodput
            return (58.0 + noise, 0.05, 0.08)
        elif arm_idx == 2:  # MCS0-7: optimal rock solid
            return (62.0 + noise, 0.01, 0.02)
        elif arm_idx == 3:  # MCS0-5: capped too low
            return (35.0 + noise, 0.00, 0.01)
        else:  # MCS0-3
            return (18.0 + noise, 0.00, 0.01)

    elif channel_state == "RAIN_FADE":
        # Link drops by 10 dB SNR: MCS7 now has 60% PER!
        # Optimal arm is now Arm 3 (MCS0-5 @ 32 Mbps, 2% PER)
        if arm_idx in [0, 1, 2]:  # High MCS fails completely
            return (12.0 + noise, 0.65, 0.70)
        elif arm_idx == 3:  # MCS0-5: solid
            return (33.0 + noise, 0.02, 0.04)
        else:  # MCS0-3: low
            return (18.0 + noise, 0.01, 0.02)


def test_bandit_convergence_and_adaptation():
    print("==========================================================================")
    print("  TESTING ADR-BANDIT RATE-MASK CONTROLLER UNDER DYNAMIC OUTDOOR FADING")
    print("==========================================================================")

    controller = ADRBanditRateController(cpe_id="CPE-381-TowerEast")

    # Phase 1: Clear Sky (100 steps) - Should converge to Arm 2 (MCS0-7)
    print("\n[+] Phase 1: Clear Sky (100 steps)...")
    for step in range(100):
        arm = controller.select_arm()
        goodput, per, retry = simulate_wireless_channel(arm.arm_id, "CLEAR_SKY")
        controller.feedback(goodput, per, retry)

    status_p1 = controller.get_status()
    print(f"    Active Arm after Clear Sky: {status_p1['active_arm']}")
    for a in status_p1["arms"]:
        print(f"    - {a['name']:<24}: pulls={a['pulls']:<3}, mean_reward={a['mean_reward']:.2f}")

    # Optimal arm under clear sky is Arm 2 (MCS0-7)
    assert status_p1["arms"][2]["pulls"] > 50, "Should heavily exploit Arm 2 under clear sky"

    # Phase 2: Sudden Rain Fade (100 steps) - Should detect drift and re-converge to Arm 3 (MCS0-5)
    print("\n[+] Phase 2: Rain Fade Transition (100 steps)...")
    for step in range(100):
        arm = controller.select_arm()
        goodput, per, retry = simulate_wireless_channel(arm.arm_id, "RAIN_FADE")
        controller.feedback(goodput, per, retry)

    status_p2 = controller.get_status()
    print(f"    Active Arm after Rain Fade: {status_p2['active_arm']}")
    for a in status_p2["arms"]:
        print(f"    - {a['name']:<24}: pulls={a['pulls']:<3}, mean_reward={a['mean_reward']:.2f}")

    # Optimal arm under rain fade is Arm 3 (MCS0-5)
    assert status_p2["arms"][3]["pulls"] > 40, "Should adapt and heavily exploit Arm 3 under rain fade"

    print("\n>>> ALL BANDIT CONVERGENCE TESTS PASSED WITH 100% SUCCESS <<<\n")


if __name__ == "__main__":
    test_bandit_convergence_and_adaptation()
