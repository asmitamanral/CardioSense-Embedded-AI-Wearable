#ifndef AUTOENCODER_ENGINE_H
#define AUTOENCODER_ENGINE_H

#include <Arduino.h>
#include <math.h>
#include "model_weights.h"

class TinyMLAutoencoderEngine {
private:
    float z1[AE_HIDDEN_DIM];
    float a1[AE_HIDDEN_DIM];

    float z2[AE_LATENT_DIM];
    float a2[AE_LATENT_DIM];

    float z3[AE_HIDDEN_DIM];
    float a3[AE_HIDDEN_DIM];

    float z4[AE_INPUT_DIM];
    float a4[AE_INPUT_DIM];

    // Online adaptive baseline tracking (running mean and variance of normal MSE)
    float baseline_mean_mse = 0.005f;
    float baseline_var_mse = 0.0001f;
    bool is_calibrated = false;
    uint32_t calibration_samples = 0;
    const uint32_t REQUIRED_CALIBRATION_SAMPLES = 300; // ~15 seconds of clean baseline

    static inline float relu(float x) {
        return (x > 0.0f) ? x : 0.0f;
    }

    static inline float sigmoid(float x) {
        // Fast clamped sigmoid approximation
        if (x < -10.0f) return 0.0f;
        if (x > 10.0f) return 1.0f;
        return 1.0f / (1.0f + expf(-x));
    }

public:
    TinyMLAutoencoderEngine() {
        memset(z1, 0, sizeof(z1));
        memset(a1, 0, sizeof(a1));
        memset(z2, 0, sizeof(z2));
        memset(a2, 0, sizeof(a2));
        memset(z3, 0, sizeof(z3));
        memset(a3, 0, sizeof(a3));
        memset(z4, 0, sizeof(z4));
        memset(a4, 0, sizeof(a4));
    }

    // Forward inference pass: Computes reconstructed 8-feature vector and returns Mean Squared Error (MSE)
    float forward(const float* normalized_in, float* reconstructed_out) {
        // Layer 1: 8 -> 4 (ReLU)
        for (int j = 0; j < AE_HIDDEN_DIM; j++) {
            float sum = b1[j];
            for (int i = 0; i < AE_INPUT_DIM; i++) {
                sum += normalized_in[i] * W1[i][j];
            }
            z1[j] = sum;
            a1[j] = relu(sum);
        }

        // Layer 2: 4 -> 2 (ReLU Latent Bottleneck)
        for (int j = 0; j < AE_LATENT_DIM; j++) {
            float sum = b2[j];
            for (int i = 0; i < AE_HIDDEN_DIM; i++) {
                sum += a1[i] * W2[i][j];
            }
            z2[j] = sum;
            a2[j] = relu(sum);
        }

        // Layer 3: 2 -> 4 (ReLU)
        for (int j = 0; j < AE_HIDDEN_DIM; j++) {
            float sum = b3[j];
            for (int i = 0; i < AE_LATENT_DIM; i++) {
                sum += a2[i] * W3[i][j];
            }
            z3[j] = sum;
            a3[j] = relu(sum);
        }

        // Layer 4: 4 -> 8 (Sigmoid Output Reconstruction)
        float total_mse = 0.0f;
        for (int j = 0; j < AE_INPUT_DIM; j++) {
            float sum = b4[j];
            for (int i = 0; i < AE_HIDDEN_DIM; i++) {
                sum += a3[i] * W4[i][j];
            }
            z4[j] = sum;
            float out = sigmoid(sum);
            a4[j] = out;
            if (reconstructed_out != nullptr) {
                reconstructed_out[j] = out;
            }

            float err = normalized_in[j] - out;
            total_mse += (err * err);
        }

        return total_mse / (float)AE_INPUT_DIM;
    }

    // Adaptive Baseline Updater
    // Calibrates wearer's individual quiescent physiology
    void updateBaseline(float mse, float motion_svm) {
        // Only update baseline during low-motion periods to learn true resting state
        if (motion_svm < 0.25f && mse < (AE_ANOMALY_THRESHOLD * 1.5f)) {
            if (calibration_samples < REQUIRED_CALIBRATION_SAMPLES) {
                calibration_samples++;
                // Running Welford algorithm for initial mean
                float delta = mse - baseline_mean_mse;
                baseline_mean_mse += delta / calibration_samples;
                if (calibration_samples >= REQUIRED_CALIBRATION_SAMPLES) {
                    is_calibrated = true;
                }
            } else {
                // Exponential moving average for long-term drift adaptation
                baseline_mean_mse = 0.998f * baseline_mean_mse + 0.002f * mse;
            }
        }
    }

    // Evaluates Risk Score with Motion-Artifact Gating
    // Returns: 
    //   - is_anomaly: true if elevated cardiac precursor risk detected
    //   - anomaly_score: Normalized risk score (0.0 to 100.0)
    //   - mse: raw autoencoder reconstruction error
    struct AnomalyResult {
        bool is_anomaly;
        float anomaly_score;
        float raw_mse;
        bool is_motion_artifact;
    };

    AnomalyResult evaluateRisk(const float* normalized_in, float raw_motion_svm) {
        float recon[AE_INPUT_DIM];
        float mse = forward(normalized_in, recon);

        AnomalyResult res;
        res.raw_mse = mse;

        // Dynamic motion threshold:
        // When motion_svm is elevated (e.g. running or walking fast), physiological arousal 
        // (elevated HR and sweating) is expected. Dynamic threshold scales with physical movement.
        float dynamic_threshold = AE_ANOMALY_THRESHOLD;
        if (raw_motion_svm > 0.40f) {
            // Scale tolerance during exercise: vigorous motion justifies higher physiological deviations
            dynamic_threshold *= (1.0f + 2.5f * (raw_motion_svm - 0.40f));
        }

        // Motion artifact gating:
        // Extreme motion (>2.2g) often loosens optical contact. Flag as motion artifact rather than arrest.
        res.is_motion_artifact = (raw_motion_svm > 2.2f);

        // Core Anomaly Decision:
        // A precursor event occurs when multi-signal discordance (MSE) exceeds the dynamic threshold
        // while the user is NOT undergoing extreme violent mechanical impact.
        if (!res.is_motion_artifact && (mse > dynamic_threshold)) {
            res.is_anomaly = true;
            // Map MSE excess to 0-100% risk score
            float ratio = mse / dynamic_threshold;
            res.anomaly_score = constrain((ratio - 1.0f) * 50.0f + 50.0f, 50.0f, 100.0f);
        } else {
            res.is_anomaly = false;
            res.anomaly_score = constrain((mse / dynamic_threshold) * 50.0f, 0.0f, 49.9f);
            updateBaseline(mse, raw_motion_svm);
        }

        return res;
    }

    bool isCalibrated() const { return is_calibrated; }
    float getBaselineMean() const { return baseline_mean_mse; }
    void getLatentEmbedding(float* latent_out) const {
        latent_out[0] = a2[0];
        latent_out[1] = a2[1];
    }
};

#endif // AUTOENCODER_ENGINE_H
