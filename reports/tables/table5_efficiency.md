### Table 5 — Inference cost per image (batch size 1, 224×224)

| Model | Total params | GFLOPs | CPU ms/img | GPU ms/img |
|---|---|---|---|---|
| MobileNetV2 | 2,305,986 | 0.599 | 22.9 | 5.3 |
| EfficientNet-B0 | 4,089,662 | 0.769 | 34.6 | 8.0 |
| ResNet50 | 23,639,298 | 8.175 | 82.8 | 6.1 |
| Xception | 20,938,218 | 9.102 | 103.4 | 6.3 |
| InceptionResNetV2 | 54,404,962 | 12.935 | 172.2 | 30.1 |
| EfficientNetV2-M | 52,940,470 | 10.722 | 161.8 | 25.1 |
| EfficientNet-B7 | 63,950,994 | 10.335 | 196.4 | 27.2 |
| ResNet101 | 42,631,426 | 15.599 | 132.2 | 11.1 |
| VGG16 | 134,293,506 | 30.693 | 165.3 | 13.3 |
| VGG19 | 139,603,202 | 39.017 | 192.6 | 17.1 |
| NASNet-Large | 84,978,392 | 20.560 | 389.5 | 39.9 |

> CPU timings: mean of 20 forward passes after 5 warm-up iterations, batch size 1. GPU timings pending (needs a Kaggle T4 session).
