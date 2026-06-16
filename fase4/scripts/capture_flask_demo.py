"""Gera imagem de demonstração do resultado Flask (probabilidades)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

FASE4 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FASE4))

from src.inferencia import predict_image  # noqa: E402


def main() -> None:
    sample_dir = FASE4.parent / "fase1" / "eletrocardiograma_dataset" / "test" / "Normal Person"
    sample = next(sample_dir.glob("*.png"))
    result = predict_image(sample)

    names = list(result["probabilidades"].keys())
    probs = [result["probabilidades"][n] for n in names]

    plt.figure(figsize=(9, 5))
    plt.barh(names, probs, color="#1565c0")
    plt.xlabel("Probabilidade")
    plt.title(
        f"CardioIA Flask — demo\nClasse: {result['classe']} ({result['confianca']*100:.1f}%)"
    )
    plt.xlim(0, 1)
    plt.tight_layout()
    out = FASE4 / "docs" / "imagens" / "flask-demo.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Salvo: {out}")


if __name__ == "__main__":
    main()
