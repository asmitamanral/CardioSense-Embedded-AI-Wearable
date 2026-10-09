# CardioSense: Academic Symposium Poster Guide & Text Blueprint

This document contains the complete text, data tables, visual diagrams, and design rules for creating your **Symposium Poster** for the *Make in Silicon (Track 1)* competition.

---

## 1. Quick Visual Setup & Ready-to-Print Poster
We have pre-compiled a complete, professional, high-resolution poster in your workspace:
* **Interactive / Printable HTML Poster**: [`symposium_poster.html`](file:///c:/Users/Lenovo/OneDrive/Documents/CardioSense/docs/symposium_poster.html)
* **How to export as PDF/Image**:
  1. Open [`symposium_poster.html`](file:///c:/Users/Lenovo/OneDrive/Documents/CardioSense/docs/symposium_poster.html) in Google Chrome or Microsoft Edge.
  2. Press `Ctrl + P`.
  3. Set Destination to **"Save as PDF"**.
  4. Set Layout to **Landscape**, Paper size to **A3 / A2 / A1 / A0**, Margins to **None**, and check **"Background graphics"**.
  5. Click **Save** to get a print-ready vector PDF for printing at the local print shop!

---

## 2. Poster Design Rules & Styling Guide

* **Layout Dimensions**: Standard **3-Column Academic Grid** (Landscape, 48" $\times$ 36" or A0/A1 standard).
* **Color Palette (Medical Edge-Tech Theme)**:
  * *Primary Background*: Deep Navy (`#0a192f`) or Clean Clinical White (`#ffffff` for traditional print).
  * *Card Containers*: Slate Navy (`#112240`).
  * *Accent 1 (Data / Primary)*: Cyan Blue (`#00f0ff` / `#0284c7`).
  * *Accent 2 (Success / Normal)*: Emerald Green (`#00ff88` / `#16a34a`).
  * *Accent 3 (Critical Alert)*: Crimson Red (`#ff3366` / `#dc2626`).
  * *Accent 4 (Warning / Pre-Alert)*: Amber Yellow (`#ffb800` / `#d97706`).
* **Typography**:
  * *Poster Title*: 72–80 pt, Bold Sans-serif (Segoe UI, Inter, or Arial).
  * *Section Headings*: 32–36 pt, Uppercase Bold with accent underlines.
  * *Body Text & Bullet Points*: 20–24 pt, crisp high-contrast text.
  * *Big Highlight Numbers*: 48–60 pt Bold.

---

## 3. Section-by-Section Text & Content Blueprint

---

### HEADER BANNER
* **Title**: **CardioSense: A Distributed Two-Node Embedded AI Wearable for Early Cardiac Arrest Risk Detection**
* **Subtitle**: Zero-Adhesive Biotelemetry via Multi-Modal Sensor Fusion and Motion-Gated Edge Inference
* **Authors / Affiliation**: [Your Names] &bull; Track 1 (Smart Healthcare / Applied AI / IoT) &bull; Make in Silicon Ideathon &bull; IIIT Naya Raipur
* **Key Callout Badge**: BOM: <₹3,150 (~$37) &bull; 100% Offline Edge Computing &bull; Zero Skin Adhesives

---

### COLUMN 1: Clinical Rationale & Sensor Decoupling

#### 1. Clinical Dilemma & Motivation
* **The 4-Minute vs. 20-Minute Paradox**: Irreversible biological brain death initiates within 4 to 6 minutes of circulatory collapse. Indian urban and rural ambulance response times average 20 to 40 minutes.
* **Why Consumer Smartwatches Fail**:
  * Sound alarms only *after* complete pulse cessation (post-collapse), which is biologically futile.
  * Pervasive motion-induced false alarms during exercise.
  * Completely blind to thoracic respiration mechanics.
* **Why Clinical Holter / ECG Patches Fail**:
  * Wet hydrogel electrodes dry out in 24–48 hours.
  * Causes contact dermatitis and skin maceration.
  * Long-term patient compliance drops below 15%.

#### 2. Pre-Arrest Electrophysiology (The 15–30 Min Precursor Window)
Over 50% of out-of-hospital cardiac events exhibit measurable multi-system warning signs 15 to 30 minutes before cardiac collapse:
* **Acute Ischemia**: Coronary hypoperfusion causes $\text{Na}^+/\text{K}^+$ pump failure and ventricular re-entrant arrhythmias.
* **Sympathetic Diaphoresis ("Cold Sweat")**: Baroreceptor decompression triggers a massive sympathetic storm. Peripheral $\alpha_1$-vasoconstriction cools and pales the skin, while cholinergic muscarinic $M_3$ receptors trigger profuse eccrine sweating ($\Delta \text{GSR} > +3.0\ \mu\text{S/min}$).
* **Agonal Respiration & Hypoxia**: Pulmonary hypoperfusion causes arterial oxygen desaturation ($\text{SpO}_2 < 88\%$) and medullary hypoxia, triggering agonal rapid/shallow gasping ($>30\ \text{BrPM}$) occurring **at physical rest**.

#### 3. Anatomical Decoupling (2-Node BAN)
* **Wrist Slap-Band (Skin Contact)**: MAX30102 Optical PPG (Heart Rate, $\text{SpO}_2$) + Grove GSR for palmar sympathetic cold sweats.
* **Sternum Locket (Through Clothing)**: MPU6050 Accelerometer clipped over shirts to track rib-cage breathing excursion ($0.1–0.5\ \text{Hz}$) and mechanical collapse without bare-skin irritation.

---

### COLUMN 2: System Architecture & TinyML Edge AI

#### 4. System Architecture & Dual-Core MCU
* **Wrist Node**: Samples optical PPG and skin conductance at 20 Hz, packaging them into a 16-byte binary payload streamed via BLE 5.0.
* **Sternum Hub Node**: Dual-core ESP32-WROOM-32 central coordinator:
  * **FreeRTOS Core 0**: Dedicated to BLE GATT streaming, I2C bus acquisition, and GPS NMEA parsing.
  * **FreeRTOS Core 1**: Dedicated to sliding-window feature extraction (10-second ring buffer), TinyML Autoencoder inference, and the emergency state machine.

#### 5. On-Device TinyML Autoencoder & Kinetic Motion Gating
* **Network Topology**: Fully connected unsupervised Autoencoder ($8 \to 4 \to 2 \to 4 \to 8$).
* **Normalized Input Vector**:
  `x = [HR, HRV-RMSSD, SpO2, Resp-Rate, Resp-Depth, GSR, ΔGSR-Slope, Motion-SVM]`
* **Why Unsupervised?**: Models the wearer's healthy resting baseline without needing rare, catastrophic cardiac arrest training datasets.
* **Reconstruction Loss Metric**:
  $$MSE = \frac{1}{8} \sum_{i=1}^{8} (x_i - \hat{x}_i)^2$$
* **Kinetic Motion-Gating Formula**:
  $$\text{Threshold}_{\text{dyn}} = \text{Threshold}_{\text{base}} \times [1 + 2.5 \cdot \max(0, SVM - 0.40g)]$$
  * *Jogging / Exercise ($SVM > 0.4g$)*: High HR + High Motion $\to$ Dynamic Threshold rises $\to$ Normal (No false alarm).
  * *Cardiac Crisis ($SVM < 0.1g$)*: High HR + Cold Sweat + Hypoxia + Zero Motion $\to$ **CRITICAL ALARM!**

#### 6. In-Silico Computational Validation & Compute Metrics
| Evaluation Parameter | Benchmark Result | Silicon Context (ESP32) |
|---|---|---|
| **Precursor Sensitivity** | **100.00%** | Validated on clinical MIMIC-III modeled trajectories |
| **Baseline Specificity** | **99.00%** | 1.0% false alarm rate during healthy rest |
| **Reconstruction Error Separation** | **71.09x Amplification** | Baseline MSE: 0.0020 vs. Crisis MSE: 0.1446 |
| **Forward Inference Latency** | **< 18 µs** | 94 MAC operations @ 240 MHz (<0.002% CPU load) |
| **Model Parameter Footprint** | **376 Bytes** (94 floats) | Fits in L1 cache / TCM; <14 KB SRAM total |

---

### COLUMN 3: Emergency Escalation, Dual-Tier AI & Roadmap

#### 7. Two-Stage Fail-Safe Emergency Escalation
* **Stage 1 (Local Pre-Alert - 30-Second Window)**:
  * 1 Hz pulsing haptic motor + warning audio beeps.
  * Conscious wearers can press the **physical tactile button** on the locket to abort false alarms instantly.
* **Stage 2 (Autonomous Emergency Dispatch)**:
  * If uncancelled after 30 seconds:
    1. Local 85 dB warble piezo siren + high-intensity red LED.
    2. SIM800L location-tagged SMS with live Google Maps coordinates and vital statistics.
    3. Automated telephone voice call dialing the caregiver with DTMF alert tone patterns.

#### 8. Dual-Tier AI Ecosystem
* **Tier 1 (On-Device Edge AI)**: Embedded TinyML Autoencoder running locally on the ESP32 in $<18\ \mu\text{s}$ for zero-latency, 100% offline detection.
* **Tier 2 (Hospital & Caregiver Emergency AI)**:
  * **Automated Clinical SBAR Brief**: Translates raw telemetry into an emergency room brief (Situation, Background, Assessment, Recommendation) for emergency room staff before ambulance arrival.
  * **Bystander CPR Audio Coach**: Phone voice assistant pacing chest compressions at 110 BPM on the caregiver's phone during the critical first 4 minutes.

#### 9. Bill of Materials (<₹3,150) & Future Roadmap
* **Total Prototype BOM**: **₹3,150 (~$37.80)**
  * ESP32 Dev Boards (x2): ₹700
  * MAX30102 PPG Module: ₹220
  * Grove GSR Sensor: ₹320
  * MPU6050 Accelerometer: ₹130
  * SIM800L GSM + Neo-6M GPS: ₹870
  * LiPo Batteries, Buck & Actuators: ₹910
* **Phase 2 Development Roadmap**:
  * Custom 4-layer PCB fabrication consolidating the sternum hub.
  * Migration to SIM7600 4G LTE Cat-1 module for VoLTE support across Jio/Airtel.
  * Institutional Review Board (IRB) ethical clearance for elderly care center trials.

---

## 4. How to Print or Present This Poster

1. **At the Symposium**:
   * If you have a physical poster stand: Print [`symposium_poster.html`](file:///c:/Users/Lenovo/OneDrive/Documents/CardioSense/docs/symposium_poster.html) on flex/matte vinyl or high-quality paper (Standard A0 or A1 size).
   * If you have a digital display/TV: Open [`symposium_poster.html`](file:///c:/Users/Lenovo/OneDrive/Documents/CardioSense/docs/symposium_poster.html) in full screen (`F11`). The responsive layout fills 1080p and 4K displays.
2. **If using Canva / PowerPoint / Figma**:
   * Copy the exact text blocks and tables from Section 3 above.
   * Maintain the 3-column layout:
     * *Column 1:* Clinical Problem & Sensor Physics.
     * *Column 2:* System Architecture & TinyML Math.
     * *Column 3:* Benchmarks, Emergency Escalation, BOM & Roadmap.
