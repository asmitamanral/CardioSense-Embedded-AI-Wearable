import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from pdf_generator_base import NumberedCanvas, get_custom_styles, create_callout, DOWNLOAD_DIR

def build_study_guide_pdf():
    pdf_filename = os.path.join(DOWNLOAD_DIR, "CardioSense_Symposium_Study_Material.pdf")
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = get_custom_styles()
    story = []

    # Title Block
    story.append(Paragraph("CardioSense: Symposium Technical Study Guide", styles['DocTitle']))
    story.append(Paragraph("Comprehensive Mastery Compendium for Topics 1, 2, 3, 7, and 11<br/><b>Core Tracks:</b> Clinical Pathophysiology, Sensor Mechanics, Denoising DSP & Competitive Economics", styles['DocSubTitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0D47A1"), spaceAfter=14))

    # Executive Overview Callout
    intro_text = "<b>Purpose of this Document:</b> This reference provides complete conceptual depth for the five core presentation themes: <b>Topic 1</b> (The Lethal Problem), <b>Topic 2</b> (Why Smartwatches and Patches Fail), <b>Topic 3</b> (The 1-to-6-Hour Biological Warning Signs), <b>Topic 7</b> (Motion Denoising and Cancelling Footsteps), and <b>Topic 11</b> (Head-to-Head Competitor Comparison). All complex calculus has been distilled into intuitive physical mechanisms and clinically grounded analogies."
    story.append(create_callout(intro_text, styles, bg_hex="#EBF8FF", border_hex="#90CDF4"))
    story.append(Spacer(1, 14))

    # =========================================================================
    # TOPIC 1
    # =========================================================================
    story.append(Paragraph("TOPIC 1: The Lethal Problem (Epidemiology & Time Dynamics)", styles['SectionH1']))
    story.append(Paragraph("Sudden Cardiac Arrest (SCA) is an abrupt cessation of mechanical cardiac pump function, causing immediate cessation of arterial circulation. It is distinct from myocardial infarction ('heart attack'), which is an acute plumbing occlusion; SCA is an electrical cataclysm, terminating in Ventricular Fibrillation (VF) or Asystole.", styles['BodyCustom']))
    
    story.append(Paragraph("The Three Foundational Numbers to Command:", styles['SectionH2']))
    story.append(Paragraph("• <b>350,000+ Fatalities Annually in India:</b> Over 7 million globally. It represents the single largest contributor to premature cardiovascular mortality in South Asia.", styles['BulletCustom']))
    story.append(Paragraph("• <b>Survival Rate Below 5% in India:</b> Compared to 10–12% in parts of North America and Europe equipped with public automated external defibrillators (AEDs) and ubiquitous bystander CPR.", styles['BulletCustom']))
    story.append(Paragraph("• <b>The 4-Minute vs. 20-to-40-Minute Paradox:</b> Neurons in the cerebral cortex consume approximately 20% of resting oxygen despite constituting only 2% of body weight. Complete anoxia results in irreversible neuronal apoptosis starting at <b>4 minutes</b>. Meanwhile, average emergency medical service (EMS) transit across Indian metro gridlocks and rural districts spans <b>20 to 40 minutes</b>.", styles['BulletCustom']))
    
    t1_box = "<b>Key Judge Defense:</b> When a judge asks why previous tech hasn't helped mortality, answer: <i>'Because conventional devices sound an alarm only AFTER collapse. Waiting for an arrest to occur leaves an unbridgeable 30-minute ambulance transit gap against a 4-minute biological survival clock. Pre-arrest prediction is the only biologically viable path.'</i>"
    story.append(Spacer(1, 4))
    story.append(create_callout(t1_box, styles, bg_hex="#FFF5F5", border_hex="#FEB2B2"))
    story.append(Spacer(1, 14))

    # =========================================================================
    # TOPIC 2
    # =========================================================================
    story.append(Paragraph("TOPIC 2: Why Smartwatches & Hospital Patches Fail", styles['SectionH1']))
    story.append(Paragraph("Existing wearable monitoring falls into three clinically and mechanically flawed categories:", styles['BodyCustom']))

    story.append(Paragraph("1. Consumer Smartwatches (Apple Watch, Samsung Galaxy Watch)", styles['SectionH2']))
    story.append(Paragraph("• <b>Post-Collapse Latency:</b> They trigger alerts only upon total cessation of pulsatile blood flow or severe bradycardia. Alerting a remote caregiver after the patient is already unconscious on the floor is biologically futile.", styles['BulletCustom']))
    story.append(Paragraph("• <b>Optical Displacement Noise:</b> Photoplethysmography (PPG) relies on steady photon reflectance through capillary beds. Arm movement creates micro-separations between the photodiodes and skin, introducing massive false-alarm motion artifacts.", styles['BulletCustom']))
    story.append(Paragraph("• <b>Anatomical Blindness:</b> The wrist is physically detached from the thoracic cavity and cannot monitor chest-wall respiration mechanics or cardiac recoil shockwaves.", styles['BulletCustom']))

    story.append(Paragraph("2. Clinical Holter & Adhesive Patches (e.g., iRhythm Zio XT, Medtronic Linq)", styles['SectionH2']))
    story.append(Paragraph("• <b>Conductive Gel Desiccation:</b> Wet hydrogel electrolyte bridges electrical biopotentials to metal contacts. Within 24 to 48 hours, cutaneous body heat evaporates moisture from the hydrogel, driving impedance above clinical limits and corrupting the trace.", styles['BulletCustom']))
    story.append(Paragraph("• <b>Contact Dermatitis & Rejection:</b> Constant chemical adhesives trap sweat and exfoliate stratum corneum layers. Over 85% of elderly patients experience severe pruritus (itching), erythema, or skin tears, driving non-compliance.", styles['BulletCustom']))
    story.append(Paragraph("• <b>Disposable Economic Waste:</b> At ~$300 per single-use patch, continuous monitoring is economically unfeasible for mass public healthcare.", styles['BulletCustom']))

    story.append(Paragraph("3. Wearable Cardioverter Defibrillators (ZOLL LifeVest)", styles['SectionH2']))
    story.append(Paragraph("• <b>The $4,000/Month Monopoly:</b> Rented at $3,500 to $4,000 every single month for patients in the 90-day post-infarction window. It is heavy, cumbersome, stigmatizing, and purely reactive (shocks after ventricular collapse).", styles['BulletCustom']))
    story.append(Spacer(1, 14))

    # =========================================================================
    # TOPIC 3
    # =========================================================================
    story.append(Paragraph("TOPIC 3: The 1-to-6-Hour Biological Warning Signs", styles['SectionH1']))
    story.append(Paragraph("Sudden cardiac arrest is rarely an instantaneous lightning bolt. In over 50% of victims, the cardiovascular and autonomic nervous systems undergo measurable physiological decompensation <b>15 to 30 minutes (and up to several hours) before mechanical collapse</b>.", styles['BodyCustom']))

    story.append(Paragraph("The Five Cardinal Precursor Biomarkers:", styles['SectionH2']))
    
    story.append(Paragraph("1. Pre-Ejection Period (PEP) Lengthening (>140 ms):", styles['BulletCustom']))
    story.append(Paragraph("PEP is the electromechanical delay between ventricular depolarization (Q-wave on ECG) and actual mechanical opening of the aortic valve (AO peak on SCG). Under acute ischemia, myocardial energy starvation halts efficient contraction; the ventricle takes significantly longer to generate enough intraventricular pressure to overcome aortic afterload. Normal PEP is 90–110 ms; pre-arrest ischemia pushes it past <b>140 ms</b>.", styles['BodyCustom']))

    story.append(Paragraph("2. Aortic Opening (AO) Recoil Amplitude Collapse (>50% Drop):", styles['BulletCustom']))
    story.append(Paragraph("Every cardiac cycle ejects a pressurized blood bolus through the aortic arch, generating a physical recoil shockwave across the sternum (seismocardiography). When ischemic stroke volume plummets, this physical recoil shockwave amplitude collapses by more than 50%.", styles['BodyCustom']))

    story.append(Paragraph("3. Autonomic Cold-Sweat Diaphoresis Surge (ΔGSR > 3.5 µS/min):", styles['BulletCustom']))
    story.append(Paragraph("Falling cardiac stroke volume drops Mean Arterial Pressure. Carotid and aortic baroreceptors immediately trigger a massive sympathetic compensatory storm. Alpha-1 adrenergic receptors cause cutaneous vasoconstriction (pale, cold skin), while cholinergic muscarinic M3 pathways violently stimulate palmar eccrine sweat glands. Result: <i>heavy, ionic cold sweating on ice-cold skin</i>.", styles['BulletCustom']))

    story.append(Paragraph("4. Arterial Oxygen Saturation Plunge (SpO2 < 88%):", styles['BulletCustom']))
    story.append(Paragraph("Pulmonary hypoperfusion reduces alveolar gas exchange efficiency, causing rapid systemic arterial desaturation at rest.", styles['BulletCustom']))

    story.append(Paragraph("5. Agonal Respiratory Tachypnea (>30 BrPM):", styles['BulletCustom']))
    story.append(Paragraph("Brainstem hypoxia in the pre-Bötzinger complex induces rapid, shallow, erratic breathing followed by ominous pauses.", styles['BulletCustom']))

    story.append(Spacer(1, 4))
    bio_box = "<b>The Scientific Linchpin:</b> The defining diagnostic signature of pre-arrest crisis is <b>concurrence at rest</b>. While running, heart rate spikes alongside high acceleration. In a pre-arrest crisis, PEP lengthens, AO collapses, cold sweat surges, and oxygen plunges <i>while the patient is completely stationary</i>."
    story.append(create_callout(bio_box, styles, bg_hex="#FEFCBF", border_hex="#ECC94B"))
    story.append(Spacer(1, 14))

    # =========================================================================
    # TOPIC 7
    # =========================================================================
    story.append(Paragraph("TOPIC 7: Motion Denoising (Cancelling Footsteps via Dual-Node DSP)", styles['SectionH1']))
    story.append(Paragraph("The greatest obstacle to ambulatory biometrics is motion artifact. Heel-strikes during walking propagate mechanical vibrations up the skeletal column into the ribcage, corrupting micro-g seismocardiography and optical PPG.", styles['BodyCustom']))

    story.append(Paragraph("The Active Noise-Cancelling (ANC) Analogy:", styles['SectionH2']))
    story.append(Paragraph("Just as noise-cancelling headphones use external microphones to capture ambient airplane engine rumble and invert it to isolate clean music, CardioSense uses the wristband as an external biological microphone:", styles['BodyCustom']))
    
    story.append(Paragraph("• <b>The Wrist as Reference:</b> Because arm swing is mechanically locked to walking cadence, the wrist IMU captures a pure, uncorrupted reference signal of the locomotive shockwaves.", styles['BulletCustom']))
    story.append(Paragraph("• <b>Adaptive NLMS Subtraction:</b> The on-device Normalized Least Mean Squares (NLMS) filter correlates the wrist reference against the sternal signal, dynamically calculating the transfer function of the body and subtracting the footstep shockwaves in real time.", styles['BulletCustom']))
    story.append(Paragraph("• <b>Discrete Wavelet Transform (DWT):</b> Multi-resolution wavelet decomposition strips away high-frequency shivering, muscle tremors, and clothing friction.", styles['BulletCustom']))

    # Table of DSP metrics
    dsp_data = [
        [Paragraph("<b>DSP Metric</b>", styles['TableHeader']), Paragraph("<b>CardioSense Benchmark</b>", styles['TableHeader']), Paragraph("<b>Clinical & Silicon Impact</b>", styles['TableHeader'])],
        [Paragraph("Execution Latency", styles['TableCellBold']), Paragraph("44,962 clock cycles / beat (<1 ms)", styles['TableCell']), Paragraph("8-bit quantized TinyML (1,538 parameters), <0.01% duty cycle", styles['TableCell'])],
        [Paragraph("Power Consumption", styles['TableCellBold']), Paragraph("1.9 KB Flash, 1.3 KB RAM", styles['TableCell']), Paragraph("Calculated 3–4 days between charges (150 mAh pod, 240 mAh band)", styles['TableCell'])],
        [Paragraph("Noise Rejection Ratio", styles['TableCellBold']), Paragraph("~24 dB Synthetic Rejection Gain", styles['TableCell']), Paragraph("Extracts diagnostic AO peaks even during active walking", styles['TableCell'])],
    ]
    t_dsp = Table(dsp_data, colWidths=[130, 150, 220])
    t_dsp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0D47A1")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(Spacer(1, 6))
    story.append(t_dsp)
    story.append(Spacer(1, 14))

    # =========================================================================
    # TOPIC 11
    # =========================================================================
    story.append(Paragraph("TOPIC 11: Head-to-Head Competitor Comparison & Market Positioning", styles['SectionH1']))
    story.append(Paragraph("CardioSense redefines the clinical monitoring matrix by bridging the gap between passive consumer wearables and clinical diagnostic patches:", styles['BodyCustom']))

    comp_data = [
        [Paragraph("<b>Feature Matrix</b>", styles['TableHeader']), Paragraph("<b>CardioSense</b>", styles['TableHeader']), Paragraph("<b>Apple Watch</b>", styles['TableHeader']), Paragraph("<b>Zio XT Patch</b>", styles['TableHeader']), Paragraph("<b>ZOLL LifeVest</b>", styles['TableHeader'])],
        [Paragraph("<b>Detection Horizon</b>", styles['TableCellBold']), Paragraph("<font color='#007A78'><b>Pre-Arrest (15–30 min)</b></font>", styles['TableCell']), Paragraph("Post-Arrest (Pulse cessation)", styles['TableCell']), Paragraph("Post-Facto (After lab read)", styles['TableCell']), Paragraph("Post-Arrest (Shocks VF)", styles['TableCell'])],
        [Paragraph("<b>Skin Adhesion</b>", styles['TableCellBold']), Paragraph("<font color='#007A78'><b>Zero (Dry Stainless)</b></font>", styles['TableCell']), Paragraph("Zero (Wrist band)", styles['TableCell']), Paragraph("Wet Gel (Dries in 48h)", styles['TableCell']), Paragraph("Bulky Fabric Vest", styles['TableCell'])],
        [Paragraph("<b>Respiration & SCG</b>", styles['TableCellBold']), Paragraph("<font color='#007A78'><b>Full Thoracic Fusion</b></font>", styles['TableCell']), Paragraph("None (Blind to chest)", styles['TableCell']), Paragraph("None (ECG only)", styles['TableCell']), Paragraph("None (ECG only)", styles['TableCell'])],
        [Paragraph("<b>Bystander CPR Metronome</b>", styles['TableCellBold']), Paragraph("<font color='#007A78'><b>Yes (110 BPM Coach)</b></font>", styles['TableCell']), Paragraph("None", styles['TableCell']), Paragraph("None", styles['TableCell']), Paragraph("None", styles['TableCell'])],
        [Paragraph("<b>Fall Lockout Safety</b>", styles['TableCellBold']), Paragraph("<font color='#007A78'><b>Yes (>3.0g Lockout)</b></font>", styles['TableCell']), Paragraph("Generic alert only", styles['TableCell']), Paragraph("None", styles['TableCell']), Paragraph("None", styles['TableCell'])],
        [Paragraph("<b>Effective Cost</b>", styles['TableCellBold']), Paragraph("<font color='#007A78'><b>$5.58 / patient</b></font>", styles['TableCell']), Paragraph("$400–$800", styles['TableCell']), Paragraph("$300 per single use", styles['TableCell']), Paragraph("$4,000 / month", styles['TableCell'])],
    ]
    t_comp = Table(comp_data, colWidths=[105, 105, 95, 95, 100])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A202C")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(Spacer(1, 6))
    story.append(t_comp)
    story.append(Spacer(1, 14))

    # =========================================================================
    # RAPID-FIRE DEFENSE BANK
    # =========================================================================
    story.append(Paragraph("Rapid-Fire Judge Q&A Defense Master Bank", styles['SectionH1']))
    
    qa_list = [
        ("Q1: Why didn't you use traditional ECG on the chest?",
         "We deliberately engineered a multi-modal mechanical and electrophysiological array using dry 316L stainless steel contacts. Traditional adhesive wet ECG requires messy hydrogels that dry out within 48 hours and induce severe dermatitis. By fusing dry contacts with sternal seismocardiography and radial pulse oximetry, we achieve continuous monitoring with zero skin breakdown and total hospital reusability."),
        
        ("Q2: In Indian summers with 44°C heat, won't sweat cause massive false alarms?",
         "Never. The Autoencoder evaluates multi-signal covariance, not isolated thresholds. In thermal heat, sweat conductance rises, but arterial oxygen remains at 98%, breathing is normal, and heart recoil is robust. CardioSense triggers an alarm only during concurrent multi-system discordance: cold sweat surging alongside collapsing oxygen (<88%) and lengthening PEP while the patient is stationary."),
        
        ("Q3: How do you mathematically guarantee that footstep cancellation doesn't erase true heart signals?",
         "Because the wrist motion reference is structurally decoupled from intra-thoracic pressure waves. The wrist accelerometer captures the external kinematic stride cadence. The NLMS filter uses this independent reference to estimate and subtract only the coherent locomotive frequency components, leaving the uncorrupted internal cardiac vibrations intact."),
        
        ("Q4: Why compare yourself to the ZOLL LifeVest if you cannot deliver a defibrillating shock?",
         "Because the LifeVest is currently the only prescribed ambulatory option for post-infarction recovery, yet its $4,000/month rental fee excludes 99% of Indian patients. Furthermore, LifeVest is purely reactive—it waits for full cardiac arrest before shocking. CardioSense provides continuous, proactive early-warning surveillance for $5.58 per patient, alerting doctors hours before the fatal arrhythmia occurs.")
    ]

    for q, a in qa_list:
        story.append(Paragraph(f"<b>{q}</b>", styles['SectionH2']))
        story.append(Paragraph(a, styles['BodyCustom']))
        story.append(Spacer(1, 3))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Study Material PDF successfully generated at: {pdf_filename}")

if __name__ == "__main__":
    build_study_guide_pdf()
