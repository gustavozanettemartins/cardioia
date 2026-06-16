"""
Métricas e visualizações para classificação ECG — Fase 4 CardioIA.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, classes: list[str]) -> dict:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "classification_report": classification_report(
            y_true, y_pred, target_names=classes, zero_division=0
        ),
    }


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    classes: list[str],
    title: str,
    out_path: Path,
) -> None:
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
    plt.title(title)
    plt.ylabel("Verdadeiro")
    plt.xlabel("Predito")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_training_history(history, out_path: Path, title: str = "Treinamento") -> None:
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history["accuracy"], label="treino")
    if "val_accuracy" in history.history:
        plt.plot(history.history["val_accuracy"], label="validação")
    plt.title(f"{title} — acurácia")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history["loss"], label="treino")
    if "val_loss" in history.history:
        plt.plot(history.history["val_loss"], label="validação")
    plt.title(f"{title} — loss")
    plt.legend()

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_metrics_comparison(metrics: dict[str, dict], out_path: Path) -> None:
    names = list(metrics.keys())
    keys = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
    labels = ["Acurácia", "Precisão", "Recall", "F1"]
    x = np.arange(len(keys))
    width = 0.35

    plt.figure(figsize=(9, 5))
    for i, name in enumerate(names):
        vals = [metrics[name][k] for k in keys]
        plt.bar(x + i * width, vals, width, label=name)

    plt.xticks(x + width / 2, labels)
    plt.ylim(0, 1.05)
    plt.ylabel("Score")
    plt.title("Comparação CNN simples vs Transfer Learning")
    plt.legend()
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
