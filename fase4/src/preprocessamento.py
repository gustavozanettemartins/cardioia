"""
Pipeline de pré-processamento de imagens ECG para a Fase 4 CardioIA.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_DIR = REPO_ROOT / "dataset" / "ecg_img"
LEGACY_DATASET_DIR = REPO_ROOT / "fase1" / "eletrocardiograma_dataset"
DEFAULT_PROCESSED_DIR = REPO_ROOT / "fase4" / "data" / "processed"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
DEFAULT_IMG_SIZE = (224, 224)
RANDOM_SEED = 42

# Dataset Kaggle (analiviafr) — rótulos por pasta train/test
KAGGLE_CLASSES = {"F", "N", "Q", "S", "V"}

# Demo sintético (fase1) — rótulos longos
DEMO_CLASSES = {
    "Normal Person",
    "Myocardial Infarction",
    "Abnormal Heartbeat",
    "Previous History of MI",
    "COVID-19",
}

VALID_CLASSES = KAGGLE_CLASSES | DEMO_CLASSES

CLASS_DISPLAY_NAMES = {
    "F": "F — batimento de fusão",
    "N": "N — batimento normal",
    "Q": "Q — batimento desconhecido / estimulado",
    "S": "S — ectópico supraventricular",
    "V": "V — ectópico ventricular",
    "Normal Person": "Normal Person",
    "Myocardial Infarction": "Myocardial Infarction",
    "Abnormal Heartbeat": "Abnormal Heartbeat",
    "Previous History of MI": "Previous History of MI",
    "COVID-19": "COVID-19",
}


def resolve_dataset_dir(path: Path | None = None) -> Path:
    if path is not None:
        return path
    if DEFAULT_DATASET_DIR.is_dir():
        return DEFAULT_DATASET_DIR
    return LEGACY_DATASET_DIR


def class_display_name(label: str) -> str:
    return CLASS_DISPLAY_NAMES.get(label, label)


def repo_root() -> Path:
    return REPO_ROOT


def has_train_test_layout(dataset_dir: Path) -> bool:
    return (dataset_dir / "train").is_dir() and (dataset_dir / "test").is_dir()


def list_class_names(dataset_dir: Path, split: str = "train") -> list[str]:
    root = dataset_dir / split
    return sorted(
        d.name
        for d in root.iterdir()
        if d.is_dir() and d.name in VALID_CLASSES
    )


def count_images_in_split(
    dataset_dir: Path,
    split: str,
    *,
    log: bool = False,
) -> dict[str, int]:
    """Conta imagens por classe sem montar lista completa de caminhos."""
    root = dataset_dir / split
    dist: dict[str, int] = {}
    for class_dir in sorted(root.iterdir()):
        if not class_dir.is_dir() or class_dir.name not in VALID_CLASSES:
            continue
        if log:
            print(f"  Contando {split}/{class_dir.name}...", flush=True)
        n = sum(
            1
            for p in class_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        )
        dist[class_dir.name] = n
    return dist


def summarize_train_test_dataset(dataset_dir: Path, *, log: bool = True) -> dict:
    """Resumo rápido para datasets grandes com pastas train/ e test/."""
    if log:
        print("Contando imagens em train/ (pode levar 1–2 min no /mnt/d/)...", flush=True)
    train_dist = count_images_in_split(dataset_dir, "train", log=log)
    if log:
        print("Contando imagens em test/...", flush=True)
    test_dist = count_images_in_split(dataset_dir, "test", log=log)
    classes = sorted(set(train_dist) | set(test_dist))
    return {
        "classes": classes,
        "train_dist": train_dist,
        "test_dist": test_dist,
        "train_total": sum(train_dist.values()),
        "test_total": sum(test_dist.values()),
        "total": sum(train_dist.values()) + sum(test_dist.values()),
    }


def class_weight_from_distribution(dist: dict[str, int]) -> dict[int, float]:
    classes = sorted(dist)
    counts = np.array([dist[c] for c in classes], dtype=np.float64)
    total = counts.sum()
    return {
        i: float(total / (len(counts) * c))
        for i, c in enumerate(counts)
        if c > 0
    }


def discover_images(dataset_dir: Path | None = None) -> tuple[list[Path], list[str]]:
    """Varre train/ e test/ (ou raiz) e retorna caminhos + rótulos (nome da pasta)."""
    dataset_dir = resolve_dataset_dir(dataset_dir)
    paths: list[Path] = []
    labels: list[str] = []

    search_roots = []
    for sub in ("train", "test"):
        p = dataset_dir / sub
        if p.is_dir():
            search_roots.append(p)

    if not search_roots and dataset_dir.is_dir():
        search_roots = [dataset_dir]

    for root in search_roots:
        for class_dir in sorted(root.iterdir()):
            if not class_dir.is_dir():
                continue
            label = class_dir.name
            if label not in VALID_CLASSES:
                continue
            for img_path in sorted(class_dir.rglob("*")):
                if img_path.is_file() and img_path.suffix.lower() in IMAGE_EXTENSIONS:
                    paths.append(img_path)
                    labels.append(label)

    return paths, labels


def load_image(path: Path | str, img_size: tuple[int, int] = DEFAULT_IMG_SIZE) -> np.ndarray:
    """Carrega imagem, converte para RGB, redimensiona e normaliza para [0, 1]."""
    with Image.open(path) as img:
        img = img.convert("RGB")
        img = img.resize(img_size, Image.Resampling.LANCZOS)
        arr = np.asarray(img, dtype=np.float32) / 255.0
    return arr


def preprocess_batch(
    paths: list[Path],
    img_size: tuple[int, int] = DEFAULT_IMG_SIZE,
) -> np.ndarray:
    return np.stack([load_image(p, img_size) for p in paths], axis=0)


def build_class_index(labels: list[str]) -> tuple[list[str], dict[str, int]]:
    classes = sorted(set(labels))
    class_to_idx = {c: i for i, c in enumerate(classes)}
    return classes, class_to_idx


def labels_to_indices(labels: list[str], class_to_idx: dict[str, int]) -> np.ndarray:
    return np.array([class_to_idx[l] for l in labels], dtype=np.int32)


def stratified_split(
    paths: list[Path],
    labels: list[str],
    val_size: float = 0.15,
    test_size: float = 0.15,
    random_state: int = RANDOM_SEED,
) -> dict[str, list]:
    """Divide em treino / validação / teste de forma estratificada."""
    _, class_to_idx = build_class_index(labels)
    y = labels_to_indices(labels, class_to_idx)

    idx = np.arange(len(paths))
    idx_train, idx_temp, y_train, y_temp = train_test_split(
        idx, y, test_size=(val_size + test_size), stratify=y, random_state=random_state
    )
    relative_test = test_size / (val_size + test_size)
    idx_val, idx_test, _, _ = train_test_split(
        idx_temp, y_temp, test_size=relative_test, stratify=y_temp, random_state=random_state
    )

    def pack(indices: np.ndarray) -> dict:
        return {
            "paths": [str(paths[i]) for i in indices],
            "labels": [labels[i] for i in indices],
            "y": y[indices].tolist(),
        }

    return {
        "train": pack(idx_train),
        "val": pack(idx_val),
        "test": pack(idx_test),
    }


def save_dataset_metadata(
    classes: list[str],
    dataset_dir: Path,
    layout: str = "train_test",
    out_dir: Path = DEFAULT_PROCESSED_DIR,
) -> Path:
    """Salva metadados leves (sem listar dezenas de milhares de caminhos)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        rel = dataset_dir.relative_to(REPO_ROOT)
    except ValueError:
        rel = dataset_dir
    payload = {
        "classes": classes,
        "class_labels": {c: class_display_name(c) for c in classes},
        "dataset_dir": str(rel).replace("\\", "/"),
        "layout": layout,
        "img_size": list(DEFAULT_IMG_SIZE),
    }
    out_file = out_dir / "splits.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return out_file


def save_splits(splits: dict, classes: list[str], out_dir: Path = DEFAULT_PROCESSED_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "classes": classes,
        "class_labels": {c: class_display_name(c) for c in classes},
        "img_size": list(DEFAULT_IMG_SIZE),
        "layout": "path_splits",
        "splits": splits,
    }
    out_file = out_dir / "splits.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return out_file


def load_splits(processed_dir: Path = DEFAULT_PROCESSED_DIR) -> dict:
    with open(processed_dir / "splits.json", encoding="utf-8") as f:
        return json.load(f)


def class_distribution(labels: list[str]) -> dict[str, int]:
    dist: dict[str, int] = {}
    for label in labels:
        dist[label] = dist.get(label, 0) + 1
    return dict(sorted(dist.items()))


def build_tf_datasets(
    dataset_dir: Path | None = None,
    img_size: tuple[int, int] = DEFAULT_IMG_SIZE,
    batch_size: int = 32,
    val_split: float = 0.15,
    seed: int = RANDOM_SEED,
):
    """Cria datasets TensorFlow a partir de train/ e test/ (eficiente para datasets grandes)."""
    from tensorflow import keras

    dataset_dir = resolve_dataset_dir(dataset_dir)
    train_dir = dataset_dir / "train"
    test_dir = dataset_dir / "test"

    train_ds = keras.utils.image_dataset_from_directory(
        train_dir,
        validation_split=val_split,
        subset="training",
        seed=seed,
        image_size=img_size,
        batch_size=batch_size,
        label_mode="int",
    )
    val_ds = keras.utils.image_dataset_from_directory(
        train_dir,
        validation_split=val_split,
        subset="validation",
        seed=seed,
        image_size=img_size,
        batch_size=batch_size,
        label_mode="int",
    )
    test_ds = keras.utils.image_dataset_from_directory(
        test_dir,
        image_size=img_size,
        batch_size=batch_size,
        label_mode="int",
        shuffle=False,
    )

    classes = list(train_ds.class_names)
    rescale = lambda x, y: (x / 255.0, y)
    train_ds = train_ds.map(rescale)
    val_ds = val_ds.map(rescale)
    test_ds = test_ds.map(rescale)

    return train_ds, val_ds, test_ds, classes
