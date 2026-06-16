"""
Baixa o dataset ECG Images do Kaggle para fase1/eletrocardiograma_dataset/.

Pré-requisitos:
  1. pip install kaggle
  2. Credenciais em ~/.kaggle/kaggle.json (Account → Create New Token no Kaggle)

Uso:
  python fase4/scripts/download_ecg_dataset.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = REPO_ROOT / "dataset" / "ecg_img"
KAGGLE_DATASET = "analiviafr/ecg-images"


def main() -> int:
    try:
        import kaggle  # noqa: F401
    except ImportError:
        print("Instale o cliente Kaggle: pip install kaggle")
        return 1

    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    tmp = DATASET_DIR / "_download_tmp"
    tmp.mkdir(exist_ok=True)

    print(f"Baixando {KAGGLE_DATASET} para {tmp} ...")
    result = subprocess.run(
        ["kaggle", "datasets", "download", "-d", KAGGLE_DATASET, "-p", str(tmp), "--unzip"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout)
        print(
            "\nSem credenciais Kaggle? Gere um dataset demo:\n"
            "  python fase4/scripts/generate_demo_ecg_dataset.py"
        )
        shutil.rmtree(tmp, ignore_errors=True)
        return 1

    # Mover conteúdo extraído para DATASET_DIR (estrutura varia por versão do zip)
    for item in tmp.iterdir():
        dest = DATASET_DIR / item.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        shutil.move(str(item), str(dest))

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Dataset disponível em {DATASET_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
