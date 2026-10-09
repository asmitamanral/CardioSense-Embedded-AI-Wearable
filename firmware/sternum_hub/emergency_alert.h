#ifndef EMERGENCY_ALERT_H
#define EMERGENCY_ALERT_H

#include <Arduino.h>
#include "cardio_features.h"

// Alert System State Machine
enum AlertState {
    STATE_NORMAL,               // Physiological baseline intact
    STATE_STAGE_1_PREALERT,     // Early anomaly detected; 30s abortable local warning
    STATE_STAGE_2_ESCALATED,    // Unaborted crisis; continuous siren + SMS + Voice Call dispatched
    STATE_ABORTED               // Canceled by wearer or bystander button press
};

// Hardware Output Pins for Sternum Hub (ESP32-WROOM-32)
#define PIN_BUZZER             19   // Piezo siren / alert buzzer
#define PIN_HAPTIC             18   // ERM / LRA haptic motor driver
#define PIN_CANCEL_BTN          4   // Momentary push button to abort false alarms (active LOW)
#define PIN_LED_GREEN          25   // Heartbeat / Normal LED
#define PIN_LED_AMBER          26   // Stage 1 Pre-alert LED
#define PIN_LED_RED            27   // Stage 2 Emergency Siren LED

// UART Configuration for SIM800L GSM and Neo-6M GPS
#define GSM_SERIAL_BAUD     9600
#define GPS_SERIAL_BAUD     9600
#define STAGE_1_TIMEOUT_MS  30000   // 30-second cancellation window

class EmergencyAlertManager {
private:
    AlertState current_state = STATE_NORMAL;
    unsigned long stage1_start_time = 0;
    unsigned long last_haptic_toggle = 0;
    bool haptic_on = false;
    HardwareSerial* gsmSerial = nullptr;
    HardwareSerial* gpsSerial = nullptr;

    String emergency_phone_number = "+919876543210"; // Default emergency caregiver contact
    float last_latitude = 12.9716f;                  // Default / latest GPS latitude (Bengaluru)
    float last_longitude = 77.5946f;                 // Default / latest GPS longitude

    void triggerHapticPulse() {
        unsigned long now = millis();
        if (now - last_haptic_toggle > 500) { // 1 Hz urgent pulsing
            last_haptic_toggle = now;
            haptic_on = !haptic_on;
            digitalWrite(PIN_HAPTIC, haptic_on ? HIGH : LOW);
            if (haptic_on) {
                // Warning beep
                tone(PIN_BUZZER, 1800, 150);
            }
        }
    }

    void sendATCommand(const String& cmd, unsigned long timeout_ms = 2000) {
        if (!gsmSerial) return;
        gsmSerial->println(cmd);
        Serial.printf("[GSM-TX] %s\n", cmd.c_str());
        unsigned long start = millis();
        while (millis() - start < timeout_ms) {
            if (gsmSerial->available()) {
                String line = gsmSerial->readStringUntil('\n');
                Serial.printf("[GSM-RX] %s\n", line.c_str());
                if (line.indexOf("OK") != -1 || line.indexOf("ERROR") != -1) break;
            }
            yield();
        }
    }

public:
    EmergencyAlertManager() {}

    void init(HardwareSerial* pGsm, HardwareSerial* pGps, const String& phone_num = "") {
        gsmSerial = pGsm;
        gpsSerial = pGps;
        if (phone_num.length() > 5) {
            emergency_phone_number = phone_num;
        }

        pinMode(PIN_BUZZER, OUTPUT);
        pinMode(PIN_HAPTIC, OUTPUT);
        pinMode(PIN_CANCEL_BTN, INPUT_PULLUP);
        pinMode(PIN_LED_GREEN, OUTPUT);
        pinMode(PIN_LED_AMBER, OUTPUT);
        pinMode(PIN_LED_RED, OUTPUT);

        digitalWrite(PIN_BUZZER, LOW);
        digitalWrite(PIN_HAPTIC, LOW);
        digitalWrite(PIN_LED_GREEN, HIGH);
        digitalWrite(PIN_LED_AMBER, LOW);
        digitalWrite(PIN_LED_RED, LOW);

        Serial.println(F("[AlertManager] Initialized pins & GSM/GPS telemetry handles."));
    }

    AlertState getState() const { return current_state; }

    void triggerStage1(float risk_score, const PhysiologicalState& vitals) {
        if (current_state == STATE_NORMAL || current_state == STATE_ABORTED) {
            current_state = STATE_STAGE_1_PREALERT;
            stage1_start_time = millis();

            digitalWrite(PIN_LED_GREEN, LOW);
            digitalWrite(PIN_LED_AMBER, HIGH);
            digitalWrite(PIN_LED_RED, LOW);

            Serial.printf("[ALERT] *** STAGE 1 PRE-ALERT ACTIVATED *** Risk: %.1f%%\n", risk_score);
            Serial.println(F("[ALERT] 30-Second Abort Window Started! Press Button to Cancel."));
        }
    }

    void abortAlert(const char* reason = "Wearer canceled") {
        current_state = STATE_ABORTED;
        digitalWrite(PIN_BUZZER, LOW);
        digitalWrite(PIN_HAPTIC, LOW);
        noTone(PIN_BUZZER);

        digitalWrite(PIN_LED_GREEN, HIGH);
        digitalWrite(PIN_LED_AMBER, LOW);
        digitalWrite(PIN_LED_RED, LOW);

        Serial.printf("[ALERT] Stage 1 Aborted: %s. Returning to baseline surveillance.\n", reason);
    }

    // Dispatches Location-Tagged Emergency SMS via SIM800L
    void dispatchEmergencySMS(const PhysiologicalState& vitals, float risk_score) {
        Serial.println(F("[GSM] Initiating Emergency Location-Tagged SMS Dispatch..."));

        sendATCommand("AT+CMGF=1", 1000); // Set Text Mode
        delay(200);

        String cmd = "AT+CMGS=\"" + emergency_phone_number + "\"";
        if (gsmSerial) {
            gsmSerial->println(cmd);
            delay(300);

            // Construct Clinical Emergency SMS Payload
            String sms = "EMERGENCY: CardioSense Pre-Arrest Risk Alert!\n";
            sms += "Risk Score: " + String(risk_score, 1) + "%\n";
            sms += "Vitals: HR=" + String(vitals.hr, 0) + "bpm, ";
            sms += "SpO2=" + String(vitals.spo2, 0) + "%, ";
            sms += "Resp=" + String(vitals.resp_rate, 0) + "brpm, ";
            sms += "GSR_Slope=+" + String(vitals.gsr_slope, 1) + "uS/m\n";
            sms += "GPS Map: https://maps.google.com/?q=" + String(last_latitude, 5) + "," + String(last_longitude, 5);

            gsmSerial->print(sms);
            gsmSerial->write(26); // Ctrl+Z to send
            Serial.println(F("[GSM] SMS payload written and queued:"));
            Serial.println(sms);
        }
    }

    // Initiates automated emergency voice telephone call via SIM800L DTMF / Tone
    void dispatchEmergencyVoiceCall() {
        Serial.println(F("[GSM] Initiating Automatic Caregiver Voice Call via SIM800L..."));
        String dialCmd = "ATD" + emergency_phone_number + ";";
        sendATCommand(dialCmd, 5000);

        // Play warning DTMF sequence into the audio line upon connection
        delay(3000);
        sendATCommand("AT+VTD=4", 1000); // 400ms DTMF duration
        sendATCommand("AT+VTS=\"9,9,9,1,1,1,9,9,9\"", 3000); // Audible alert burst over telephony line
        Serial.println(F("[GSM] Emergency voice call active with audio alert pattern."));
    }

    void triggerStage2(const PhysiologicalState& vitals, float risk_score) {
        current_state = STATE_STAGE_2_ESCALATED;

        digitalWrite(PIN_LED_GREEN, LOW);
        digitalWrite(PIN_LED_AMBER, LOW);
        digitalWrite(PIN_LED_RED, HIGH);
        digitalWrite(PIN_HAPTIC, HIGH);

        // Continuous high-decibel warble siren on local buzzer
        tone(PIN_BUZZER, 3200);

        Serial.println(F("=========================================================="));
        Serial.println(F(" [CRITICAL] STAGE 2 EMERGENCY ESCALATED! DISPATCHING ALERTS"));
        Serial.println(F("=========================================================="));

        // 1. Dispatch Location-Tagged SMS
        dispatchEmergencySMS(vitals, risk_score);

        // 2. Dispatch Automated Emergency Voice Call (DTMF / Tone)
        dispatchEmergencyVoiceCall();
    }

    void update(const PhysiologicalState& vitals, float risk_score) {
        // Read cancel push-button (active LOW with internal pull-up)
        if (digitalRead(PIN_CANCEL_BTN) == LOW) {
            if (current_state == STATE_STAGE_1_PREALERT || current_state == STATE_STAGE_2_ESCALATED) {
                abortAlert("Physical cancel button pressed");
                delay(400); // Debounce
                return;
            }
        }

        // Handle Stage 1 countdown and transitions
        if (current_state == STATE_STAGE_1_PREALERT) {
            triggerHapticPulse();

            unsigned long elapsed = millis() - stage1_start_time;
            if (elapsed >= STAGE_1_TIMEOUT_MS) {
                // Countdown expired without wearer cancellation -> Escalation to Stage 2!
                triggerStage2(vitals, risk_score);
            } else {
                // Print countdown remaining every 5 seconds
                uint32_t sec_remaining = (STAGE_1_TIMEOUT_MS - elapsed) / 1000;
                if ((elapsed % 5000) < 60) {
                    Serial.printf("[ALERT] Abort window countdown: %u seconds remaining...\n", sec_remaining);
                }
            }
        } else if (current_state == STATE_NORMAL) {
            digitalWrite(PIN_LED_GREEN, (millis() % 2000 < 100) ? HIGH : LOW); // Heartbeat flash
            digitalWrite(PIN_LED_AMBER, LOW);
            digitalWrite(PIN_LED_RED, LOW);
            digitalWrite(PIN_HAPTIC, LOW);
            noTone(PIN_BUZZER);
        }
    }

    void setCoordinates(float lat, float lon) {
        last_latitude = lat;
        last_longitude = lon;
    }
};

#endif // EMERGENCY_ALERT_H
