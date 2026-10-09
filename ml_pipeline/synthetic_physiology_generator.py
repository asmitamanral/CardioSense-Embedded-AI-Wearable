"""
CardioSense: Synthetic Physiological Dataset Generator
Generates clinically grounded physiological trajectories for:
1. Normal Quiescent Baseline (Resting, desk work, sleeping)
2. Normal Physical Exertion (Walking, jogging, stair climbing)
3. Acute Cardiac Arrest Precursor Crisis (Sympathetic surge, hypoxia, cold sweat, agonal respiration at rest)
4. Transient Motion Artifacts
"""

import numpy as np
import json
import os

FEATURE_NAMES = [
    "hr",          # BPM (40 - 200)
    "hrv_rmssd",   # ms (5 - 120)
    "spo2",        # % (70 - 100)
    "resp_rate",   # BrPM (6 - 45)
    "resp_depth",  # index (0.05 - 1.0)
    "gsr_level",   # uS (0.5 - 25.0)
    "gsr_slope",   # uS/min (-2.0 - 8.0)
    "motion_svm"   # g (0.0 - 2.5)
]

BOUNDS = {
    "hr": (40.0, 200.0),
    "hrv_rmssd": (5.0, 120.0),
    "spo2": (70.0, 100.0),
    "resp_rate": (6.0, 45.0),
    "resp_depth": (0.05, 1.0),
    "gsr_level": (0.5, 25.0),
    "gsr_slope": (-2.0, 8.0),
    "motion_svm": (0.0, 2.5)
}

def normalize_features(data_matrix):
    """Normalize [N, 8] matrix to [0.0, 1.0] using defined bounds."""
    norm = np.zeros_like(data_matrix, dtype=np.float32)
    for i, name in enumerate(FEATURE_NAMES):
        low, high = BOUNDS[name]
        norm[:, i] = np.clip((data_matrix[:, i] - low) / (high - low), 0.0, 1.0)
    return norm

def denormalize_features(norm_matrix):
    """Denormalize [N, 8] matrix back to clinical units."""
    raw = np.zeros_like(norm_matrix, dtype=np.float32)
    for i, name in enumerate(FEATURE_NAMES):
        low, high = BOUNDS[name]
        raw[:, i] = norm_matrix[:, i] * (high - low) + low
    return raw

def generate_normal_baseline(n_samples=5000, seed=42):
    """
    Generates normal everyday physiological states:
    - 65% Resting/Sedentary
    - 25% Routine activity (walking, household tasks)
    - 10% Aerobic exercise (jogging, climbing) with matched motion
    """
    rng = np.random.default_rng(seed)
    data = np.zeros((n_samples, len(FEATURE_NAMES)), dtype=np.float32)

    for i in range(n_samples):
        activity_type = rng.choice(["rest", "routine", "exercise"], p=[0.65, 0.25, 0.10])

        if activity_type == "rest":
            hr = rng.normal(70.0, 6.0)
            hrv = rng.normal(45.0, 10.0)
            spo2 = rng.normal(98.2, 0.8)
            resp_rate = rng.normal(14.0, 2.0)
            resp_depth = rng.normal(0.40, 0.08)
            gsr_level = rng.normal(4.2, 1.2)
            gsr_slope = rng.normal(0.02, 0.15)
            motion_svm = rng.exponential(0.04)

        elif activity_type == "routine":
            hr = rng.normal(86.0, 9.0)
            hrv = rng.normal(32.0, 8.0)
            spo2 = rng.normal(97.8, 1.0)
            resp_rate = rng.normal(18.0, 3.0)
            resp_depth = rng.normal(0.55, 0.10)
            gsr_level = rng.normal(6.5, 1.8)
            gsr_slope = rng.normal(0.15, 0.35)
            motion_svm = rng.normal(0.35, 0.12)

        else: # exercise
            motion_svm = rng.normal(1.20, 0.30)
            hr = 100.0 + motion_svm * 35.0 + rng.normal(0, 8.0) # HR tightly coupled to motion
            hrv = max(15.0, 45.0 - motion_svm * 18.0 + rng.normal(0, 5.0))
            spo2 = rng.normal(97.0, 1.2) # Oxygen preserved in healthy exercise
            resp_rate = 16.0 + motion_svm * 12.0 + rng.normal(0, 3.0)
            resp_depth = min(0.95, 0.50 + motion_svm * 0.25)
            gsr_level = rng.normal(9.5, 2.5) # Thermal sweating
            gsr_slope = rng.normal(0.40, 0.30)

        # Clip values to realistic ranges
        data[i, 0] = np.clip(hr, 45.0, 185.0)
        data[i, 1] = np.clip(hrv, 10.0, 110.0)
        data[i, 2] = np.clip(spo2, 93.0, 100.0)
        data[i, 3] = np.clip(resp_rate, 8.0, 40.0)
        data[i, 4] = np.clip(resp_depth, 0.15, 0.98)
        data[i, 5] = np.clip(gsr_level, 1.0, 20.0)
        data[i, 6] = np.clip(gsr_slope, -1.5, 3.0)
        data[i, 7] = np.clip(motion_svm, 0.0, 2.2)

    return data

def generate_cardiac_precursors(n_samples=1000, seed=101):
    """
    Generates acute sudden cardiac arrest precursor scenarios:
    - Pre-arrest Ventricular Tachycardia (extreme HR, low HRV, falling SpO2, diaphoresis)
    - Acute Ischemia / Cardiogenic shock (bradycardia or extreme tachycardia, plummeting SpO2, severe cold sweat)
    - Agonal / labored shallow breathing while sedentary (near-zero motion)
    """
    rng = np.random.default_rng(seed)
    data = np.zeros((n_samples, len(FEATURE_NAMES)), dtype=np.float32)

    for i in range(n_samples):
        crisis_type = rng.choice(["ventricular_tachycardia", "ischemic_collapse", "agonal_shock"], p=[0.45, 0.35, 0.20])

        if crisis_type == "ventricular_tachycardia":
            hr = rng.normal(165.0, 15.0)       # Acute tachycardia
            hrv = rng.normal(9.0, 2.5)          # Collapsed HRV
            spo2 = rng.normal(84.0, 4.0)        # Hypoperfusion / dropping oxygenation
            resp_rate = rng.normal(34.0, 5.0)   # Tachypnea (labored breathing)
            resp_depth = rng.normal(0.18, 0.06) # Shallow respiration
            gsr_level = rng.normal(17.5, 3.0)   # Profuse cold sweating
            gsr_slope = rng.normal(4.8, 1.2)    # Rapid surge in skin conductance
            motion_svm = rng.exponential(0.08)  # Minimal or zero motion (crucial discriminator!)

        elif crisis_type == "ischemic_collapse":
            hr = rng.normal(42.0, 5.0)          # Severe sudden bradycardia / heart block
            hrv = rng.normal(7.0, 2.0)
            spo2 = rng.normal(78.0, 5.0)        # Severe cyanosis / hypoxia
            resp_rate = rng.normal(10.0, 3.0)   # Depressed erratic respiration
            resp_depth = rng.normal(0.12, 0.04)
            gsr_level = rng.normal(19.0, 2.8)   # Cold, clammy skin
            gsr_slope = rng.normal(5.2, 1.0)
            motion_svm = rng.exponential(0.05)  # Patient is stationary or slumping

        else: # agonal shock
            hr = rng.normal(148.0, 18.0)
            hrv = rng.normal(8.0, 2.0)
            spo2 = rng.normal(75.0, 4.5)
            resp_rate = rng.normal(38.0, 4.0)   # Agonal gasping pattern
            resp_depth = rng.normal(0.15, 0.05)
            gsr_level = rng.normal(16.0, 2.5)
            gsr_slope = rng.normal(4.0, 1.1)
            motion_svm = rng.exponential(0.12)

        data[i, 0] = np.clip(hr, 35.0, 200.0)
        data[i, 1] = np.clip(hrv, 5.0, 25.0)
        data[i, 2] = np.clip(spo2, 68.0, 89.0)
        data[i, 3] = np.clip(resp_rate, 6.0, 45.0)
        data[i, 4] = np.clip(resp_depth, 0.05, 0.35)
        data[i, 5] = np.clip(gsr_level, 12.0, 24.5)
        data[i, 6] = np.clip(gsr_slope, 2.5, 7.8)
        data[i, 7] = np.clip(motion_svm, 0.0, 0.35) # Near zero motion during collapse

    return data

if __name__ == "__main__":
    print("Generating CardioSense physiological datasets...")
    normal_data = generate_normal_baseline(6000)
    precursor_data = generate_cardiac_precursors(1500)

    os.makedirs("data", exist_ok=True)
    np.save("data/normal_physiology.npy", normal_data)
    np.save("data/cardiac_precursors.npy", precursor_data)
    print(f"Saved: {normal_data.shape[0]} normal baseline samples and {precursor_data.shape[0]} precursor crisis samples.")
