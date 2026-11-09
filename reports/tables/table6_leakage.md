### Table 6 — Leakage control experiment on a re-augmented dataset (D2'): random split versus source-grouped split, under two training-set regimes.

| Setting | Train frac. | Model | Acc. random | Acc. grouped | Δ acc. | F1 random | F1 grouped | Δ F1 | AUC random | AUC grouped | Train n random | Train n grouped |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | 100% | VGG16 | 1.0000 | 0.9882 | +0.0118 | 1.0000 | 0.9883 | +0.0117 | 1.0000 | 0.9998 | 2,087 | 2,079 |
| full | 100% | ResNet50 | 0.9916 | 0.9966 | -0.0050 | 0.9916 | 0.9966 | -0.0050 | 0.9999 | 0.9999 | 2,087 | 2,079 |
| full | 100% | MobileNetV2 | 0.9983 | 1.0000 | -0.0017 | 0.9983 | 1.0000 | -0.0017 | 1.0000 | 1.0000 | 2,087 | 2,079 |
| small15 | 15% | VGG16 | 0.9698 | 0.9731 | -0.0033 | 0.9691 | 0.9733 | -0.0043 | 0.9990 | 0.9977 | 313 | 312 |
| small15 | 15% | ResNet50 | 0.9664 | 0.9764 | -0.0100 | 0.9656 | 0.9764 | -0.0108 | 0.9983 | 0.9978 | 313 | 312 |
| small15 | 15% | MobileNetV2 | 0.9799 | 0.9949 | -0.0151 | 0.9795 | 0.9950 | -0.0154 | 0.9996 | 0.9999 | 313 | 312 |

> D2' is re-augmented from D1 with source IDs preserved, so every image can be traced back to its source photograph. n_test = 596 in every row; Δ = random − source-grouped (a positive Δ means the leak-prone split scores higher). The full-data regime already sits at the accuracy ceiling, which is why the 15%-training regime is reported as well.
