#ifndef MODEL_WEIGHTS_H
#define MODEL_WEIGHTS_H

// Auto-generated TinyML Autoencoder Model for CardioSense
// Input: 8 features -> Latent: 2 features -> Output: 8 features

#define AE_INPUT_DIM   8
#define AE_HIDDEN_DIM  4
#define AE_LATENT_DIM  2

// Baseline Anomaly Detection Threshold (MSE)
// Samples with Reconstruction MSE > AE_ANOMALY_THRESHOLD are flagged as potential precursors
const float AE_ANOMALY_THRESHOLD = 0.008113f;

// Layer 1: 8 -> 4 (ReLU)
const float W1[AE_INPUT_DIM][AE_HIDDEN_DIM] = {
    { -0.0099974f, -0.1838933f, -0.5156183f, +0.0969872f },
    { -0.6555152f, +0.2885519f, +0.8661420f, +0.2709761f },
    { +0.0224813f, -0.1611946f, +0.0538827f, -0.7629652f },
    { +0.2366356f, -0.3355448f, -0.6102670f, +0.0681606f },
    { -1.0616826f, -0.3299847f, -0.3199732f, +0.1688846f },
    { -0.2390980f, +0.4139607f, -0.1976248f, +0.5634034f },
    { -0.0206789f, -0.0729889f, -0.0785249f, +0.5370153f },
    { -0.0553025f, +0.0025572f, -0.2012150f, -0.6151161f }
};
const float b1[AE_HIDDEN_DIM] = { +1.0779459f, +0.0000000f, +1.3956431f, +0.0000000f };

// Layer 2: 4 -> 2 (ReLU Bottleneck)
const float W2[AE_HIDDEN_DIM][AE_LATENT_DIM] = {
    { +0.4674841f, -1.6579422f },
    { -0.2617337f, +0.1162343f },
    { +1.0560122f, +1.2248493f },
    { +0.7023860f, -0.2061368f }
};
const float b2[AE_LATENT_DIM] = { +0.1725247f, +0.2897297f };

// Layer 3: 2 -> 4 (ReLU)
const float W3[AE_LATENT_DIM][AE_HIDDEN_DIM] = {
    { +0.2850148f, -1.2616004f, +1.7391461f, -0.1564753f },
    { -1.0232707f, -0.6390601f, -0.4848760f, -0.3927849f }
};
const float b3[AE_HIDDEN_DIM] = { +1.2592807f, +0.0000000f, -0.4312698f, +0.0000000f };

// Layer 4: 4 -> 8 (Sigmoid Output)
const float W4[AE_HIDDEN_DIM][AE_INPUT_DIM] = {
    { +0.6655898f, -1.4340534f, -0.1088736f, +0.9570201f, -0.4470079f, +0.1042104f, +0.0649248f, +0.7681118f },
    { -0.3519756f, -0.6075447f, +0.0883069f, +0.4018700f, -0.2217132f, -0.2280536f, -0.1292036f, -0.1880554f },
    { -1.0375859f, +0.6052892f, +0.3062341f, -0.9256401f, -1.3081163f, -0.6474937f, -0.1077252f, -1.7660682f },
    { +0.3890461f, +0.6203431f, +0.6956181f, -0.1015961f, -0.2040215f, +0.0406605f, +0.0523959f, -0.2997448f }
};
const float b4[AE_INPUT_DIM] = { +0.3995411f, -1.1359150f, +2.2075222f, +0.0637343f, +2.6197345f, -0.2514956f, -1.1479934f, +0.1455240f };

#endif // MODEL_WEIGHTS_H
