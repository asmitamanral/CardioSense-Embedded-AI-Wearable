# CardioSense: Hardware Bill of Materials (BOM) & Pinout Specification

This document details the complete hardware configuration, circuit connections, and component sourcing for building the **CardioSense Two-Node Wearable** using standard **ESP32-WROOM-32** development boards.

---

## 1. System Architecture & Node Division (Option A: Sternum Hub)

```
+-------------------------------------------------------------+
|               NODE 1: WRIST SLAP-BAND                       |
|  - ESP32-WROOM-32 (BLE Peripheral Mode)                     |
|  - MAX30102 Pulse Oximeter & Heart Rate Sensor (I2C)        |
|  - Grove / Analog Galvanic Skin Response (GSR) Sensor (ADC) |
|  - 3.7V 400mAh LiPo Battery + TP4056 USB-C Charger          |
+-------------------------------------------------------------+
                                │
                                │ 20 Hz Synchronized BLE Stream
                                ▼
+-------------------------------------------------------------+
|               NODE 2: STERNUM LOCKET (CENTRAL HUB)          |
|  - ESP32-WROOM-32 (Dual-Core Central Coordinator & TinyML)  |
|  - MPU6050 6-Axis IMU (Chest Respiration & Motion Gating)   |
|  - Secondary MAX30102 Pulse Oximeter (Chest Contact)        |
|  - SIM800L GSM/GPRS Cellular Module (SMS & Voice Telephony) |
|  - u-blox Neo-6M GPS Module (Location Coordinates)          |
|  - ERM Vibration Motor + 85dB Piezo Buzzer                  |
|  - Momentary Push-to-Cancel Tactile Switch                  |
|  - Tri-color Status LEDs (Normal, Pre-Alert, Siren)         |
|  - 3.7V 1000mAh LiPo Battery + Step-Down Buck Converter     |
|  - Breakaway Safety Lanyard & Magnetic Clothing Clip        |
+-------------------------------------------------------------+
```

---

## 2. Bill of Materials (BOM) & Indian Market Sourcing

Components are standard, off-the-shelf maker modules widely available in India (e.g., Robu.in, QuartzComponents, Evelta):

| Component | Description / Function | Target Source | Est. Cost (INR ₹) | Est. Cost (USD $) |
|---|---|---|---|---|
| **ESP32-WROOM-32 Dev Board (x2)** | Dual-Core 240MHz MCU, BLE 5.0, Wi-Fi | Robu.in / Amazon.in | ₹700 (₹350 ea) | $8.40 |
| **MAX30102 Sensor Module (x2)** | Optical PPG (Red + IR) for HR & SpO2 | Robu.in | ₹440 (₹220 ea) | $5.30 |
| **Grove GSR Skin Sensor** | Electrodermal activity / cold sweat detection | QuartzComponents | ₹320 | $3.85 |
| **MPU-6050 6-Axis IMU** | Triple-axis accelerometer & gyro (respiration) | Robu.in | ₹130 | $1.55 |
| **SIM800L GSM/GPRS Module** | Quad-band cellular for emergency SMS & Call | Robu.in / Evelta | ₹450 | $5.40 |
| **u-blox Neo-6M GPS Module** | GPS receiver with ceramic patch antenna | Robu.in | ₹420 | $5.05 |
| **TP4056 LiPo Chargers (x2)** | 1A Lithium battery charge module with protection | QuartzComponents | ₹50 (₹25 ea) | $0.60 |
| **3.7V LiPo 400mAh (Wrist)** | Compact lightweight lithium pouch cell | Robu.in | ₹220 | $2.65 |
| **3.7V LiPo 1000mAh (Sternum)**| High-capacity cell for GSM burst power | Robu.in | ₹380 | $4.55 |
| **LM2596 / Buck Regulator** | Provides clean 4.0V / 2A burst power for SIM800L | Robu.in | ₹75 | $0.90 |
| **Piezo Buzzer & ERM Motor** | Dual alert: 85dB sounder + haptic coin vibrator | QuartzComponents | ₹60 | $0.70 |
| **Passives & Mechanics** | Slap-band silicone strap, push button, LEDs, lanyard | Local / Amazon | ₹150 | $1.80 |
| **TOTAL ESTIMATED BOM** | | | **₹3,395** | **~$40.75** |

*Note: For mass manufacturing (1,000+ units), consolidating components onto custom PCBs with bare ESP32-WROOM modules reduces total unit BOM to under ₹1,800 ($21.50).*

---

## 3. Node 1: Wrist Slap-Band Pinout Table

The Wrist Node reads optical pulsatile data (PPG) and galvanic skin conductance, streaming them as a BLE Peripheral.

| Peripheral | Sensor Pin | ESP32 GPIO | Description / Notes |
|---|---|---|---|
| **MAX30102 (PPG)** | `VCC` | `3V3` | Regulated 3.3V power |
| | `GND` | `GND` | Common ground |
| | `SDA` | `GPIO 21` | Standard I2C Data line |
| | `SCL` | `GPIO 22` | Standard I2C Clock line |
| | `INT` | `GPIO 19` (Optional) | Data ready interrupt |
| **Grove GSR Sensor** | `VCC` | `3V3` | 3.3V excitation voltage |
| | `GND` | `GND` | Common ground |
| | `SIG` | `GPIO 34` | ADC1 Channel 6 (Input-only pin, zero digital crosstalk) |
| **Status LED** | Anode | `GPIO 2` | Onboard blue LED (Heartbeat / BLE Connected) |

---

## 4. Node 2: Sternum Locket Hub Pinout Table

The Sternum Locket serves as the BLE Central receiver, housing the primary ESP32 coordinator, chest wall accelerometer, secondary PPG, SIM800L cellular modem, Neo-6M GPS, and alert actuators.

| Peripheral | Module Pin | ESP32 GPIO | Description / Notes |
|---|---|---|---|
| **MPU-6050 (IMU)** | `VCC` | `3V3` | 3.3V Power |
| | `GND` | `GND` | Common ground |
| | `SDA` | `GPIO 21` | Shared I2C Data line |
| | `SCL` | `GPIO 22` | Shared I2C Clock line |
| **Secondary MAX30102** | `VCC` / `GND` | `3V3` / `GND` | Shared power |
| | `SDA` / `SCL` | `GPIO 21` / `22` | Secondary sternum PPG (I2C address toggle) |
| **SIM800L GSM Modem**| `VCC` | External 4.0V Buck | **CRITICAL**: SIM800L draws up to 2A bursts during TX; do NOT power from ESP32 3.3V pin |
| | `GND` | Common `GND` | Must share ground with ESP32 |
| | `TXD` | `GPIO 16` (`RX2`) | UART2 Receive |
| | `RXD` | `GPIO 17` (`TX2`) | UART2 Transmit (Use voltage divider: 3.3V logic) |
| **Neo-6M GPS** | `VCC` | `3V3` | 3.3V Power |
| | `GND` | `GND` | Common ground |
| | `TXD` | `GPIO 32` (`RX1`) | UART1 Receive |
| | `RXD` | `GPIO 33` (`TX1`) | UART1 Transmit |
| **Haptic Motor** | Gate / Base | `GPIO 18` | Transistor / MOSFET switch driving ERM coin motor |
| **Piezo Siren** | Positive | `GPIO 19` | Direct or transistor-driven buzzer (PWM / tone) |
| **Cancel Button** | Pin 1 | `GPIO 4` | Momentary tactile switch (Active LOW, internal pull-up) |
| | Pin 2 | `GND` | Ground |
| **LED Green (Normal)**| Anode | `GPIO 25` | 330Ω resistor to ground |
| **LED Amber (Stage 1)**| Anode | `GPIO 26` | 330Ω resistor to ground |
| **LED Red (Stage 2)** | Anode | `GPIO 27` | 330Ω resistor to ground |

---

## 5. Critical Hardware Wiring & Power Notes

> [!CAUTION]
> **SIM800L Power Supply Requirement**:
> The SIM800L operates between **3.7V and 4.2V** (nominal 4.0V). Connecting it directly to the ESP32's 3.3V regulator will cause the modem to brown out and reset during network handshakes or SMS dispatch due to 2A current bursts. 
> Always power the SIM800L from the 3.7V LiPo battery stepped through a dedicated high-current Schottky diode or a small buck converter, with a **1000µF low-ESR electrolytic capacitor** soldered across the SIM800L `VCC` and `GND` pins.

> [!IMPORTANT]
> **Sensor Placement Guidelines**:
> 1. **Wrist Slap-Band**: The MAX30102 optical window must press firmly against the radial artery on the inside of the wrist or dorsal wrist surface. The two GSR finger/band electrodes must maintain gentle, constant contact with palmar or ventral wrist skin where sweat gland density is highest.
> 2. **Sternum Locket**: Fasten the clip securely to clothing against the mid-sternum. Contact with the sternal body eliminates soft-tissue damping, allowing the MPU6050 accelerometer to record clean micromotion oscillations (0.1–0.5 Hz) corresponding to chest-wall respiration.
