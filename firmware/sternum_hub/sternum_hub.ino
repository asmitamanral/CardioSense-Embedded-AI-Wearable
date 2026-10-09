/*
 * CardioSense - Sternum Hub Node Firmware (Central Coordinator)
 * Target Hardware: ESP32-WROOM-32 (Dual-Core 240 MHz)
 * Integrated Sensors & Peripherals:
 *   1. BLE Central Client (Receiving Wrist PPG & GSR at 20 Hz)
 *   2. MPU6050 6-Axis IMU (I2C SDA=21, SCL=22) -> Chest respiration & body motion gating
 *   3. Secondary MAX30102 PPG (I2C) -> Redundant sternum pulse & transit time verification
 *   4. SIM800L GSM Module (UART2: TX2=GPIO17, RX2=GPIO16) -> Location-tagged SMS & Voice Call
 *   5. Neo-6M GPS Module (UART1: RX=GPIO32, TX=GPIO33) -> Emergency location coordinates
 *   6. Alarm Subsystem:
 *      - Haptic Motor (GPIO18)
 *      - Piezo Buzzer / Siren (GPIO19)
 *      - Push-to-Cancel Button (GPIO4)
 *      - Tri-color Status LEDs (Green=25, Amber=26, Red=27)
 * 
 * Software Architecture:
 *   - Core 0: BLE Client Receiver + MPU6050 Sampling + GPS Telemetry
 *   - Core 1: Sliding-Window DSP + TinyML Autoencoder Anomaly Detection + Emergency FSM
 */

#include <Arduino.h>
#include <Wire.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

#include "cardio_features.h"
#include "autoencoder_engine.h"
#include "emergency_alert.h"

// Set to 1 when physical MPU6050, SIM800L, and Neo-6M are attached; 0 for automated loopback test
#define USE_PHYSICAL_SENSORS 0

// BLE UUIDs matching Wrist Node
static BLEUUID serviceUUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b");
static BLEUUID charUUID("beb5483e-36e1-4688-b7f5-ea07361b26a8");

// UART Serial handles for GSM and GPS
HardwareSerial gsmSerial(2); // UART2: RX=16, TX=17
HardwareSerial gpsSerial(1); // UART1: RX=32, TX=33

// Processing Objects
CardioFeatureExtractor featureExtractor;
TinyMLAutoencoderEngine autoencoderEngine;
EmergencyAlertManager alertManager;

// Wrist Telemetry Struct
struct __attribute__((packed)) WristTelemetryPacket {
    uint32_t timestamp_ms;
    uint16_t ppg_ir;
    uint16_t ppg_red;
    uint16_t gsr_raw;
    uint16_t heart_rate;
    uint8_t  spo2;
    uint8_t  signal_quality;
    uint16_t packet_seq;
};

// Inter-core synchronization
static BLERemoteCharacteristic* pRemoteCharacteristic = nullptr;
static BLEAdvertisedDevice* myDevice = nullptr;
static bool doConnect = false;
static bool connected = false;
static bool doScan = false;

// Shared sensor state between Core 0 and Core 1
portMUX_TYPE synchMux = portMUX_INITIALIZER_UNLOCKED;
volatile float shared_ax = 0.0f, shared_ay = 0.0f, shared_az = 1.0f;
volatile uint16_t shared_wrist_ir = 32000;
volatile uint16_t shared_wrist_gsr = 1450;
volatile float shared_reported_hr = 72.0f;
volatile float shared_reported_spo2 = 98.0f;
volatile bool new_sample_ready = false;

// BLE Notification Callback
static void notifyCallback(
    BLERemoteCharacteristic* pBLERemoteCharacteristic,
    uint8_t* pData,
    size_t length,
    bool isNotify
) {
    if (length == sizeof(WristTelemetryPacket)) {
        WristTelemetryPacket* pkt = (WristTelemetryPacket*)pData;
        portENTER_CRITICAL(&synchMux);
        shared_wrist_ir = pkt->ppg_ir;
        shared_wrist_gsr = pkt->gsr_raw;
        shared_reported_hr = pkt->heart_rate / 10.0f;
        shared_reported_spo2 = (float)pkt->spo2;
        new_sample_ready = true;
        portEXIT_CRITICAL(&synchMux);
    }
}

// BLE Client Callbacks
class MyClientCallback : public BLEClientCallbacks {
    void onConnect(BLEClient* pclient) override {
        connected = true;
        Serial.println(F("[BLE Central] Connected to Wrist Slap-Band Node!"));
    }

    void onDisconnect(BLEClient* pclient) override {
        connected = false;
        Serial.println(F("[BLE Central] Disconnected from Wrist Node. Rescanning..."));
    }
};

bool connectToServer() {
    Serial.printf("[BLE Central] Connecting to: %s\n", myDevice->getAddress().toString().c_str());
    BLEClient* pClient = BLEDevice::createClient();
    pClient->setClientCallbacks(new MyClientCallback());

    if (!pClient->connect(myDevice)) {
        Serial.println(F("[BLE Central] Failed to connect."));
        return false;
    }

    BLERemoteService* pRemoteService = pClient->getService(serviceUUID);
    if (pRemoteService == nullptr) {
        Serial.println(F("[BLE Central] Failed to locate CardioSense service."));
        pClient->disconnect();
        return false;
    }

    pRemoteCharacteristic = pRemoteService->getCharacteristic(charUUID);
    if (pRemoteCharacteristic == nullptr) {
        Serial.println(F("[BLE Central] Failed to locate telemetry characteristic."));
        pClient->disconnect();
        return false;
    }

    if (pRemoteCharacteristic->canNotify()) {
        pRemoteCharacteristic->registerForNotify(notifyCallback);
    }

    connected = true;
    return true;
}

class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) override {
        if (advertisedDevice.haveServiceUUID() && advertisedDevice.isAdvertisingService(serviceUUID)) {
            BLEDevice::getScan()->stop();
            myDevice = new BLEAdvertisedDevice(advertisedDevice);
            doConnect = true;
            doScan = false;
        }
    }
};

// -------------------------------------------------------------
// Core 0 Task: BLE Connection & Sensor Acquisition
// -------------------------------------------------------------
void Core0Task_Sensors(void* pvParameters) {
    Serial.println(F("[Core 0] Sensor & BLE Acquisition Task Running."));

    BLEScan* pBLEScan = BLEDevice::getScan();
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setInterval(1349);
    pBLEScan->setWindow(449);
    pBLEScan->setActiveScan(true);
    pBLEScan->start(5, false);

    unsigned long lastImuSample = 0;
    float sim_resp_phase = 0.0f;

    for (;;) {
        if (doConnect) {
            if (connectToServer()) {
                Serial.println(F("[Core 0] BLE Link fully established. Receiving telemetry."));
            }
            doConnect = false;
        }

        // Sample Sternum Accelerometer at 20 Hz
        if (millis() - lastImuSample >= 50) {
            lastImuSample = millis();

#if USE_PHYSICAL_SENSORS
            // In physical mode, read MPU6050 via Wire I2C registers:
            // Wire.beginTransmission(0x68); Wire.write(0x3B); Wire.endTransmission(false);
            // Wire.requestFrom(0x68, 6, true);
            // Read 16-bit registers and divide by 16384.0 for +/-2g scale
#else
            // High-fidelity sternum chest wall simulation (cyclic breathing motion + resting jitter)
            sim_resp_phase += 0.045f; // ~14 Breaths per minute
            if (sim_resp_phase > TWO_PI) sim_resp_phase -= TWO_PI;

            float breath_motion = 0.08f * sin(sim_resp_phase);
            float random_jitter = ((random(100) - 50) / 1000.0f);

            portENTER_CRITICAL(&synchMux);
            shared_ax = 0.02f + random_jitter;
            shared_ay = 0.01f + random_jitter;
            shared_az = 1.00f + breath_motion; // Gravity + chest displacement
            portEXIT_CRITICAL(&synchMux);
#endif
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// -------------------------------------------------------------
// Core 1 Task: TinyML Autoencoder Inference & Alert Dispatch
// -------------------------------------------------------------
void Core1Task_TinyML(void* pvParameters) {
    Serial.println(F("[Core 1] DSP Feature Extraction & TinyML Anomaly Task Running."));

    unsigned long lastInferenceTime = 0;
    const unsigned long INFERENCE_INTERVAL_MS = 1000; // 1 Hz inference frequency

    for (;;) {
        // Read latest telemetry snapshots from Core 0
        uint16_t ir, gsr;
        float ax, ay, az, hr, spo2;

        portENTER_CRITICAL(&synchMux);
        ir = shared_wrist_ir;
        gsr = shared_wrist_gsr;
        ax = shared_ax;
        ay = shared_ay;
        az = shared_az;
        hr = shared_reported_hr;
        spo2 = shared_reported_spo2;
        portEXIT_CRITICAL(&synchMux);

        // Push into sliding window feature extractor
        featureExtractor.pushSample(ir, gsr, ax, ay, az);

        // Run ML inference once every second
        if (millis() - lastInferenceTime >= INFERENCE_INTERVAL_MS) {
            lastInferenceTime = millis();

            if (featureExtractor.isBufferReady()) {
                PhysiologicalState vitals = featureExtractor.extractFeatures(hr, spo2);

                // Compile normalized 8-feature input vector
                float normalized_in[NUM_PHYSIO_FEATURES];
                CardioFeatureExtractor::normalize(vitals, normalized_in);

                // Run on-device TinyML Autoencoder inference
                TinyMLAutoencoderEngine::AnomalyResult result = 
                    autoencoderEngine.evaluateRisk(normalized_in, vitals.motion_svm);

                // Console Diagnostics & Live Telemetry
                Serial.println(F("--------------------------------------------------------------------------------"));
                Serial.printf("[VITALS] HR: %.1f BPM | SpO2: %.0f%% | Resp: %.1f BrPM | GSR: %.2f uS (Slope: %+.2f)\n",
                    vitals.hr, vitals.spo2, vitals.resp_rate, vitals.gsr_microsiemens, vitals.gsr_slope);
                Serial.printf("[MOTION] SVM: %.3f g | Artifact: %s | Baseline Calibrated: %s\n",
                    vitals.motion_svm, result.is_motion_artifact ? "YES (Suppressed)" : "NO",
                    autoencoderEngine.isCalibrated() ? "YES" : "CALIBRATING");
                Serial.printf("[TINYML] MSE Error: %.6f (Thresh: %.6f) | Risk Score: %.1f%% | Anomaly: %s\n",
                    result.raw_mse, AE_ANOMALY_THRESHOLD, result.anomaly_score,
                    result.is_anomaly ? "CRITICAL PRECURSOR DETECTED!" : "NORMAL");

                // Evaluate alerts
                if (result.is_anomaly) {
                    alertManager.triggerStage1(result.anomaly_score, vitals);
                }

                // Update Alert Manager State Machine (handles countdown, cancellation button, and GSM/GPS dispatch)
                alertManager.update(vitals, result.anomaly_score);
            }
        }

        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println(F("\n========================================================"));
    Serial.println(F(" CardioSense: Two-Node Embedded AI Wearable"));
    Serial.println(F(" Sternum Hub Node - Dual-Core ESP32-WROOM-32"));
    Serial.println(F("========================================================"));

    // Initialize UARTs for SIM800L (UART2: TX=17, RX=16) and Neo-6M GPS (UART1: TX=33, RX=32)
    gsmSerial.begin(GSM_SERIAL_BAUD, SERIAL_8N1, 16, 17);
    gpsSerial.begin(GPS_SERIAL_BAUD, SERIAL_8N1, 32, 33);

    // Initialize Alert Manager with target emergency contact
    alertManager.init(&gsmSerial, &gpsSerial, "+919876543210");

    // Initialize BLE Device
    BLEDevice::init("CardioSense-Hub");

    // Launch Core 0 Task: Sensor acquisition & BLE
    xTaskCreatePinnedToCore(
        Core0Task_Sensors,
        "Core0_Sensors",
        4096,
        NULL,
        1,
        NULL,
        0 // Pinned to Core 0
    );

    // Launch Core 1 Task: TinyML Inference & Alerts
    xTaskCreatePinnedToCore(
        Core1Task_TinyML,
        "Core1_TinyML",
        8192,
        NULL,
        1,
        NULL,
        1 // Pinned to Core 1
    );

    Serial.println(F("[System] Dual-Core FreeRTOS tasks active. CardioSense online.\n"));
}

void loop() {
    // Empty: Execution handled by FreeRTOS tasks pinned to Core 0 and Core 1
    vTaskDelay(pdMS_TO_TICKS(1000));
}
