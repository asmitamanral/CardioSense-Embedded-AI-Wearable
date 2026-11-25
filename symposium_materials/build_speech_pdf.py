import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from pdf_generator_base import NumberedCanvas, get_custom_styles, create_callout, DOWNLOAD_DIR

def build_speech_pdf():
    pdf_filename_local = os.path.join(r"c:\Users\Lenovo\OneDrive\Documents\CardioSense\symposium_materials", "CardioSense_Symposium_Speech_Master.pdf")
    pdf_filename_dl = os.path.join(DOWNLOAD_DIR, "CardioSense_Symposium_Speech_Master.pdf")
    
    doc = SimpleDocTemplate(
        pdf_filename_local,
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = get_custom_styles()
    story = []

    # Title Block
    story.append(Paragraph("CardioSense: Official Team Pitch & Defense Script", styles['DocTitle']))
    story.append(Paragraph("<b>MakeInSilicon 2026 Ideathon · Registration ID: 27198 · Track 1: Smart Innovation in AI with Embedded Platform</b><br/>"
                           "<b>Team Code Blue:</b> Asmita Manral (Lead), Gautam Batra, Nikhil Gavel · DSPM IIIT Naya Raipur", styles['DocSubTitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#C53030"), spaceAfter=12))

    # Stage Instructions Callout
    intro_text = (
        "<b>Stage Choreography & Presentation Protocol:</b><br/>"
        "• <b>Total Duration:</b> 10 Minutes (~1,250 words total at 125–130 WPM cadence).<br/>"
        "• <b>Speaker Positions:</b> Asmita stands center stage (opening and closing); Gautam stands stage right by hardware & sensor diagrams; Nikhil stands stage left by Edge AI & verification panels.<br/>"
        "• <b>Gold Standard Articulation:</b> Deliver key figures with absolute deliberate clarity. Pause 1 full second after every clinical number.<br/>"
        "• <b>Strict Evidence Guardrail:</b> Never claim unverified whole-device clinical sensitivity or field accuracy. Cite simulated checks (77/77), pattern match (2,064/2,064), and public dataset replays strictly."
    )
    story.append(create_callout(intro_text, styles, bg_hex="#FFF5F5", border_hex="#FEB2B2"))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 1: ASMITA MANRAL - OPENING HOOK & THE LETHAL PROBLEM
    # =========================================================================
    story.append(Paragraph("PART 1: The Problem & Biological Mismatch", styles['SpeechSpeaker']))
    story.append(Paragraph("Speaker: Asmita Manral (Team Lead) | 0:00 – 1:45 (~220 words) | Center Stage", styles['SpeechDirection']))
    
    speech_1 = (
        "“Respected members of the jury, distinguished faculty, and colleagues.<br/><br/>"
        "Every single year in India, sudden cardiac arrest takes an estimated <b>5 to 7 lakh lives</b>. "
        "Outside the hospital, our survival rate is barely <b>1 to 5 percent</b>.<br/><br/>"
        "This tragedy is governed by an inescapable biological mismatch. "
        "When circulatory arrest occurs, irreversible brain injury begins within <b>4 to 6 minutes</b>. "
        "Yet across Indian cities and semi-urban communities, ambulance transit averages <b>20 to 40 minutes</b>. "
        "If we wait for collapse before calling for help, the biological race is lost before it begins.<br/><br/>"
        "<i>[Hold up the Sternum Pod and Wristband props]</i><br/>"
        "However, clinical cardiology reveals a vital window of hope. The Oregon Sudden Unexpected Death Study proved that <b>51% of victims—over half—experience warning symptoms in the four weeks before collapse</b>.<br/><br/>"
        "In India, this vulnerability is heightened. The ICMR-INDIAB study confirms that <b>101 million Indians live with diabetes</b>. "
        "Because diabetic neuropathy damages autonomic pain pathways, <b>one in five—over 22%—suffer from completely silent ischemia</b>. They feel no crushing chest pain; their hearts suffer silently.<br/><br/>"
        "To bridge this gap, we present <b>CardioSense: The Autonomous Sternal Sentry</b>. "
        "It is a distributed, two-node wearable Body Area Network that listens to the heart's mechanical and electrical signals on the body itself, learns each wearer's individual normal, and acts autonomously before biological collapse.<br/><br/>"
        "My teammate Gautam Batra will walk you through our sensing architecture.”"
    )
    story.append(Paragraph(speech_1, styles['SpeechBody']))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 2: GAUTAM BATRA - HARDWARE ARCHITECTURE & MOTION DENOISING
    # =========================================================================
    story.append(Paragraph("PART 2: Multi-Modal Sensing & Zero-Glue Build", styles['SpeechSpeaker']))
    story.append(Paragraph("Speaker: Gautam Batra | 1:45 – 4:45 (~370 words) | Pointing to Hardware Panels", styles['SpeechDirection']))
    
    speech_2 = (
        "“Thank you, Asmita. To understand why CardioSense succeeds where others fail, look at current technology:<br/><br/>"
        "Consumer smartwatches measure only wrist pulse and sound alarms only <i>after</i> pulse is gone. "
        "Hospital Holter patches record single-channel ECG passively for retrospective review, but they cannot intervene. "
        "Crucially, hospital patches rely on aggressive chemical adhesives. A 2024 meta-analysis in the <i>Journal of Tissue Viability</i> showed that <b>medical adhesives injure the skin of approximately 16% of hospital inpatients</b>—causing tears, blisters, and severe dermatitis.<br/><br/>"
        "We designed a zero-glue, dual-node architecture engineered for continuous comfort:<br/>"
        "<b>Node A is the Sternal Pod</b>, worn over the lower sternum via a soft chest cord or breathable undershirt cradle. "
        "It combines dry 316L medical stainless steel contacts with multi-modal physiological sensors: an ADS1292R front-end for ECG, a MAX30001 for chest bioimpedance, an LSM6DSOX 6-axis IMU capturing sternal recoil vibrations, an acoustic Knowles I2S digital microphone capturing heart sounds, and a TMP117 skin temperature sensor, managed by a dual-core Nordic nRF5340 microcontroller.<br/><br/>"
        "<b>Node B is the PulseBand</b>, worn on the wrist. It houses a MAX86141 optical PPG sensor for peripheral pulse and dual dry steel electrodes for Galvanic Skin Response, paired with an nRF52840 SoC.<br/><br/>"
        "<i>[Step to the Noise Cancellation diagram]</i><br/>"
        "The greatest obstacle in wearable biometrics is body motion. When walking, foot strikes transmit shockwaves up the skeleton, corrupting micro-cardiac signals. "
        "We solve this using <b>Dual-Node Active Motion Denoising</b>—analogous to active noise-cancelling headphones.<br/><br/>"
        "Because the arm swings in direct cadence with walking gait, the wristband accelerometer captures an uncorrupted reference of footstrike cadence. "
        "Our sternum pod uses an on-device Normalized Least Mean Squares (NLMS) adaptive filter to subtract walking vibrations in real time, demonstrating <b>approximately 24 dB of synthetic motion cancellation gain in simulation</b>.<br/><br/>"
        "If severe motion renders signals indeterminate, the Sentry pauses analysis and explicitly reports <i>'Not Monitoring'</i> rather than guessing.<br/><br/>"
        "I will now pass the stage to Nikhil Gavel to explain our on-device AI and verification.”"
    )
    story.append(Paragraph(speech_2, styles['SpeechBody']))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 3: NIKHIL GAVEL - EDGE AI, ESCALATION & SILICON VERIFICATION
    # =========================================================================
    story.append(Paragraph("PART 3: 1.9 KB Edge AI, Escalation & Silicon Proof", styles['SpeechSpeaker']))
    story.append(Paragraph("Speaker: Nikhil Gavel | 4:45 – 7:45 (~380 words) | Pointing to Silicon & Modeling", styles['SpeechDirection']))
    
    speech_3 = (
        "“Thank you, Gautam. Our intelligence runs strictly on the body, preserving privacy and eliminating dependence on cloud connectivity.<br/><br/>"
        "<i>[Point to the Silicon Card on the poster]</i><br/>"
        "We designed an ultra-compact 8-bit quantized neural network containing exactly <b>1,538 parameters</b>. "
        "It requires only <b>1.9 KB of Flash memory</b> and <b>1.3 KB of RAM</b>. "
        "Per heartbeat, it executes just <b>43,144 multiply-accumulates</b>, completing in <b>44,962 clock cycles</b>. "
        "At 64 MHz, inference finishes in well under 1 millisecond. This tiny footprint allows the main processor core to sleep over 99% of the time.<br/><br/>"
        "Every patient's cardiovascular dynamics are unique. CardioSense adapts to each wearer's individual resting baseline. "
        "On public clinical records from the European ST-T Database, adapting to individual baseline dynamics improves the ranking score from <b>0.64 to 0.80 AUROC</b>.<br/><br/>"
        "<i>[Point to the Two-Tier Escalation Timeline]</i><br/>"
        "Our alarm state machine operates in two deterministic tiers:<br/>"
        "• <b>Tier 1 (Check-in):</b> If physiological parameters drift from the learned baseline, the wristband issues only a quiet haptic vibration. No panic, no false sirens.<br/>"
        "• <b>Tier 2 (Emergency Dispatch):</b> If peripheral wrist pulse is lost AND the chest IMU confirms physical stillness for 5 seconds, an abortable <b>30-second cancel window</b> opens with audio-tactile alerts. "
        "The wearer can abort false triggers simply by holding the tactile button for 2 seconds.<br/><br/>"
        "If uncancelled after 30 seconds, the pod autonomously triggers emergency dispatch: an automated emergency call to <b>112</b> with GPS location, an <b>85 dB onboard siren</b>, and a steady <b>110 BPM metronome pacing beat</b> to guide bystanders in CPR.<br/><br/>"
        "<i>[Emphasize verification integrity]</i><br/>"
        "We verified this rigorously: <b>77 of 77 simulated test cases pass</b>, covering 35 whole-device fault modes and 22 decision checks. "
        "When translated into Verilog hardware RTL, it achieved a <b>perfect 2,064 out of 2,064 pattern match against Python</b> in Vivado simulation. "
        "Replayed on public PhysioNet NSRDB recordings, it achieved <b>99.95% beat finding</b>, and on 17.9 hours of real daily activity from the PPG-DaLiA dataset, cross-checking the chest eliminated all 13 wrist-alone false alarms.<br/><br/>"
        "As an honest engineering team, our boundary is clear: all logic is simulated and replayed on public databases; human clinical trials represent future work.<br/><br/>"
        "Asmita will now conclude with our social impact and economic viability.”"
    )
    story.append(Paragraph(speech_3, styles['SpeechBody']))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 4: ASMITA MANRAL - CLOSING, ECONOMICS & NATIONAL ALIGNMENT
    # =========================================================================
    story.append(Paragraph("PART 4: Social Impact, Costing & National Vision", styles['SpeechSpeaker']))
    story.append(Paragraph("Speaker: Asmita Manral (Team Lead) | 7:45 – 10:00 (~280 words) | Center Stage", styles['SpeechDirection']))
    
    speech_4 = (
        "“Thank you, Nikhil.<br/><br/>"
        "CardioSense is engineered for real Indian healthcare realities.<br/><br/>"
        "Our first deployment targets post-stent and post-infarction patients discharged home during their highest-risk 30-day recovery window, as well as high-risk diabetic individuals.<br/><br/>"
        "<i>[Point to the Economics section]</i><br/>"
        "Consider the economics: A commercial smartwatch with loss-of-pulse calling costs ₹39,900 at retail, while wearable defibrillators rent for lakhs per month. "
        "CardioSense's total bill of materials is <b>₹3,180 at 10,000 units</b> (~$33.50). "
        "Because our pods are fully sealed, sanitized with alcohol wipes, and reused across ~6 successive patients with washable cradles, the effective hardware cost plummets to <b>just ₹530 per patient</b>.<br/><br/>"
        "Our architecture directly advances Indian national priorities:<br/>"
        "1. <b>Indigenous Semiconductors:</b> Our 1.9 KB silicon footprint is purposefully sized to fit within India's <i>Chips to Startup (C2S)</i> programme, enabling domestic ASIC tape-outs across 305 partner institutions.<br/>"
        "2. <b>National Infrastructure:</b> It integrates directly into India's 112 Emergency Response Support System.<br/>"
        "3. <b>Regulatory Readiness:</b> Its privacy-preserving on-device architecture aligns with the Digital Personal Data Protection (DPDP) Act 2023 and CDSCO medical device investigational pathways.<br/><br/>"
        "<i>[Final resolute closing]</i><br/>"
        "CardioSense transforms cardiac monitoring from passive, post-collapse panic into proactive, autonomous protection. "
        "It is indigenous, affordable, and built to ensure that no Indian life is lost simply because help arrived too late.<br/><br/>"
        "Thank you. We are ready for your questions.”"
    )
    story.append(Paragraph(speech_4, styles['SpeechBody']))
    story.append(Spacer(1, 12))

    # Summary timing table
    time_data = [
        [Paragraph("<b>Speaker</b>", styles['TableHeader']), Paragraph("<b>Assigned Segment</b>", styles['TableHeader']), Paragraph("<b>Timing & Cadence</b>", styles['TableHeader']), Paragraph("<b>Key Visual / Poster Target</b>", styles['TableHeader'])],
        [Paragraph("<b>Asmita Manral</b><br/>(Team Lead)", styles['TableCellBold']), Paragraph("1. Lethal Problem & Mismatch<br/>• 5–7 lakh deaths, 1–5% survival<br/>• 101M diabetics, silent ischemia", styles['TableCell']), Paragraph("0:00 – 1:45<br/>(1m 45s / 220 words)", styles['TableCell']), Paragraph("Center Stage; Props in hand; Abstract & Social Impact boxes", styles['TableCell'])],
        [Paragraph("<b>Gautam Batra</b>", styles['TableCellBold']), Paragraph("2. Hardware & Denoising<br/>• 16% adhesive injury meta-analysis<br/>• Pod & Band build, ~24 dB NLMS filter", styles['TableCell']), Paragraph("1:45 – 4:45<br/>(3m 00s / 370 words)", styles['TableCell']), Paragraph("Stage Right; Circuit diagram, exploded pod view, noise filter", styles['TableCell'])],
        [Paragraph("<b>Nikhil Gavel</b>", styles['TableCellBold']), Paragraph("3. Edge AI & Verification<br/>• 1.9 KB Flash, 1.3 KB RAM, 44,962 cyc<br/>• 77/77 checks, 2,064 pattern match", styles['TableCell']), Paragraph("4:45 – 7:45<br/>(3m 00s / 380 words)", styles['TableCell']), Paragraph("Stage Left; Silicon card, 2-tier escalation timeline, test checks", styles['TableCell'])],
        [Paragraph("<b>Asmita Manral</b><br/>(Team Lead)", styles['TableCellBold']), Paragraph("4. Economics, Vision & Q&A<br/>• ₹3,180 BOM / ₹530 reuse vs ₹39,900<br/>• C2S 305 chips, 112 dispatch, CDSCO", styles['TableCell']), Paragraph("7:45 – 10:00<br/>(2m 15s / 280 words)", styles['TableCell']), Paragraph("Center Stage; Cost table, Made for India panel, defense open", styles['TableCell'])],
    ]
    t_time = Table(time_data, colWidths=[95, 175, 95, 145])
    t_time.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#C53030")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_time)

    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Also copy to download folder
    import shutil
    try:
        shutil.copy2(pdf_filename_local, pdf_filename_dl)
    except Exception as e:
        print("Note on DL copy:", e)
        
    print(f"Speech Master PDF successfully generated at: {pdf_filename_local}")

if __name__ == "__main__":
    build_speech_pdf()
