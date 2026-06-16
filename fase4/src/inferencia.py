"""
Inferência com modelo treinado — reutilizado pelo Flask e notebooks.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from tensorflow import keras

from .preprocessamento import DEFAULT_IMG_SIZE, load_image, load_splits

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = REPO_ROOT / "fase4" / "models" / "ecg_transfer_best.keras"


class ECGClassifier:
    def __init__(
        self,
        model_path: Path | str = DEFAULT_MODEL_PATH,
        processed_dir: Path | None = None,
    ):
        self.model_path = Path(model_path)
        self.model = keras.models.load_model(self.model_path)
        meta = load_splits(processed_dir) if processed_dir else load_splits()
        self.classes: list[str] = meta["classes"]
        self.class_labels: dict[str, str] = meta.get("class_labels", {})
        self.img_size = tuple(meta.get("img_size", list(DEFAULT_IMG_SIZE)))

    def predict(self, image_path: Path | str) -> dict:
        arr = load_image(image_path, self.img_size)
        batch = np.expand_dims(arr, axis=0)
        probs = self.model.predict(batch, verbose=0)[0]
        idx = int(np.argmax(probs))
        label = self.classes[idx]
        return {
            "classe": label,
            "classe_exibicao": self.class_labels.get(label, label),
            "confianca": float(probs[idx]),
            "probabilidades": {
                self.class_labels.get(self.classes[i], self.classes[i]): float(probs[i])
                for i in range(len(self.classes))
            },
        }


def predict_image(
    image_path: Path | str,
    model_path: Path | str = DEFAULT_MODEL_PATH,
) -> dict:
    return ECGClassifier(model_path=model_path).predict(image_path)
