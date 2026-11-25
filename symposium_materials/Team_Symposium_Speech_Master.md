# CardioSense: Official Team Pitch & Defense Script

> **Event:** MakeInSilicon 2026 Ideathon (International Symposium on Enabling Indigenous Semiconductor Infrastructure)  
> **Registration ID:** 27198  
> **Track:** Track 1: Smart Innovation in AI with Embedded Platform  
> **Team Code Blue:**  
> • **Asmita Manral (Team Lead)** — Opening, Problem Framing, Social Impact, Economics, Q&A Lead (Center Stage)  
> • **Gautam Batra** — Hardware Architecture, Sensing Modalities, Zero-Glue Design, Motion Denoising (Stage Right)  
> • **Nikhil Gavel** — Edge AI, 1.9 KB Silicon Model, Personal Baseline, Two-Tier Escalation, Silicon Verification (Stage Left)  
> **Affiliation:** Dr. Shyama Prasad Mukherjee International Institute of Information Technology, Naya Raipur (DSPM IIITNR)

---

## Stage Choreography & Presentation Protocol

| Parameter | Specification |
| :--- | :--- |
| **Total Duration** | 10 Minutes (~1,250 spoken words total at 125–130 WPM cadence) |
| **Stage Positions** | **Asmita** stands center stage (opening & closing); **Gautam** stands stage right by hardware diagrams; **Nikhil** stands stage left by Edge AI & verification panels |
| **Physical Props** | Asmita holds the 3D sternum pod and wristband mockups during the opening hook |
| **Pacing Rule** | Pause for exactly 1 full second after stating key clinical metrics to allow the jury to absorb the clinical gravity |
| **Evidence Guardrails** | Never cite whole-device field accuracy or unverified clinical sensitivity. Strictly cite: **77/77 simulated checks**, **2,064/2,064 pattern match in Vivado**, **0.64 $\to$ 0.80 AUROC** on European ST-T DB, **99.95% beat finding** on NSRDB, and **13 daily-life false starts eliminated** on PPG-DaLiA |

---

## Speaking Allocation Table

| Speaker | Assigned Segment | Timing & Cadence | Key Visual & Poster Target |
| :--- | :--- | :--- | :--- |
| **Asmita Manral** *(Lead)* | **Part 1: The Problem & Biological Mismatch**<br/>• 5–7 lakh annual deaths, 1–5% survival<br/>• 4 min vs 20–40 min mismatch<br/>• 51% warning symptoms, 101M diabetics, silent ischemia | **0:00 – 1:45**<br/>(1m 45s / 220 words) | Center stage; Props in hand; Abstract & Social Impact poster boxes |
| **Gautam Batra** | **Part 2: Multi-Modal Sensing & Zero-Glue Build**<br/>• 16% medical adhesive injury meta-analysis<br/>• Pod & Band hardware, dry steel electrodes<br/>• Dual-node NLMS filter (~24 dB sim. rejection) | **1:45 – 4:45**<br/>(3m 00s / 370 words) | Stage right; Circuit diagram, exploded pod view, noise filter |
| **Nikhil Gavel** | **Part 3: 1.9 KB Edge AI, Escalation & Silicon Proof**<br/>• 1,538 parameters, 1.9 KB Flash, 1.3 KB RAM<br/>• 44,962 cycles/beat (<1 ms), 0.64 $\to$ 0.80 AUROC<br/>• 2-tier escalation (30s window, 112 dispatch, 85 dB siren, 110 BPM CPR)<br/>• 77/77 simulation checks, 2,064 pattern match | **4:45 – 7:45**<br/>(3m 00s / 380 words) | Stage left; Silicon card, 2-tier escalation timeline, test checks |
| **Asmita Manral** *(Lead)* | **Part 4: Social Impact, Costing & National Vision**<br/>• ₹3,180 factory kit / ₹530 per patient reuse vs ₹39,900 retail<br/>• C2S 305 chips programme, 112 dispatch, CDSCO & DPDP Act<br/>• Final call to action & Q&A Open | **7:45 – 10:00**<br/>(2m 15s / 280 words) | Center stage; Cost table, Made for India panel, defense open |

---

## Verbatim Master Script

### PART 1: The Problem & Biological Mismatch
**Speaker:** Asmita Manral (Team Lead)  
**Target Timing:** 0:00 – 1:45 (~220 words) | *Center Stage, holding physical props*

> “Respected members of the jury, distinguished faculty, and colleagues.
>
> Every single year in India, sudden cardiac arrest takes an estimated **5 to 7 lakh lives**. Outside the hospital, our survival rate is barely **1 to 5 percent**.
>
> This tragedy is governed by an inescapable biological mismatch. When circulatory arrest occurs, irreversible brain injury begins within **4 to 6 minutes**. Yet across Indian cities and semi-urban communities, ambulance transit averages **20 to 40 minutes**. If we wait for collapse before calling for help, the biological race is lost before it begins.
>
> *[Hold up the Sternum Pod and Wristband props]*
>
> However, clinical cardiology reveals a vital window of hope. The Oregon Sudden Unexpected Death Study proved that **51% of victims—over half—experience warning symptoms in the four weeks before collapse**.
>
> In India, this vulnerability is heightened. The ICMR-INDIAB study confirms that **101 million Indians live with diabetes**. Because diabetic neuropathy damages autonomic pain pathways, **one in five—over 22%—suffer from completely silent ischemia**. They feel no crushing chest pain; their hearts suffer silently.
>
> To bridge this gap, we present **CardioSense: The Autonomous Sternal Sentry**. It is a distributed, two-node wearable Body Area Network that listens to the heart's mechanical and electrical signals on the body itself, learns each wearer's individual normal, and acts autonomously before biological collapse.
>
> My teammate Gautam Batra will walk you through our sensing architecture.”

---

### PART 2: Multi-Modal Sensing & Zero-Glue Build
**Speaker:** Gautam Batra  
**Target Timing:** 1:45 – 4:45 (~370 words) | *Stage Right, pointing to hardware panels*

> “Thank you, Asmita. To understand why CardioSense succeeds where others fail, look at current technology:
>
> Consumer smartwatches measure only wrist pulse and sound alarms only *after* pulse is gone. Hospital Holter patches record single-channel ECG passively for retrospective review, but they cannot intervene. Crucially, hospital patches rely on aggressive chemical adhesives. A 2024 meta-analysis in the *Journal of Tissue Viability* showed that **medical adhesives injure the skin of approximately 16% of hospital inpatients**—causing tears, blisters, and severe contact dermatitis.
>
> We designed a zero-glue, dual-node architecture engineered for continuous comfort:
>
> **Node A is the Sternal Pod**, worn over the lower sternum via a soft chest cord or breathable undershirt cradle. It combines dry 316L medical stainless steel contacts with multi-modal physiological sensors: an ADS1292R front-end for ECG, a MAX30001 for chest bioimpedance, an LSM6DSOX 6-axis IMU capturing sternal recoil vibrations, an acoustic Knowles I2S digital microphone capturing heart sounds, and a TMP117 skin temperature sensor, managed by a dual-core Nordic nRF5340 microcontroller.
>
> **Node B is the PulseBand**, worn on the wrist. It houses a MAX86141 optical PPG sensor for peripheral pulse and dual dry steel electrodes for Galvanic Skin Response, paired with an nRF52840 SoC.
>
> *[Step to the Noise Cancellation diagram]*
>
> The greatest obstacle in wearable biometrics is body motion. When walking, foot strikes transmit shockwaves up the skeleton, corrupting micro-cardiac signals. We solve this using **Dual-Node Active Motion Denoising**—analogous to active noise-cancelling headphones.
>
> Because the arm swings in direct cadence with walking gait, the wristband accelerometer captures an uncorrupted reference of footstrike cadence. Our sternum pod uses an on-device Normalized Least Mean Squares (NLMS) adaptive filter to subtract walking vibrations in real time, demonstrating **approximately 24 dB of synthetic motion cancellation gain in simulation**.
>
> If severe motion renders signals indeterminate, the Sentry pauses analysis and explicitly reports *'Not Monitoring'* rather than guessing.
>
> I will now pass the stage to Nikhil Gavel to explain our on-device AI and verification.”

---

### PART 3: 1.9 KB Edge AI, Escalation & Silicon Proof
**Speaker:** Nikhil Gavel  
**Target Timing:** 4:45 – 7:45 (~380 words) | *Stage Left, pointing to silicon & modeling cards*

> “Thank you, Gautam. Our intelligence runs strictly on the body, preserving privacy and eliminating dependence on cloud connectivity.
>
> *[Point to the Silicon Card on the poster]*
>
> We designed an ultra-compact 8-bit quantized neural network containing exactly **1,538 parameters**. It requires only **1.9 KB of Flash memory** and **1.3 KB of RAM**. Per heartbeat, it executes just **43,144 multiply-accumulates**, completing in **44,962 clock cycles**. At 64 MHz, inference finishes in well under 1 millisecond. This tiny footprint allows the main processor core to sleep over 99% of the time.
>
> Every patient's cardiovascular dynamics are unique. CardioSense adapts to each wearer's individual resting baseline. On public clinical records from the European ST-T Database, adapting to individual baseline dynamics improves the ranking score from **0.64 to 0.80 AUROC**.
>
> *[Point to the Two-Tier Escalation Timeline]*
>
> Our alarm state machine operates in two deterministic tiers:
> • **Tier 1 (Check-in):** If physiological parameters drift from the learned baseline, the wristband issues only a quiet haptic vibration. No panic, no false sirens.  
> • **Tier 2 (Emergency Dispatch):** If peripheral wrist pulse is lost AND the chest IMU confirms physical stillness for 5 seconds, an abortable **30-second cancel window** opens with audio-tactile alerts. The wearer can abort false triggers simply by holding the tactile button for 2 seconds.
>
> If uncancelled after 30 seconds, the pod autonomously triggers emergency dispatch: an automated emergency call to **112** with GPS location, an **85 dB onboard siren**, and a steady **110 BPM metronome pacing beat** to guide bystanders in CPR.
>
> *[Emphasize verification integrity]*
>
> We verified this rigorously: **77 of 77 simulated test cases pass**, covering 35 whole-device fault modes and 22 decision checks. When translated into Verilog hardware RTL, it achieved a **perfect 2,064 out of 2,064 pattern match against Python** in Vivado simulation. Replayed on public PhysioNet NSRDB recordings, it achieved **99.95% beat finding**, and on 17.9 hours of real daily activity from the PPG-DaLiA dataset, cross-checking the chest eliminated all 13 wrist-alone false alarms.
>
> As an honest engineering team, our boundary is clear: all logic is simulated and replayed on public databases; human clinical trials represent future work.
>
> Asmita will now conclude with our social impact and economic viability.”

---

### PART 4: Social Impact, Costing & National Vision
**Speaker:** Asmita Manral (Team Lead)  
**Target Timing:** 7:45 – 10:00 (~280 words) | *Center Stage, concluding with authority*

> “Thank you, Nikhil.
>
> CardioSense is engineered for real Indian healthcare realities.
>
> Our first deployment targets post-stent and post-infarction patients discharged home during their highest-risk 30-day recovery window, as well as high-risk diabetic individuals.
>
> *[Point to the Economics section]*
>
> Consider the economics: A commercial smartwatch with loss-of-pulse calling costs ₹39,900 at retail, while wearable defibrillators rent for lakhs per month. CardioSense's total bill of materials is **₹3,180 at 10,000 units** (~$33.50). Because our pods are fully sealed, sanitized with alcohol wipes, and reused across ~6 successive patients with washable cradles, the effective hardware cost plummets to **just ₹530 per patient**.
>
> Our architecture directly advances Indian national priorities:
> 1. **Indigenous Semiconductors:** Our 1.9 KB silicon footprint is purposefully sized to fit within India's *Chips to Startup (C2S)* programme, enabling domestic ASIC tape-outs across 305 partner institutions.  
> 2. **National Infrastructure:** It integrates directly into India's 112 Emergency Response Support System.  
> 3. **Regulatory Readiness:** Its privacy-preserving on-device architecture aligns with the Digital Personal Data Protection (DPDP) Act 2023 and CDSCO medical device investigational pathways.
>
> *[Final resolute closing]*
>
> CardioSense transforms cardiac monitoring from passive, post-collapse panic into proactive, autonomous protection. It is indigenous, affordable, and built to ensure that no Indian life is lost simply because help arrived too late.
>
> Thank you. We are ready for your questions.”
