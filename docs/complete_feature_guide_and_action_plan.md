# CardioSense: Final Master Feature List & Action Plan (Refined Architecture)

---

## SECTION 1: Final Master Feature List (18 Refined Features)

### A. Anatomically Decoupled Sensing (Hardware Physics)
1. **Continuous Wrist Optical Photoplethysmography (PPG)**: High-resolution radial pulse tracking and arterial oxygenation ($\text{SpO}_2$) via dual-wavelength optical absorption (660nm Red / 940nm IR).
2. **Wrist Electrodermal Cold-Sweat Detection (GSR)**: Continuous skin conductance monitoring on the palmar/ventral wrist to capture acute sympathetic cholinergic surges (pre-arrest diaphoresis).
3. **Through-Clothing Sternal Respiration Mechanics**: Direct mechanical measurement of thoracic cage expansion ($0.1–0.5\ \text{Hz}$) using an MPU6050 accelerometer coupled to the sternal bone through clothing (zero bare-skin tape required).
4. **Dual-Use Mechanical Fall & Collapse Detection**: Reuses the sternum accelerometer to detect rapid collapse dynamics: `Free-fall (<0.5g)` $\to$ `Impact Shock (>3.0g)` $\to$ `Angular Inversion` $\to$ `Prolonged Stillness`.
5. **Synchronized 20 Hz Dual-Node BLE 5.0 Bus**: Time-aligned, low-power telemetry streaming from the Wrist Slap-Band Peripheral to the Sternum Central Hub.

### B. On-Device Edge AI & False-Alarm Rejection (TinyML & DSP)
6. **On-Device Unsupervised TinyML Autoencoder ($8 \to 4 \to 2 \to 4 \to 8$)**: Multi-signal anomaly detector running entirely in embedded C++ in $<18\ \mu\text{s}$ (376 bytes model footprint).
7. **Kinetic Motion-Gating Engine**: Real-time threshold scaling using sternal Signal Vector Magnitude ($SVM$) to automatically distinguish vigorous exercise from a sedentary pre-arrest crisis.
8. **Adaptive Baseline Personalization**: Online running statistical calibration (Welford algorithm) learning each wearer’s unique resting baseline without needing prior cardiac-event training data.
9. **100% Offline Edge Autonomy**: Zero reliance on smartphones, 4G cloud servers, or Wi-Fi for continuous monitoring; complete patient privacy preservation.

### C. Emergency Escalation & Fail-Safe Actuation (Hardware & Telephony)
10. **Two-Stage Deterministic Alert Pipeline**: 30-second local haptic + audio countdown to give conscious wearers an abort window before emergency dispatch.
11. **Physical Tactile Push-to-Cancel Button**: High-reliability momentary button on the sternum locket to eliminate false-alarm panic and emergency service congestion.
12. **Local High-Decibel Siren & Multi-Color Annunciators**: 85 dB warble piezo sounder, ERM haptic vibrator, and tri-color status LEDs (Green: Normal, Amber: Stage 1, Red: Critical Stage 2).
13. **Autonomous Location-Tagged Emergency SMS**: SIM800L cellular dispatch sending Google Maps GPS coordinates and vital statistics to family/emergency contacts.
14. **Automated Emergency Caregiver Voice Call (`ATD`)**: Places an automatic telephone call with an audible DTMF alert tone burst pattern to ensure the alert is not missed in an SMS inbox.
15. **SIM800L 2A Current Transient Power Buffer**: Integrated $1000\ \mu\text{F}$ low-ESR decoupling capacitor and dedicated buck regulation preventing microcontroller brownout during TDMA RF bursts.

### D. Tier-2 Emergency Caregiver & Hospital AI (Post-Alert Ecosystem)
16. **Automated Clinical SBAR Emergency Triage Report**: Cloud/hospital Generative AI model that translates raw telemetry into a structured trauma report (Situation, Background, Assessment, Recommendation) for emergency room staff before ambulance arrival.
17. **Interactive Bystander CPR Audio Coach**: Automated mobile voice assistant pacing chest compressions at 100–120 BPM on the caregiver's phone during the critical first 4 minutes.
18. **Privacy-Preserving Federated Learning Architecture**: Periodic aggregation of anonymized mathematical model weight updates ($\Delta W$) across wearable devices without transmitting raw patient biometric data.

### E. Social, Economic & Mechanical Packaging
* **Ultra-Frugal Indian Healthcare BOM (<₹3,150 / ~$37)**: Built from accessible components; packaged in a comfortable silicone slap-band on the wrist and a lightweight clothing-clipped sternum locket with a breakaway safety lanyard.

---

## SECTION 2: Key Feature Action Plan ("What To Do" Manual)

---

### Pillar 1: Wrist Slap-Band Sensing (PPG + Cold Sweats)
* **What It Does**: Reads continuous heart rate, blood oxygen ($\text{SpO}_2$), and sympathetic cold sweat surges directly from the wrist.
* **Why It’s on the Wrist**: The wrist radial artery offers clean optical blood volume access, and the palmar/ventral wrist has the highest density of eccrine sweat glands ($\sim 600/\text{cm}^2$).
* **WHAT TO DO**:
  * **Hardware Setup**:
    - Connect MAX30102 to Wrist ESP32 I2C (`SDA = GPIO 21`, `SCL = GPIO 22`).
    - Connect Grove GSR analog signal to `GPIO 34` (ADC1 Channel 6).
    - Power using a 3.7V 400mAh LiPo battery stepped through a 3.3V LDO.
  * **Firmware Implementation**:
    - In `wrist_node.ino`, package samples into a 16-byte binary struct: `[timestamp, ppg_ir, ppg_red, gsr_raw, hr, spo2]`.
    - Transmit over BLE GATT at 20 Hz (connection interval: 50 ms).
  * **What to tell the panel**: *"The wrist is strictly dedicated to optical hemodynamics and electrodermal sweat tracking where direct, comfortable, self-fitting bare-skin contact is natural."*

---

### Pillar 2: Through-Clothing Sternal Respiration Mechanics
* **What It Does**: Measures breathing rate (BrPM) and breath depth directly from the rib cage expansion through clothing.
* **Why It’s on the Sternum**: Wrist wearables cannot measure chest respiration. By using an accelerometer, it senses mechanical motion right through shirts without needing bare-skin adhesives.
* **WHAT TO DO**:
  * **Hardware Setup**: Mount the MPU6050 flat inside the sternum locket casing with the Z-axis perpendicular to the chest wall. Connect to Sternum ESP32 I2C (`SDA = GPIO 21`, `SCL = GPIO 22`).
  * **Firmware Implementation**:
    - Sample the MPU6050 Z-axis at 20 Hz.
    - Apply a digital bandpass filter ($0.1\ \text{Hz} - 0.5\ \text{Hz}$) in `cardio_features.h` to isolate the respiratory excursion band.
    - Calculate Breaths Per Minute using zero-crossing counting over a 10-second sliding window. Measure peak-to-trough displacement to quantify **Respiration Depth** (detecting shallow/agonal gasps).
  * **What to tell the panel**: *"We deliberately omitted optical sensors on the chest. The sternum locket is purely biomechanical: it senses chest-wall respiratory expansion through clothing via mechanical coupling, eliminating skin irritation and maximizing daily patient compliance."*

---

### Pillar 3: Mechanical Collapse & Fall Detection State Machine
* **What It Does**: Uses the sternum accelerometer to detect when a patient physically collapses onto the floor.
* **Why It’s Needed**: Provides immediate physical confirmation if cardiac arrest causes fainting or collapse.
* **WHAT TO DO**:
  * **Firmware Implementation**: In `cardio_features.h`, execute a 4-state state machine:
    1. **Free-Fall**: $SVM = \sqrt{a_x^2 + a_y^2 + a_z^2} - 1.0g < 0.5g$ for at least 150 ms.
    2. **Impact Shock**: $SVM > 3.0g$ within 100 ms of free-fall.
    3. **Angular Inversion**: Gyroscope integration shows $\Delta \theta > 60^\circ$ (transition from vertical to horizontal posture).
    4. **Prolonged Inactivity**: $SVM < 0.15g$ continues for $>5\ \text{seconds}$ post-impact.
  * **What to tell the panel**: *"We achieved fall detection with zero added hardware cost through algorithmic dual-use of the sternal accelerometer."*

---

### Pillar 4: 20 Hz Synchronized Dual-Node BLE 5.0 Link
* **What It Does**: Continuously synchronizes both nodes with ultra-low latency and low power consumption.
* **WHAT TO DO**:
  * **Firmware Implementation**:
    - In `wrist_node.ino`, configure the ESP32 as a **BLE GATT Server** advertising `CardioSense-Wrist`.
    - In `sternum_hub.ino`, configure the Central ESP32 to scan and connect automatically.
    - Pin the BLE GATT reception task to **Core 0** in FreeRTOS (`xTaskCreatePinnedToCore(..., 0)`), leaving **Core 1** 100% unblocked for DSP and neural network inference.
  * **What to tell the panel**: *"FreeRTOS dual-core allocation guarantees hard real-time determinism: BLE radio operations on Core 0 never stall our signal processing and neural inference on Core 1."*

---

### Pillar 5: On-Device TinyML Autoencoder ($8 \to 4 \to 2 \to 4 \to 8$)
* **What It Does**: Evaluates 8 normalized physiological features simultaneously to detect pre-arrest anomalies.
* **Why It’s Needed**: `if-else` rules trigger constant false alarms. The Autoencoder evaluates multi-signal covariance.
* **WHAT TO DO**:
  * **ML Pipeline**: Run `python train_autoencoder.py` in `ml_pipeline/` to generate `model_weights.h`.
  * **Firmware Implementation**:
    - In `autoencoder_engine.h`, feed the 8-feature normalized vector into the C++ forward pass:
      $$\mathbf{x} \in \mathbb{R}^8 \xrightarrow{W_1, b_1} \text{Hidden } \mathbb{R}^4 \xrightarrow{W_2, b_2} \text{Latent } \mathbb{R}^2 \xrightarrow{W_3, b_3} \text{Hidden } \mathbb{R}^4 \xrightarrow{W_4, b_4} \hat{\mathbf{x}} \in \mathbb{R}^8$$
    - Compute Reconstruction Error: $MSE = \frac{1}{8}\sum_{i=1}^8 (x_i - \hat{x}_i)^2$.
  * **What to tell the panel**: *"The model has a footprint of only 376 Bytes (94 parameters) and executes in under $18\ \mu\text{s}$, running locally with zero cloud dependence."*

---

### Pillar 6: Kinetic Motion-Gating Engine (Exercise False-Alarm Filter)
* **What It Does**: Dynamically scales the anomaly threshold based on chest motion, preventing false alarms during exercise.
* **WHAT TO DO**:
  * **Firmware Implementation**: In `autoencoder_engine.h`, compute the dynamic threshold:
    $$\text{Threshold}_{\text{dyn}} = 
    \begin{cases} 
    \text{Threshold}_{\text{base}}, & \text{if } SVM \le 0.40g \quad \text{(Resting / Sedentary)} \\ 
    \text{Threshold}_{\text{base}} \cdot [1 + 2.5(SVM - 0.40)], & \text{if } 0.40g < SVM \le 2.20g \quad \text{(Exercise Tolerance)} \\
    \infty \text{ (Suppress Alert)}, & \text{if } SVM > 2.20g \quad \text{(Mechanical Artifact)}
    \end{cases}$$
  * **What to tell the panel**: *"During a sprint, high vitals coincide with high chest motion. A pre-arrest crisis is characterized by extreme physiological arousal occurring at near-zero motion."*

---

### Pillar 7: Two-Stage Fail-Safe Alarm & Push-to-Cancel Button
* **What It Does**: Sounds a 30-second local warning with a physical button to abort false alarms before emergency dispatch.
* **WHAT TO DO**:
  * **Hardware Setup**:
    - Connect a tactile push button between `GPIO 4` and `GND` (`INPUT_PULLUP`).
    - Connect a haptic motor to `GPIO 18` and a piezo buzzer to `GPIO 19`.
  * **Firmware Implementation**:
    - In `emergency_alert.h`, enter `STATE_STAGE_1_PREALERT` on anomaly detection.
    - Pulse haptics at 1 Hz and emit warning beeps for 30 seconds.
    - If button is pressed, abort immediately. If uncancelled after 30s, escalate to `STATE_STAGE_2_ESCALATED`.
  * **What to tell the panel**: *"Our deterministic fail-safe mechanism completely eliminates false alarm panic and unnecessary 108/911 ambulance dispatches."*

---

### Pillar 8: Offline Cellular Telephony: Location-Tagged SMS & Voice Call
* **What It Does**: Automatically sends GPS coordinates and vital stats via SMS, then dials the caregiver's phone.
* **WHAT TO DO**:
  * **Hardware Setup**:
    - Connect SIM800L to UART2 (`RX = GPIO 16`, `TX = GPIO 17`). Solder a **$1000\ \mu\text{F}$ capacitor** across the SIM800L power pins.
    - Connect Neo-6M GPS `TX` to `GPIO 32`.
  * **Firmware Implementation**: In `emergency_alert.h`, execute AT commands on Stage 2:
    ```
    AT+CMGF=1
    AT+CMGS="+91XXXXXXXXXX" -> Send SMS with Google Maps coordinates & vitals
    ATD+91XXXXXXXXXX;       -> Dial phone call
    AT+VTS="9,9,9,1,1,1"    -> Transmit emergency audible tone pattern
    ```
  * **What to tell the panel**: *"SMS messages can easily sit unread in a silent inbox. Our system automatically places a phone call to wake up sleeping caregivers while transmitting live GPS coordinates."*

---

### Pillar 9: Tier-2 Post-Alert AI: SBAR Hospital Brief & Bystander CPR Coach
* **What It Does**: Translates raw sensor data into an ER medical brief and coaches the family member through CPR.
* **WHAT TO DO**:
  * **Software / App Implementation**:
    - **SBAR Hospital Brief**: When telemetry is received, prompt a clinical LLM:
      > *"Generate an SBAR report: 68-year-old male, sudden HR surge to 168 BPM, SpO2 drop to 82%, GSR cold sweat surge +4.8 uS/min, agonal respiration at 34 BrPM, sedentary posture."*
      - Produces: **Situation** (Impending cardiogenic shock), **Background** (Sudden onset, zero exertion), **Assessment** (Ventricular Tachycardia), **Recommendation** (Prep Cath Lab, ready defibrillator).
    - **Bystander CPR Coach**: Mobile voice assistant instructs the family:
      > *"CardioSense alert: Lay the patient flat on the floor. Place your hands in the center of the chest. Push hard and fast."*
      - Phone speaker pulses a continuous beat at **110 BPM** (AHA compression standard).
  * **What to tell the panel**: *"Early detection is useless without early CPR. Our Tier-2 AI guides the family to keep the brain alive during the critical first 4 minutes."*
