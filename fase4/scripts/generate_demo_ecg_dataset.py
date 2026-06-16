"""
Gera imagens ECG sintéticas para desenvolvimento local quando o Kaggle não está disponível.

Substitua por dados reais via download_ecg_dataset.py quando possível.
"""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = REPO_ROOT / "fase1" / "eletrocardiograma_dataset"

CLASSES = [
    "Normal Person",
    "Myocardial Infarction",
    "Abnormal Heartbeat",
    "Previous History of MI",
    "COVID-19",
]

SPLITS = {"train": 80, "test": 20}


def _grid(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    for x in range(0, w, 20):
        draw.line([(x, 0), (x, h)], fill=(240, 230, 230))
    for y in range(0, h, 20):
        draw.line([(0, y), (w, y)], fill=(240, 230, 230))
    for x in range(0, w, 100):
        draw.line([(x, 0), (x, h)], fill=(220, 200, 200), width=1)
    for y in range(0, h, 100):
        draw.line([(0, y), (w, y)], fill=(220, 200, 200), width=1)


def _trace_normal(w: int, h: int, rng: random.Random) -> list[tuple[int, int]]:
    mid = h // 2
    pts: list[tuple[int, int]] = []
    x = 0
    while x < w - 10:
        beat = int(rng.uniform(90, 130))
        for i in range(beat):
            if x >= w:
                break
            y = mid + int(8 * np.sin(i / 6))
            if i == beat // 3:
                y -= 35
            elif i == beat // 3 + 1:
                y += 50
            elif i == beat // 3 + 2:
                y -= 15
            pts.append((x, y))
            x += 1
    return pts


def _trace_mi(w: int, h: int, rng: random.Random) -> list[tuple[int, int]]:
    pts = _trace_normal(w, h, rng)
    for i, (x, y) in enumerate(pts):
        if 0.25 * w < x < 0.55 * w:
            pts[i] = (x, y - 25)
    return pts


def _trace_abnormal(w: int, h: int, rng: random.Random) -> list[tuple[int, int]]:
    mid = h // 2
    pts: list[tuple[int, int]] = []
    x = 0
    while x < w - 5:
        beat = int(rng.uniform(40, 180))
        for i in range(beat):
            if x >= w:
                break
            y = mid + int(rng.uniform(-20, 20))
            if i == beat // 4:
                y -= rng.randint(20, 45)
            pts.append((x, y))
            x += 1
    return pts


def _trace_history(w: int, h: int, rng: random.Random) -> list[tuple[int, int]]:
    pts = _trace_normal(w, h, rng)
    for i, (x, y) in enumerate(pts):
        if x > 0.6 * w and rng.random() < 0.08:
            pts[i] = (x, y + rng.randint(5, 15))
    return pts


def _trace_covid(w: int, h: int, rng: random.Random) -> list[tuple[int, int]]:
    pts = _trace_abnormal(w, h, rng)
    for i, (x, y) in enumerate(pts):
        if 0.1 * w < x < 0.3 * w:
            pts[i] = (x, y + int(10 * np.sin(x / 15)))
    return pts


GENERATORS = {
    "Normal Person": _trace_normal,
    "Myocardial Infarction": _trace_mi,
    "Abnormal Heartbeat": _trace_abnormal,
    "Previous History of MI": _trace_history,
    "COVID-19": _trace_covid,
}


def generate_image(class_name: str, seed: int) -> Image.Image:
    rng = random.Random(seed)
    w, h = 400, 260
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    _grid(draw, w, h)
    pts = GENERATORS[class_name](w, h, rng)
    if len(pts) > 1:
        draw.line(pts, fill=(20, 20, 120), width=2)
    return img


def main() -> None:
    for split, count in SPLITS.items():
        for cls in CLASSES:
            out_dir = DATASET_DIR / split / cls
            out_dir.mkdir(parents=True, exist_ok=True)
            for i in range(count):
                img = generate_image(cls, seed=hash((split, cls, i)) % (2**31))
                img.save(out_dir / f"{cls.replace(' ', '_').lower()}_{i:04d}.png")

    total = sum(SPLITS.values()) * len(CLASSES)
    print(f"Geradas {total} imagens sintéticas em {DATASET_DIR}")
    print("Para dados reais: python fase4/scripts/download_ecg_dataset.py")


if __name__ == "__main__":
    main()
