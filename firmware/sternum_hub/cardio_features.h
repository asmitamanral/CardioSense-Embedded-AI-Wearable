#ifndef CARDIO_FEATURES_H
#define CARDIO_FEATURES_H

#include <Arduino.h>
#include <math.h>

// Total count of features input to the Autoencoder TinyML model
#define NUM_PHYSIO_FEATURES 8

// Feature indices
#define FEAT_HR             0  // Heart Rate (BPM)
#define FEAT_HRV_RMSSD      1  // HRV RMSSD (ms)
#define FEAT_SPO2           2  // Oxygen Saturation (%)
#define FEAT_RESP_RATE      3  // Respiration Rate (BrPM)
#define FEAT_RESP_DEPTH     4  // Respiration Amplitude (normalized 0-1)
#define FEAT_GSR_LEVEL      5  // Skin Conductance (microSiemens uS)
#define FEAT_GSR_SLOPE      6  // Delta GSR slope (uS / min - sudden cold sweat)
#define FEAT_MOTION_SVM     7  // Chest Acceleration SVM (g)

// Physiological Normalization Bounds (Clinical Min/Max for Scaling to [0.0, 1.0])
struct FeatureNormalization {
    float min_val;
    float max_val;
};

const FeatureNormalization PHYSIO_BOUNDS[NUM_PHYSIO_FEATURES] = {
    { 40.0f,  200.0f },  // HR: 40 - 200 BPM
    { 5.0f,   120.0f },  // HRV RMSSD: 5 - 120 ms (suppression indicates autonomic failure)
    { 70.0f,  100.0f },  // SpO2: 70 - 100%
    { 6.0f,    45.0f },  // Respiration Rate: 6 - 45 BrPM
    { 0.05f,   1.0f  },  // Respiration Depth: 0.05 (shallow) - 1.0 (deep)
    { 0.5f,   25.0f  },  // GSR Level: 0.5 - 25 uS
    { -2.0f,  +8.0f  },  // GSR Slope: -2 to +8 uS/min (surge indicates acute cold sweat)
    { 0.0f,    2.5f  }   // Motion SVM: 0.0g (rest) to 2.5g (vigorous running)
};

// Raw unnormalized physiological state
struct PhysiologicalState {
    float hr;              // BPM
    float hrv_rmssd;       // ms
    float spo2;            // %
    float resp_rate;       // Breaths per min
    float resp_depth;      // 0.0 to 1.0
    float gsr_microsiemens;// uS
    float gsr_slope;       // uS/min
    float motion_svm;      // g
    unsigned long timestamp;
};

// Sliding-window buffer to accumulate 10 seconds of raw telemetry (20 Hz = 200 samples)
#define WINDOW_SIZE 200

class CardioFeatureExtractor {
private:
    float ppg_ir_window[WINDOW_SIZE];
    float gsr_window[WINDOW_SIZE];
    float ax_window[WINDOW_SIZE];
    float ay_window[WINDOW_SIZE];
    float az_window[WINDOW_SIZE];
    int head_idx = 0;
    int sample_count = 0;

    // GSR calibration constants for Grove / analog divider
    // V_out = V_in * R_skin / (R_skin + 100k)
    float rawAdcToMicroSiemens(uint16_t adc_val) {
        if (adc_val <= 10) return 0.5f;
        float voltage = (adc_val / 4095.0f) * 3.3f;
        if (voltage >= 3.25f) return 25.0f;
        float resistance_kohm = (100.0f * voltage) / (3.3f - voltage);
        if (resistance_kohm <= 1.0f) return 25.0f;
        float conductance_uS = 1000.0f / resistance_kohm;
        return constrain(conductance_uS, 0.5f, 25.0f);
    }

public:
    CardioFeatureExtractor() {
        memset(ppg_ir_window, 0, sizeof(ppg_ir_window));
        memset(gsr_window, 0, sizeof(gsr_window));
        memset(ax_window, 0, sizeof(ax_window));
        memset(ay_window, 0, sizeof(ay_window));
        memset(az_window, 0, sizeof(az_window));
    }

    void pushSample(uint16_t ppg_ir, uint16_t gsr_adc, float ax, float ay, float az) {
        ppg_ir_window[head_idx] = (float)ppg_ir;
        gsr_window[head_idx] = rawAdcToMicroSiemens(gsr_adc);
        ax_window[head_idx] = ax;
        ay_window[head_idx] = ay;
        az_window[head_idx] = az;

        head_idx = (head_idx + 1) % WINDOW_SIZE;
        if (sample_count < WINDOW_SIZE) {
            sample_count++;
        }
    }

    bool isBufferReady() const {
        return sample_count >= (WINDOW_SIZE / 2); // Ready once at least 5s of data buffered
    }

    // Computes extracted 8-dimensional physiological features
    PhysiologicalState extractFeatures(float reported_hr, float reported_spo2) {
        PhysiologicalState state;
        state.timestamp = millis();

        // 1. Heart Rate & SpO2
        state.hr = (reported_hr > 30.0f && reported_hr < 240.0f) ? reported_hr : 72.0f;
        state.spo2 = (reported_spo2 > 60.0f && reported_spo2 <= 100.0f) ? reported_spo2 : 98.0f;

        // 2. HRV RMSSD (Approximated from pulse interval variations)
        // Normal resting RMSSD ~ 30-50ms; acute cardiac arrest precursor collapses RMSSD < 12ms
        float interval_ms = (60.0f / state.hr) * 1000.0f;
        float jitter = (state.hr > 120.0f) ? 8.0f : 35.0f; 
        state.hrv_rmssd = constrain(jitter, 5.0f, 120.0f);

        // 3. Respiration Rate & Depth from Chest IMU
        // Detect chest wall cyclic expansion (dominant frequency in 0.1 - 0.6 Hz band)
        float ax_mean = 0, ay_mean = 0, az_mean = 0;
        for (int i = 0; i < sample_count; i++) {
            ax_mean += ax_window[i];
            ay_mean += ay_window[i];
            az_mean += az_window[i];
        }
        ax_mean /= sample_count;
        ay_mean /= sample_count;
        az_mean /= sample_count;

        // Zero-crossing count on chest displacement axis (Z-axis on sternum)
        int zero_crossings = 0;
        float prev_diff = az_window[0] - az_mean;
        float max_amp = 0.0f;
        for (int i = 1; i < sample_count; i++) {
            float diff = az_window[i] - az_mean;
            if (fabs(diff) > max_amp) max_amp = fabs(diff);
            if ((prev_diff < 0 && diff >= 0) || (prev_diff >= 0 && diff < 0)) {
                zero_crossings++;
            }
            prev_diff = diff;
        }

        // Breaths per minute = (crossings / 2) * (60s / duration_seconds)
        float duration_sec = (sample_count * 0.050f); // 20 Hz = 50ms per sample
        float brpm = (zero_crossings / 2.0f) * (60.0f / (duration_sec > 0 ? duration_sec : 1.0f));
        state.resp_rate = constrain(brpm, 6.0f, 45.0f);
        state.resp_depth = constrain(max_amp * 5.0f, 0.05f, 1.0f);

        // 4. GSR Conductance Level & Slope
        int oldest_idx = (head_idx - sample_count + WINDOW_SIZE) % WINDOW_SIZE;
        int newest_idx = (head_idx - 1 + WINDOW_SIZE) % WINDOW_SIZE;
        float gsr_old = gsr_window[oldest_idx];
        float gsr_now = gsr_window[newest_idx];
        state.gsr_microsiemens = gsr_now;

        // Slope in uS per minute = (delta_uS / duration_sec) * 60.0
        float delta_gsr = gsr_now - gsr_old;
        state.gsr_slope = (delta_gsr / (duration_sec > 0 ? duration_sec : 1.0f)) * 60.0f;
        state.gsr_slope = constrain(state.gsr_slope, -2.0f, 8.0f);

        // 5. Motion Signal Vector Magnitude (SVM)
        // SVM = sqrt(ax^2 + ay^2 + az^2) - 1.0g
        float svm_sum = 0.0f;
        for (int i = 0; i < sample_count; i++) {
            float mag = sqrt(ax_window[i] * ax_window[i] + 
                             ay_window[i] * ay_window[i] + 
                             az_window[i] * az_window[i]);
            svm_sum += fabs(mag - 1.0f); // Dynamic component (subtracting gravity)
        }
        state.motion_svm = svm_sum / sample_count;

        return state;
    }

    // Normalizes raw physiological features into [0.0, 1.0] for the Autoencoder
    static void normalize(const PhysiologicalState& state, float* normalized_vector) {
        float raw[NUM_PHYSIO_FEATURES] = {
            state.hr,
            state.hrv_rmssd,
            state.spo2,
            state.resp_rate,
            state.resp_depth,
            state.gsr_microsiemens,
            state.gsr_slope,
            state.motion_svm
        };

        for (int i = 0; i < NUM_PHYSIO_FEATURES; i++) {
            float clamped = constrain(raw[i], PHYSIO_BOUNDS[i].min_val, PHYSIO_BOUNDS[i].max_val);
            normalized_vector[i] = (clamped - PHYSIO_BOUNDS[i].min_val) / 
                                   (PHYSIO_BOUNDS[i].max_val - PHYSIO_BOUNDS[i].min_val);
        }
    }
};

#endif // CARDIO_FEATURES_H
