#!/usr/bin/env python3
"""
CardioSense: Interactive End-to-End Testbench Simulator
Simulates:
1. Wrist Slap-Band Node (PPG + GSR streaming at 20 Hz)
2. Sternum Hub Node (MPU6050 Respiration/Motion + Secondary PPG)
3. On-device DSP Sliding Window & Feature Normalizer
4. TinyML Autoencoder Anomaly Detection Engine
5. Emergency Alert State Machine (30s abortable countdown -> SIM800L SMS & Call dispatch)

Usage:
  python simulator.py
"""

import time
import math
import random
import sys
import os
import json

# Ensure numpy is imported
try:
    import numpy as np
except ImportError:
    print("NumPy not found. Installing or running in fallback mode...")
    os.system(f"{sys.executable} -m pip install numpy")
    import numpy as np

# Load trained model metadata
META_PATH = os.path.join(os.path.dirname(__file__), "..", "ml_pipeline", "model_meta.json")
if os.path.exists(META_PATH):
    with open(META_PATH, "r") as f:
        MODEL_META = json.load(f)
        AE_THRESHOLD = MODEL_META.get("threshold", 0.0081)
else:
    AE_THRESHOLD = 0.0081

# ANSI Color codes for clean terminal UI
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"

class CardioSimulator:
    def __init__(self):
        self.scenario = "rest" # "rest", "exercise", "precursor", "artifact"
        self.running = True
        self.tick = 0
        self.time_elapsed_sec = 0

        # Physiological states
        self.hr = 72.0
        self.spo2 = 98.0
        self.resp_rate = 14.0
        self.resp_depth = 0.45
        self.gsr_level = 4.5
        self.gsr_slope = 0.0
        self.motion_svm = 0.04
        self.hrv_rmssd = 45.0

        # Alert state machine
        self.alert_state = "NORMAL" # NORMAL, STAGE_1, STAGE_2, ABORTED
        self.stage1_timer = 0
        self.STAGE1_DURATION = 30 # 30 seconds

        # Load weights directly from model_weights.h or synthetic initialization
        self._init_weights()

    def _init_weights(self):
        # Read from model_weights.h if available
        weights_file = os.path.join(os.path.dirname(__file__), "..", "ml_pipeline", "model_weights.h")
        self.W1 = np.zeros((8, 4), dtype=np.float32)
        self.b1 = np.zeros(4, dtype=np.float32)
        self.W2 = np.zeros((4, 2), dtype=np.float32)
        self.b2 = np.zeros(2, dtype=np.float32)
        self.W3 = np.zeros((2, 4), dtype=np.float32)
        self.b3 = np.zeros(4, dtype=np.float32)
        self.W4 = np.zeros((4, 8), dtype=np.float32)
        self.b4 = np.zeros(8, dtype=np.float32)

        # Fallback to trained weights from training script if available
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml_pipeline"))
        try:
            from train_autoencoder import TinyMLAutoencoder, generate_normal_baseline, normalize_features
            model = TinyMLAutoencoder(in_dim=8, h1_dim=4, latent_dim=2, seed=123)
            # Train briefly or set values
            X_train = normalize_features(generate_normal_baseline(1000, seed=42))
            from train_autoencoder import train
            train(model, X_train, epochs=80, batch_size=64, lr=0.01)
            self.W1 = model.W1
            self.b1 = model.b1
            self.W2 = model.W2
            self.b2 = model.b2
            self.W3 = model.W3
            self.b3 = model.b3
            self.W4 = model.W4
            self.b4 = model.b4
        except Exception as e:
            print(f"Weight loader notice: {e}")

    def relu(self, x):
        return np.maximum(0.0, x)

    def sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -12.0, 12.0)))

    def evaluate_autoencoder(self, norm_vec):
        z1 = norm_vec @ self.W1 + self.b1
        a1 = self.relu(z1)
        z2 = a1 @ self.W2 + self.b2
        a2 = self.relu(z2)
        z3 = a2 @ self.W3 + self.b3
        a3 = self.relu(z3)
        z4 = a3 @ self.W4 + self.b4
        reconstruction = self.sigmoid(z4)

        mse = np.mean((norm_vec - reconstruction) ** 2)
        return mse, a2

    def normalize(self):
        bounds = [
            (40.0, 200.0), # hr
            (5.0, 120.0),  # hrv
            (70.0, 100.0), # spo2
            (6.0, 45.0),   # resp_rate
            (0.05, 1.0),   # resp_depth
            (0.5, 25.0),   # gsr_level
            (-2.0, 8.0),   # gsr_slope
            (0.0, 2.5)     # motion_svm
        ]
        raw = [
            self.hr, self.hrv_rmssd, self.spo2, self.resp_rate,
            self.resp_depth, self.gsr_level, self.gsr_slope, self.motion_svm
        ]
        norm = []
        for val, (low, high) in zip(raw, bounds):
            clamped = max(low, min(high, val))
            norm.append((clamped - low) / (high - low))
        return np.array(norm, dtype=np.float32)

    def update_physiology(self):
        self.tick += 1
        self.time_elapsed_sec += 1

        if self.scenario == "rest":
            self.hr = 70.0 + 3.0 * math.sin(self.tick / 5.0) + random.uniform(-1, 1)
            self.spo2 = 98.2 + random.uniform(-0.3, 0.3)
            self.resp_rate = 14.0 + 1.0 * math.sin(self.tick / 8.0)
            self.resp_depth = 0.42 + random.uniform(-0.03, 0.03)
            self.gsr_level = 4.2 + 0.2 * math.sin(self.tick / 12.0)
            self.gsr_slope = 0.02 + random.uniform(-0.05, 0.05)
            self.motion_svm = max(0.02, 0.04 + random.uniform(-0.02, 0.03))
            self.hrv_rmssd = 45.0 + random.uniform(-3, 3)

        elif self.scenario == "exercise":
            # Jogging / stair climbing: high HR and sweating, BUT high motion!
            self.motion_svm = 1.35 + random.uniform(-0.15, 0.15)
            self.hr = 138.0 + 6.0 * math.sin(self.tick / 4.0) + random.uniform(-2, 2)
            self.spo2 = 97.0 + random.uniform(-0.5, 0.5) # Preserved oxygen
            self.resp_rate = 28.0 + 2.0 * math.sin(self.tick / 6.0)
            self.resp_depth = 0.78 + random.uniform(-0.05, 0.05) # Deep respiration
            self.gsr_level = 10.5 + 0.5 * (self.tick % 10)
            self.gsr_slope = 0.45 + random.uniform(-0.1, 0.1) # Gentle thermal sweat
            self.hrv_rmssd = 22.0 + random.uniform(-2, 2)

        elif self.scenario == "precursor":
            # Acute Pre-Arrest Crisis: Tachycardia, severe hypoxia, cold sweat surge, agonal respiration, NO MOTION!
            self.motion_svm = max(0.01, 0.05 + random.uniform(-0.02, 0.03)) # Sitting/collapsing
            self.hr = min(178.0, 145.0 + (self.tick % 40) * 1.0 + random.uniform(-3, 3))
            self.spo2 = max(74.0, 92.0 - (self.tick % 30) * 0.7) # Falling oxygen saturation
            self.resp_rate = 36.0 + random.uniform(-2, 3) # Agonal rapid breathing
            self.resp_depth = 0.14 + random.uniform(-0.03, 0.03) # Very shallow
            self.gsr_level = min(22.0, 12.0 + (self.tick % 25) * 0.4)
            self.gsr_slope = 5.2 + random.uniform(-0.4, 0.6) # Cold sweat surge
            self.hrv_rmssd = max(6.0, 10.0 - (self.tick % 20) * 0.2) # Collapsed autonomic rhythm

        elif self.scenario == "artifact":
            # Sensor motion jiggle / loose strap
            self.motion_svm = 2.45 + random.uniform(-0.2, 0.2)
            self.hr = 85.0 + random.uniform(-15, 15)
            self.spo2 = 96.0
            self.resp_rate = 16.0
            self.resp_depth = 0.50
            self.gsr_level = 5.0
            self.gsr_slope = 0.1
            self.hrv_rmssd = 38.0

        # Evaluate TinyML Autoencoder
        norm_vec = self.normalize()
        mse, latent = self.evaluate_autoencoder(norm_vec)

        # Dynamic motion-adjusted threshold
        dyn_threshold = AE_THRESHOLD
        if self.motion_svm > 0.40:
            dyn_threshold *= (1.0 + 2.5 * (self.motion_svm - 0.40))

        is_motion_artifact = (self.motion_svm > 2.2)
        is_anomaly = (not is_motion_artifact) and (mse > dyn_threshold)
        risk_score = min(100.0, max(0.0, (mse / dyn_threshold) * 50.0))

        # Alert State Machine Update
        if self.alert_state == "NORMAL":
            if is_anomaly:
                self.alert_state = "STAGE_1"
                self.stage1_timer = self.STAGE1_DURATION

        elif self.alert_state == "STAGE_1":
            self.stage1_timer -= 1
            if self.stage1_timer <= 0:
                self.alert_state = "STAGE_2"
            elif not is_anomaly:
                # If physiological crisis spontaneously resolves before timeout
                pass

        return mse, dyn_threshold, risk_score, is_anomaly, is_motion_artifact, latent

    def cancel_alert(self):
        if self.alert_state in ["STAGE_1", "STAGE_2"]:
            self.alert_state = "ABORTED"
            return True
        return False

    def render_dashboard(self, mse, dyn_threshold, risk_score, is_anomaly, is_motion_artifact, latent):
        out = []
        out.append(f"{CLEAR}{BOLD}{CYAN}========================================================================================{RESET}")
        out.append(f"{BOLD}{CYAN}      CardioSense: Two-Node Embedded AI Wearable Real-Time Simulation Testbench         {RESET}")
        out.append(f"{BOLD}{CYAN}========================================================================================{RESET}")

        # Current scenario & status
        scen_labels = {
            "rest": f"{GREEN}[1] Normal Rest Baseline{RESET}",
            "exercise": f"{YELLOW}[2] Jogging / Exercise (Motion Gating Active){RESET}",
            "precursor": f"{RED}{BOLD}[3] CARDIAC ARREST PRECURSOR CRISIS{RESET}",
            "artifact": f"{CYAN}[4] Sensor Contact Artifact{RESET}"
        }
        out.append(f" Active Scenario: {scen_labels[self.scenario]} | Elapsed: {self.time_elapsed_sec}s")
        out.append(f" Controls: Type {BOLD}'1'{RESET} (Rest) | {BOLD}'2'{RESET} (Exercise) | {BOLD}'3'{RESET} (Precursor) | {BOLD}'4'{RESET} (Artifact) | {BOLD}'c'{RESET} (Cancel Alert) | {BOLD}'q'{RESET} (Quit)")
        out.append("----------------------------------------------------------------------------------------")

        # Telemetry columns
        col1 = f"Heart Rate (Wrist PPG):  {BOLD}{self.hr:5.1f} BPM{RESET}"
        col2 = f"Oxygen (SpO2):           {BOLD}{self.spo2:5.1f} %{RESET}"
        col3 = f"HRV RMSSD:               {BOLD}{self.hrv_rmssd:5.1f} ms{RESET}"
        col4 = f"Respiration Rate (Chest):{BOLD}{self.resp_rate:5.1f} BrPM{RESET}"
        col5 = f"Respiration Depth:       {BOLD}{self.resp_depth:5.2f}{RESET}"
        col6 = f"GSR Level (Cold Sweat):  {BOLD}{self.gsr_level:5.2f} uS{RESET}"
        col7 = f"GSR Slope (delta uS/min):{BOLD}{self.gsr_slope:+5.2f} uS/m{RESET}"
        col8 = f"Chest Motion SVM:        {BOLD}{self.motion_svm:5.3f} g{RESET}"

        out.append(f" {col1:<44} | {col2}")
        out.append(f" {col3:<44} | {col4}")
        out.append(f" {col5:<44} | {col6}")
        out.append(f" {col7:<44} | {col8}")
        out.append("----------------------------------------------------------------------------------------")

        # TinyML Anomaly Meter
        bar_len = 36
        ratio = min(1.0, mse / (dyn_threshold * 3.0))
        filled = int(ratio * bar_len)
        bar_color = RED if mse > dyn_threshold else GREEN
        meter = f"[{bar_color}{'#' * filled}{'-' * (bar_len - filled)}{RESET}]"

        out.append(f" {BOLD}TinyML Autoencoder Anomaly Detection:{RESET}")
        out.append(f" Reconstruction MSE: {mse:.6f}  Threshold: {dyn_threshold:.6f}  Meter: {meter}")
        out.append(f" Anomaly Risk Score: {BOLD}{risk_score:5.1f}%{RESET} | Motion Artifact Rejected: {BOLD}{'YES' if is_motion_artifact else 'NO'}{RESET}")
        out.append(f" Latent 2D Projection: z1={latent[0]:+.3f}, z2={latent[1]:+.3f}")
        out.append("----------------------------------------------------------------------------------------")

        # Alert State Box
        if self.alert_state == "NORMAL":
            out.append(f" {GREEN}{BOLD}[STATUS: NORMAL]{RESET} Physiological baseline stable. Continuous edge surveillance active.")
        elif self.alert_state == "STAGE_1":
            out.append(f" {YELLOW}{BOLD}[STATUS: STAGE 1 PRE-ALERT ACTIVATED!]{RESET}")
            out.append(f" >> Haptic pulsing (1 Hz) + Intermittent Audio Beeps active.")
            out.append(f" >> {BOLD}ABORT COUNTDOWN: {self.stage1_timer:02d} SECONDS REMAINING!{RESET} Press 'c' to cancel false alarm.")
        elif self.alert_state == "STAGE_2":
            out.append(f" {RED}{BOLD}[STATUS: STAGE 2 CRITICAL EMERGENCY ESCALATED!]{RESET}")
            out.append(f" >> High-decibel continuous local siren active!")
            out.append(f" >> {BOLD}[SIM800L GSM-SMS DISPATCHED]:{RESET}")
            sms_text = (
                f"    \"EMERGENCY: CardioSense Pre-Arrest Risk Alert!\n"
                f"     Vitals: HR={self.hr:.0f}bpm, SpO2={self.spo2:.0f}%, Resp={self.resp_rate:.0f}brpm, GSR_Slope={self.gsr_slope:+.1f}uS/m\n"
                f"     Location: https://maps.google.com/?q=12.9716,77.5946\""
            )
            out.append(sms_text)
            out.append(f" >> {BOLD}[SIM800L AUTOMATED VOICE CALL INITIATED]:{RESET} ATD+919876543210; -> Playing emergency alert tone pattern")
        elif self.alert_state == "ABORTED":
            out.append(f" {CYAN}{BOLD}[STATUS: ALARM ABORTED BY USER]{RESET} Bystander/Patient canceled countdown. Returning to baseline.")

        out.append(f"{BOLD}{CYAN}========================================================================================{RESET}")
        print("\n".join(out))

def main():
    sim = CardioSimulator()
    print("Initializing CardioSense testbench...")
    time.sleep(1)

    import msvcrt # Windows non-blocking input

    try:
        while sim.running:
            # Check non-blocking keyboard input
            if msvcrt.kbhit():
                ch = msvcrt.getch().decode("utf-8", errors="ignore").lower()
                if ch == '1':
                    sim.scenario = "rest"
                    if sim.alert_state == "ABORTED":
                        sim.alert_state = "NORMAL"
                elif ch == '2':
                    sim.scenario = "exercise"
                elif ch == '3':
                    sim.scenario = "precursor"
                elif ch == '4':
                    sim.scenario = "artifact"
                elif ch == 'c':
                    sim.cancel_alert()
                elif ch == 'q':
                    sim.running = False
                    break

            mse, dyn_th, risk, is_ano, is_art, latent = sim.update_physiology()
            sim.render_dashboard(mse, dyn_th, risk, is_ano, is_art, latent)
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass

    print("\nSimulation stopped.")

if __name__ == "__main__":
    main()
