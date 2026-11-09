# Author: Lead + agent | Task: evaluation and metrics | PR: TBD
# Status: original implementation by this team. Uses sklearn.metrics to compute the metrics (calls only, see NOTICE.md)
"""Evaluation: 10 metrics plus the confusion matrix.

Definitions are documented in docs/RESULTS.md section 4. **positive = defect**, so reversing the
definition flips every metric.
Confusion matrix convention: [[TN, FP], [FN, TP]], rows = true labels, columns = predictions,
order nondefect -> defect.
"""

from __future__ import annotations

METRIC_NAMES = [
    "accuracy", "precision", "recall", "f1", "mcc",
    "kappa", "auc", "map", "sensitivity", "specificity",
]


def compute_metrics(y_true, y_prob, threshold: float = 0.5) -> dict:
    """y_true: array-like of 0/1; y_prob: predicted probability of defect. Returns 10 metrics in [0, 1]."""
    import numpy as np
    from sklearn.metrics import (accuracy_score, average_precision_score,
                                 cohen_kappa_score, f1_score,
                                 matthews_corrcoef, precision_score,
                                 recall_score, roc_auc_score)

    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob, dtype=float)
    y_pred = (y_prob >= threshold).astype(int)

    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    try:
        auc = roc_auc_score(y_true, y_prob)
    except ValueError:
        auc = 0.0
    try:
        ap = average_precision_score(y_true, y_prob)
    except ValueError:
        ap = 0.0
    # With only one class present sklearn returns nan (common for smoke tests / tiny test sets);
    # record 0.0 consistently so it stays visible in the logs.
    if not np.isfinite(auc):
        auc = 0.0
    if not np.isfinite(ap):
        ap = 0.0

    result = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)) if len(set(y_true.tolist())) > 1 else 0.0,
        "kappa": float(cohen_kappa_score(y_true, y_pred)) if len(set(y_true.tolist())) > 1 else 0.0,
        "auc": float(auc),
        "map": float(ap),
        "sensitivity": float(recall),
        "specificity": float(specificity),
    }
    # Floating-point error can push a value slightly above 1.0 (e.g. 1.0000000000000002); clamp to [0, 1]
    return {k: max(0.0, min(1.0, v)) if isinstance(v, float) else v for k, v in result.items()}


def confusion_matrix_2x2(y_true, y_prob, threshold: float = 0.5) -> list[list[int]]:
    """Return [[TN, FP], [FN, TP]]."""
    import numpy as np

    y_true = np.asarray(y_true).astype(int)
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    return [[tn, fp], [fn, tp]]


def plot_confusion(cm: list[list[int]], title: str, out_path) -> None:
    """Draw a 2x2 confusion matrix for the report figures."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(3.6, 3.2))
    im = ax.imshow(cm, cmap="Blues")
    labels = ["nondefect", "defect"]
    ax.set_xticks([0, 1], labels)
    ax.set_yticks([0, 1], labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i][j]), ha="center", va="center", color="black")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_curves(train_log: list[dict], out_path) -> None:
    """Training/validation loss and accuracy curves."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    epochs = [r["epoch"] for r in train_log]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    axes[0].plot(epochs, [r["train_loss"] for r in train_log], label="train")
    axes[0].plot(epochs, [r["val_loss"] for r in train_log], label="val")
    axes[0].set_title("Loss")
    axes[0].set_xlabel("epoch")
    axes[0].legend()
    axes[1].plot(epochs, [r["train_acc"] for r in train_log], label="train")
    axes[1].plot(epochs, [r["val_acc"] for r in train_log], label="val")
    axes[1].set_title("Accuracy")
    axes[1].set_xlabel("epoch")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
