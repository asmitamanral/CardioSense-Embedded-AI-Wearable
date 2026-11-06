import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from pdf_generator_base import NumberedCanvas, get_custom_styles, create_callout, DOWNLOAD_DIR

def build_speech_pdf():
    pdf_filename = os.path.join(DOWNLOAD_DIR, "CardioSense_Symposium_Speech_Master.pdf")
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
    story.append(Paragraph("CardioSense: Symposium Complete Spoken Master Script", styles['DocTitle']))
    story.append(Paragraph("Verbatim Stage Choreography & Speaking Delivery for Full Presentation<br/><b>Assigned Core Segments:</b> Topic 1, Topic 2, Topic 3, Topic 7, and Topic 11", styles['DocSubTitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#C53030"), spaceAfter=14))

    # Stage Instruction Callout
    intro_text = "<b>Stage Delivery Blueprint:</b> Target cadence is approximately <b>125 to 130 words per minute</b> with deliberate, steady articulation. Never rush through the numbers—pause for exactly one full second after stating key clinical metrics to allow the jury to absorb the clinical gravity. Physical cues, poster pointing targets, and vocal inflections are highlighted in brackets."
    story.append(create_callout(intro_text, styles, bg_hex="#FFF5F5", border_hex="#FEB2B2"))
    story.append(Spacer(1, 14))

    # =========================================================================
    # PART 1: THE OPENING HOOK (TOPIC 1)
    # =========================================================================
    story.append(Paragraph("SEGMENT 1: The Lethal Problem & The Time Mismatch", styles['SpeechSpeaker']))
    story.append(Paragraph("[Target Timing: 0:00 – 0:50 | Stand tall, make direct eye contact with the lead professor or director]", styles['SpeechDirection']))
    
    speech_1 = (
        "“Respected members of the jury, distinguished faculty, and guests.<br/><br/>"
        "Sudden Cardiac Arrest claims over <b>350,000 lives</b> every single year in India alone. "
        "In our country, the out-of-hospital survival rate is <b>below 5%</b>.<br/><br/>"
        "The reason for this tragic loss of life is not a lack of medicine; it is a brutal, lethal mathematical mismatch:<br/>"
        "When a human heart stops beating, irreversible biological brain death begins in just <b>4 minutes</b>.<br/>"
        "Yet, across our cities and rural districts, an emergency ambulance takes anywhere from <b>20 to 40 minutes</b> to reach the patient.<br/><br/>"
        "<i>[Pause for 1 second. Lower pitch slightly for emphasis.]</i><br/>"
        "Waiting for a patient to collapse, and only then sounding an alarm, is biologically futile. "
        "You cannot bridge a 30-minute ambulance transit gap with a 4-minute biological survival clock.”"
    )
    story.append(Paragraph(speech_1, styles['SpeechBody']))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 2: THE CURRENT FAILURES (TOPIC 2)
    # =========================================================================
    story.append(Paragraph("SEGMENT 2: Why Smartwatches & Hospital Patches Fail", styles['SpeechSpeaker']))
    story.append(Paragraph("[Target Timing: 0:50 – 1:45 | Gesture toward the competitor comparison section on the poster]", styles['SpeechDirection']))
    
    speech_2 = (
        "“So why hasn't existing wearable technology solved this crisis?<br/><br/>"
        "Look at consumer smartwatches, like the Apple Watch or Galaxy Watch. They detect pulse loss <b>after</b> the heart has already stopped pumping. "
        "An alert delivered when a patient is already lying unconscious on the floor is biologically too late. Furthermore, single-wrist sensors suffer from massive motion false alarms and are completely blind to respiration.<br/><br/>"
        "Now look at clinical hospital patches, like the Zio Patch. They rely on wet hydrogel glue to conduct electrical signals. "
        "Within 48 hours, body heat evaporates the water in the gel, signal impedance spikes, and the chemical adhesive causes painful skin maceration and contact dermatitis. "
        "Over <b>85% of elderly cardiac patients abandon them</b> in under a week.<br/><br/>"
        "And finally, wearable defibrillator garments like the ZOLL LifeVest cost an astronomical <b>4,000 dollars every single month</b>—making them entirely inaccessible for Indian families.<br/><br/>"
        "We are trapped between consumer toys that alert too late, and medical patches that patients refuse to wear.”"
    )
    story.append(Paragraph(speech_2, styles['SpeechBody']))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 3: THE BIOLOGICAL WARNING SIGNS (TOPIC 3)
    # =========================================================================
    story.append(Paragraph("SEGMENT 3: The 1-to-6-Hour Biological Warning Signs", styles['SpeechSpeaker']))
    story.append(Paragraph("[Target Timing: 1:45 – 2:50 | Point firmly to the Pathophysiology diagram on the poster]", styles['SpeechDirection']))
    
    speech_3 = (
        "“The core clinical breakthrough behind CardioSense is a foundational medical reality: "
        "<b>Sudden cardiac arrest is rarely an instantaneous event.</b><br/><br/>"
        "In over 50% of victims, the cardiovascular and autonomic nervous systems emit clear, measurable distress precursors <b>15 to 30 minutes before collapse</b>.<br/><br/>"
        "When coronary arteries occlude and the heart muscle is starved of oxygen, five physiological signals cascade across the body simultaneously:<br/>"
        "<b>First:</b> The Pre-Ejection Period lengthens. The ischemic left ventricle becomes weak and sluggish, taking over <b>140 milliseconds</b> just to generate enough pressure to force open the aortic valve.<br/>"
        "<b>Second:</b> Sternal recoil shockwaves from aortic valve ejection collapse by more than <b>50%</b>.<br/>"
        "<b>Third:</b> The autonomic cold-sweat surge. As blood pressure falls, the sympathetic nervous system clamps peripheral vessels while firing sweat glands, creating heavy ionic sweating on ice-cold skin.<br/>"
        "<b>Fourth:</b> Arterial blood oxygen plummets below <b>88%</b>.<br/>"
        "<b>And Fifth:</b> Breathing deteriorates into rapid, shallow, agonal gasps.<br/><br/>"
        "<i>[Emphasize with open hand gesture]</i><br/>"
        "Crucially, these five distress signals occur <b>while the patient is at physical rest</b>. "
        "When captured together, they represent the definitive biological signature of an impending cardiac arrest.”"
    )
    story.append(Paragraph(speech_3, styles['SpeechBody']))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 4: MOTION DENOISING (TOPIC 7)
    # =========================================================================
    story.append(Paragraph("SEGMENT 4: Cancelling Footsteps (Dual-Node DSP)", styles['SpeechSpeaker']))
    story.append(Paragraph("[Target Timing: 2:50 – 3:45 | Show your physical slap-band and locket props in hand]", styles['SpeechDirection']))
    
    speech_4 = (
        "“Now, the single greatest engineering challenge in wearable medicine is movement. "
        "Whenever a person walks, heel-strike shockwaves travel up the skeletal column into the chest, completely corrupting subtle heart recoil vibrations.<br/><br/>"
        "We solved this using an elegant physical principle: <b>Dual-Node Active Noise Cancellation</b>, working exactly like noise-cancelling headphones.<br/><br/>"
        "Because our wristband swings in cadence with the gait, its accelerometer captures an uncorrupted reference signal of the walking rhythm. "
        "Our sternum pod uses this wrist reference to model the body's physical vibration transfer and <b>mathematically subtracts the footstep shockwaves in real time</b>.<br/><br/>"
        "This algorithm executes on-device in just <b>28 microseconds</b>, consumes barely <b>38 microwatts</b> of power, and achieves over <b>28 decibels of noise rejection</b>.<br/>"
        "It completely strips away walking shockwaves and shivering tremors, isolating pure, diagnostic cardiac recoil even while the patient is actively moving.”"
    )
    story.append(Paragraph(speech_4, styles['SpeechBody']))
    story.append(Spacer(1, 10))

    # =========================================================================
    # PART 5: HEAD-TO-HEAD COMPARISON & CLOSE (TOPIC 11)
    # =========================================================================
    story.append(Paragraph("SEGMENT 5: Head-to-Head Comparison & The Final Pitch", styles['SpeechSpeaker']))
    story.append(Paragraph("[Target Timing: 3:45 – 4:35 | Point to the Comparison Table and conclude with conviction]", styles['SpeechDirection']))
    
    speech_5 = (
        "“To see the complete clinical and economic picture, look at our competitors head-to-head:<br/><br/>"
        "Consumer smartwatches tell you that you've collapsed only after your pulse has ceased.<br/>"
        "<b>CardioSense gives you a 15-to-30-minute early warning window before collapse occurs.</b><br/><br/>"
        "Hospital patches require sticky, single-use adhesives that cost 300 dollars and get thrown in the trash after 7 days.<br/>"
        "<b>CardioSense uses medical-grade 316L dry stainless steel contacts that never dry out, never cause dermatitis, and can be sanitized with alcohol wipes to be reused across multiple patients for just 5 dollars and 58 cents per patient.</b><br/><br/>"
        "And while the ZOLL LifeVest rents for ₹3.5 lakh every month, our entire functional benchtop prototype costs <b>under ₹4,800</b>, scaling to a mass-production kit cost of <b>just 33 dollars</b>.<br/><br/>"
        "<i>[Final concluding delivery, steady and confident]</i><br/>"
        "CardioSense is not another wearable gadget. It is a zero-adhesive, proactive early-warning Body Area Network, engineered from first principles to save Indian lives before the biological window expires.<br/><br/>"
        "Thank you. We now welcome your questions.”"
    )
    story.append(Paragraph(speech_5, styles['SpeechBody']))
    story.append(Spacer(1, 14))

    # Summary timing table
    time_data = [
        [Paragraph("<b>Presentation Segment</b>", styles['TableHeader']), Paragraph("<b>Assigned Topic</b>", styles['TableHeader']), Paragraph("<b>Allocated Window</b>", styles['TableHeader']), Paragraph("<b>Key Goal</b>", styles['TableHeader'])],
        [Paragraph("1. The Lethal Problem", styles['TableCellBold']), Paragraph("Topic 1", styles['TableCell']), Paragraph("0:00 – 0:50 (50s)", styles['TableCell']), Paragraph("Establish urgency & 4-min vs 30-min transit gap", styles['TableCell'])],
        [Paragraph("2. Why Current Devices Fail", styles['TableCellBold']), Paragraph("Topic 2", styles['TableCell']), Paragraph("0:50 – 1:45 (55s)", styles['TableCell']), Paragraph("Expose smartwatch, patch & LifeVest flaws", styles['TableCell'])],
        [Paragraph("3. Biological Warning Signs", styles['TableCellBold']), Paragraph("Topic 3", styles['TableCell']), Paragraph("1:45 – 2:50 (65s)", styles['TableCell']), Paragraph("Prove PEP, AO collapse & cold sweat at rest", styles['TableCell'])],
        [Paragraph("4. Footstep Noise Cancellation", styles['TableCellBold']), Paragraph("Topic 7", styles['TableCell']), Paragraph("2:50 – 3:45 (55s)", styles['TableCell']), Paragraph("Deliver headphone analogy & 28 µs / 28 dB proof", styles['TableCell'])],
        [Paragraph("5. Head-to-Head Comparison", styles['TableCellBold']), Paragraph("Topic 11", styles['TableCell']), Paragraph("3:45 – 4:35 (50s)", styles['TableCell']), Paragraph("Dismantle competitors & state $5.58 reuse win", styles['TableCell'])],
    ]
    t_time = Table(time_data, colWidths=[120, 80, 110, 190])
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
    print(f"Speech Master PDF successfully generated at: {pdf_filename}")

if __name__ == "__main__":
    build_speech_pdf()
