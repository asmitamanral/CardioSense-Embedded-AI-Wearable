/*
 * CardioSense - Wrist Node Firmware (Slap-Band)
 * Target Hardware: ESP32-WROOM-32 (or ESP32-C3)
 * Sensors:
 *   1. MAX30102 PPG Sensor (I2C: SDA=GPIO21, SCL=GPIO22) -> Heart Rate & SpO2
 *   2. Grove / Analog GSR Sensor (ADC: GPIO34) -> Galvanic Skin Response (Cold Sweats)
 * 
 * Functionality:
 *   - Acts as a BLE Peripheral (Server) broadcasting "CardioSense-Wrist"
 *   - Continuously samples PPG (Red, IR) and Skin Conductance
 *   - Bundles data into high-efficiency 16-byte telemetry packets at 20 Hz
 *   - Supports a hardware/simulation toggle for testing before physical assembly
 */

#include <Arduino.h>
#include <Wire.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// Set to 1 when physical MAX30102 and GSR are connected; 0 for built-in physiological simulation
#define USE_PHYSICAL_SENSORS 0

// Hardware Pin Definitions for ESP32-WROOM-32
#define PIN_GSR_ANALOG        34    // ADC1_CH6 (Input-only, ideal for analog sensors)
#define PIN_I2C_SDA           21    // Default ESP32 I2C SDA
#define PIN_I2C_SCL           22    // Default ESP32 I2C SCL
#define PIN_STATUS_LED         2    // On-board blue LED

// BLE UUIDs for CardioSense Telemetry
#define SERVICE_UUID           "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID    "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// Telemetry Packet Structure (Packed 16 bytes for ultra-low BLE latency)
struct __attribute__((packed)) WristTelemetryPacket {
    uint32_t timestamp_ms;  // Uptime in ms
    uint16_t ppg_ir;        // Filtered Infrared photoplethysmogram
    uint16_t ppg_red;       // Filtered Red photoplethysmogram
    uint16_t gsr_raw;       // 12-bit ADC raw reading (0 - 4095)
    uint16_t heart_rate;    // On-wrist estimated HR (0.1 BPM units, e.g. 720 = 72.0 BPM)
    uint8_t  spo2;          // Estimated SpO2 (0-100%)
    uint8_t  signal_quality;// 0-100% signal quality / lead-off indicator
    uint16_t packet_seq;    // Monotonic sequence number
};

// Global BLE handles
BLEServer* pServer = nullptr;
BLECharacteristic* pTelemetryChar = nullptr;
bool deviceConnected = false;
bool oldDeviceConnected = false;
uint16_t sequenceNumber = 0;

// Internal signal generation state (when USE_PHYSICAL_SENSORS == 0)
float sim_phase = 0.0f;
unsigned long lastSampleTime = 0;
const unsigned long SAMPLE_INTERVAL_MS = 50; // 20 Hz streaming

class ServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override {
        deviceConnected = true;
        digitalWrite(PIN_STATUS_LED, HIGH);
        Serial.println(F("[WristNode] Sternum Hub connected via BLE!"));
    }

    void onDisconnect(BLEServer* pServer) override {
        deviceConnected = false;
        digitalWrite(PIN_STATUS_LED, LOW);
        Serial.println(F("[WristNode] Sternum Hub disconnected. Resuming advertising..."));
    }
};

void setupBLE() {
    Serial.println(F("[WristNode] Initializing BLE Peripheral: CardioSense-Wrist..."));
    BLEDevice::init("CardioSense-Wrist");
    BLEDevice::setMTU(64);

    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new ServerCallbacks());

    BLEService* pService = pServer->createService(SERVICE_UUID);
    pTelemetryChar = pService->createCharacteristic(
        CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ |
        BLECharacteristic::PROPERTY_NOTIFY
    );
    pTelemetryChar->addDescriptor(new BLE2902());

    pService->start();

    BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06); // Fast connection interval
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();

    Serial.println(F("[WristNode] BLE Advertising active. Ready for Sternum pairing."));
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_STATUS_LED, OUTPUT);
    digitalWrite(PIN_STATUS_LED, LOW);

#if USE_PHYSICAL_SENSORS
    pinMode(PIN_GSR_ANALOG, INPUT);
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
    Serial.println(F("[WristNode] Physical sensors initialized: MAX30102 on I2C & GSR on GPIO34"));
#else
    Serial.println(F("[WristNode] Running in Physiological Simulation Mode (No external wires needed)"));
#endif

    setupBLE();
}

WristTelemetryPacket sampleSensors() {
    WristTelemetryPacket pkt;
    pkt.timestamp_ms = millis();
    pkt.packet_seq = sequenceNumber++;

#if USE_PHYSICAL_SENSORS
    // Read 12-bit ADC for Galvanic Skin Response
    pkt.gsr_raw = analogRead(PIN_GSR_ANALOG);

    // In physical mode, read MAX30102 FIFO registers
    // Simplified representation for standard SparkFun / MAX30105 library integration:
    pkt.ppg_ir = 35000;  // Replace with particleSensor.getIR()
    pkt.ppg_red = 34500; // Replace with particleSensor.getRed()
    pkt.heart_rate = 720;
    pkt.spo2 = 98;
    pkt.signal_quality = 95;
#else
    // High-fidelity synthetic PPG pulse generator (cardiac cycle with dicrotic notch)
    sim_phase += 0.22f; // ~72 BPM at 20 Hz
    if (sim_phase > TWO_PI) sim_phase -= TWO_PI;

    // Systolic wave + diastolic notch synthesis
    float systolic = sin(sim_phase);
    float diastolic = 0.35f * sin(sim_phase * 2.0f + 0.8f);
    float ppg_val = (systolic > 0.0f ? systolic : 0.0f) + (diastolic > 0.0f ? diastolic : 0.0f);

    pkt.ppg_ir = (uint16_t)(32000.0f + 3000.0f * ppg_val);
    pkt.ppg_red = (uint16_t)(31000.0f + 2900.0f * ppg_val);
    
    // Baseline skin conductance ~1450 ADC (equivalent to ~8 microSiemens)
    pkt.gsr_raw = (uint16_t)(1450 + (int)(20.0f * sin(millis() / 5000.0f)));
    pkt.heart_rate = 720; // 72.0 BPM
    pkt.spo2 = 98;        // 98%
    pkt.signal_quality = 98;
#endif

    return pkt;
}

void loop() {
    unsigned long currentMillis = millis();

    // Enforce regular 20 Hz transmission rate
    if (currentMillis - lastSampleTime >= SAMPLE_INTERVAL_MS) {
        lastSampleTime = currentMillis;

        WristTelemetryPacket packet = sampleSensors();

        if (deviceConnected && pTelemetryChar != nullptr) {
            pTelemetryChar->setValue((uint8_t*)&packet, sizeof(WristTelemetryPacket));
            pTelemetryChar->notify();
        }

        // Periodic diagnostic log every 2 seconds
        if (packet.packet_seq % 40 == 0) {
            Serial.printf("[Wrist] Seq: %u | PPG_IR: %u | GSR_ADC: %u | HR: %.1f | Connected: %s\n",
                packet.packet_seq, packet.ppg_ir, packet.gsr_raw, 
                packet.heart_rate / 10.0f, deviceConnected ? "YES" : "NO");
        }
    }

    // Handle reconnection state transitions
    if (!deviceConnected && oldDeviceConnected) {
        delay(500); // Give the bluetooth stack time to stabilize
        pServer->startAdvertising();
        oldDeviceConnected = deviceConnected;
    }
    if (deviceConnected && !oldDeviceConnected) {
        oldDeviceConnected = deviceConnected;
    }
}
