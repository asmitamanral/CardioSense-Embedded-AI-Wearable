// ============================================================================
// Module: ecg_motion_canceller_and_gate.v
// Project: CardioSense — Dual-Node Pre-Arrest Prediction Wearable
// Track: Make in Silicon Ideathon (Track 1 / Silicon Validation)
//
// Functionality:
//   1. 4-Tap Adaptive LMS Noise Canceller:
//      Takes raw noisy chest ECG [d_noisy] and correlated wrist motion [x_ref].
//      Predicts footstep/motion artifact y_est = SUM(w_i * x_ref[n-i])
//      Subtracts artifact: e_clean = d_noisy - y_est
//      Updates filter weights: w_i[n+1] = w_i[n] + mu * e_clean * x_ref[n-i]
//
//   2. Multi-Modal Anomaly & Motion Gate:
//      - If motion magnitude > MOTION_THRESH: Gating active (suppress false alarm)
//      - If motion == 0 (Rest) AND clean ECG shows ST-elevation / QRS anomaly
//        AND SpO2 < 88% AND Cold Sweat > THRESH:
//        -> ASSERT EMERGENCY_ALERT
// ============================================================================

`timescale 1ns / 1ps

module ecg_motion_canceller_and_gate #(
    parameter DATA_WIDTH    = 16,     // Q1.15 fixed-point or 16-bit signed ADC counts
    parameter ACC_WIDTH     = 16,     // 16-bit accelerometer SVM
    parameter NUM_TAPS      = 4,      // 4-tap FIR adaptive filter
    parameter SHIFT_MU      = 6       // Step size mu = 1/(2^6) = 0.015625 for stability
)(
    input  wire                   clk,
    input  wire                   rst_n,
    input  wire                   sample_valid,   // 200 Hz ADC sample clock tick
    
    // Raw Biological Inputs (Synchronized via BLE)
    input  wire signed [DATA_WIDTH-1:0] raw_chest_ecg, // d[n]: ECG + Motion Shockwave
    input  wire signed [DATA_WIDTH-1:0] wrist_motion,  // x[n]: Reference footstep cadence
    input  wire        [ACC_WIDTH-1:0]  chest_svm,     // Chest motion magnitude (g)
    input  wire        [7:0]            spo2_level,    // Arterial SpO2 (0 - 100%)
    input  wire        [15:0]           gsr_conductance,// Skin sweat level (uS)
    
    // Clean Filtered Outputs
    output reg  signed [DATA_WIDTH-1:0] clean_ecg,     // e[n] = d[n] - y[n]
    output reg  signed [DATA_WIDTH-1:0] estimated_artifact, // y[n]
    
    // Safety & Decision Status Flags
    output reg                    motion_gate_active,  // High = Walking detected, alarms gated
    output reg                    ecg_ischemia_detected, // High = Clean ECG exceeds anomaly envelope
    output reg                    emergency_alert      // High = Pre-Arrest Crisis Verified AT REST
);

    // Constant Clinical Decision Bounds
    localparam [ACC_WIDTH-1:0]  MOTION_REST_THRESH = 16'd200; // 0.20g in fixed integer
    localparam [7:0]           SPO2_CRITICAL_BOUND = 8'd88;   // 88% arterial hypoxia
    localparam [15:0]          GSR_COLD_SWEAT_BOUND= 16'd350; // High sympathetic sweat
    localparam signed [DATA_WIDTH-1:0] ECG_ANOMALY_BOUND = 16'd450; // Pathologic ST displacement

    // Adaptive Filter Delay Line & Weights
    reg signed [DATA_WIDTH-1:0] x_pipe [0:NUM_TAPS-1];
    reg signed [DATA_WIDTH-1:0] weights [0:NUM_TAPS-1];

    integer i;

    // Intermediate 32-bit accumulation for multiply-accumulate (MAC)
    reg signed [31:0] dot_product;
    reg signed [31:0] weight_update;
    reg signed [DATA_WIDTH-1:0] err_calc;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            clean_ecg             <= 16'sd0;
            estimated_artifact    <= 16'sd0;
            motion_gate_active    <= 1'b0;
            ecg_ischemia_detected <= 1'b0;
            emergency_alert       <= 1'b0;
            
            for (i = 0; i < NUM_TAPS; i = i + 1) begin
                x_pipe[i]  <= 16'sd0;
                weights[i] <= 16'sd0;
            end
        end 
        else if (sample_valid) begin
            // -------------------------------------------------------------
            // STEP 1: Shift wrist reference into filter delay pipeline
            // -------------------------------------------------------------
            x_pipe[0] <= wrist_motion;
            for (i = 1; i < NUM_TAPS; i = i + 1) begin
                x_pipe[i] <= x_pipe[i-1];
            end

            // -------------------------------------------------------------
            // STEP 2: Compute predicted footstep shockwave: y[n] = SUM(w_i * x[n-i])
            // -------------------------------------------------------------
            dot_product = 32'sd0;
            for (i = 0; i < NUM_TAPS; i = i + 1) begin
                dot_product = dot_product + (weights[i] * x_pipe[i]);
            end
            
            // Truncate Q-format product back to 16 bits
            estimated_artifact <= dot_product[30:15];

            // -------------------------------------------------------------
            // STEP 3: Subtract predicted walking noise: e[n] = d[n] - y[n]
            // -------------------------------------------------------------
            err_calc = raw_chest_ecg - dot_product[30:15];
            clean_ecg <= err_calc;

            // -------------------------------------------------------------
            // STEP 4: Update weights: w_i[n+1] = w_i[n] + mu * e[n] * x[n-i]
            // (Shift-right replaces costly floating-point multiplier)
            // -------------------------------------------------------------
            for (i = 0; i < NUM_TAPS; i = i + 1) begin
                weight_update = (err_calc * x_pipe[i]) >>> SHIFT_MU;
                weights[i] <= weights[i] + weight_update[15:0];
            end

            // -------------------------------------------------------------
            // STEP 5: Kinetic Motion Gate Evaluation
            // -------------------------------------------------------------
            if (chest_svm > MOTION_REST_THRESH) begin
                motion_gate_active <= 1'b1; // User is moving -> Suppress alert
            end else begin
                motion_gate_active <= 1'b0; // User is still -> Pre-arrest monitoring armed
            end

            // -------------------------------------------------------------
            // STEP 6: Multi-Modal Anomaly Verification (Never Trust ECG Alone)
            // -------------------------------------------------------------
            if ((err_calc > ECG_ANOMALY_BOUND) || (err_calc < -ECG_ANOMALY_BOUND)) begin
                ecg_ischemia_detected <= 1'b1;
            end else begin
                ecg_ischemia_detected <= 1'b0;
            end

            // Emergency alert fires ONLY if:
            // 1. ECG is abnormal
            // 2. Patient is at REST (motion_gate_active == 0)
            // 3. Arterial SpO2 is hypoxic (<88%)
            // 4. Cold sweat diaphoresis is surging (>350 uS)
            if (!motion_gate_active && 
                ecg_ischemia_detected && 
                (spo2_level < SPO2_CRITICAL_BOUND) && 
                (gsr_conductance > GSR_COLD_SWEAT_BOUND)) begin
                emergency_alert <= 1'b1;
            end else begin
                emergency_alert <= 1'b0;
            end
        end
    end

endmodule
