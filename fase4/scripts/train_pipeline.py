"""
Pipeline completo: pré-processamento + treino CNN + métricas (Fase 4).

Uso:
  python fase4/scripts/train_pipeline.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Menos ruído do TensorFlow; saída Python sem buffer
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "1")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

import numpy as np
from tensorflow import keras

FASE4_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = FASE4_DIR.parent
sys.path.insert(0, str(FASE4_DIR))

from src.avaliacao import (  # noqa: E402
    compute_metrics,
    plot_confusion_matrix,
    plot_metrics_comparison,
    plot_training_history,
)
from src.modelos import build_cnn_simples, build_transfer_learning  # noqa: E402
from src.preprocessamento import (  # noqa: E402
    DEFAULT_PROCESSED_DIR,
    build_class_index,
    build_tf_datasets,
    class_weight_from_distribution,
    discover_images,
    has_train_test_layout,
    preprocess_batch,
    resolve_dataset_dir,
    save_dataset_metadata,
    save_splits,
    stratified_split,
    summarize_train_test_dataset,
)

MODELS_DIR = FASE4_DIR / "models"
IMAGES_DIR = FASE4_DIR / "docs" / "imagens"
BATCH_SIZE = 32


def _epochs_for_dataset(n_images: int) -> tuple[int, int]:
    if n_images > 10_000:
        return 3, 3
    if n_images > 2_000:
        return 5, 4
    return 8, 6


def load_xy(split: dict) -> tuple[np.ndarray, np.ndarray]:
    paths = [Path(p) for p in split["paths"]]
    X = preprocess_batch(paths)
    y = np.array(split["y"], dtype=np.int32)
    return X, y


def predict_dataset(model: keras.Model, dataset) -> tuple[np.ndarray, np.ndarray]:
    y_true: list[int] = []
    y_pred: list[int] = []
    for images, labels in dataset:
        probs = model.predict(images, verbose=0)
        y_pred.extend(np.argmax(probs, axis=1).tolist())
        y_true.extend(labels.numpy().tolist())
    return np.array(y_true), np.array(y_pred)


def train_and_evaluate_arrays(
    name: str,
    model: keras.Model,
    X_train,
    y_train,
    X_val,
    y_val,
    X_test,
    y_test,
    classes: list[str],
    epochs: int,
    model_out: Path,
) -> dict:
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=3, restore_best_weights=True
        ),
        keras.callbacks.ModelCheckpoint(
            str(model_out), monitor="val_accuracy", save_best_only=True
        ),
    ]
    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )
    y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
    metrics = compute_metrics(y_test, y_pred, classes)
    plot_training_history(history, IMAGES_DIR / f"historico_{name}.png", title=name)
    plot_confusion_matrix(
        y_test,
        y_pred,
        classes,
        title=f"Matriz de confusão — {name}",
        out_path=IMAGES_DIR / f"matriz_confusao_{name}.png",
    )
    return metrics


def train_and_evaluate_tf(
    name: str,
    model: keras.Model,
    train_ds,
    val_ds,
    test_ds,
    classes: list[str],
    epochs: int,
    model_out: Path,
    class_weight: dict[int, float] | None = None,
) -> dict:
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=2, restore_best_weights=True
        ),
        keras.callbacks.ModelCheckpoint(
            str(model_out), monitor="val_accuracy", save_best_only=True
        ),
    ]
    print(f"\n>>> Treinando {name} — {epochs} época(s)...", flush=True)
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks,
        class_weight=class_weight,
        verbose=1,
    )
    y_test, y_pred = predict_dataset(model, test_ds)
    metrics = compute_metrics(y_test, y_pred, classes)
    plot_training_history(history, IMAGES_DIR / f"historico_{name}.png", title=name)
    plot_confusion_matrix(
        y_test,
        y_pred,
        classes,
        title=f"Matriz de confusão — {name}",
        out_path=IMAGES_DIR / f"matriz_confusao_{name}.png",
    )
    return metrics


def compute_class_weight(labels: list[str]) -> dict[int, float]:
    _, class_to_idx = build_class_index(labels)
    counts = np.zeros(len(class_to_idx))
    for label in labels:
        counts[class_to_idx[label]] += 1
    total = counts.sum()
    return {
        i: float(total / (len(counts) * c)) for i, c in enumerate(counts) if c > 0
    }


def main() -> int:
    print("CardioIA — train_pipeline.py", flush=True)
    dataset_dir = resolve_dataset_dir()
    if not dataset_dir.is_dir():
        print(f"Dataset não encontrado em {dataset_dir}")
        return 1

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    num_classes = 0
    metrics_cnn = None
    metrics_transfer = None
    class_weight = None
    epochs_simple = 8
    epochs_transfer = 6

    if has_train_test_layout(dataset_dir):
        summary = summarize_train_test_dataset(dataset_dir)
        classes = summary["classes"]
        total = summary["total"]
        if total < 20:
            print("Dataset insuficiente.")
            return 1
        epochs_simple, epochs_transfer = _epochs_for_dataset(total)
        class_weight = class_weight_from_distribution(summary["train_dist"])

        print(f"\nDataset: {dataset_dir}", flush=True)
        print(f"Classes ({len(classes)}): {classes}", flush=True)
        print(f"Train: {summary['train_total']} | Test: {summary['test_total']}", flush=True)
        print(f"Épocas CNN/TL: {epochs_simple}/{epochs_transfer}", flush=True)

        save_dataset_metadata(classes, dataset_dir, out_dir=DEFAULT_PROCESSED_DIR)
        print("\nMontando datasets TensorFlow (train/val/test)...", flush=True)
        train_ds, val_ds, test_ds, tf_classes = build_tf_datasets(
            dataset_dir, batch_size=BATCH_SIZE
        )
        classes = tf_classes
        num_classes = len(classes)

        print("\nConstruindo CNN simples...", flush=True)
        cnn = build_cnn_simples(num_classes=num_classes)
        metrics_cnn = train_and_evaluate_tf(
            "cnn_simples",
            cnn,
            train_ds,
            val_ds,
            test_ds,
            classes,
            epochs_simple,
            MODELS_DIR / "ecg_cnn_simples_best.keras",
            class_weight=class_weight,
        )

        print("\nConstruindo VGG16 (transfer learning; baixa pesos ImageNet na 1ª vez)...", flush=True)
        transfer = build_transfer_learning(num_classes=num_classes, backbone="vgg16")
        metrics_transfer = train_and_evaluate_tf(
            "transfer_learning",
            transfer,
            train_ds,
            val_ds,
            test_ds,
            classes,
            epochs_transfer,
            MODELS_DIR / "ecg_transfer_best.keras",
            class_weight=class_weight,
        )
    else:
        print("Escaneando imagens...", flush=True)
        paths, labels = discover_images(dataset_dir)
        if len(paths) < 20:
            print("Dataset insuficiente. Verifique dataset/ecg_img ou generate_demo_ecg_dataset.py")
            return 1

        classes, _ = build_class_index(labels)
        epochs_simple, epochs_transfer = _epochs_for_dataset(len(paths))
        class_weight = compute_class_weight(labels)

        print(f"\nDataset: {dataset_dir}", flush=True)
        print(f"Classes ({len(classes)}): {classes}", flush=True)
        print(f"Total imagens: {len(paths)} | epochs CNN/TL: {epochs_simple}/{epochs_transfer}", flush=True)

        splits = stratified_split(paths, labels)
        save_splits(splits, classes, DEFAULT_PROCESSED_DIR)
        X_train, y_train = load_xy(splits["train"])
        X_val, y_val = load_xy(splits["val"])
        X_test, y_test = load_xy(splits["test"])
        print(f"Treino: {len(y_train)} | Val: {len(y_val)} | Teste: {len(y_test)}")

        cnn = build_cnn_simples(num_classes=num_classes)
        metrics_cnn = train_and_evaluate_arrays(
            "cnn_simples",
            cnn,
            X_train,
            y_train,
            X_val,
            y_val,
            X_test,
            y_test,
            classes,
            epochs_simple,
            MODELS_DIR / "ecg_cnn_simples_best.keras",
        )

        transfer = build_transfer_learning(num_classes=num_classes, backbone="vgg16")
        metrics_transfer = train_and_evaluate_arrays(
            "transfer_learning",
            transfer,
            X_train,
            y_train,
            X_val,
            y_val,
            X_test,
            y_test,
            classes,
            epochs_transfer,
            MODELS_DIR / "ecg_transfer_best.keras",
        )

    plot_metrics_comparison(
        {"CNN simples": metrics_cnn, "Transfer Learning": metrics_transfer},
        IMAGES_DIR / "metricas_comparacao.png",
    )

    summary = {
        "CNN simples": {
            "accuracy": metrics_cnn["accuracy"],
            "precision_macro": metrics_cnn["precision_macro"],
            "recall_macro": metrics_cnn["recall_macro"],
            "f1_macro": metrics_cnn["f1_macro"],
        },
        "Transfer Learning (VGG16)": {
            "accuracy": metrics_transfer["accuracy"],
            "precision_macro": metrics_transfer["precision_macro"],
            "recall_macro": metrics_transfer["recall_macro"],
            "f1_macro": metrics_transfer["f1_macro"],
        },
    }
    with open(IMAGES_DIR / "metricas_resumo.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    for name, m in [("CNN simples", metrics_cnn), ("Transfer Learning (VGG16)", metrics_transfer)]:
        print(f"\n=== {name} ===")
        print(f"Acurácia: {m['accuracy']:.4f}")
        print(m["classification_report"])

    print(f"\nModelos salvos em {MODELS_DIR}")
    print(f"Figuras em {IMAGES_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
