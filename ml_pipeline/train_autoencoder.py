"""
CardioSense: Embedded TinyML Autoencoder Trainer
Architecture: 8 -> 4 -> 2 -> 4 -> 8 (Bottleneck Anomaly Detector)
Trains directly using NumPy with Adam optimizer for zero-dependency portability.
Exports:
1. 'model_weights.h' - Production C/C++ header for ESP32 firmware
2. 'model_meta.json' - Evaluation metrics, thresholds, and clinical stats
"""

import numpy as np
import json
import os
from synthetic_physiology_generator import (
    generate_normal_baseline,
    generate_cardiac_precursors,
    normalize_features,
    FEATURE_NAMES,
    BOUNDS
)

def relu(x):
    return np.maximum(0.0, x)

def relu_deriv(x):
    return (x > 0.0).astype(np.float32)

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -15.0, 15.0)))

def sigmoid_deriv(out):
    return out * (1.0 - out)

class TinyMLAutoencoder:
    def __init__(self, in_dim=8, h1_dim=4, latent_dim=2, seed=42):
        rng = np.random.default_rng(seed)
        
        # He initialization for ReLU / Xavier for Sigmoid
        self.W1 = rng.normal(0, np.sqrt(2.0 / in_dim), (in_dim, h1_dim)).astype(np.float32)
        self.b1 = np.zeros(h1_dim, dtype=np.float32)

        self.W2 = rng.normal(0, np.sqrt(2.0 / h1_dim), (h1_dim, latent_dim)).astype(np.float32)
        self.b2 = np.zeros(latent_dim, dtype=np.float32)

        self.W3 = rng.normal(0, np.sqrt(2.0 / latent_dim), (latent_dim, h1_dim)).astype(np.float32)
        self.b3 = np.zeros(h1_dim, dtype=np.float32)

        self.W4 = rng.normal(0, np.sqrt(2.0 / (h1_dim + in_dim)), (h1_dim, in_dim)).astype(np.float32)
        self.b4 = np.zeros(in_dim, dtype=np.float32)

    def forward(self, X):
        # Layer 1
        self.z1 = X @ self.W1 + self.b1
        self.a1 = relu(self.z1)

        # Layer 2 (Bottleneck)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = relu(self.z2)

        # Layer 3
        self.z3 = self.a2 @ self.W3 + self.b3
        self.a3 = relu(self.z3)

        # Layer 4 (Output Reconstruction)
        self.z4 = self.a3 @ self.W4 + self.b4
        self.a4 = sigmoid(self.z4)
        return self.a4

    def compute_loss(self, X, X_hat):
        # Mean Squared Error
        return np.mean((X - X_hat) ** 2)

    def compute_sample_mse(self, X, X_hat):
        # Per-sample reconstruction error (MSE across 8 features)
        return np.mean((X - X_hat) ** 2, axis=1)

    def backward(self, X, X_hat):
        N = X.shape[0]

        # dLoss / da4
        da4 = (2.0 / (N * X.shape[1])) * (X_hat - X)
        dz4 = da4 * sigmoid_deriv(X_hat)

        dW4 = self.a3.T @ dz4
        db4 = np.sum(dz4, axis=0)

        da3 = dz4 @ self.W4.T
        dz3 = da3 * relu_deriv(self.z1 if False else self.z3)

        dW3 = self.a2.T @ dz3
        db3 = np.sum(dz3, axis=0)

        da2 = dz3 @ self.W3.T
        dz2 = da2 * relu_deriv(self.z2)

        dW2 = self.a1.T @ dz2
        db2 = np.sum(dz2, axis=0)

        da1 = dz2 @ self.W2.T
        dz1 = da1 * relu_deriv(self.z1)

        dW1 = X.T @ dz1
        db1 = np.sum(dz1, axis=0)

        return (dW1, db1, dW2, db2, dW3, db3, dW4, db4)

def train(model, X_train, epochs=250, batch_size=64, lr=0.008):
    # Adam optimizer moments
    params = [model.W1, model.b1, model.W2, model.b2, model.W3, model.b3, model.W4, model.b4]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    beta1 = 0.9
    beta2 = 0.999
    eps = 1e-8

    t = 0
    N = X_train.shape[0]

    for epoch in range(1, epochs + 1):
        perm = np.random.permutation(N)
        X_shuffled = X_train[perm]

        for i in range(0, N, batch_size):
            t += 1
            batch = X_shuffled[i:i + batch_size]
            X_hat = model.forward(batch)
            grads = model.backward(batch, X_hat)

            # Adam update step
            for p, g, m_arr, v_arr in zip(params, grads, m, v):
                m_arr[:] = beta1 * m_arr + (1 - beta1) * g
                v_arr[:] = beta2 * v_arr + (1 - beta2) * (g ** 2)
                m_hat = m_arr / (1 - beta1 ** t)
                v_hat = v_arr / (1 - beta2 ** t)
                p -= lr * m_hat / (np.sqrt(v_hat) + eps)

        if epoch % 50 == 0 or epoch == 1:
            preds = model.forward(X_train)
            mse = model.compute_loss(X_train, preds)
            print(f"Epoch {epoch:3d}/{epochs} | Baseline Train MSE Loss: {mse:.6f}")

def export_c_header(model, threshold, filepath):
    """Exports model weights, biases, and thresholds into C++ header for ESP32."""
    def fmt_2d(arr):
        rows = []
        for r in arr:
            row_str = ", ".join(f"{val:+.7f}f" for val in r)
            rows.append(f"    {{ {row_str} }}")
        return ",\n".join(rows)

    def fmt_1d(arr):
        return ", ".join(f"{val:+.7f}f" for val in arr)

    header = f"""#ifndef MODEL_WEIGHTS_H
#define MODEL_WEIGHTS_H

// Auto-generated TinyML Autoencoder Model for CardioSense
// Input: 8 features -> Latent: 2 features -> Output: 8 features

#define AE_INPUT_DIM   8
#define AE_HIDDEN_DIM  4
#define AE_LATENT_DIM  2

// Baseline Anomaly Detection Threshold (MSE)
// Samples with Reconstruction MSE > AE_ANOMALY_THRESHOLD are flagged as potential precursors
const float AE_ANOMALY_THRESHOLD = {threshold:.6f}f;

// Layer 1: 8 -> 4 (ReLU)
const float W1[AE_INPUT_DIM][AE_HIDDEN_DIM] = {{
{fmt_2d(model.W1)}
}};
const float b1[AE_HIDDEN_DIM] = {{ {fmt_1d(model.b1)} }};

// Layer 2: 4 -> 2 (ReLU Bottleneck)
const float W2[AE_HIDDEN_DIM][AE_LATENT_DIM] = {{
{fmt_2d(model.W2)}
}};
const float b2[AE_LATENT_DIM] = {{ {fmt_1d(model.b2)} }};

// Layer 3: 2 -> 4 (ReLU)
const float W3[AE_LATENT_DIM][AE_HIDDEN_DIM] = {{
{fmt_2d(model.W3)}
}};
const float b3[AE_HIDDEN_DIM] = {{ {fmt_1d(model.b3)} }};

// Layer 4: 4 -> 8 (Sigmoid Output)
const float W4[AE_HIDDEN_DIM][AE_INPUT_DIM] = {{
{fmt_2d(model.W4)}
}};
const float b4[AE_INPUT_DIM] = {{ {fmt_1d(model.b4)} }};

#endif // MODEL_WEIGHTS_H
"""
    with open(filepath, "w") as f:
        f.write(header)
    print(f"Exported C++ header to: {filepath}")

def main():
    print("=== Training CardioSense Embedded Autoencoder ===")
    
    # 1. Generate normal physiological training data (representing personalized baseline)
    raw_train = generate_normal_baseline(n_samples=5000, seed=42)
    raw_test_normal = generate_normal_baseline(n_samples=1000, seed=999)
    raw_test_precursor = generate_cardiac_precursors(n_samples=1000, seed=777)

    X_train = normalize_features(raw_train)
    X_val_norm = normalize_features(raw_test_normal)
    X_val_precursor = normalize_features(raw_test_precursor)

    # 2. Train Autoencoder
    model = TinyMLAutoencoder(in_dim=8, h1_dim=4, latent_dim=2, seed=123)
    train(model, X_train, epochs=250, batch_size=64, lr=0.010)

    # 3. Evaluate Reconstruction Error
    norm_preds = model.forward(X_val_norm)
    norm_errors = model.compute_sample_mse(X_val_norm, norm_preds)

    prec_preds = model.forward(X_val_precursor)
    prec_errors = model.compute_sample_mse(X_val_precursor, prec_preds)

    # Anomaly threshold: 99th percentile of normal baseline
    threshold = float(np.percentile(norm_errors, 99.0))
    false_positives = np.mean(norm_errors > threshold) * 100.0
    true_positives = np.mean(prec_errors > threshold) * 100.0

    print("\n--- Model Evaluation ---")
    print(f"Normal Baseline Mean Reconstruction Error: {np.mean(norm_errors):.6f}")
    print(f"Cardiac Precursor Mean Reconstruction Error: {np.mean(prec_errors):.6f}")
    print(f"Separation Ratio: {np.mean(prec_errors) / np.mean(norm_errors):.2f}x error amplification on precursor crisis")
    print(f"Calibrated Anomaly Threshold (99th percentile): {threshold:.6f}")
    print(f"Precursor Sensitivity (Detection Rate): {true_positives:.2f}%")
    print(f"Normal Baseline Specificity: {100.0 - false_positives:.2f}% (False Alarm Rate: {false_positives:.2f}%)")

    # 4. Export to firmware directory and ML metadata
    firmware_header_path = os.path.join("..", "firmware", "sternum_hub", "model_weights.h")
    export_c_header(model, threshold, firmware_header_path)

    # Also keep a local copy in ml_pipeline
    export_c_header(model, threshold, "model_weights.h")

    meta = {
        "features": FEATURE_NAMES,
        "bounds": BOUNDS,
        "threshold": threshold,
        "normal_mean_mse": float(np.mean(norm_errors)),
        "precursor_mean_mse": float(np.mean(prec_errors)),
        "sensitivity": true_positives,
        "specificity": 100.0 - false_positives
    }
    with open("model_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("Saved metadata to: model_meta.json")

if __name__ == "__main__":
    main()
