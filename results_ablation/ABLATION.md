# No-transfer ablation — mobilenet_v2

All cells are the **mean over the three optimisers** (Adam / SGD / RMSprop), same splits, same head, same hyper-parameters; only the backbone initialisation differs.

| Configuration | D1 accuracy / f1 / mcc | D2 accuracy / f1 / mcc |
|---|---|---|
| ImageNet pretrained + frozen conv (main method) | 1.0000 / 1.0000 / 1.0000  (n=3) | 0.9950 / 0.9920 / 0.9884  (n=3) |
| random init + frozen conv (weights only) | 0.5000 / 0.6667 / 0.0000  (n=3) | 0.7717 / 0.4878 / 0.4002  (n=3) |
| random init + all parameters trainable (from scratch) | 1.0000 / 1.0000 / 1.0000  (n=3) | 0.9950 / 0.9920 / 0.9885  (n=3) |

## Per-run detail

| dataset | init | optimizer | accuracy | f1 | mcc |
|---|---|---|---|---|---|
| D1 | rand_frozen | adam | 0.5000 | 0.6667 | 0.0000 |
| D1 | rand_frozen | rmsprop | 0.5000 | 0.6667 | 0.0000 |
| D1 | rand_frozen | sgd | 0.5000 | 0.6667 | 0.0000 |
| D1 | rand_full | adam | 1.0000 | 1.0000 | 1.0000 |
| D1 | rand_full | rmsprop | 1.0000 | 1.0000 | 1.0000 |
| D1 | rand_full | sgd | 1.0000 | 1.0000 | 1.0000 |
| D1 | transfer | adam | 1.0000 | 1.0000 | 1.0000 |
| D1 | transfer | rmsprop | 1.0000 | 1.0000 | 1.0000 |
| D1 | transfer | sgd | 1.0000 | 1.0000 | 1.0000 |
| D2 | rand_frozen | adam | 0.8358 | 0.7442 | 0.6238 |
| D2 | rand_frozen | rmsprop | 0.7927 | 0.7191 | 0.5769 |
| D2 | rand_frozen | sgd | 0.6866 | 0.0000 | 0.0000 |
| D2 | rand_full | adam | 0.9950 | 0.9920 | 0.9885 |
| D2 | rand_full | rmsprop | 0.9950 | 0.9920 | 0.9885 |
| D2 | rand_full | sgd | 0.9950 | 0.9920 | 0.9885 |
| D2 | transfer | adam | 0.9950 | 0.9920 | 0.9884 |
| D2 | transfer | rmsprop | 0.9950 | 0.9920 | 0.9884 |
| D2 | transfer | sgd | 0.9950 | 0.9920 | 0.9885 |
