# CardioSense: Abstract & Technical Proposal

> **Registration ID:** 27198  
> **Track:** Track 1: Smart Innovation in AI with Embedded Platform  
> **Event:** MakeInSilicon 2026 Ideathon — IIIT Naya Raipur (IIITNR)  
> **Team Code Blue:** Asmita Manral (Lead), Nikhil Gavel, Gautam Batra  
> **Affiliation:** Dr. Shyama Prasad Mukherjee International Institute of Information Technology, Naya Raipur (DSPM IIITNR)  

---

## 1. Project Title
**CardioSense: A Distributed Two-Node Embedded AI Wearable for Pre-Arrest Cardiac Anomaly Detection via Multi-Modal Sensor Fusion and Motion-Gated Edge Inference**

---

## 2. Executive Summary / Abstract (250 Words)
Sudden Cardiac Arrest (SCA) claims over 350,000 lives annually in out-of-hospital environments, with an out-of-hospital survival rate below 5% in developing regions such as India where emergency medical response times average 20–40 minutes. Existing consumer wearables predominantly rely on a single wrist photoplethysmography (PPG) channel, alerting users only *after* complete pulse loss has occurred, while suffering from pervasive motion-induced false alarms. 

We propose **CardioSense**, a distributed two-node embedded AI wearable designed to catch the 15-to-30 minute precursor window before cardiac collapse. The system separates sensors into physiologically optimal sites: a self-fitting wrist slap-band housing an optical PPG sensor (Heart Rate, $\text{SpO}_2$) and a Galvanic Skin Response (GSR) sensor (autonomic cold sweat diaphoresis); and a clothing-clipped sternum locket housing an MPU6050 6-axis IMU for chest-wall respiration rate/depth detection through clothing, as well as automated mechanical fall/collapse detection (`free-fall` $\to$ `impact` $\to$ `prolonged stillness`). 

Both nodes stream synchronized telemetry at 20 Hz via Bluetooth Low Energy (BLE) to an on-device dual-core ESP32 processor running an unsupervised TinyML Autoencoder anomaly detection model ($8 \to 4 \to 2 \to 4 \to 8$). The system personalizes to each wearer's physiological baseline and employs a kinetic motion gate to differentiate genuine cardiac distress from vigorous exercise. On detecting sustained pre-arrest discordance, a deterministic two-stage alarm sounds a 30-second abortable local alert before dispatching a location-tagged emergency SMS and automated cellular voice call via SIM800L. Operating 100% offline with a total BOM under ₹3,150 ($37), CardioSense provides an accessible, privacy-preserving lifesaver for mass deployment.

---

## 3. Problem Statement & Clinical Gap
1. **The "Post-Arrest" Fallacy**: The human brain experiences irreversible biological death within 4 to 6 minutes of complete circulatory cessation. Smartwatches detecting pulse loss trigger emergency services far too late to beat rural or urban transit delays.
2. **The "Wrist Fallacy"**: Wrist-only devices cannot measure chest-wall respiratory expansion and are heavily susceptible to hand-motion artifacts, leading to rampant false alarms and alert fatigue.
3. **The Precursor Opportunity**: Clinical electrophysiology indicates that $>50\%$ of out-of-hospital cardiac events are preceded by multi-system warning signs 15 to 30 minutes prior: acute arrhythmias (ventricular tachycardia / bradycardia), systemic arterial oxygen desaturation ($\text{SpO}_2 < 88\%$), sympathetic autonomic surge causing cold diaphoresis ($\Delta \text{GSR} > +3.0\ \mu\text{S/min}$), and agonal/shallow respiration occurring **while the patient is physically at rest**.

---

## 4. Proposed Solution & System Architecture

```
 [ NODE 1: WRIST SLAP-BAND ]             [ NODE 2: STERNUM LOCKET (HUB) ]
 • MAX30102 PPG (HR, SpO2)               • MPU6050 IMU (Chest Respiration Waveform)
 • Grove GSR (Cold Sweats / EDA)         • Dual-Use Fall Detection (Impact > 3.0g)
 • ESP32 BLE Peripheral (20 Hz)          • Sensed Through Clothing (Zero Adhesives)
                                         • Dual-Core ESP32 Central + TinyML Engine
                     │                   • SIM800L Cellular Modem + Neo-6M GPS
                     └────────► BLE 5.0 ─────────►│
                                                 ▼
                                     [ Sliding-Window DSP Buffer ]
                                                 │
                                                 ▼
                                     [ Motion-Gated TinyML Autoencoder ]
                                                 │
                                 ┌───────────────┴───────────────┐
                                 ▼                               ▼
                       [ Stage 1: Pre-Alert ]          [ Stage 2: Escalation ]
                       30s Local Haptic + Tone         High-Decibel Siren +
                       Push-to-Cancel Button           GPS SMS & Voice Call
```

### A. Anatomical Decoupling (Wrist vs. Chest)
* **Wrist Slap-Band (Optical & Electrodermal)**: The flexible slap-band format provides self-tensioning, repeatable contact pressure against the radial artery and palmar sweat glands without requiring skin adhesives.
* **Sternum Locket (Biomechanical & Communication Hub)**: Clipped to clothing over the sternal bone with a breakaway safety lanyard. The MPU6050 accelerometer isolates cyclic sternal excursion ($0.1–0.5\ \text{Hz}$) through clothing, measuring respiration rate and depth without bare-skin irritation.

### B. Dual-Core FreeRTOS Task Allocation (ESP32-WROOM-32)
* **Core 0**: Dedicated to BLE GATT reception, I2C acquisition, and GPS NMEA parsing.
* **Core 1**: Dedicated to sliding-window feature extraction (10-second ring buffer), TinyML Autoencoder inference, and the emergency state machine.

### C. On-Device TinyML Autoencoder & Kinetic Motion Gating
Rather than relying on rare, brittle labeled cardiac arrest datasets, an unsupervised Autoencoder ($8 \to 4 \to 2 \to 4 \to 8$) learns the manifold of the wearer’s healthy resting baseline:
* **8 Features Fused**: Mean Heart Rate, HRV RMSSD, $\text{SpO}_2$, Respiration Rate, Respiration Depth, GSR Level, GSR Delta Slope, and Motion Signal Vector Magnitude ($SVM$).
* **Kinetic Motion Gate**: During vigorous running ($SVM > 0.40g$), physiological arousal is expected; the decision threshold scales dynamically ($\text{Th}_{\text{dyn}} = \text{Th}_{\text{base}} \times [1 + 2.5(SVM - 0.40)]$). A critical alarm is only flagged when multi-signal discordance occurs **without physical exertion** (quiescent or collapsed posture).

### D. Dual-Stage Fail-Safe Emergency Escalation
* **Stage 1 (Local Pre-Alert)**: $1\ \text{Hz}$ haptic vibration + intermittent audio beeps for 30 seconds. A physical tactile push-button allows conscious wearers to abort false alarms instantly.
* **Stage 2 (Autonomous Dispatch)**: If uncancelled after 30 seconds, an 85dB continuous siren activates, followed by a SIM800L location-tagged SMS with Google Maps coordinates and vital statistics, accompanied by an automated caregiver voice call.

### E. Dual-Tier AI Integration (Emergency Handoff)
* **Tier 1 (On-Device Edge AI)**: Embedded Autoencoder on the ESP32 for deterministic, zero-latency precursor detection.
* **Tier 2 (Hospital & Caregiver AI)**:
  1. **Automated Clinical SBAR Report**: Converts raw telemetry into an emergency room brief (Situation, Background, Assessment, Recommendation) for emergency room staff before ambulance arrival.
  2. **Interactive Bystander CPR Audio Coach**: Mobile voice assistant pacing chest compressions at 100–120 BPM on the caregiver's phone during the critical first 4 minutes.

---

## 5. Key Novelty & Competitive Advantage

| Feature | Standard Smartwatches (Apple / Samsung) | Wearable Defibrillators (Zoll LifeVest) | CardioSense (Our Proposal) |
|---|---|---|---|
| **Detection Window** | Post-arrest only (pulse loss) | Post-ventricular fibrillation | **Pre-arrest early warning (15–30 min)** |
| **Sensor Sites** | Single site (Wrist only) | Chest only | **Two-node distributed (Wrist + Sternum)** |
| **Respiration & Sweat** | None / Inaccurate PPG surrogate | None | **Direct IMU chest-wall wave + Wrist GSR** |
| **Motion Gating** | Vulnerable to exercise false alarms | High false alarm rate | **Dynamic IMU multi-signal cross-check** |
| **Connectivity** | Requires smartphone + cloud | Proprietary base station | **100% On-Device & Offline via GSM** |
| **Cost** | ₹30,000 – ₹80,000 ($350–$900) | >₹2,50,000 / month (Rental) | **< ₹3,150 ($37 total BOM)** |

---

## 6. Validation Methodology (In-Silico Simulation & Analytical Benchmarking)
In accordance with ethical research practices prior to clinical trials, the system was validated using an **in-silico computational simulation pipeline**:
* **Dataset Modeling**: The TinyML Autoencoder was trained and evaluated on physiological trajectories modeled on clinical bounds from the MIMIC-III database and cardiology literature.
* **Reconstruction Error Separation**: In simulation, normal baseline MSE was $0.002034$ vs. precursor crisis MSE of $0.144579$ (**$71.09\times$ error amplification**), yielding **$100.00\%$ sensitivity** and **$99.00\%$ specificity**.
* **Silicon Compute Benchmark**: Analytically verified on the dual-core ESP32 Xtensa LX6 architecture: **376 Bytes** model parameter footprint, executing in **$<18\ \mu\text{s}$** ($94\ \text{MAC}$ operations) with **$<14\ \text{KB}$ SRAM** utilization.

---

## 7. Bill of Materials & Economic Feasibility

| Component | Function | Indian Market Cost (INR) |
|---|---|:---:|
| **ESP32-WROOM-32 Dev Boards (x2)** | Dual-Core BLE Central & Peripheral MCUs | ₹700 |
| **MAX30102 PPG Module (Wrist)** | Radial artery pulse & $\text{SpO}_2$ | ₹220 |
| **Grove GSR Skin Conductance Module** | Autonomic cold sweat detection | ₹320 |
| **MPU-6050 6-Axis IMU (Sternum)** | Chest respiration & fall detection | ₹130 |
| **SIM800L Cellular Modem** | Offline SMS & automated telephony | ₹450 |
| **u-blox Neo-6M GPS Module** | Emergency coordinate acquisition | ₹420 |
| **LiPo Batteries + TP4056 + Buck** | Power supply & GSM 2A current buffering | ₹700 |
| **Haptic, Buzzer, Button & Casing** | Actuators & mechanical strap/lanyard | ₹210 |
| **TOTAL PROTOTYPE BOM** | | **₹3,150 (~$37.80)** |

---

## 8. Societal & Healthcare Impact
CardioSense directly addresses India's high burden of out-of-hospital cardiovascular mortality, particularly in elderly individuals living alone, remote tier-2/3 towns lacking rapid EMS infrastructure, and high-risk patients post-myocardial infarction. Because all computation is on-device and relies on standard 2G/3G GSM rather than 4G data subscriptions or smartphone pairing, it remains accessible across socioeconomic strata while preserving patient data privacy.
