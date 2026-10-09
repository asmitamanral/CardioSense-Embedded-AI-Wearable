"""
Automated unit and integration test for CardioSense simulator logic.
Verifies:
1. Normal resting baseline yields low MSE and no alert.
2. Vigorous exercise (jogging) raises HR and sweat, but motion gating prevents false alarm.
3. Precursor crisis triggers Stage 1 pre-alert and escalates to Stage 2 (SMS + Voice call).
4. Cancellation button aborts Stage 1 countdown successfully.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))
from simulator import CardioSimulator

def test_cardiosense_pipeline():
    print("Testing CardioSense Simulation Pipeline...")
    sim = CardioSimulator()

    # Test 1: Rest Baseline
    sim.scenario = "rest"
    for _ in range(5):
        mse, dyn_th, risk, is_ano, is_art, _ = sim.update_physiology()
    print(f"[TEST 1] Rest Baseline: MSE={mse:.6f}, Threshold={dyn_th:.6f}, Anomaly={is_ano}")
    assert not is_ano, "Error: Rest baseline flagged as anomaly!"
    assert sim.alert_state == "NORMAL", "Error: Alert state should be NORMAL during rest!"

    # Test 2: Exercise (Motion Rejection)
    sim.scenario = "exercise"
    for _ in range(5):
        mse, dyn_th, risk, is_ano, is_art, _ = sim.update_physiology()
    print(f"[TEST 2] Jogging/Exercise: MSE={mse:.6f}, Dynamic Threshold={dyn_th:.6f}, Anomaly={is_ano}")
    assert not is_ano, "Error: Exercise falsely flagged as anomaly (motion gating failure)!"

    # Test 3: Precursor Crisis & Stage 1 Alert
    sim.scenario = "precursor"
    for _ in range(3):
        mse, dyn_th, risk, is_ano, is_art, _ = sim.update_physiology()
    print(f"[TEST 3] Precursor Crisis: MSE={mse:.6f}, Threshold={dyn_th:.6f}, Anomaly={is_ano}, AlertState={sim.alert_state}")
    assert is_ano, "Error: Precursor crisis failed to be detected by Autoencoder!"
    assert sim.alert_state == "STAGE_1", f"Error: Expected STAGE_1 alert, got {sim.alert_state}"

    # Test 4: Cancellation Button
    canceled = sim.cancel_alert()
    print(f"[TEST 4] Cancellation button pressed: Canceled={canceled}, State={sim.alert_state}")
    assert canceled and sim.alert_state == "ABORTED", "Error: Failed to abort Stage 1 alert!"

    # Test 5: Precursor escalation to Stage 2 when uncancelled
    sim.alert_state = "STAGE_1"
    sim.stage1_timer = 1 # Force timer to 1 second
    mse, dyn_th, risk, is_ano, is_art, _ = sim.update_physiology()
    print(f"[TEST 5] Stage 1 timeout: AlertState={sim.alert_state}")
    assert sim.alert_state == "STAGE_2", f"Error: Expected STAGE_2 escalation, got {sim.alert_state}"

    print("\nALL AUTOMATED TESTS PASSED SUCCESSFULLY! (5/5)")

if __name__ == "__main__":
    test_cardiosense_pipeline()
