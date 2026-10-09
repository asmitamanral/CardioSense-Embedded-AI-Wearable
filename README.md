# CardioSense: Two-Node Embedded AI Wearable for Early Cardiac Arrest Precursor Detection

CardioSense is a distributed, privacy-preserving embedded AI wearable that detects precursor indicators of sudden cardiac arrest (such as ventricular arrhythmias, acute hypoxia, sudden cold sweat surges, and labored breathing) minutes before collapse occurs.

```
       [ Wrist Node: Slap-Band ]
       • MAX30102 PPG (Heart Rate, SpO2)
       • Grove GSR (Skin Conductance / Cold Sweats)
       • ESP32-WROOM-32 (BLE Peripheral)
                  │
                  │ BLE 5.0 (20 Hz Streaming)
                  ▼
   ┌────────────────────────────────────────────────────────┐
   │       Sternum Hub Node: Locket (Central Coordinator)    │
   │ ────────────────────────────────────────────────────── │
   │ • MPU6050 6-Axis IMU (Chest Respiration & Motion Gate) │
   │ • Secondary MAX30102 PPG (Sternal Pulse / PAT)         │
   │ • Dual-Core ESP32-WROOM-32 Central MCU                 │
   │   - Core 0: BLE Receiver & I2C Sensor Acquisition      │
   │   - Core 1: 10s DSP Ring Buffer & TinyML Autoencoder   │
   │ • Peripherals:                                         │
   │   - 1 Hz Haptic Motor & Dual-Frequency Piezo Siren     │
   │   - Momentary Tactile Push-to-Cancel Button            │
   │   - SIM800L GSM Modem (Location SMS & Voice Call)      │
   │   - u-blox Neo-6M GPS Module                           │
   └──────────────────────────┬─────────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        [ Stage 1 Alert ]          [ Stage 2 Alert ]
        30s Haptic + Audio         High-Decibel Siren +
        Countdown (Abortable)      Location-Tagged SMS +
                                   Automated EMS Voice Call
```

---

## Repository Structure

```
CardioSense/
├── firmware/
│   ├── wrist_node/
│   │   └── wrist_node.ino            # ESP32 BLE peripheral sampling MAX30102 & GSR
│   └── sternum_hub/
│       ├── sternum_hub.ino           # ESP32 BLE central coordinator (Dual-Core FreeRTOS)
│       ├── cardio_features.h         # 10-second DSP sliding-window feature extractor
│       ├── autoencoder_engine.h      # Ultra-fast zero-dependency C++ TinyML inference engine
│       ├── model_weights.h           # Pre-trained Autoencoder weights & baseline thresholds
│       └── emergency_alert.h         # Two-stage alert state machine with SIM800L SMS & Call
├── ml_pipeline/
│   ├── synthetic_physiology_generator.py # Physiological trajectory generator (Normal vs Precursor)
│   ├── train_autoencoder.py          # Autoencoder trainer (NumPy + Adam), evaluator, and C header exporter
│   ├── model_meta.json               # Trained model metrics (71x error separation, 100% sensitivity)
│   └── model_weights.h               # Exported C header weights
├── simulation/
│   ├── simulator.py                  # Interactive CLI testbench with live ANSI telemetry dashboard
│   ├── dashboard.html                # Interactive Generative UI / HTML5 monitor with animated waveforms
│   └── test_simulator.py             # Automated unit & integration tests (5/5 passing)
└── docs/
    ├── hardware_bom_and_pinout.md    # Complete Indian market BOM (~₹3,400 / $40) & ESP32 pinouts
    └── system_architecture.md        # Comprehensive clinical rationale, DSP, and TinyML math
```

---

## Quick Start & Verification

### 1. Run the Interactive Web Dashboard
Simply double-click or open [`simulation/dashboard.html`](file:///c:/Users/Lenovo/OneDrive/Documents/CardioSense/simulation/dashboard.html) in any modern web browser:
- Watch live animated waveforms for **Wrist PPG**, **Chest Respiration (IMU)**, and **Galvanic Skin Conductance**.
- Click **"3. Sudden Cardiac Arrest Precursor"** to simulate acute multi-signal divergence.
- Observe the **Autoencoder Reconstruction Error (MSE)** surge, triggering the **Stage 1 (30s Countdown)**.
- Test the **"Push-to-Cancel"** button to abort false alarms or let the timer expire to witness the simulated **SIM800L Emergency SMS and Voice Call dispatch**!

### 2. Run the Command-Line Testbench
```bash
cd CardioSense/simulation
python simulator.py
```
- Press `1` for Resting Baseline
- Press `2` for Jogging / Exercise (verifies motion artifact rejection)
- Press `3` for Acute Precursor Crisis
- Press `c` to abort pre-alert

### 3. Retrain the TinyML Autoencoder Model
```bash
cd CardioSense/ml_pipeline
python train_autoencoder.py
```
- Trains an $8 \to 4 \to 2 \to 4 \to 8$ Autoencoder.
- Achieves **100% precursor sensitivity** and **99% specificity**.
- Automatically regenerates `model_weights.h` in `firmware/sternum_hub/`.

### 4. Uploading Firmware to ESP32 Hardware
1. Open the [Arduino IDE](https://www.arduino.cc/en/software).
2. Install the **esp32 by Espressif Systems** board package (`Tools > Board > Boards Manager`).
3. Flash [`wrist_node.ino`](file:///c:/Users/Lenovo/OneDrive/Documents/CardioSense/firmware/wrist_node/wrist_node.ino) to your Wrist ESP32 board.
4. Flash [`sternum_hub.ino`](file:///c:/Users/Lenovo/OneDrive/Documents/CardioSense/firmware/sternum_hub/sternum_hub.ino) to your Sternum ESP32 board.
5. Refer to [`docs/hardware_bom_and_pinout.md`](file:///c:/Users/Lenovo/OneDrive/Documents/CardioSense/docs/hardware_bom_and_pinout.md) for exact GPIO wiring tables.
