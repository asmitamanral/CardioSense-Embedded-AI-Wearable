# CardioSense: Comprehensive Biomedical, Hardware, & TinyML Research Compendium

---

## MODULE 1: Human Pathophysiology & Electrophysiology

### 1.1 The Cardiac Conduction System & Ischemic Cascade
The heart’s mechanical pumping is driven by an intrinsic electrical conduction pathway:
1. **Sinoatrial (SA) Node** (the natural pacemaker in the right atrium) fires at 60–100 BPM.
2. The action potential propagates through the atria to the **Atrioventricular (AV) Node**, which introduces a physiological delay (~120–200 ms) to allow ventricular filling.
3. The impulse travels down the **Bundle of His**, branches into the **Left and Right Bundle Branches**, and terminates in the **Purkinje Fiber network**, causing synchronized ventricular depolarization (the QRS complex).

#### What Happens During a Sudden Cardiac Arrest (SCA) Precursor Window?
SCA is distinct from a myocardial infarction (heart attack). A heart attack is a **"plumbing problem"** (coronary artery thrombosis), whereas SCA is an **"electrical catastrophe"** (ventricular fibrillation/asystole). However, acute myocardial ischemia is the trigger for >80% of lethal arrhythmias.
* **Phase 1: Regional Ischemia (Minutes 0–10)**: Coronary perfusion drops. Cardiomyocytes switch to anaerobic glycolysis, lactic acid accumulates, and intracellular ATP depletes.
* **Phase 2: Membrane Depolarization & Re-entry**: The $Na^+/K^+$ ATPase ion pump fails. Extracellular potassium ($K^+$) rises locally. This depolarizes the resting membrane potential, slows action potential conduction, and causes heterogeneity in ventricular refractoriness.
* **Phase 3: Lethal Re-entrant Arrhythmia**: The electrical wavefront loops around ischemic tissue, triggering **Ventricular Tachycardia (VT)** at 150–250 BPM. 
* **Phase 4: Degeneration to Ventricular Fibrillation (VF) & Collapse**: Ventricular muscle quivers chaotically with zero stroke volume. Cardiac output plummets to zero. Brain death initiates within 4 minutes.

---

### 1.2 Autonomic Nervous System & Sympathetic Diaphoresis ("Cold Sweat")
Why does a patient experience a profuse "cold sweat" minutes before collapsing?
* **Baroreceptor Reflex Activation**: When ventricular output begins faltering, Mean Arterial Pressure (MAP) drops. Carotid sinus and aortic arch baroreceptors detect this decompression and inhibit vagal parasympathetic tone.
* **Massive Sympathetic Storm**: The brainstem (rostral ventrolateral medulla) triggers an intense systemic release of **norepinephrine** and **epinephrine** from the adrenal medulla.
* **Cutaneous Vasoconstriction ($\alpha_1$ receptors)**: Norepinephrine acts on vascular $\alpha_1$ receptors in the skin, causing severe vasoconstriction to shunt blood to the brain and heart. The skin turns **pale, cold, and clammy**.
* **Eccrine Gland Innervation (Cholinergic Sympathetic)**: While most sympathetic fibers use norepinephrine, postganglionic sympathetic fibers innervating the **eccrine sweat glands** release **Acetylcholine (ACh)** acting on **Muscarinic $M_3$ receptors**.
* **Clinical Significance for CardioSense**: This creates the definitive clinical paradox: **extreme sweating occurring simultaneously with skin cooling and low ambient temperature**. On a Galvanic Skin Response (GSR) sensor, this manifests as an acute, steep surge in skin conductance ($\Delta \text{GSR} > +3.0\ \mu\text{S/min}$) occurring without physical exertion.

---

### 1.3 Pulmonary Hemodynamics & Agonal Respiration Mechanics
* **Ventilation-Perfusion ($V/Q$) Mismatch**: As left ventricular output fails, pulmonary capillary blood flow drops, impairing gas exchange in the alveoli. Arterial oxygen saturation drops rapidly ($\text{SpO}_2 < 88\%$).
* **Medullary Hypoperfusion**: The medullary respiratory centers (the pre-Bötzinger complex) become hypoxic.
* **Respiratory Pattern Shift**:
  1. **Phase 1 (Tachypnea)**: Rapid, labored compensatory breathing (>30 BrPM).
  2. **Phase 2 (Agonal Respiration / Gasping)**: Erratic, shallow gasping with long irregular pauses (<8 BrPM or disordered gasps) immediately preceding loss of consciousness.
* **Sternal Mechanics**: The sternum provides direct bone-coupled mechanical excursion of the rib cage via the intercostal muscles and diaphragm, oscillating cleanly at **$0.1\text{ to }0.5\ \text{Hz}$**.

---

## MODULE 2: Biomedical Sensor Physics & Circuitry

### 2.1 Photoplethysmography (PPG) & Pulse Oximetry ($\text{SpO}_2$)
PPG measures subcutaneous blood volume changes using optical transmission and reflection governed by the **Modified Beer-Lambert Law**:
$$I = I_0 \cdot e^{-(\epsilon_{Hb} c_{Hb} + \epsilon_{HbO_2} c_{HbO_2}) d} \cdot \text{e}^{-G}$$
Where $I_0$ is incident light, $\epsilon$ is the extinction coefficient, $c$ is concentration, $d$ is path length, and $G$ is a scattering factor.

#### The Dual-Wavelength Mechanism (MAX30102):
The sensor alternates between two wavelengths at 25–100 Hz:
1. **Red LED ($\lambda = 660\ \text{nm}$)**: Deoxygenated hemoglobin ($Hb$) has a much higher optical absorption coefficient than oxygenated hemoglobin ($HbO_2$).
2. **Infrared LED ($\lambda = 880–940\ \text{nm}$)**: Oxygenated hemoglobin ($HbO_2$) absorbs light more strongly than $Hb$.

#### $\text{SpO}_2$ Calculation (Ratio-of-Ratios):
The PPG signal consists of a **DC component** (static absorption by bone, tissue, venous blood) and an **AC component** (pulsatile arterial blood corresponding to cardiac systole).
The normalized modulation ratio $R$ is:
$$R = \frac{(AC_{\text{Red}} / DC_{\text{Red}})}{(AC_{\text{IR}} / DC_{\text{IR}})}$$
$\text{SpO}_2$ is calculated empirically:
$$\text{SpO}_2 \approx 110 - 25 \times R$$
* At $R = 1.0$, $\text{SpO}_2 \approx 85\%$.
* At $R = 0.4$, $\text{SpO}_2 \approx 100\%$.

---

### 2.2 Galvanic Skin Response (GSR) / Electrodermal Activity (EDA)
GSR measures the electrical conductance ($G$) of the skin, which varies dynamically based on the filling of sweat ducts in the dermis.
* **Tonic Component (SCL - Skin Conductance Level)**: Slowly shifting baseline ($2–10\ \mu\text{S}$).
* **Phasic Component (SCR - Skin Conductance Response)**: Rapid transient peaks ($0.5–5\ \mu\text{S}$) resulting from sympathetic bursts.

#### Hardware Voltage Divider & Conductance Conversion:
The Grove GSR sensor applies an excitation voltage ($V_{in} = 3.3\text{V}$) across two skin electrodes in series with a reference resistance ($R_{\text{ref}} = 100\ \text{k}\Omega$):
$$V_{out} = V_{in} \cdot \frac{R_{\text{skin}}}{R_{\text{skin}} + R_{\text{ref}}}$$
Solving for skin resistance $R_{\text{skin}}$:
$$R_{\text{skin}} = R_{\text{ref}} \cdot \frac{V_{out}}{V_{in} - V_{out}}$$
Skin Conductance ($G$) in microSiemens ($\mu\text{S}$):
$$G (\mu\text{S}) = \frac{10^6}{R_{\text{skin}} (\Omega)}$$

---

### 2.3 MEMS Accelerometer (MPU6050) & Sternal Mechanics
The MPU6050 contains micro-machined capacitive proof masses suspended by silicon springs. Dynamic acceleration deflects the proof mass, altering capacitance measured by on-chip differential charge amplifiers.

#### Signal Vector Magnitude (SVM):
To make acceleration invariant to device orientation:
$$SVM = \sqrt{a_x^2 + a_y^2 + a_z^2} - 1.0g$$
Where $1.0g$ is baseline gravitational acceleration ($9.81\ \text{m/s}^2$).

#### Fall / Collapse Detection State Machine:
A physical collapse follows a deterministic mechanical signature:
1. **Free-Fall State**: $SVM < 0.5g$ for $\Delta t \in [150\text{ms}, 400\text{ms}]$.
2. **Impact State**: High-g deceleration shock ($SVM > 3.0g$) within $100\text{ms}$ of free-fall.
3. **Angular Reorientation**: Gyroscope integration shows chest orientation change $\Delta \theta > 60^\circ$ (transition from upright to recumbent).
4. **Post-Fall Stillness**: $SVM < 0.15g$ sustained for $>5\text{ seconds}$ (confirming patient is unconscious/immobile).

---

### 2.4 Pulse Arrival Time (PAT) & Cuffless Hemodynamics
Pulse Arrival Time (PAT) is the interval between ventricular electrical ejection and pulse wave arrival at a peripheral vascular site.
In CardioSense:
$$PAT = t_{\text{Wrist PPG Peak}} - t_{\text{Sternum PPG Peak}}$$
Governed by the **Moens-Korteweg equation** and **Hughes equation**:
$$PWV = \frac{\text{Distance}}{PAT} = \sqrt{\frac{E_0 \cdot e^{\gamma P} \cdot h}{\rho \cdot d}}$$
Where $PWV$ is Pulse Wave Velocity, $P$ is blood pressure, $h$ is arterial wall thickness, and $\rho$ is blood density.
* When acute cardiovascular collapse occurs, Mean Arterial Pressure ($P$) crashes, causing $PWV$ to drop and **PAT to lengthen significantly** (>40 ms delay), serving as an instantaneous cuffless indicator of hemodynamic shock.

---

## MODULE 3: Embedded Silicon, FreeRTOS & Firmware

### 3.1 Dual-Core FreeRTOS Architecture (ESP32-WROOM-32)
The ESP32 features two Xtensa 32-bit LX6 cores operating at 240 MHz. To prevent latency jitter, tasks are pinned deterministically:
* **Core 0 (Peripheral & RF Core)**:
  - `Task_BLEClient`: Scans and maintains 20 Hz GATT streaming from Wrist Node without packet drops.
  - `Task_I2C_Sensors`: Polling MPU6050 and secondary MAX30102 at 50 ms intervals.
  - `Task_GPS`: HardwareSerial NMEA parsing (`$GPRMC` sentence for Latitude/Longitude).
* **Core 1 (Application & Edge AI Core)**:
  - `Task_DSP_RingBuffer`: Sliding window accumulation (200 samples at 20 Hz = 10-second history).
  - `Task_TinyML_Inference`: Executes $8 \to 4 \to 2 \to 4 \to 8$ Autoencoder inference every 1.0 second.
  - `Task_Alert_FSM`: Evaluates cancellation push-button, 30s timer, buzzer/haptic PWM, and SIM800L AT commands.

---

### 3.2 SIM800L Power Engineering & Current Spikes
The SIM800L operates on a 2G GSM cellular protocol using Time Division Multiple Access (TDMA).
* **Current Burst Dynamics**: During transmission bursts, the RF Power Amplifier transmits in $577\ \mu\text{s}$ timeslots every $4.615\ \text{ms}$, drawing peak currents up to **$2.0\text{ Amps}$**.
* **Brownout Failure Mode**: If connected directly to the ESP32’s 3.3V pin, the voltage sags below $3.4\text{V}$, triggering a hardware Brownout Reset (BOR).
* **Solution**: Power the SIM800L directly from the 3.7V LiPo battery via a Schottky diode ($V_f \approx 0.3\text{V}$) or high-current buck regulator (4.0V steady), with a **$1000\ \mu\text{F}$ low-ESR tantalum capacitor** placed directly across SIM800L $VCC$ and $GND$.

---

## MODULE 4: TinyML Mathematics & Anomaly Detection

### 4.1 Autoencoder Mathematical Formulation
An Autoencoder is an unsupervised neural network trained to reconstruct its input:
$$f_{\theta}: \mathbb{R}^8 \to \mathbb{R}^2 \quad (\text{Encoder})$$
$$g_{\phi}: \mathbb{R}^2 \to \mathbb{R}^8 \quad (\text{Decoder})$$

#### Forward Pass Equations:
1. **Layer 1 (Hidden 1)**:
   $$\mathbf{z}_1 = \mathbf{W}_1 \mathbf{x} + \mathbf{b}_1, \quad \mathbf{a}_1 = \text{ReLU}(\mathbf{z}_1) = \max(0, \mathbf{z}_1) \quad (\mathbf{W}_1 \in \mathbb{R}^{8 \times 4})$$
2. **Layer 2 (Latent Bottleneck)**:
   $$\mathbf{z}_2 = \mathbf{W}_2 \mathbf{a}_1 + \mathbf{b}_2, \quad \mathbf{a}_2 = \text{ReLU}(\mathbf{z}_2) \quad (\mathbf{W}_2 \in \mathbb{R}^{4 \times 2})$$
3. **Layer 3 (Hidden 2)**:
   $$\mathbf{z}_3 = \mathbf{W}_3 \mathbf{a}_2 + \mathbf{b}_3, \quad \mathbf{a}_3 = \text{ReLU}(\mathbf{z}_3) \quad (\mathbf{W}_3 \in \mathbb{R}^{2 \times 4})$$
4. **Layer 4 (Output Reconstruction)**:
   $$\mathbf{z}_4 = \mathbf{W}_4 \mathbf{a}_3 + \mathbf{b}_4, \quad \hat{\mathbf{x}} = \sigma(\mathbf{z}_4) = \frac{1}{1 + e^{-\mathbf{z}_4}} \quad (\mathbf{W}_4 \in \mathbb{R}^{4 \times 8})$$

#### Parameter Footprint:
$$\text{Total Parameters} = (8 \times 4 + 4) + (4 \times 2 + 2) + (2 \times 4 + 4) + (4 \times 8 + 8) = 36 + 10 + 12 + 40 = 98 \text{ floats} = 392 \text{ Bytes!}$$

---

### 4.2 Dynamic Motion-Gated Anomaly Decision Rule
Reconstruction Mean Squared Error ($MSE$):
$$\text{MSE}(\mathbf{x}, \hat{\mathbf{x}}) = \frac{1}{8} \sum_{j=1}^{8} \left(x_j - \hat{x}_j\right)^2$$
The anomaly decision threshold scales with chest motion ($SVM$):
$$\text{Threshold}_{\text{dyn}} = 
\begin{cases} 
\text{Threshold}_{\text{base}}, & \text{if } SVM \le 0.40g \\ 
\text{Threshold}_{\text{base}} \cdot \left[1 + 2.5 \cdot (SVM - 0.40)\right], & \text{if } 0.40g < SVM \le 2.20g \\
\infty \text{ (Suppress - Mechanical Artifact)}, & \text{if } SVM > 2.20g
\end{cases}$$

An alarm triggers if and only if:
$$\text{MSE} > \text{Threshold}_{\text{dyn}} \quad \text{AND} \quad SVM \le 2.20g$$

---

## MODULE 5: Key Citations & Study Materials

### Landmark Clinical Papers:
1. **Muller, D. et al.** *"Warning symptoms before out-of-hospital cardiac arrest."* *The Lancet Public Health*, 2017. (Documents the 15-30 minute precursor window and diaphoresis prevalence).
2. **Kragholm, K. et al.** *"Bystander First Aid and Out-of-Hospital Cardiac Arrest Survival."* *New England Journal of Medicine (NEJM)*, 2017. (Proves why minutes matter and post-arrest alarms fail).
3. **Poh, M. Z. et al.** *"Continuous monitoring of electrodermal activity and heart rate variability on the wrist."* *IEEE Transactions on Biomedical Engineering*, 2010. (Validates palmar/wrist GSR for sympathetic detection).
4. **Charlton, P. H. et al.** *"Breathing rate estimation from the photoplethysmogram: a review."* *IEEE Reviews in Biomedical Engineering*, 2018. (Shows why wrist PPG breathing estimation fails and chest IMUs succeed).

### Key Clinical Datasets:
1. **MIMIC-III / MIMIC-IV (PhysioNet)**: Intensive Care Unit physiological database containing high-resolution arterial waveforms, $\text{SpO}_2$, and pre-arrest cardiac telemetry.
2. **WESAD (Wearable Stress and Affect Detection)**: Multimodal ambulatory dataset containing synchronized wrist GSR, chest respiration, and 3-axis accelerometry.
3. **CapnoBase / BIDMC PPG Respiration Dataset (PhysioNet)**: Gold-standard benchmark for respiratory waveform extraction from optical signals.
